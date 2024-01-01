#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-16 00:00:27
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.6

import os
import re
from copy import copy
import shutil
from tomlkit import dumps, loads, array, comment, nl
from colorama import Fore


class ImgDictAtmpl:
    """ 图像词典（模板A） """
    def __init__(self, amb):
        self.settings = amb.settings
        self.func = amb.func

    def make_source_file(self):
        """ 制作预备 txt 源文本 """
        # 清空临时目录下所有文件
        for fname in os.listdir(self.settings.dir_output_tmp):
            fpath = os.path.join(self.settings.dir_output_tmp, fname)
            if os.path.isfile(fpath):
                os.remove(fpath)
        # 检查原材料: index, toc, imgs, syns, info
        check_result = self._check_raw_files()
        # 开始制作
        if check_result:
            print('\n材料检查通过, 开始制作词典……\n')
            # 预定义输出文件名
            file_final_txt = os.path.join(self.settings.dir_output_tmp, self.settings.fname_final_txt)
            file_dict_info = os.path.join(self.settings.dir_output_tmp, self.settings.fname_dict_info)
            dir_imgs_tmp = os.path.join(self.settings.dir_output_tmp, self.settings.dname_imgs)
            # 1.分步生成各部分源文本
            file_1 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entries_img)  # 图像词条
            file_2 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entry_toc)  # 总目词条
            file_3 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_relinks_headword)  # 词目重定向
            file_4 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_relinks_syn)  # 同义词重定向
            file_5 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_relinks_st)  # 繁简重定向
            # 0.准备图像, 确定 navi_items
            navi_items = None
            if self.settings.multi_volume:
                imgs, img_lens = self.func.prepare_imgs(check_result[2], dir_imgs_tmp, self.settings.volume_num)
                # 判断是否有 toc
                if isinstance(check_result[1], list):
                    lst = list(filter(lambda item: item is not None, check_result[1]))
                    if len(lst) > 0:
                        navi_items = self.settings.navi_items
                elif check_result[1]:
                    navi_items = self.settings.navi_items
            else:
                imgs, img_lens = self.func.prepare_imgs(check_result[2], dir_imgs_tmp)
                if check_result[1]:
                    navi_items = self.settings.navi_items
            # 1.开始生成各部分源文本
            # (1) 生成主体(图像)词条
            self._make_entries_img(imgs, navi_items, file_1)
            # (2) 生成目录词条
            self._make_entries_toc(check_result[1], file_2)
            # (3) 生成词目重定向
            headwords = self._make_relinks_headword(check_result[0], check_result[1], file_3)
            # (4) 生成同义词重定向
            if check_result[3]:
                headwords += self.func.make_relinks_syn(check_result[3], file_4)
            # (5) 生成繁简通搜重定向
            if self.settings.simp_trad_flg:
                self.func.make_relinks_st(headwords, file_5)
            # 2.合并成最终 txt 源文本
            entry_total = self.func.merge_and_count([file_1, file_2, file_3, file_4, file_5], file_final_txt)
            print(f'\n源文本 "{self.settings.fname_final_txt}"（共 {entry_total} 词条）生成完毕！')
            # 3.生成 info.html
            if self.settings.multi_volume:
                self.func.generate_info_html(check_result[4], file_dict_info, self.settings.name, 'A', self.settings.volume_num)
            else:
                self.func.generate_info_html(check_result[4], file_dict_info, self.settings.name, 'A')
            # 返回制作结果
            return [file_final_txt, dir_imgs_tmp, file_dict_info]
        else:
            print(Fore.RED + "\n材料检查不通过, 请确保材料准备无误再执行程序" + Fore.RESET)
            return None

    def extract_final_txt(self, file_final_txt, out_dir, dict_name, file_css=None):
        """ 从模板A词典的源 txt 文本中提取 index, toc, syns 信息 """
        # 1.提取信息
        with open(file_final_txt, 'r', encoding='utf-8') as fr:
            text = fr.read()
            # 识别 name_abbr, body_start
            body_start = 1
            names = []
            for m in re.findall(r'^<div class="main-img">.*?<div class="pic"><img src="/([a-zA-Z|\d]+)_A(\d+)\.\w+">', text, flags=re.M):
                if int(m[1])+1 > body_start:
                    body_start = int(m[1])+1
                if m[0].upper() not in names:
                    names.append(m[0].upper())
            if len(names) > 0:
                name_abbr = names[0].upper()
            else:
                print(Fore.MAGENTA + "WARN: " + Fore.RESET + "未识别到词典首字母缩写, 已设置默认值")
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
        # 判断分栏选项
        if file_css and os.path.split(file_css)[1].lower() == name_abbr.lower()+'.css':
            with open(file_css, 'r', encoding='utf-8') as fr:
                if not re.search(r'/\*<insert_css: auto_split>\*/', fr.read(), flags=re.I):
                    self.settings.build["template"]["a"]["auto_split_columns"] = 2
        # 判断 navi_items
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

    def _get_toc_entry_txt(self, pairs, mix_flg=False, vol_i=None):
        entry_txt = ''
        # 1.开头
        if vol_i is None:
            # 总目录
            entry_txt += f'TOC_{self.settings.name_abbr}\n<link rel="stylesheet" type="text/css" href="/{self.settings.name_abbr.lower()}.css"/>\n'
            if mix_flg:
                entry_txt += '<div class="toc-title">总目录</div>\n<div class="toc-text">\n<ul>\n'
            else:
                entry_txt += '<div class="toc-title">目录</div>\n<div class="toc-text">\n<ul>\n'
        else:
            # 分目录
            entry_txt += f'TOC_{self.settings.name_abbr}[{str(vol_i+1).zfill(2)}]\n<link rel="stylesheet" type="text/css" href="/{self.settings.name_abbr.lower()}.css"/>\n'
            if self.settings.vol_names:
                entry_txt += f'<div class="toc-title">分目录（{self.settings.vol_names[vol_i]}）</div>\n<div class="toc-text">\n<ul>\n'
            else:
                entry_txt += f'<div class="toc-title">分目录（第 {str(vol_i+1).zfill(2)} 卷）</div>\n<div class="toc-text">\n<ul>\n'
        # 2.主体部分
        n_total = len(pairs)
        tab = '\t'
        prefix = '<ul>'
        suffix = '</ul></li>'
        # 根据层级生成 html 列表结构
        for i in range(n_total):
            pair = pairs[i]
            # 1.确定列表项内容
            if mix_flg:
                str_b = self.settings.name_abbr + f'[{str(pair["vol_n"]).zfill(2)}]'
            elif vol_i is not None:
                str_b = self.settings.name_abbr + f'[{str(vol_i+1).zfill(2)}]'
            else:
                str_b = self.settings.name_abbr
            if pair["page"] == 0:
                str_li = pair["title"]
            else:
                str_li = f'<a href="entry://{str_b}_{pair["title"]}">{pair["title"]}</a>'
            # 2.得到列表项的完整 html 代码
            # 识别下一级
            try:
                l_after = pairs[i+1]["level"]
            except IndexError:
                l_after = 0
            # 与后同
            if pair["level"] == l_after:
                entry_txt += f'{tab*pair["level"]}<li>{str_li}</li>\n'
            # 比后高(说明将要展开)
            elif pair["level"] < l_after:
                entry_txt += f'{tab*pair["level"]}<li>{str_li}{prefix}\n'
            # 比后低(说明展开到此结束)
            else:
                gap = pair["level"] - l_after
                entry_txt += f'{tab*pair["level"]}<li>{str_li}</li>{suffix*gap}\n'
        # 3.结尾
        entry_txt += '</ul>\n</div>\n</>\n'
        return entry_txt

    def _make_entries_toc(self, file_toc, file_out):
        """ (二) 生成目录词条 """
        if self.settings.multi_volume:
            # 情况一: 有分目录
            if isinstance(file_toc, list):
                # 生成总目词条
                toc_txts = []
                top_toc_txt = ''
                top_toc_txt += f'TOC_{self.settings.name_abbr}\n<link rel="stylesheet" type="text/css" href="/{self.settings.name_abbr.lower()}.css"/>\n'
                top_toc_txt += '<div class="toc-title">总目录</div>\n<div class="toc-text">\n<ul>\n'
                for i in range(self.settings.volume_num):
                    # 生成子目录词条
                    if file_toc[i]:
                        pairs = self.func.read_toc_file(file_toc[i], i)
                        toc_txts.append(self._get_toc_entry_txt(pairs, False, i))
                        if self.settings.vol_names:
                            top_toc_txt += f'\t<li><a href="entry://TOC_{self.settings.name_abbr}[{str(i+1).zfill(2)}]">{self.settings.vol_names[i]}</a></li>\n'
                        else:
                            top_toc_txt += f'\t<li><a href="entry://TOC_{self.settings.name_abbr}[{str(i+1).zfill(2)}]">第 {str(i+1).zfill(2)} 卷</a></li>\n'
                top_toc_txt += '</ul>\n</div>\n</>\n'
                # 写入词条
                if toc_txts:
                    with open(file_out, 'w', encoding='utf-8') as fw:
                        fw.write(top_toc_txt)
                        for txt in toc_txts:
                            fw.write(txt)
                    print("目录词条已生成")
            # 情况二: 无分目录
            else:
                pairs = self.func.read_toc_file(file_toc)
                with open(file_out, 'w', encoding='utf-8') as fw:
                    fw.write(self._get_toc_entry_txt(pairs, True))
        else:
            if file_toc:
                pairs = self.func.read_toc_file(file_toc)
                with open(file_out, 'w', encoding='utf-8') as fw:
                    fw.write(self._get_toc_entry_txt(pairs, False))
                print("目录词条已生成")

    def _make_relinks_headword(self, file_index, file_toc, file_out):
        """ (三) 生成词目重定向 """
        headwords = []
        len_digit = self.settings.len_digit
        if self.settings.multi_volume:
            # 1.读取 index
            pairs = []
            for i in range(self.settings.volume_num):
                if file_index[i]:
                    pairs += self.func.read_index_file(file_index[i], i)
            # 2.读取 toc
            # 情况一: 有分目录
            if isinstance(file_toc, list):
                toc_pairs = []
                for i in range(self.settings.volume_num):
                    if file_toc[i]:
                        toc_pairs += self.func.read_toc_file(file_toc[i], i)
            # 情况二: 无分目录
            else:
                toc_pairs = self.func.read_toc_file(file_toc)
            # 3.生成重定向
            with open(file_out, 'w', encoding='utf-8') as fw:
                # a.词条部分
                for pair in pairs:
                    str_link = f'{self.settings.name_abbr}[{str(pair["vol_n"]).zfill(2)}]_B{str(pair["page"]).zfill(len_digit)}'
                    fw.write(f'{pair["title"]}\n@@@LINK={str_link}\n</>\n')
                    headwords.append(pair["title"])
                # b.目录部分
                for pair in toc_pairs:
                    if pair["page"] != 0:
                        str_b = f'{self.settings.name_abbr}[{str(pair["vol_n"]).zfill(2)}]'
                        if pair["page"] < 0:
                            str_link = f'{str_b}_A{str(pair["page"]+self.settings.body_start[pair["vol_n"]-1]).zfill(len_digit)}'
                        else:
                            str_link = f'{str_b}_B{str(pair["page"]).zfill(len_digit)}'
                        fw.write(f'{str_b}_{pair["title"]}\n@@@LINK={str_link}\n</>\n')
                        fw.write(f'{pair["title"]}[{str(pair["vol_n"]).zfill(2)}]\n@@@LINK={str_b}_{pair["title"]}\n</>\n')
                        headwords.append(pair["title"])
        else:
            with open(file_out, 'w', encoding='utf-8') as fw:
                # a.词条部分
                if file_index:
                    for pair in self.func.read_index_file(file_index):
                        str_link = f'{self.settings.name_abbr}_B{str(pair["page"]).zfill(len_digit)}'
                        fw.write(f'{pair["title"]}\n@@@LINK={str_link}\n</>\n')
                        headwords.append(pair["title"])
                # b.目录部分
                if file_toc:
                    for pair in self.func.read_toc_file(file_toc):
                        if pair["page"] != 0:
                            if pair["page"] < 0:
                                str_link = f'{self.settings.name_abbr}_A{str(pair["page"]+self.settings.body_start[0]).zfill(len_digit)}'
                            else:
                                str_link = f'{self.settings.name_abbr}_B{str(pair["page"]).zfill(len_digit)}'
                            fw.write(f'{self.settings.name_abbr}_{pair["title"]}\n@@@LINK={str_link}\n</>\n')
                            fw.write(f'{pair["title"]}\n@@@LINK={self.settings.name_abbr}_{pair["title"]}\n</>\n')
                            headwords.append(pair["title"])
        print("重定向(词目)词条已生成")
        return headwords

    def _make_entries_img(self, imgs, navi_items, file_out):
        """ 生成图像词条 """
        p_total = len(imgs)
        with open(file_out, 'w', encoding='utf-8') as fw:
            part_css = f'<link rel="stylesheet" type="text/css" href="{self.settings.name_abbr.lower()}.css"/>\n'
            part_middle = self._generate_navi_middle(navi_items)
            for i in range(p_total):
                img = imgs[i]
                part_title = f'{img["title"]}\n'
                part_img = '<div class="main-img">'
                # 判断是否要分栏
                body_start = self.settings.body_start[img["vol_n"]-1]
                body_end_page = self.settings.body_end_page[img["vol_n"]-1]
                if self.settings.split_columns == 2 and (i >= body_start-1 and i <= body_end_page+body_start-2):
                    part_img += f'<div class="left"><div class="pic"><img src="/{img["path"]}"></div></div>'
                    part_img += f'<div class="right"><div class="pic"><img src="/{img["path"]}"></div></div>'
                else:
                    part_img += f'<div class="pic"><img src="/{img["path"]}"></div>'
                part_img += '</div>\n'
                # 生成翻页部分(首末页特殊)
                # 备用: [☚,☛] [☜,☞] [◀,▶] [上一页,下一页] [☚&#12288;&#8197;,&#8197;&#12288;☛]
                if i == 0:
                    part_left = ''
                    part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i+1]["title"]}">&#8197;&#12288;☛</a></span>'
                elif i == p_total-1:
                    part_left = f'<span class="navi-item-left"><a href="entry://{imgs[i-1]["title"]}">☚&#12288;&#8197;</a></span>'
                    part_right = ''
                else:
                    part_left = f'<span class="navi-item-left"><a href="entry://{imgs[i-1]["title"]}">☚&#12288;&#8197;</a></span>'
                    part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i+1]["title"]}">&#8197;&#12288;☛</a></span>'
                # 组合
                part_top = '<div class="top-navi">' + part_left + part_middle + part_right + '</div>\n'
                part_bottom = '<div class="bottom-navi">' + part_left + part_middle + part_right + '</div>\n'
                # 将完整词条写入文件
                fw.write(part_title+part_css+part_top+part_img+part_bottom+'</>\n')
        print("\n图像词条已生成")
        return True

    def _generate_navi_middle(self, navi_items):
        """ 生成导航栏中间(链接)部分 """
        html = '<span class="navi-item-middle">'
        if navi_items is None:
            html += '&#8197;&#12288;&#8197;'
        elif self.settings.multi_volume:
            html += f'<span class="navi-item"><a href="entry://TOC_{self.settings.name_abbr}">🕮</a></span>'
            for item in navi_items:
                mth = re.match(r'\[(\d+)\](.+?)$', item["ref"], flags=re.I)
                if mth:
                    html += f'<span class="navi-item"><a href="entry://{self.settings.name_abbr}[{mth.group(1).zfill(2)}]_{mth.group(2)}">{item["a"]}</a></span>'
                else:
                    html += f'<span class="navi-item"><a href="entry://{self.settings.name_abbr}[01]_{item["ref"]}">{item["a"]}</a></span>'
        else:
            html += f'<span class="navi-item"><a href="entry://TOC_{self.settings.name_abbr}">🕮</a></span>'
            for item in navi_items:
                html += f'<span class="navi-item"><a href="entry://{self.settings.name_abbr}_{item["ref"]}">{item["a"]}</a></span>'
        html += '</span>'
        return html

    def _check_img_vol(self, file_index, file_toc, dir_imgs, vol_i=0):
        pass_flg = True
        min_index = 0
        max_index = 0
        dname = os.path.split(dir_imgs)[1]
        # 1.读取词条索引
        if file_index:
            with open(file_index, 'r', encoding='utf-8') as fr:
                for line in fr:
                    mth = self.settings.pat_index.match(line)
                    if mth:  # 前面 check_txt 其实已经检查过了, 此处必然为真
                        min_index = min(min_index, int(mth.group(2)))
                        max_index = max(max_index, int(mth.group(2)))
                if self.settings.body_end_page[vol_i] == 99999:
                    self.settings.body_end_page[vol_i] = copy(max_index)
        # 2.检查目录文件
        if file_toc:
            # 读取目录索引
            with open(file_toc, 'r', encoding='utf-8') as fr:
                for line in fr:
                    mth = self.settings.pat_toc.match(line)
                    if mth:  # 只检查有页码的
                        min_index = min(min_index, int(mth.group(3)))
                        max_index = max(max_index, int(mth.group(3)))
            if self.settings.body_start[vol_i] < abs(min_index) + 1:
                print(Fore.RED + "ERROR: " + Fore.RESET + f"{dname} 对应正文起始页设置有误(小于最小索引)")
                pass_flg = False
        # 3.检查图像
        if file_index or file_toc:
            n = 0
            for fname in os.listdir(dir_imgs):
                if os.path.splitext(fname)[1] in self.settings.img_exts:
                    n += 1
            if n == 0:
                print(Fore.RED + "ERROR: " + Fore.RESET + f"图像文件夹 {dname} 为空")
                pass_flg = False
            elif n < self.settings.body_start[vol_i]:
                print(Fore.RED + "ERROR: " + Fore.RESET + f"{dname} 图像数量不足(少于起始页码)")
                pass_flg = False
            elif n < max_index-min_index:
                print(Fore.RED + "ERROR: " + Fore.RESET + f"{dname} 图像数量不足(少于索引范围)")
                pass_flg = False
            elif n < max_index+self.settings.body_start[vol_i]-1:
                print(Fore.RED + "ERROR: " + Fore.RESET + f"{dname} 图像数量不足(少于设定范围)")
                pass_flg = False
        return pass_flg

    def _check_txt_vols(self, dir_input, prefix, dir_out):
        """ 识别分卷的 index, toc 文本 """
        done_flg = True
        pat = re.compile(prefix+r'_(\d+)', flags=re.I)
        # 1.开始识别,读取
        lst_vols = [[] for i in range(self.settings.volume_num)]
        break_flg = False
        for fname in os.listdir(dir_input):
            if fname.endswith('.txt') and pat.match(fname):
                vol_n = int(pat.match(fname).group(1))
                fp = os.path.join(dir_input, fname)
                index_check_num = self.func.text_file_check(fp)
                if index_check_num == 1:
                    done_flg = False
                    break
                elif index_check_num == 2 and vol_n <= self.settings.volume_num:
                    with open(fp, 'r', encoding='utf-8') as fr:
                        i = 0
                        if prefix == 'index':
                            for line in fr:
                                i += 1
                                mth = self.settings.pat_index.match(line)
                                if mth:
                                    lst_vols[vol_n-1].append(f'{mth.group(1)}\t{mth.group(2)}\n')
                                elif self.settings.pat_index_vol.match(line):
                                    # 有卷标词条, 去卷标
                                    mth_vol = self.settings.pat_index_vol.match(line)
                                    if int(mth_vol.group(2)) == vol_n:
                                        lst_vols[vol_n-1].append(f'{mth_vol.group(1)}\t{mth_vol.group(3)}\n')
                                    else:
                                        print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"{fname} 第 {i} 行卷标与文件名不符, 已忽略")
                                else:
                                    print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"{fname} 第 {i} 行未匹配, 已忽略")
                        elif prefix == 'toc':
                            for line in fr:
                                i += 1
                                mth = self.settings.pat_toc.match(line)
                                if mth:
                                    lst_vols[vol_n-1].append(f'{mth.group(1)}{mth.group(2)}\t{mth.group(3)}\n')
                                elif self.settings.pat_toc_vol.match(line):
                                    # 有卷标目录, 去卷标
                                    mth_vol = self.settings.pat_toc_vol.match(line)
                                    if int(mth_vol.group(3)) == vol_n:
                                        lst_vols[vol_n-1].append(f'{mth_vol.group(1)}{mth_vol.group(2)}\t{mth_vol.group(4)}\n')
                                    else:
                                        print(Fore.RED + "ERROR: " + Fore.RESET + f"{fname} 第 {i} 行卷标与文件名不符, 请检查")
                                        done_flg = False
                                        break_flg = True
                                        break
                                elif self.settings.pat_toc_blank.match(line):
                                    # 无页码的
                                    mth_blank = self.settings.pat_toc_blank.match(line)
                                    lst_vols[vol_n-1].append(f'{mth_blank.group(1)}{mth_blank.group(2)}\n')
                                else:
                                    print(Fore.RED + "ERROR: " + Fore.RESET + f"{fname} 第 {i} 行未匹配")
                                    done_flg = False
                                    break_flg = True
                                    break
                else:
                    print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"{fname} 不在分卷范围, 已忽略")
                if break_flg:
                    break
        # 2.生成新的 index, toc
        if done_flg:
            for i in range(len(lst_vols)):
                if lst_vols[i]:
                    with open(os.path.join(dir_out, f'{prefix}_{str(i+1).zfill(2)}.txt'), 'a', encoding='utf-8') as fa:
                        for item in lst_vols[i]:
                            fa.write(item)
        return done_flg

    def _check_txt_top(self, file_in, prefix, dir_out):
        """ 识别总 index, toc 文本 """
        done_flg = True
        check_num = self.func.text_file_check(file_in)
        if check_num == 1:
            done_flg = False
        elif check_num == 2:
            fname = os.path.split(file_in)[1]
            lst_vols = [[] for i in range(self.settings.volume_num)]
            with open(file_in, 'r', encoding='utf-8') as fr:
                i = 0
                if prefix == 'index':
                    for line in fr:
                        i += 1
                        mth = self.settings.pat_index.match(line)
                        if mth:
                            # 未标分卷的一律归到第一卷
                            lst_vols[0].append(f'{mth.group(1)}\t{mth.group(2)}\n')
                        elif self.settings.pat_index_vol.match(line):
                            mth_vol = self.settings.pat_index_vol.match(line)
                            if int(mth_vol.group(2)) <= self.settings.volume_num:
                                lst_vols[int(mth_vol.group(2))-1].append(f'{mth_vol.group(1)}\t{mth_vol.group(3)}\n')
                            else:
                                print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"{fname} 第 {i} 行分卷号超出范围, 已忽略")
                        else:
                            print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"{fname} 第 {i} 行未匹配, 已忽略")
                elif prefix == 'toc':
                    lst_top = []
                    for line in fr:
                        i += 1
                        mth = self.settings.pat_toc.match(line)
                        if mth:
                            # 未标分卷的一律归到第一卷
                            lst_vols[0].append(f'{mth.group(1)}{mth.group(2)}\t{mth.group(3)}\n')
                            lst_top.append(f'{mth.group(1)}{mth.group(2)}\t{mth.group(3)}\n')
                        elif self.settings.pat_toc_vol.match(line):
                            # 标示分卷的
                            mth_vol = self.settings.pat_toc_vol.match(line)
                            if int(mth_vol.group(3)) <= self.settings.volume_num:
                                lst_vols[int(mth_vol.group(3))-1].append(f'{mth_vol.group(1)}{mth_vol.group(2)}\t{mth_vol.group(4)}\n')
                                lst_top.append(f'{mth_vol.group(1)}{mth_vol.group(2)}\t[{mth_vol.group(3)}]{mth_vol.group(4)}\n')
                            else:
                                print(Fore.RED + "ERROR: " + Fore.RESET + f"{fname} 第 {i} 行分卷号超出范围")
                                done_flg = False
                                break
                        elif self.settings.pat_toc_blank.match(line):
                            # 空白无页码的, 无需归入分卷
                            mth_blank = self.settings.pat_toc_blank.match(line)
                            lst_top.append(f'{mth_blank.group(1)}{mth_blank.group(2)}\n')
                        else:
                            print(Fore.RED + "ERROR: " + Fore.RESET + f"{fname} 第 {i} 行未匹配")
                            done_flg = False
                            break
            if done_flg:
                # 生成分 index/toc 文件
                for i in range(len(lst_vols)):
                    if lst_vols[i]:
                        with open(os.path.join(dir_out, f'{prefix}_{str(i+1).zfill(2)}.txt'), 'a', encoding='utf-8') as fa:
                            for item in lst_vols[i]:
                                fa.write(item)
                # 生成总 toc 文件
                if prefix == 'toc':
                    with open(os.path.join(dir_out, f'{prefix}.txt'), 'w', encoding='utf-8') as fw:
                        for item in lst_top:
                            fw.write(item)
        return done_flg

    def _check_raw_files(self):
        """ 检查原材料
        * 必要文本存在(文本编码均要是 utf-8 无 bom)
        * 图像文件夹存在, 正文起始数要大于1, 图像个数要大于正文起始数
        * 图像个数与索引范围匹配, 不冲突
        * 检查 info.html 的编码
        """
        check_result = []
        # (一) 初步检查, 确定输入文件路径
        prepare_flg = True
        dir_input = self.settings.dir_input
        dir_imgs = os.path.join(dir_input, self.settings.dname_imgs)
        file_index = os.path.join(dir_input, self.settings.fname_index)
        file_toc = os.path.join(dir_input, self.settings.fname_toc)
        # 准备临时文件夹
        dir_index = self.settings.dir_index
        if os.path.exists(dir_index):
            shutil.rmtree(dir_index)
            os.makedirs(dir_index)
        else:
            os.makedirs(dir_index)
        dir_toc = self.settings.dir_toc
        if os.path.exists(dir_toc):
            shutil.rmtree(dir_toc)
            os.makedirs(dir_toc)
        else:
            os.makedirs(dir_toc)
        # 场景一: 多卷 (imgs 文件夹存在是先决条件)
        if os.path.exists(dir_imgs) and self.settings.multi_volume:
            # --- 1.index ---
            # 依次检查分索引, 总索引
            if self._check_txt_top(file_index, 'index', dir_index):
                prepare_flg = self._check_txt_vols(dir_input, 'index', dir_index)
            lst_file_index = [None for i in range(self.settings.volume_num)]
            for fname in os.listdir(dir_index):
                vol_n = int(re.match(r'index_(\d+)', fname, flags=re.I).group(1))
                lst_file_index[vol_n-1] = os.path.join(dir_index, fname)
            # --- 2.toc ---
            # 检查总目录
            prepare_flg = self._check_txt_top(file_toc, 'toc', dir_toc)
            if prepare_flg and not os.path.exists(os.path.join(dir_toc, 'toc.txt')):
                # 不存在则检查分目录
                file_toc = None
                prepare_flg = self._check_txt_vols(dir_input, 'toc', dir_toc)
            elif prepare_flg:
                file_toc = os.path.join(dir_toc, 'toc.txt')
            lst_file_toc = [None for i in range(self.settings.volume_num)]
            for fname in os.listdir(dir_toc):
                # 要先判断是否匹配, 因为可能存在 toc.txt
                mth = re.match(r'toc_(\d+)', fname, flags=re.I)
                if mth:
                    vol_n = int(mth.group(1))
                    lst_file_toc[vol_n-1] = os.path.join(dir_toc, fname)
            # --- 3.dir_imgs ---
            if prepare_flg and len(os.listdir(dir_index)) == 0 and len(os.listdir(dir_toc)) == 0:
                print(Fore.RED + "ERROR: " + Fore.RESET + "未读取到 index 或 toc")
                prepare_flg = False
            else:
                # 检查图像文件夹
                lst_dir_imgs = [None for i in range(self.settings.volume_num)]
                dct_dir_imgs = {"main": lst_dir_imgs, "others": []}
                pat_imgs = re.compile(r'vol_(\d+)', flags=re.I)
                for fname in os.listdir(dir_imgs):
                    fp = os.path.join(dir_imgs, fname)
                    if os.path.isdir(fp) and pat_imgs.match(fname):
                        vol_n = int(pat_imgs.match(fname).group(1))
                        if vol_n <= self.settings.volume_num:
                            dct_dir_imgs["main"][vol_n-1] = fp
                        else:
                            print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"图像文件夹 {fname} 未设置 body_start, 将不纳入检索范围, 仅打包")
                            dct_dir_imgs["others"].append(fp)
                    elif os.path.isdir(fp):
                        print(Fore.YELLOW + "INFO: " + Fore.RESET + f"图像文件夹 {fname} 非分卷名称, 将不纳入检索范围, 仅打包")
                        dct_dir_imgs["others"].append(fp)
                # check
                if None in dct_dir_imgs["main"]:
                    print(Fore.RED + "ERROR: " + Fore.RESET + "分卷图像文件夹数目不足")
                    prepare_flg = False
        # 场景二: 单卷 (imgs 文件夹存在是先决条件)
        elif os.path.exists(dir_imgs):
            # 1.index
            prepare_flg = self._check_txt_top(file_index, 'index', dir_index)
            if os.path.exists(os.path.join(dir_index, 'index_01.txt')):
                file_index = os.path.join(dir_index, 'index_01.txt')
            else:
                file_index = None
            # 2.toc
            prepare_flg = self._check_txt_top(file_toc, 'toc', dir_toc)
            if os.path.exists(os.path.join(dir_toc, 'toc.txt')):
                file_toc = os.path.join(dir_toc, 'toc.txt')
            else:
                file_toc = None
            # check: index or toc
            if prepare_flg and file_toc is None and file_index is None:
                prepare_flg = False
                print(Fore.RED + "ERROR: " + Fore.RESET + "未读取到 index 或 toc")
        else:
            print(Fore.RED + "ERROR: " + Fore.RESET + f"{self.settings.dname_imgs} 图像文件夹不存在")
            prepare_flg = False
        # (二) 开始进一步检查
        if prepare_flg:
            # 1,2,3.开始检查索引, 目录, 图像文件夹
            if self.settings.multi_volume:
                if file_toc:
                    check_result = [lst_file_index, file_toc, dct_dir_imgs]
                else:
                    check_result = [lst_file_index, lst_file_toc, dct_dir_imgs]
                for i in range(self.settings.volume_num):
                    if lst_file_index[i] or lst_file_toc[i]:
                        if not self._check_img_vol(lst_file_index[i], lst_file_toc[i], dct_dir_imgs["main"][i], i):
                            check_result = []
                            break
            else:
                if self._check_img_vol(file_index, file_toc, dir_imgs):
                    check_result = [file_index, file_toc, dir_imgs]
            # 4.检查同义词文件: 若存在就要合格
            file_syns = os.path.join(self.settings.dir_input, self.settings.fname_syns)
            syns_check_num = self.func.text_file_check(file_syns)
            if syns_check_num == 0:
                check_result.append(None)
            elif syns_check_num == 2:
                check_result.append(file_syns)
            # 5.检查 info.html: 若存在就要合格
            file_dict_info = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
            info_check_num = self.func.text_file_check(file_dict_info)
            if info_check_num == 0:
                check_result.append(None)
            elif info_check_num == 2:
                check_result.append(file_dict_info)
        # (三) 返回最终检查结果
        if len(check_result) == 5:
            return check_result
        else:
            return False
