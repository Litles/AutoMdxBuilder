#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-16 00:00:48
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.5

import os
import re
from tomlkit import dumps
from colorama import init, Fore
from func_lib import FuncLib


class TextDictDtmpl:
    """ 文本词典（模板D） """
    def __init__(self, amb):
        self.settings = amb.settings
        self.func = FuncLib(amb)
        init(autoreset=True)

    def make_source_file(self):
        """ 制作预备 txt 源文本 """
        # 初始化, 检查原材料
        self.proc_flg, self.proc_flg_syns = self._check_raw_files()
        # 开始制作
        if self.proc_flg:
            print('\n材料检查通过, 开始制作词典……\n')
            # 清空临时目录下所有文件
            for fname in os.listdir(self.settings.dir_output_tmp):
                fpath = os.path.join(self.settings.dir_output_tmp, fname)
                if os.path.isfile(fpath):
                    os.remove(fpath)
            step = 0
            # (一) 生成文本(主)词条, 带层级导航
            file_1 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entries_text_with_navi)
            file_index_all = os.path.join(self.settings.dir_input, self.settings.fname_index_all)
            words_part1 = self._make_entries_text_with_navi(file_index_all, file_1)
            step += 1
            print(f'{step}.文件 "{self.settings.fname_entries_text_with_navi}" 已生成；')
            # (二) 生成近义词重定向
            file_2 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_syn)
            words_part2 = []
            if self.proc_flg_syns:
                words_part2 = self.func.make_redirects_syn(file_2)
                step += 1
                print(f'{step}.文件 "{self.settings.fname_redirects_syn}" 已生成；')
            # (三) 生成繁简通搜重定向
            file_3 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_st)
            if self.settings.simp_trad_flg:
                self.func.make_redirects_st(words_part1+words_part2, file_3)
                step += 1
                print(f'{step}.文件 "{self.settings.fname_redirects_st}" 已生成；')
            # 合并成最终 txt 源文本
            file_final_txt = os.path.join(self.settings.dir_output_tmp, self.settings.fname_final_txt)
            entry_total = self.func.merge_and_count([file_1, file_2, file_3], file_final_txt)
            print(f'\n源文本 "{self.settings.fname_final_txt}"（共 {entry_total} 词条）生成完毕！')
            # 生成 info.html
            file_info_raw = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
            file_dict_info = self.func.generate_info_html(self.settings.name, file_info_raw, 'D')
            return self.proc_flg, file_final_txt, file_dict_info
        else:
            print(Fore.RED + "\n材料检查不通过, 请确保材料准备无误再执行程序")
            return self.proc_flg, None, None

    def extract_final_txt(self, file_final_txt, out_dir, dict_name):
        """ 从模板D词典的源 txt 文本中提取 index, syns 信息 """
        dcts = []
        # 提取资料
        with open(file_final_txt, 'r', encoding='utf-8') as fr:
            text = fr.read()
            # 1.提取 index_all
            pat_index = re.compile(r'^<div class="index-all" style="display:none;">(\d+)\|(.+?)</div>.+?(<div class="(entry-body|toc-list)">[^\r\n]+</div>)$', flags=re.M+re.S)
            for t in pat_index.findall(text):
                if t[2].startswith('<div class="entry-body">'):
                    body = re.search(r'<div class="entry-body">(.+?)</div>$', t[2], flags=re.M).group(1)
                else:
                    body = ''
                dct = {
                    "id": t[0],
                    "name": t[1],
                    "body": body
                }
                dcts.append(dct)
            # 2.提取 syns
            syns_flg = False
            pat_syn = re.compile(r'^([^\r\n]+)[\r\n]+@@@LINK=([^\r\n]+)[\r\n]+</>$', flags=re.M)
            with open(os.path.join(out_dir, 'syns.txt'), 'w', encoding='utf-8') as fw:
                for t in pat_syn.findall(text):
                    fw.write(f'{t[0]}\t{t[1]}\n')
                    syns_flg = True
            if not syns_flg:
                os.remove(os.path.join(out_dir, 'syns.txt'))
            # 3.识别 name_abbr
            mth = re.search(r'^<link rel="stylesheet" type="text/css" href="([^>/\"\.]+?)\.css"/>$', text, flags=re.M)
            if mth:
                name_abbr = mth.group(1).upper()
            else:
                print(Fore.YELLOW + "WARN: " + Fore.RESET + "未识别到词典缩略字母, 已设置默认值")
                name_abbr = 'XXXXCD'
        # 整理 index, 输出 index_all.txt
        dcts.sort(key=lambda dct: dct["id"], reverse=False)
        with open(os.path.join(out_dir, 'index_all.txt'), 'w', encoding='utf-8') as fw:
            for dct in dcts:
                if dct["body"] == '':
                    fw.write(f'{dct["name"]}\t\n')
                else:
                    fw.write(f'{dct["name"]}\t{dct["body"]}\n')
        # 输出 build.toml 文件
        self.settings.load_build_toml(os.path.join(self.settings.dir_lib, self.settings.build_tmpl), False)
        self.settings.build["global"]["templ_choice"] = "D"
        self.settings.build["global"]["name"] = dict_name
        self.settings.build["global"]["name_abbr"] = name_abbr
        with open(os.path.join(out_dir, 'build.toml'), 'w', encoding='utf-8') as fw:
            fw.write(dumps(self.settings.build))

    def _make_entries_text_with_navi(self, file_index_all, file_out):
        words = []
        """ (一) 生成文本(主)词条, 带层级导航 """
        # 1.读取全索引文件
        proc_flg, dcts = self.func.read_index_all(False, file_index_all)
        # 2.生成主体词条
        if proc_flg:
            with open(file_out, 'w', encoding='utf-8') as fw:
                tops = []
                i = 0
                len_dcts = len(dcts)
                for dct in dcts:
                    # 词头部分
                    part_title = f'{dct["title"]}\n'
                    part_css = f'<link rel="stylesheet" type="text/css" href="{self.settings.name_abbr.lower()}.css"/>\n'
                    # 保留索引
                    if dct["level"] == -1:
                        part_index = f'<div class="index-all" style="display:none;">{str(dct["id"]).zfill(10)}|{dct["title"]}</div>\n'
                    else:
                        part_index = f'<div class="index-all" style="display:none;">{str(dct["id"]).zfill(10)}|【L{str(dct["level"])}】{dct["title"]}</div>\n'
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
                    # 词条部分
                    if dct["level"] != -1 and dct["body"] == '':
                        part_headword = ''
                        part_body = ''
                    elif dct["level"] != -1 and dct["body"] != '':
                        part_headword = ''
                        part_body = f'<div class="entry-body">{dct["body"]}</div>\n'
                    elif re.match(r'<(p|div|html|body|title|head)>', dct["body"], flags=re.I):
                        part_headword = f'<div class="entry-headword">{dct["title"]}</div>\n'
                        part_body = f'<div class="entry-body">{dct["body"]}</div>\n'
                    else:
                        part_headword = f'<div class="entry-headword">{dct["title"]}</div>\n'
                        part_body = f'<div class="entry-body"><p>{dct["body"]}</p></div>\n'
                    # bottom-navi 部分
                    if i == 0:
                        part_left = ''
                        part_right = f'<span class="navi-item-right"><a href="entry://{dcts[i+1]["title"]}">{dcts[i+1]["title"]}</a>&#8197;☛</span>'
                    elif i == len_dcts-1:
                        part_left = f'<span class="navi-item-left">☚&#8197;<a href="entry://{dcts[i-1]["title"]}">{dcts[i-1]["title"]}</a></span>'
                        part_right = ''
                    else:
                        part_left = f'<span class="navi-item-left">☚&#8197;<a href="entry://{dcts[i-1]["title"]}">{dcts[i-1]["title"]}</a></span>'
                        part_right = f'<span class="navi-item-right"><a href="entry://{dcts[i+1]["title"]}">{dcts[i+1]["title"]}</a>&#8197;☛</span>'
                    part_bottom = '<div class="bottom-navi">' + part_left + '<span class="navi-item-middle">&#8197;&#12288;&#8197;</span>' + part_right + '</div>\n'
                    # 合并写入
                    fw.write(part_title+part_css+part_index+part_top+part_list+part_headword+part_body+part_bottom+'</>\n')
                    words.append(dct["title"])
                    # 收集顶级章节
                    if dct["level"] == 0:
                        tops.append(dct["title"])
                    i += 1
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
        * 检查 info.html 的编码
        """
        proc_flg = True
        proc_flg_syns = True
        file_index_all = os.path.join(self.settings.dir_input, self.settings.fname_index_all)
        file_syns = os.path.join(self.settings.dir_input, self.settings.fname_syns)
        file_dict_info = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
        # 1.检查索引文件: 必须存在且合格
        if self.func.text_file_check(file_index_all) != 2:
            proc_flg = False
        else:
            proc_flg, dcts = self.func.read_index_all(False, file_index_all)
        # 2.检查同义词文件: 若存在就要合格
        syns_check_result = self.func.text_file_check(file_syns)
        if syns_check_result == 0:
            proc_flg_syns = False
        elif syns_check_result == 1:
            proc_flg = False
        else:
            pass
        # 3.检查 info.html: 若存在就要合格
        if self.func.text_file_check(file_dict_info) == 1:
            proc_flg = False
        return proc_flg, proc_flg_syns
