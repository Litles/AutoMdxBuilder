#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-16 00:00:34
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.5

import os
import re
from tomlkit import dumps
from colorama import Fore
from func_lib import FuncLib


class ImgDictBtmpl:
    """ 图像词典（模板B） """
    def __init__(self, amb):
        self.settings = amb.settings
        self.func = FuncLib(amb)

    def make_source_file(self):
        """ 制作预备 txt 源文本 """
        # 初始化, 检查原材料
        self.proc_flg, self.proc_flg_syns, self.index_all_flg = self._check_raw_files()
        # 开始制作
        if self.proc_flg:
            print('\n材料检查通过, 开始制作词典……\n')
            # 清空临时目录下所有文件
            for fname in os.listdir(self.settings.dir_output_tmp):
                fpath = os.path.join(self.settings.dir_output_tmp, fname)
                if os.path.isfile(fpath):
                    os.remove(fpath)
            step = 0
            # (一) 生成图像词条
            file_1 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entries_img)
            dir_imgs_out, imgs, p_total, n_len = self.func.make_entries_img(False, file_1)
            step += 1
            print(f'\n{step}.文件 "{self.settings.fname_entries_img}" 已生成；')
            # (二) 生成主体词条, 带层级导航
            file_2 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entries_with_navi)
            if self.index_all_flg:
                file_index_all = os.path.join(self.settings.dir_input, self.settings.fname_index_all)
            else:
                file_toc_all = os.path.join(self.settings.dir_input, self.settings.fname_toc_all)  # index_all 的替代
                file_index_all = os.path.join(self.settings.dir_output_tmp, self.settings.fname_index_all)
                self.func.toc_all_to_index(file_toc_all, file_index_all)
            words_part1 = self._make_entries_with_navi(imgs, file_index_all, file_2)
            step += 1
            print(f'{step}.文件 "{self.settings.fname_entries_with_navi}" 已生成；')
            # (三) 生成近义词重定向
            file_3 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_syn)
            words_part2 = []
            if self.proc_flg_syns:
                words_part2 = self.func.make_redirects_syn(file_3)
                step += 1
                print(f'{step}.文件 "{self.settings.fname_redirects_syn}" 已生成；')
            # (四) 生成繁简通搜重定向
            file_4 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_st)
            if self.settings.simp_trad_flg:
                self.func.make_redirects_st(words_part1+words_part2, file_4)
                step += 1
                print(f'{step}.文件 "{self.settings.fname_redirects_st}" 已生成；')
            # 合并成最终 txt 源文本
            file_final_txt = os.path.join(self.settings.dir_output_tmp, self.settings.fname_final_txt)
            entry_total = self.func.merge_and_count([file_1, file_2, file_3, file_4], file_final_txt)
            print(f'\n源文本 "{self.settings.fname_final_txt}"（共 {entry_total} 词条）生成完毕！')
            # 生成 info.html
            file_info_raw = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
            file_dict_info = self.func.generate_info_html(self.settings.name, file_info_raw, 'B')
            return self.proc_flg, file_final_txt, dir_imgs_out, file_dict_info
        else:
            print(Fore.RED + "\n材料检查不通过, 请确保材料准备无误再执行程序" + Fore.RESET)
            return self.proc_flg, None, None, None

    def extract_final_txt(self, file_final_txt, out_dir, dict_name):
        """ 从模板B词典的源 txt 文本中提取 index_all, syns 信息 """
        dcts = []
        with open(file_final_txt, 'r', encoding='utf-8') as fr:
            text = fr.read()
            # 1.提取 index_all
            pat_index = re.compile(r'^<div class="index-all" style="display:none;">(\d+)\|(.*?)\|([\d|\-]+)</div>$', flags=re.M)
            for t in pat_index.findall(text):
                dct = {
                    "id": t[0],
                    "name": t[1],
                    "page": int(t[2])
                }
                dcts.append(dct)
            # 2.提取 syns, 并同时输出 syns.txt
            syns_flg = False
            pat_syn = re.compile(r'^([^\r\n]+)[\r\n]+@@@LINK=([^\r\n]+)[\r\n]+</>$', flags=re.M)
            with open(os.path.join(out_dir, 'syns.txt'), 'w', encoding='utf-8') as fw:
                for t in pat_syn.findall(text):
                    fw.write(f'{t[0]}\t{t[1]}\n')
                    syns_flg = True
            if not syns_flg:
                os.remove(os.path.join(out_dir, 'syns.txt'))
            # 3.识别 name_abbr, body_start
            body_start = 1
            names = []
            for m in re.findall(r'^([A-Z|\d]+)_A(\d+)[\r\n]+<link rel="stylesheet"', text, flags=re.M):
                if m[0].upper() not in names:
                    names.append(m[0].upper())
                if int(m[1])+1 > body_start:
                    body_start = int(m[1])+1
            if len(names) > 0:
                name_abbr = names[0]
            else:
                print(Fore.YELLOW + "WARN: " + Fore.RESET + "未识别到词典缩略字母, 已设置默认值")
                name_abbr = 'XXXXCD'
        # 整理 index, 输出 index_all.txt
        dcts.sort(key=lambda dct: dct["id"], reverse=False)
        with open(os.path.join(out_dir, 'index_all.txt'), 'w', encoding='utf-8') as fw:
            for dct in dcts:
                if dct["page"] == 0:
                    fw.write(f'{dct["name"]}\t\n')
                else:
                    fw.write(f'{dct["name"]}\t{str(dct["page"])}\n')
        # 输出 build.toml 文件
        self.settings.load_build_toml(os.path.join(self.settings.dir_lib, self.settings.build_tmpl), False)
        self.settings.build["global"]["templ_choice"] = "B"
        self.settings.build["global"]["name"] = dict_name
        self.settings.build["global"]["name_abbr"] = name_abbr
        self.settings.build["template"]["b"]["body_start"] = body_start
        with open(os.path.join(out_dir, 'build.toml'), 'w', encoding='utf-8') as fw:
            fw.write(dumps(self.settings.build))

    def _make_entries_with_navi(self, imgs, file_index_all, file_out):
        """ (二) 生成主体词条, 带层级导航 """
        words = []
        # 1.读取全索引文件
        proc_flg, dcts = self.func.read_index_all(True, file_index_all)
        # 2.生成主体词条
        if proc_flg:
            with open(file_out, 'w', encoding='utf-8') as fw:
                tops = []
                for dct in dcts:
                    words.append(dct["title"])
                    # 词头部分
                    part_title = f'{dct["title"]}\n'
                    part_css = f'<link rel="stylesheet" type="text/css" href="{self.settings.name_abbr.lower()}.css"/>\n'
                    # 保留索引
                    if dct["level"] == -1:
                        part_index = f'<div class="index-all" style="display:none;">{str(dct["id"]).zfill(10)}|{dct["title"]}|{dct["body"]}</div>\n'
                    else:
                        part_index = f'<div class="index-all" style="display:none;">{str(dct["id"]).zfill(10)}|【L{str(dct["level"])}】{dct["title"]}|{dct["body"]}</div>\n'
                    # top-navi-level 部分
                    part_top = '<div class="top-navi-level">'
                    part_top += f'<span class="navi-item"><a href="entry://TOC_{self.settings.name_abbr}">🕮</a></span>'
                    for x in range(len(dct["navi_bar"])):
                        if x == len(dct["navi_bar"])-1 and dct["level"] == -1:
                            part_top += f'<span class="sep-navi">»</span><span class="navi-item-entry"><a href="entry://{dct["navi_bar"][x]}">{dct["navi_bar"][x]}</a></span>'
                        else:
                            part_top += f'<span class="sep-navi">»</span><span class="navi-item"><a href="entry://{dct["navi_bar"][x]}">{dct["navi_bar"][x]}</a></span>'
                    part_top += '</div>\n'
                    # item-list 部分
                    part_list = self.func.get_item_list(dct)
                    # 图像(正文)部分
                    if dct["body"] < 0:
                        i = dct["body"]+self.settings.body_start-1
                    else:
                        i = dct["body"]+self.settings.body_start-2
                    if dct["level"] != -1 and dct["body"] == 0:
                        part_img = ''
                    else:
                        part_img = '<div class="main-img">'
                        part_img += f'<div class="left"><div class="pic"><img src="/{imgs[i]["name"]}"></div></div>'
                        part_img += f'<div class="right"><div class="pic"><img src="/{imgs[i]["name"]}"></div></div>'
                        part_img += '</div>\n'
                    # bottom-navi 部分
                    if i == 0:
                        part_left = ''
                        part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i+1]["title"]}">&#8197;&#12288;☛</a></span>'
                    elif i == len(imgs)-1:
                        part_left = f'<span class="navi-item-left"><a href="entry://{imgs[i-1]["title"]}">☚&#12288;&#8197;</a></span>'
                        part_right = ''
                    else:
                        part_left = f'<span class="navi-item-left"><a href="entry://{imgs[i-1]["title"]}">☚&#12288;&#8197;</a></span>'
                        part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i+1]["title"]}">&#8197;&#12288;☛</a></span>'
                    part_bottom = '<div class="bottom-navi">' + part_left + '<span class="navi-item-middle">&#8197;&#12288;&#8197;</span>' + part_right + '</div>\n'
                    # 合并写入
                    fw.write(part_title+part_css+part_index+part_top+part_list+part_img+part_bottom+'</>\n')
                    # 收集顶级章节
                    if dct["level"] == 0:
                        tops.append(dct["title"])
                # 写入总目词条
                toc_entry = f'TOC_{self.settings.name_abbr}\n'
                toc_entry += f'<link rel="stylesheet" type="text/css" href="{self.settings.name_abbr.lower()}.css"/>\n'
                toc_entry += f'<div class="top-navi-level"><span class="navi-item"><a href="entry://TOC_{self.settings.name_abbr}">🕮</a></span></div>\n'
                toc_entry += '<div class="toc-list"><ul>'
                for top in tops:
                    toc_entry += f'<li><a href="entry://{top}">{top}</a></li>'
                toc_entry += '</ul><div class="bottom-navi">' + '<span class="navi-item-middle">&#8197;&#12288;&#8197;</span>' + '</div>\n'
                toc_entry += '</div>\n</>\n'
                fw.write(toc_entry)
        return words

    def _check_raw_files(self):
        """ 检查原材料
        * 必要文本存在(文本编码均要是 utf-8 无 bom)
        * 图像文件夹存在, 正文起始数要大于1, 图像个数要大于正文起始数
        * 图像个数与索引范围匹配, 不冲突
        * 检查 info.html 的编码
        """
        proc_flg = True
        proc_flg_syns = True
        dir_imgs = os.path.join(self.settings.dir_input, self.settings.dname_imgs)
        index_all_flg = True
        file_index_all = os.path.join(self.settings.dir_input, self.settings.fname_index_all)
        file_toc_all = os.path.join(self.settings.dir_input, self.settings.fname_toc_all)  # index_all 的替代
        file_syns = os.path.join(self.settings.dir_input, self.settings.fname_syns)
        file_dict_info = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
        min_index = 0
        max_index = 0
        # 1.检查索引文件: 必须存在且合格
        if self.func.text_file_check(file_index_all) == 2:
            # 读取词条索引
            p_last = -100000
            mess_items = []
            with open(file_index_all, 'r', encoding='utf-8') as fr:
                lines = fr.readlines()
                pat = re.compile(r'^([^\t]+)\t([\-\d]+)[\r\n]*$')
                for line in lines:
                    mth = pat.match(line)
                    if mth:
                        i = int(mth.group(2))
                        max_index = max(max_index, i)
                        if i < p_last:
                            mess_items.append(f"{mth.group(1)}\t{mth.group(2)}\n")
                        p_last = i
            proc_flg, dcts = self.func.read_index_all(True, file_index_all)
            if len(mess_items) > 0:
                with open(os.path.join(self.settings.dir_input, '_need_checking.log'), 'w', encoding='utf-8') as fw:
                    for mi in mess_items:
                        fw.write(mi)
                print(Fore.YELLOW + "INFO: " + Fore.RESET + "索引中存在乱序的词条, 已输出在日志 _need_checking.log 中, 请检查")
        elif self.func.text_file_check(file_toc_all) == 2:
            index_all_flg = False
            # 读取词条索引
            with open(file_toc_all, 'r', encoding='utf-8') as fr:
                lines = fr.readlines()
                pat = re.compile(r'^(\t*)([^\t]+)\t([\-\d]+)[\r\n]*$')
                for line in lines:
                    if pat.match(line):
                        i = int(pat.match(line).group(3))
                        max_index = max(max_index, i)
        else:
            proc_flg = False
        # 2.检查同义词文件: 若存在就要合格
        syns_check_result = self.func.text_file_check(file_syns)
        if syns_check_result == 0:
            proc_flg_syns = False
        elif syns_check_result == 1:
            proc_flg = False
        else:
            pass
        # 3.检查图像
        n = 0
        if os.path.exists(dir_imgs):
            for fname in os.listdir(dir_imgs):
                n += 1
        if n == 0:
            print(Fore.RED + "ERROR: " + Fore.RESET + f"图像文件夹 {dir_imgs} 不存在或为空")
            proc_flg = False
        elif n < self.settings.body_start:
            print(Fore.RED + "ERROR: " + Fore.RESET + f"图像数量不足(少于起始页码)")
            proc_flg = False
        elif n < max_index - min_index:
            print(Fore.RED + "ERROR: " + Fore.RESET + f"图像数量不足(少于索引范围)")
            proc_flg = False
        # 4.检查 info.html: 若存在就要合格
        if self.func.text_file_check(file_dict_info) == 1:
            proc_flg = False
        return proc_flg, proc_flg_syns, index_all_flg
