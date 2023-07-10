#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-07-08 23:33:40
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.1

import os, re
from datetime import datetime
import chardet
from colorama import init, Fore, Back, Style
from settings import Settings

class FuncLib():
    """ functions for usage """
    def __init__(self):
        self.settings = Settings()

    def text_file_check(self, text_file):
        check_result = 0
        if not os.path.exists(text_file):
            print(Fore.YELLOW + "INFO: " + Fore.RESET + f"文件 {text_file} 不存在")
        elif self._is_blank_file(text_file):
            print(Fore.RED + "ERROR: " + Fore.RESET + f"文件 {text_file} 内容为空")
            check_result = 1
        else:
            check_result = 2
        return check_result

    def merge_and_count(self, file_list, file_final):
        # 筛选出有效文件
        parts = []
        for f in file_list:
            if os.path.exists(f):
                parts.append(f)
        # 开始计数和合并
        entry_total = 0
        if len(parts) == 1 and file_final in parts:
            # 只有单个文件自身, 则不需要写
            with open(file_final, 'r', encoding='utf-8') as fr:
                lines = fr.readlines()
                for line in lines:
                    if line == '</>\n':
                        entry_total += 1
        else:
            # 用临时文件存储, 完了再重命名
            file_tmp = os.path.join(self.settings.dir_output_tmp, 'tmp.xxx')
            with open(file_tmp, 'a+', encoding='utf-8') as fa:
                for part in parts:
                    with open(part, 'r', encoding='utf-8') as fr:
                        lines = fr.readlines()
                        for line in lines:
                            if line == '</>\n':
                                entry_total += 1
                            fa.write(line)
            if os.path.isfile(file_final):
                os.remove(file_final)
            os.rename(file_tmp, file_final)
        return entry_total

    def generate_info_html(self, dict_name, file_info_raw, entry_total, p_total):
        # 创建好临时文件夹
        if not os.path.exists(self.settings.dir_output_tmp):
            os.makedirs(self.settings.dir_output_tmp)
        file_info = os.path.join(self.settings.dir_output_tmp, self.settings.fname_dict_info)
        if os.path.isfile(file_info):
            os.remove(file_info)
        # 生成临时 info.html
        with open(file_info, 'a+', encoding='utf-8') as fa:
            if file_info_raw and os.path.exists(file_info_raw):
                with open(file_info_raw, 'r', encoding='utf-8') as fr:
                    fa.write(fr.read())
                fa.write(f"\n<div><br/>built with AMB on {datetime.now().strftime('%Y/%m/%d')}<br/></div>\n")
            else:
                print(Fore.YELLOW + "INFO: " + Fore.RESET + f"未找到描述文件, 将生成默认词典描述")
                fa.write(f"<div>Name: {dict_name}</div>\n")
                # 写词条数, 页码数
                if p_total != 0:
                    fa.write(f"<div>Pages: {p_total}</div>\n")
                fa.write(f"<div>Entries: {entry_total}</div>\n")
                fa.write(f"<div><br/>built with AMB on {datetime.now().strftime('%Y/%m/%d')}<br/></div>\n")
        return file_info

    def _detect_code(self, text_file):
        with open(text_file, 'rb') as frb:
            data = frb.read()
            dcts = chardet.detect(data)
        return dcts["encoding"]

    def _is_blank_file(self, text_file):
        blank_flg = False
        with open(text_file, 'r', encoding='utf-8') as fr:
            text = fr.read()
            if re.match(r'^\s*$', text):
                blank_flg = True
        return blank_flg
