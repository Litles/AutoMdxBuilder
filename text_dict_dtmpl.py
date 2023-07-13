#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-07-13 19:50:20
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.3

import os
import re
from colorama import init, Fore, Back, Style
from settings import Settings
from func_lib import FuncLib


class TextDictDtmpl:
    """ 图像词典（模板B） """
    def __init__(self):
        self.settings = Settings()
        self.func = FuncLib()
        # 初始化, 检查原材料
        self.proc_flg, self.proc_flg_syns = self._check_raw_files()

    def make_source_file(self):
        """ 制作预备 txt 源文本 """
        if self.proc_flg:
            print('\n材料检查通过, 开始制作词典……\n')
            # 创建临时输出目录, 并清空目录下所有文件
            if not os.path.exists(self.settings.dir_output_tmp):
                os.makedirs(self.settings.dir_output_tmp)
            for fname in os.listdir(self.settings.dir_output_tmp):
                fpath = os.path.join(self.settings.dir_output_tmp, fname)
                if os.path.isfile(fpath):
                    os.remove(fpath)
            step = 0
            # (一) 生成文本(主)词条, 带层级导航
            file_1 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entries_text_with_navi)
            file_index_all = os.path.join(self.settings.dir_input, self.settings.fname_index_all)
            self._make_entries_text_with_navi(file_index_all, file_1)
            step += 1
            print(f'{step}.文件 "{self.settings.fname_entries_text_with_navi}" 已生成；')
            # (二) 生成近义词重定向
            file_2 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_syn)
            if self.proc_flg_syns:
                self._make_redirects_syn(file_2)
                step += 1
                print(f'{step}.文件 "{self.settings.fname_redirects_syn}" 已生成；')
            # (三) 合并成最终 txt 源文本
            file_final_txt = os.path.join(self.settings.dir_output_tmp, self.settings.fname_final_txt)
            entry_total = self.func.merge_and_count([file_1, file_2], file_final_txt)
            print(f'\n最终源文本 "{self.settings.fname_final_txt}"（共 {entry_total} 词条）生成完毕！')
            # (四) 生成 css 文件
            file_css = os.path.join(self.settings.dir_css, self.settings.css_dtmpl)
            file_css_out = os.path.join(self.settings.dir_output_tmp, self.settings.fname_css)
            os.system(f"copy /y {file_css} {file_css_out}")
            # (五) 生成 info.html
            file_info_raw = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
            file_dict_info = self.func.generate_info_html(self.settings.name, file_info_raw, entry_total, 0)
            return self.proc_flg, file_final_txt, file_dict_info
        else:
            print(Fore.RED + "\n材料检查不通过, 请确保材料准备无误再执行程序")
            return self.proc_flg, None, None

    def _make_entries_text_with_navi(self, file_index_all, file_out):
        """ (一) 生成文本(主)词条, 带层级导航 """
        # 1.读取全索引文件
        proc_flg, dcts = self._read_index_all(file_index_all)
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
                        part_index = f'<div class="index-all">{str(dct["id"]).zfill(10)}|{dct["title"]}</div>\n'
                    else:
                        part_index = f'<div class="index-all">{str(dct["id"]).zfill(10)}|【L{str(dct["level"])}】{dct["title"]}</div>\n'
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
                    part_list = self._get_item_list(dct)
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
                    fw.write(part_title+part_css+part_top+part_list+part_headword+part_body+part_bottom+'</>\n')
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

    def _get_item_list(self, dct):
        html = ''
        if dct["level"] == -1:
            pass
        elif dct["entry_list"]:
            html += '<div class="toc-list"><p>'
            i = 0
            for item in dct["children"]:
                i += 1
                if i == 1:
                    html += f'<a href="entry://{item}">{item}</a>'
                else:
                    html += f'<span class="sep-list">／</span><a href="entry://{item}">{item}</a>'
            html += '</p></div>\n'
        elif len(dct["children"]) != 0:
            html += '<div class="toc-list"><ul>'
            for item in dct["children"]:
                html += f'<li><a href="entry://{item}">{item}</a></li>'
            html += '</ul></div>\n'
        else:
            pass
        return html

    def _read_index_all(self, file_index_all):
        done_flg = True
        dcts = []
        dct_chaps = []
        tail_ids = []
        # 用于收集末章节的子词条
        tail_list = []
        tail = {"id": 0, "children": []}
        with open(file_index_all, 'r', encoding='utf-8') as fr:
            pat1 = re.compile(r'^【L(\d+)】([^\t]+)\t([^\t\r\n]*)[\r\n]*$')  # 匹配章节词头
            pat2 = re.compile(r'^([^【][^\t]*)\t([^\t\r\n]+)[\r\n]*$')  # 匹配词条词头
            lines = fr.readlines()
            i = 0
            navi_bar = [None, None, None, None, None, None, None, None]
            navi_bar_tmp = []
            for line in lines:
                i += 1
                checked_flg = False
                # 匹配到章节
                if pat1.match(line):
                    mth = pat1.match(line)
                    dct = {
                        "id": i,
                        "level": int(mth.group(1)),
                        "title": mth.group(2),
                        "body": mth.group(3)
                    }
                    # navi_bar 构造
                    navi_bar[int(mth.group(1))] = mth.group(2)
                    navi_bar_tmp = navi_bar[:int(mth.group(1))+1]
                    dct["navi_bar"] = navi_bar_tmp
                    dct_chaps.append(dct)
                    # 子词条清“篮子”
                    if len(tail["children"]) != 0:
                        tail_list.append({"id": tail["id"], "children": tail["children"]})
                        tail_ids.append(tail["id"])
                    checked_flg = True
                    tail["id"] = i
                    tail["children"] = []
                # 匹配到词条
                elif pat2.match(line):
                    mth = pat2.match(line)
                    dct = {
                        "id": i,
                        "level": -1,
                        "title": mth.group(1),
                        "body": mth.group(2)
                    }
                    dct["navi_bar"] = navi_bar_tmp + [mth.group(1)]
                    # 收集子词条
                    tail["children"].append(mth.group(1))
                else:
                    print(f"第 {i} 行未匹配, 请检查")
                    done_flg = False
                    break
                dcts.append(dct)
            # 遍历完成后补漏
            if not checked_flg and len(tail["children"]) != 0:
                tail_list.append({"id": tail["id"], "children": tail["children"]})
                tail_ids.append(tail["id"])
        # 用于收集大章节的子章节
        stem_ids = []
        stem_list = []
        stem = {"id": 0, "children": []}
        for i in range(len(dct_chaps)-1):
            dct_obj = dct_chaps[i]
            stem["id"] = dct_obj["id"]
            stem["children"] = []
            checked_flg = False
            for dct in dct_chaps[i+1:]:
                if dct["level"] == dct_obj["level"]+1:
                    stem["children"].append(dct["title"])
                elif dct["level"] <= dct_obj["level"]:
                    # 收集子章节
                    if len(stem["children"]) != 0:
                        stem_list.append({"id": stem["id"], "children": stem["children"]})
                        stem_ids.append(stem["id"])
                    checked_flg = True
                    break
            # 补漏收
            if not checked_flg and len(stem["children"]) != 0:
                stem_list.append({"id": stem["id"], "children": stem["children"]})
                stem_ids.append(stem["id"])
        # 检查
        if len(tail_ids+stem_ids) != len(set(tail_ids+stem_ids)):
            done_flg = False
            print(Fore.RED + "ERROR: " + Fore.RESET + f"文件 {file_index_all} 解析出现矛盾, 请检查索引顺序")
        else:
            # 整合所有信息
            for dct in dcts:
                if dct["level"] == -1:
                    dct["children"] = []
                    dct["entry_list"] = False
                elif dct["id"] in tail_ids:
                    for item in tail_list:
                        if dct["id"] == item["id"]:
                            dct["children"] = item["children"]
                            dct["entry_list"] = True
                            break
                elif dct["id"] in stem_ids:
                    for item in stem_list:
                        if dct["id"] == item["id"]:
                            dct["children"] = item["children"]
                            dct["entry_list"] = False
                            break
                else:
                    dct["children"] = []
                    dct["entry_list"] = False
        return done_flg, dcts

    def _make_redirects_syn(self, file_out):
        """ (二) 生成近义词重定向 """
        # 1.读取重定向索引
        file_syns = os.path.join(self.settings.dir_input, self.settings.fname_syns)
        syns = []
        with open(file_syns, 'r', encoding='utf-8') as fr:
            lines = fr.readlines()
            pat = re.compile(r'^([^\t]+)\t([^\t\r\n]+)[\r\n]*$')
            i = 1
            for line in lines:
                if pat.match(line):
                    part_1 = pat.match(line).group(1)
                    part_2 = pat.match(line).group(2)
                    syn = {
                        "syn": part_1,
                        "origin": part_2
                    }
                    syns.append(syn)
                else:
                    print(Fore.YELLOW + "INFO: " + Fore.RESET + f"第 {i} 行未匹配, 已忽略")
                i += 1
        # 2.生成重定向
        with open(file_out, 'w', encoding='utf-8') as fw:
            for syn in syns:
                fw.write(f'{syn["syn"]}\n@@@LINK={syn["origin"]}\n</>\n')

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
            proc_flg, dcts = self._read_index_all(file_index_all)
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
