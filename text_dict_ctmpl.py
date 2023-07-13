#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-07-13 19:50:13
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.3

import os
import re
from colorama import init, Fore, Back, Style
from settings import Settings
from func_lib import FuncLib


class TextDictCtmpl:
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
            # (一) 生成文本(主)词条
            file_index = os.path.join(self.settings.dir_input, self.settings.fname_index)
            file_1 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entries_text)
            self._make_entries_text(file_index, file_1)
            step += 1
            print(f'\n{step}.文件 "{self.settings.fname_entries_img}" 已生成；')
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
            file_css = os.path.join(self.settings.dir_css, self.settings.css_ctmpl)
            file_css_out = os.path.join(self.settings.dir_output_tmp, self.settings.fname_css)
            os.system(f"copy /y {file_css} {file_css_out}")
            # (五) 生成 info.html
            file_info_raw = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
            file_dict_info = self.func.generate_info_html(self.settings.name, file_info_raw, entry_total, 0)
            return self.proc_flg, file_final_txt, file_dict_info
        else:
            print(Fore.RED + "\n材料检查不通过, 请确保材料准备无误再执行程序")
            return self.proc_flg, None, None

    def _make_entries_text(self, file_index, file_out):
        """ (一) 生成文本(主)词条 """
        with open(file_out, 'a', encoding='utf-8') as fa:
            with open(file_index, 'r', encoding='utf-8') as fr:
                lines = fr.readlines()
                pat = re.compile(r'^([^\t]+)\t([^\t\r\n]+)[\r\n]*$')
                i = 0
                for line in lines:
                    i += 1
                    if pat.match(line):
                        mth = pat.match(line)
                        part_title = f'{mth.group(1)}\n'
                        part_css = f'<link rel="stylesheet" type="text/css" href="{self.settings.name_abbr.lower()}.css"/>\n'
                        part_headword = f'<div class="entry-headword">{mth.group(1)}</div>\n'
                        if re.match(r'<(p|div|html|body|title|head)>', mth.group(2), flags=re.I):
                            part_body = f'<div class="entry-body">{mth.group(2)}</div>\n'
                        else:
                            part_body = f'<div class="entry-body"><p>{mth.group(2)}</p></div>\n'
                        # 将完整词条写入文件
                        fa.write(part_title+part_css+part_headword+part_body+'</>\n')
                    else:
                        print(Fore.YELLOW + "INFO: " + Fore.RESET + f"第 {i} 行未匹配, 已忽略")

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
        file_index = os.path.join(self.settings.dir_input, self.settings.fname_index)
        file_syns = os.path.join(self.settings.dir_input, self.settings.fname_syns)
        file_dict_info = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
        # 1.检查索引文件: 必须存在且合格
        if self.func.text_file_check(file_index) != 2:
            proc_flg = False
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
