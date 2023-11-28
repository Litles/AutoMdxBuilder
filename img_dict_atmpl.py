#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-16 00:00:27
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.5

import os
import re
from tomlkit import dumps, loads, array, comment, nl
from colorama import Fore


class ImgDictAtmpl:
    """ 图像词典（模板A） """
    def __init__(self, amb):
        self.settings = amb.settings
        self.func = amb.func

    def make_source_file(self):
        """ 制作预备 txt 源文本 """
        # 检查原材料
        check_result = self._check_raw_files()
        # 开始制作
        if check_result:
            print('\n材料检查通过, 开始制作词典……\n')
            # 清空临时目录下所有文件
            for fname in os.listdir(self.settings.dir_output_tmp):
                fpath = os.path.join(self.settings.dir_output_tmp, fname)
                if os.path.isfile(fpath):
                    os.remove(fpath)
            # 预定义输出文件名
            file_final_txt = os.path.join(self.settings.dir_output_tmp, self.settings.fname_final_txt)
            file_dict_info = os.path.join(self.settings.dir_output_tmp, self.settings.fname_dict_info)
            dir_imgs_tmp = os.path.join(self.settings.dir_output_tmp, self.settings.dname_imgs)
            # 1.分步生成各部分源文本
            file_1 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entries_img)  # 图像词条
            file_2 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entry_toc)  # 总目词条
            file_3 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_headword)  # 词目重定向
            file_4 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_syn)  # 同义词重定向
            file_5 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_st)  # 繁简重定向
            # (1) 生成主体(图像)词条
            if check_result[1]:
                imgs, n_len = self.func.make_entries_img(check_result[2], dir_imgs_tmp, file_1, self.settings.navi_items)
            else:
                imgs, n_len = self.func.make_entries_img(check_result[2], dir_imgs_tmp, file_1, None)
            # (2) 生成总目词条
            if check_result[1]:
                self._make_entry_toc(check_result[1], file_2)
            # (3) 生成词目重定向
            headwords = self._make_redirects_headword(check_result[0], file_3, n_len, check_result[1])
            # (4) 生成同义词重定向
            if check_result[3]:
                headwords.append(self.func.make_redirects_syn(check_result[3], file_4))
            # (5) 生成繁简通搜重定向
            if self.settings.simp_trad_flg:
                self.func.make_redirects_st(headwords, file_5)
            # 2.合并成最终 txt 源文本
            entry_total = self.func.merge_and_count([file_1, file_2, file_3, file_4, file_5], file_final_txt)
            print(f'\n源文本 "{self.settings.fname_final_txt}"（共 {entry_total} 词条）生成完毕！')
            # 3.生成 info.html
            self.func.generate_info_html(check_result[4], file_dict_info, self.settings.name, 'A')
            # 返回制作结果
            return [file_final_txt, dir_imgs_tmp, file_dict_info]
        else:
            print(Fore.RED + "\n材料检查不通过, 请确保材料准备无误再执行程序" + Fore.RESET)
            return None

    def extract_final_txt(self, file_final_txt, out_dir, dict_name):
        """ 从模板A词典的源 txt 文本中提取 index, toc, syns 信息 """
        # 1.提取信息
        with open(file_final_txt, 'r', encoding='utf-8') as fr:
            text = fr.read()
            # 识别 name_abbr, body_start
            body_start = 1
            names = []
            for m in re.findall(r'^<div class="main-img"><div class="left"><div class="pic"><img src="/([A-Z|\d]+)_A(\d+)\.\w+">', text, flags=re.M):
                if int(m[1])+1 > body_start:
                    body_start = int(m[1])+1
                if m[0].upper() not in names:
                    names.append(m[0].upper())
            if len(names) > 0:
                name_abbr = names[0]
            else:
                print(Fore.MAGENTA + "WARN: " + Fore.RESET + "未识别到词典缩略字母, 已设置默认值")
                name_abbr = 'XXXXCD'
            # 提取 navi_items
            navi_items = array()
            top_navi = re.search(r'^<div class="top-navi">(.*?)</div>$', text, flags=re.M)
            for m in re.findall(r'<span class="navi-item"><a href="entry://[A-Z|\d]+_([^">]+)">([^<]+)</a></span>', top_navi[1]):
                if m[1] != '🕮':
                    navi_items.add_line({"a": m[1], "ref": m[0]})
            # 提取 index, toc, syns
            index = []
            toc = []
            syns = []
            for m in re.findall(r'^([^\r\n]+)[\r\n]+@@@LINK=([^\r\n]+)[\r\n]+</>$', text, flags=re.M):
                # 区分: 索引, 目录, 同义词
                dct = {}
                if m[1].startswith(name_abbr+'_'):
                    # 获取页码
                    n = len(name_abbr) + 2
                    if m[1].startswith(name_abbr+'_A'):
                        dct["page"] = int(m[1][n:]) - body_start
                    else:
                        dct["page"] = int(m[1][n:])
                    # 区分目录和索引
                    if m[0].startswith(name_abbr+'_'):
                        dct["name"] = m[0][n-1:]
                        toc.append(dct)
                    else:
                        dct["name"] = m[0]
                        index.append(dct)
                else:
                    syns.append((m[0], m[1]))
        # 2.整理提取结果
        # (a) index.txt
        if len(index) != 0:
            index.sort(key=lambda x: x["page"], reverse=False)
            with open(os.path.join(out_dir, 'index.txt'), 'w', encoding='utf-8') as fw:
                for d in index:
                    fw.write(f'{d["name"]}\t{str(d["page"])}\n')
        # (b) toc.txt
        if len(toc) != 0:
            with open(os.path.join(out_dir, 'toc.txt'), 'w', encoding='utf-8') as fw:
                # 获取TOC总目录词条
                toc_entry = re.search(r'^TOC_.*?</>$', text, flags=re.S+re.M)
                if toc_entry:
                    for m in re.findall(r'^(\t*)<li><a href="entry://'+name_abbr+r'_([^\">]+)\">', toc_entry.group(0), flags=re.M):
                        p = 0
                        for d in toc:
                            if m[1] == d["name"]:
                                p = d["page"]
                                break
                        fw.write(f'{m[0]}{m[1]}\t{str(p)}\n')
        # (c) syns.txt
        if len(syns) != 0:
            with open(os.path.join(out_dir, 'syns.txt'), 'w', encoding='utf-8') as fw:
                for s in syns:
                    fw.write(f'{s[0]}\t{s[1]}\n')
        # (d) build.toml
        self.settings.load_build_toml(os.path.join(self.settings.dir_lib, self.settings.build_tmpl), False)
        self.settings.build["global"]["templ_choice"] = "A"
        self.settings.build["global"]["name"] = dict_name
        self.settings.build["global"]["name_abbr"] = name_abbr
        self.settings.build["template"]["a"]["body_start"] = body_start
        if len(navi_items) > 0:
            build_str = re.sub(r'[\r\n]+#navi_items = \[.*?#\][^\r\n]*?', '', dumps(self.settings.build), flags=re.S+re.I)
            build_str = re.sub(r'[\r\n]+#\s*?（可选）导航栏链接.+$', '', build_str, flags=re.M)
            self.settings.build = loads(build_str)
            self.settings.build["template"]["a"].add(comment("（可选）导航栏链接, 有目录 (toc.txt) 就可以设置"))
            self.settings.build["template"]["a"].add("navi_items", navi_items.multiline(True))
            self.settings.build["template"]["a"].add(nl())
            self.settings.build["template"]["a"].add(nl())
        with open(os.path.join(out_dir, 'build.toml'), 'w', encoding='utf-8') as fw:
            fw.write(dumps(self.settings.build))

    def _make_entry_toc(self, file_toc, file_out):
        """ (二) 生成总目词条 """
        # 1.读取目录书签文件
        pairs = self.func.read_toc_file(file_toc)
        # 2.生成总目词条
        with open(file_out, 'w', encoding='utf-8') as fw:
            # 开头
            fw.write(f'TOC_{self.settings.name_abbr}\n<link rel="stylesheet" type="text/css" href="/{self.settings.name_abbr.lower()}.css"/>\n')
            fw.write('<div class="toc-title">目录</div>\n<div class="toc-text">\n<ul>\n')
            # 主体部分
            n_total = len(pairs)
            tab = '\t'
            prefix = '<ul>'
            suffix = '</ul></li>'
            # 根据层级生成 html 列表结构
            for i in range(n_total):
                try:
                    l_after = pairs[i+1]["level"]
                except IndexError:
                    l_after = 0
                pair = pairs[i]
                # 与后同
                if pair["level"] == l_after:
                    fw.write(f'{tab*pair["level"]}<li><a href="entry://{self.settings.name_abbr}_{pair["title"]}">{pair["title"]}</a></li>\n')
                # 比后高(说明将要展开)
                elif pair["level"] < l_after:
                    fw.write(f'{tab*pair["level"]}<li><a href="entry://{self.settings.name_abbr}_{pair["title"]}">{pair["title"]}</a>{prefix}\n')
                # 比后低(说明展开到此结束)
                else:
                    gap = pair["level"] - l_after
                    fw.write(f'{tab*pair["level"]}<li><a href="entry://{self.settings.name_abbr}_{pair["title"]}">{pair["title"]}</a></li>{suffix*gap}\n')
            # 结尾
            fw.write('</ul>\n</div>\n</>\n')
        print("总目词条已生成")

    def _make_redirects_headword(self, file_index, file_out, n_len, file_toc):
        """ (三) 生成词目重定向 """
        headwords = []
        # 1.读取词条索引
        pairs = []
        with open(file_index, 'r', encoding='utf-8') as fr:
            lines = fr.readlines()
            pat = re.compile(r'^([^\t]+)\t([\-\d]+)[\r\n]*$')
            i = 1
            for line in lines:
                if pat.match(line):
                    part_1 = pat.match(line).group(1)
                    part_2 = pat.match(line).group(2)
                    pair = {
                        "title": part_1,
                        "page": int(part_2)
                    }
                    pairs.append(pair)
                else:
                    print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"第 {i} 行未匹配, 已忽略")
                i += 1
        # 2.生成重定向
        with open(file_out, 'w', encoding='utf-8') as fw:
            # a.词条部分
            for pair in pairs:
                fw.write(f'{pair["title"]}\n@@@LINK={self.settings.name_abbr}_B{str(pair["page"]).zfill(n_len)}\n</>\n')
                headwords.append(pair["title"])
            # b.目录部分
            if file_toc:
                for pair in self.func.read_toc_file(file_toc):
                    if pair["page"] < 0:
                        fw.write(f'{self.settings.name_abbr}_{pair["title"]}\n@@@LINK={self.settings.name_abbr}_A{str(pair["page"]+self.settings.body_start).zfill(n_len)}\n</>\n')
                    else:
                        fw.write(f'{self.settings.name_abbr}_{pair["title"]}\n@@@LINK={self.settings.name_abbr}_B{str(pair["page"]).zfill(n_len)}\n</>\n')
                    headwords.append(pair["title"])
        print("重定向(词目)词条已生成")
        return headwords

    def _check_raw_files(self):
        """ 检查原材料
        * 必要文本存在(文本编码均要是 utf-8 无 bom)
        * 图像文件夹存在, 正文起始数要大于1, 图像个数要大于正文起始数
        * 图像个数与索引范围匹配, 不冲突
        * 检查 info.html 的编码
        """
        check_result = []
        # 预定义输入文件路径
        dir_imgs = os.path.join(self.settings.dir_input, self.settings.dname_imgs)
        file_index = os.path.join(self.settings.dir_input, self.settings.fname_index)
        file_toc = os.path.join(self.settings.dir_input, self.settings.fname_toc)
        file_syns = os.path.join(self.settings.dir_input, self.settings.fname_syns)
        file_dict_info = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
        min_index = 0
        max_index = 0
        # 0.检查索引文件: 必须存在且合格
        if self.func.text_file_check(file_index) == 2:
            check_result.append(file_index)
            # 1.读取词条索引
            with open(file_index, 'r', encoding='utf-8') as fr:
                lines = fr.readlines()
                pat = re.compile(r'^([^\t]+)\t([\-\d]+)[\r\n]*$')
                for line in lines:
                    if pat.match(line):
                        i = int(pat.match(line).group(2))
                        max_index = max(max_index, i)
            # 2.检查目录文件: 若存在就要合格
            toc_check_num = self.func.text_file_check(file_toc)
            if toc_check_num == 0:
                check_result.append(None)
            elif toc_check_num == 2:
                # 读取目录索引
                with open(file_toc, 'r', encoding='utf-8') as fr:
                    lines = fr.readlines()
                    pat = re.compile(r'^(\t*)([^\t]+)\t([\-\d]+)[\r\n]*$')
                    for line in lines:
                        if pat.match(line):
                            i = int(pat.match(line).group(3))
                            min_index = min(min_index, i)
                if self.settings.body_start < abs(min_index) + 1:
                    print(Fore.RED + "ERROR: " + Fore.RESET + "正文起始页设置有误(小于最小索引)")
                else:
                    check_result.append(file_toc)
            # 3.检查图像
            n = 0
            if os.path.exists(dir_imgs):
                for fname in os.listdir(dir_imgs):
                    if os.path.splitext(fname)[1] in self.settings.img_exts:
                        n += 1
            if n == 0:
                print(Fore.RED + "ERROR: " + Fore.RESET + f"图像文件夹 {dir_imgs} 不存在或为空")
            elif n < self.settings.body_start:
                print(Fore.RED + "ERROR: " + Fore.RESET + "图像数量不足(少于起始页码)")
            elif n < max_index - min_index:
                print(Fore.RED + "ERROR: " + Fore.RESET + "图像数量不足(少于索引范围)")
            else:
                check_result.append(dir_imgs)
            # 4.检查同义词文件: 若存在就要合格
            syns_check_num = self.func.text_file_check(file_syns)
            if syns_check_num == 0:
                check_result.append(None)
            elif syns_check_num == 2:
                check_result.append(file_syns)
            # 5.检查 info.html: 若存在就要合格
            info_check_num = self.func.text_file_check(file_dict_info)
            if info_check_num == 0:
                check_result.append(None)
            elif info_check_num == 2:
                check_result.append(file_dict_info)
        # 返回最终检查结果
        if len(check_result) == 5:
            return check_result
        else:
            return None
