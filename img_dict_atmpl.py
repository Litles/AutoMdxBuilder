#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-07-13 19:49:56
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.4

import os
import re
from colorama import init, Fore, Back, Style
from settings import Settings
from func_lib import FuncLib


class ImgDictAtmpl:
    """ 图像词典（模板A） """
    def __init__(self):
        self.settings = Settings()
        self.func = FuncLib()
        # 初始化, 检查原材料
        self.proc_flg, self.proc_flg_toc, self.proc_flg_syns = self._check_raw_files()

    def make_source_file(self):
        """ 制作预备 txt 源文本 """
        if self.proc_flg:
            print('\n材料检查通过, 开始制作词典……\n')
            # 创建临时输出目录, 清空目录下所有文件
            if not os.path.exists(self.settings.dir_output_tmp):
                os.makedirs(self.settings.dir_output_tmp)
            for fname in os.listdir(self.settings.dir_output_tmp):
                fpath = os.path.join(self.settings.dir_output_tmp, fname)
                if os.path.isfile(fpath):
                    os.remove(fpath)
            step = 0
            # (一) 生成主体(图像)词条
            file_1 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entries_img)
            dir_imgs_out, imgs, p_total, n_len = self.func.make_entries_img(self.proc_flg_toc, file_1)
            step += 1
            print(f'\n{step}.文件 "{self.settings.fname_entries_img}" 已生成；')
            # (二) 生成总目词条
            file_2 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entry_toc)
            if self.proc_flg_toc:
                self._make_entry_toc(file_2)
                step += 1
                print(f'{step}.文件 "{self.settings.fname_entry_toc}" 已生成；')
            # (三) 生成词目重定向
            file_3 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_headword)
            words_part1 = self._make_redirects_headword(n_len, file_3, self.proc_flg_toc)
            step += 1
            print(f'{step}.文件 "{self.settings.fname_redirects_headword}" 已生成；')
            # (四) 生成近义词重定向
            file_4 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_syn)
            words_part2 = []
            if self.proc_flg_syns:
                words_part2 = self.func.make_redirects_syn(file_4)
                step += 1
                print(f'{step}.文件 "{self.settings.fname_redirects_syn}" 已生成；')
            # (五) 生成繁简通搜重定向
            file_5 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_st)
            if self.settings.simp_trad_flg:
                self.func.make_redirects_st(words_part1+words_part2, file_5)
                step += 1
                print(f'{step}.文件 "{self.settings.fname_redirects_st}" 已生成；')
            # 合并成最终 txt 源文本
            file_final_txt = os.path.join(self.settings.dir_output_tmp, self.settings.fname_final_txt)
            entry_total = self.func.merge_and_count([file_1, file_2, file_3, file_4, file_5], file_final_txt)
            print(f'\n最终源文本 "{self.settings.fname_final_txt}"（共 {entry_total} 词条）生成完毕！')
            # 生成 css 文件
            file_css = os.path.join(self.settings.dir_css, self.settings.css_atmpl)
            file_css_out = os.path.join(self.settings.dir_output_tmp, self.settings.fname_css)
            os.system(f'copy /y "{file_css}" "{file_css_out}"')
            # 生成 info.html
            file_info_raw = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
            file_dict_info = self.func.generate_info_html(self.settings.name, file_info_raw, entry_total, p_total)
            return self.proc_flg, file_final_txt, dir_imgs_out, file_dict_info
        else:
            print(Fore.RED + "\n材料检查不通过, 请确保材料准备无误再执行程序")
            return self.proc_flg, None, None, None

    def _check_raw_files(self):
        """ 检查原材料
        * 必要文本存在(文本编码均要是 utf-8 无 bom)
        * 图像文件夹存在, 正文起始数要大于1, 图像个数要大于正文起始数
        * 图像个数与索引范围匹配, 不冲突
        * 检查 info.html 的编码
        """
        proc_flg = True
        proc_flg_toc = True
        proc_flg_syns = True
        dir_imgs = os.path.join(self.settings.dir_input, self.settings.dname_imgs)
        file_index = os.path.join(self.settings.dir_input, self.settings.fname_index)
        file_syns = os.path.join(self.settings.dir_input, self.settings.fname_syns)
        file_toc = os.path.join(self.settings.dir_input, self.settings.fname_toc)
        file_dict_info = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
        min_index = 0
        max_index = 0
        # 1.检查索引文件: 必须存在且合格
        if self.func.text_file_check(file_index) == 2:
            # 读取词条索引
            with open(file_index, 'r', encoding='utf-8') as fr:
                lines = fr.readlines()
                pat = re.compile(r'^([^\t]+)\t([\-\d]+)[\r\n]*$')
                for line in lines:
                    if pat.match(line):
                        i = int(pat.match(line).group(2))
                        max_index = max(max_index, i)
        else:
            proc_flg = False
        # 2.检查目录文件: 若存在就要合格
        toc_check_result = self.func.text_file_check(file_toc)
        if toc_check_result == 0:
            proc_flg_toc = False
        elif toc_check_result == 1:
            proc_flg = False
        else:
            # 读取目录索引
            with open(file_toc, 'r', encoding='utf-8') as fr:
                lines = fr.readlines()
                pat = re.compile(r'^(\t*)([^\t]+)\t([\-\d]+)[\r\n]*$')
                for line in lines:
                    if pat.match(line):
                        i = int(pat.match(line).group(3))
                        min_index = min(min_index, i)
            if self.settings.body_start < abs(min_index) + 1:
                print(Fore.RED + "ERROR: " + Fore.RESET + f"正文起始页设置有误(小于最小索引)")
                proc_flg = False
        # 3.检查同义词文件: 若存在就要合格
        syns_check_result = self.func.text_file_check(file_syns)
        if syns_check_result == 0:
            proc_flg_syns = False
        elif syns_check_result == 1:
            proc_flg = False
        else:
            pass
        # 4.检查图像
        n = 0
        if os.path.exists(dir_imgs):
            for fname in os.listdir(dir_imgs):
                n += 1
        if n == 0:
            print(Fore.RED + "ERROR: " + Fore.RESET + f"图像文件夹 {dir_imgs} 不存在或为空")
            proc_flg = False
        elif n < self.settings.body_start:
            print(Fore.RED + "ERROR: " + Fore.RESET + "图像数量不足(少于起始页码)")
            proc_flg = False
        elif n < max_index - min_index:
            print(Fore.RED + "ERROR: " + Fore.RESET + "图像数量不足(少于索引范围)")
            proc_flg = False
        # 5.检查 info.html: 若存在就要合格
        if self.func.text_file_check(file_dict_info) == 1:
            proc_flg = False
        return proc_flg, proc_flg_toc, proc_flg_syns

    def _make_entry_toc(self, file_out):
        """ (二) 生成总目词条 """
        # 1.读取目录书签文件
        file_toc = os.path.join(self.settings.dir_input, self.settings.fname_toc)
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

    def _make_redirects_headword(self, n_len, file_out, proc_flg_toc):
        """ (三) 生成词目重定向 """
        words = []
        # 1a.读取词条索引
        file_index = os.path.join(self.settings.dir_input, self.settings.fname_index)
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
                    print(Fore.YELLOW + "INFO: " + Fore.RESET + f"第 {i} 行未匹配, 已忽略")
                i += 1
        # 1b.读取目录索引
        if proc_flg_toc:
            file_toc = os.path.join(self.settings.dir_input, self.settings.fname_toc)
            pairs_toc = self.func.read_toc_file(file_toc)
        # 2.生成重定向
        with open(file_out, 'w', encoding='utf-8') as fw:
            # a.词条部分
            for pair in pairs:
                fw.write(f'{pair["title"]}\n@@@LINK={self.settings.name_abbr}_B{str(pair["page"]).zfill(n_len)}\n</>\n')
                words.append(pair["title"])
            # b.目录部分
            if proc_flg_toc:
                for pair in pairs_toc:
                    if pair["page"] < 0:
                        fw.write(f'{self.settings.name_abbr}_{pair["title"]}\n@@@LINK={self.settings.name_abbr}_A{str(pair["page"]+self.settings.body_start).zfill(n_len)}\n</>\n')
                    else:
                        fw.write(f'{self.settings.name_abbr}_{pair["title"]}\n@@@LINK={self.settings.name_abbr}_B{str(pair["page"]).zfill(n_len)}\n</>\n')
                    words.append(pair["title"])
        return words

    def extract_final_txt(self, file_final_txt, out_dir):
        """ 从模板A词典的源 txt 文本中提取 index, toc, syns 信息 """
        with open(file_final_txt, 'r', encoding='utf-8') as fr:
            text = fr.read()
            # 0.识别正文起始页数
            name_abbr = ''
            body_start = 1
            for m in re.findall(r'^<div class="main-img"><img src="/([A-Z|\d]+)_A(\d+)\.\w+"></div>$', text, flags=re.M+re.I):
                if int(m[1]) > body_start:
                    body_start = int(m[1])
                name_abbr = m[0].upper()
            body_start = body_start + 1
            # 1.提取 index, toc, syns
            index = []
            toc = []
            syns = []
            for m in re.findall(r'^([^\r\n]+)[\r\n]+@@@LINK=([^\r\n]+)[\r\n]+</>$', text, flags=re.M+re.I):
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
                        for m in re.findall(r'^(\t*)<li><a href="entry://'+name_abbr+r'_([^\">]+)\">', toc_entry.group(0), flags=re.M+re.I):
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
        return True
