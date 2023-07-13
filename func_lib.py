#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-07-13 19:50:28
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.3

import os, re
from datetime import datetime
import chardet
from colorama import init, Fore, Back, Style
from settings import Settings


class FuncLib():
    """ functions for usage """
    def __init__(self):
        self.settings = Settings()

    def index_to_toc(self, file_index_all, file_toc_all):
        """ 处理成 toc_all.txt 文件 """
        done_flg = True
        if self.text_file_check(file_index_all) == 2:
            pat1 = re.compile(r'^【L(\d+)】([^\t]+\t[\-\d]+[\r\n]*)$')
            pat2 = re.compile(r'^[^【][^\t]*\t[\-\d]+[\r\n]*$')
            with open(file_toc_all, 'w', encoding='utf-8') as fw:
                with open(file_index_all, 'r', encoding='utf-8') as fr:
                    lines = fr.readlines()
                    level = 0
                    i = 0
                    for line in lines:
                        i += 1
                        if pat1.match(line):
                            mth = pat1.match(line)
                            level = int(mth.group(1))
                            fw.write('\t'*level + mth.group(2))
                        elif pat2.match(line):
                            fw.write('\t'*(level+1) + line)
                        else:
                            print(Fore.YELLOW + "INFO: " + Fore.RESET + f"第 {i} 行未匹配, 请检查")
                            done_flg = False
            # 如果中途失败把半成品删了
            if not done_flg and os.path.exists(file_toc_all):
                os.remove(file_toc_all)
        else:
            done_flg = False
        return done_flg

    def toc_to_index(self, file_toc_all, file_index_all):
        """ 处理成 index_all.txt 文件 """
        done_flg = True
        if self.text_file_check(file_toc_all) == 2:
            pairs = self.read_toc_file(file_toc_all)
            with open(file_index_all, 'w', encoding='utf-8') as fw:
                n_total = len(pairs)
                for i in range(n_total):
                    try:
                        l_after = pairs[i+1]["level"]
                    except IndexError:
                        l_after = 0
                    pair = pairs[i]
                    # 顶级章节, 或者将要展开
                    if pair["level"] == 0 or pair["level"] < l_after:
                        fw.write('【L'+str(pair["level"])+'】'+pair["title"]+'\t'+str(pair["page"])+'\n')
                    else:
                        fw.write(pair["title"]+'\t'+str(pair["page"])+'\n')
        else:
            done_flg = False
        return done_flg

    def read_toc_file(self, file_toc):
        pairs = []
        with open(file_toc, 'r', encoding='utf-8') as fr:
            lines = fr.readlines()
            pat = re.compile(r'^(\t*)([^\t]+)\t([\-\d]+)[\r\n]*$')
            i = 1
            for line in lines:
                if pat.match(line):
                    part_1 = pat.match(line).group(1)
                    part_2 = pat.match(line).group(2)
                    part_3 = pat.match(line).group(3)
                    pair = {
                        "level": len(part_1),
                        "title": part_2,
                        "page": int(part_3)
                    }
                    pairs.append(pair)
                else:
                    print(Fore.YELLOW + "INFO: " + Fore.RESET + f"第 {i} 行未匹配, 已忽略")
                i += 1
        return pairs

    def text_file_check(self, text_file):
        check_result = 0
        if not os.path.exists(text_file) or not os.path.isfile(text_file):
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
            with open(file_tmp, 'a', encoding='utf-8') as fa:
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
        with open(file_info, 'w', encoding='utf-8') as fw:
            if file_info_raw and os.path.exists(file_info_raw):
                with open(file_info_raw, 'r', encoding='utf-8') as fr:
                    fw.write(fr.read())
                fw.write(f"\n<div><br/>built with AMB on {datetime.now().strftime('%Y/%m/%d')}<br/></div>\n")
            else:
                print(Fore.YELLOW + "INFO: " + Fore.RESET + f"未找到描述文件, 将生成默认词典描述")
                fw.write(f"<div>Name: {dict_name}</div>\n")
                # 写词条数, 页码数
                if p_total != 0:
                    fw.write(f"<div>Pages: {p_total}</div>\n")
                fw.write(f"<div>Entries: {entry_total}</div>\n")
                fw.write(f"<div><br/>built with AMB on {datetime.now().strftime('%Y/%m/%d')}<br/></div>\n")
        return file_info

    def _detect_code(self, text_file):
        with open(text_file, 'rb') as frb:
            data = frb.read()
            dcts = chardet.detect(data)
        return dcts["encoding"]

    def _is_blank_file(self, text_file):
        blank_flg = False
        text = ''
        with open(text_file, 'r', encoding='utf-8') as fr:
            lines = fr.readlines()
            i = 0
            for line in lines:
                i += 1
                if i < 6:
                    text += line
                else:
                    break
        if re.match(r'^\s*$', text):
            blank_flg = True
        return blank_flg
