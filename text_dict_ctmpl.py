#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-16 00:00:41
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.6

import os
import re
from tomlkit import dumps
from colorama import Fore


class TextDictCtmpl:
    """ 文本词典（模板C） """
    def __init__(self, amb):
        self.settings = amb.settings
        self.func = amb.func

    def make_source_file(self):
        """ 制作预备 txt 源文本 """
        # 初始化, 检查原材料
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
            # 1.分步生成各部分源文本
            file_1 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entries_text)  # 文本词条
            file_2 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_syn)  # 同义词重定向
            file_3 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_st)  # 繁简重定向
            # (1) 生成文本(主)词条
            headwords = self._make_entries_text(check_result[0], file_1)
            # (2) 生成同义词重定向
            if check_result[1]:
                headwords += self.func.make_redirects_syn(check_result[1], file_2)
            # (3) 生成繁简通搜重定向
            if self.settings.simp_trad_flg:
                self.func.make_redirects_st(headwords, file_3)
            # 2.合并成最终 txt 源文本
            entry_total = self.func.merge_and_count([file_1, file_2, file_3], file_final_txt)
            print(f'\n源文本 "{self.settings.fname_final_txt}"（共 {entry_total} 词条）生成完毕！')
            # 3.生成 info.html
            self.func.generate_info_html(check_result[2], file_dict_info, self.settings.name, 'C')
            # 返回制作结果
            return [file_final_txt, check_result[3], file_dict_info]
        else:
            print(Fore.RED + "\n材料检查不通过, 请确保材料准备无误再执行程序" + Fore.RESET)
            return None

    def extract_final_txt(self, file_final_txt, out_dir, dict_name):
        """ 从模板C词典的源 txt 文本中提取 index, syns 信息 """
        # 提取资料
        with open(file_final_txt, 'r', encoding='utf-8') as fr:
            text = fr.read()
            # 1.提取 index
            pat_index = re.compile(r'^<div class="entry-headword">(.+?)</div>[\r\n]+<div class="entry-body">(.+?)</div>[\r\n]+</>$', flags=re.M)
            with open(os.path.join(out_dir, 'index.txt'), 'w', encoding='utf-8') as fw:
                for t in pat_index.findall(text):
                    fw.write(f'{t[0]}\t{t[1]}\n')
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
                print(Fore.MAGENTA + "WARN: " + Fore.RESET + "未识别到词典缩略字母, 已设置默认值")
                name_abbr = 'XXXXCD'
        # 输出 build.toml 文件
        self.settings.load_build_toml(os.path.join(self.settings.dir_lib, self.settings.build_tmpl), False)
        self.settings.build["global"]["templ_choice"] = "C"
        self.settings.build["global"]["name"] = dict_name
        self.settings.build["global"]["name_abbr"] = name_abbr
        with open(os.path.join(out_dir, 'build.toml'), 'w', encoding='utf-8') as fw:
            fw.write(dumps(self.settings.build))

    def _make_entries_text(self, file_index, file_out):
        headwords = []
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
                        if not self.settings.add_headwords:
                            part_headword = ''
                        else:
                            part_headword = f'<div class="entry-headword">{mth.group(1)}</div>\n'
                        if re.match(r'<(p|div|html|body|title|head)', mth.group(2), flags=re.I):
                            part_body = f'<div class="entry-body">{mth.group(2)}</div>\n'
                        else:
                            part_body = f'<div class="entry-body"><p>{mth.group(2)}</p></div>\n'
                        # 将完整词条写入文件
                        fa.write(part_title+part_css+part_headword+part_body+'</>\n')
                        headwords.append(mth.group(1))
                    else:
                        print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"第 {i} 行未匹配, 已忽略")
        print("文本词条已生成")
        return headwords

    def _check_raw_files(self):
        """ 检查原材料
        * 必要文本存在(文本编码均要是 utf-8 无 bom)
        * 检查 info.html 的编码
        """
        check_result = []
        # 预定义输入文件路径
        file_index = os.path.join(self.settings.dir_input, self.settings.fname_index)
        file_syns = os.path.join(self.settings.dir_input, self.settings.fname_syns)
        file_dict_info = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
        dir_data = os.path.join(self.settings.dir_input, self.settings.dname_data)
        # 1.检查索引文件: 必须存在且合格
        if self.func.text_file_check(file_index) == 2:
            check_result.append(file_index)
            # 2.检查同义词文件: 若存在就要合格
            syns_check_num = self.func.text_file_check(file_syns)
            if syns_check_num == 0:
                check_result.append(None)
            elif syns_check_num == 2:
                check_result.append(file_syns)
            # 3.检查 info.html: 若存在就要合格
            info_check_num = self.func.text_file_check(file_dict_info)
            if info_check_num == 0:
                check_result.append(None)
            elif info_check_num == 2:
                check_result.append(file_dict_info)
            # 4.检查 data 文件夹
            if os.path.isdir(dir_data) and len(os.listdir(dir_data)) != 0:
                check_result.append(dir_data)
            else:
                check_result.append(None)
        # 返回最终检查结果
        if len(check_result) == 4:
            return check_result
        else:
            return None
