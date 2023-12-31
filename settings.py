#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-16 00:00:58
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.6

import os
import sys
import re
from tomli import load
from tomlkit import loads
from colorama import Fore


class Settings:
    """ 词典设置 """
    # 【提示】 AMB 1.4 及以后的版本已不在此处配置词典, 请移步 build.toml 文件
    def __init__(self):
        # 程序版本
        self.version = '1.6'

        # 输入文件
        self.dname_imgs = 'imgs'
        self.img_exts = ['.jpg', 'jpeg', '.jp2', '.png', '.gif', '.bmp', '.tif', '.tiff']
        self.len_digit = 6
        self.dname_data = 'data'
        self.fname_index = 'index.txt'
        self.fname_index_all = 'index_all.txt'
        self.fname_toc_all = 'toc_all.txt'
        self.fname_toc = 'toc.txt'
        self.fname_syns = 'syns.txt'
        self.fname_dict_info = 'info.html'

        # 输出文件
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            self.dir_bundle = sys._MEIPASS
        else:
            self.dir_bundle = os.getcwd()
        self.dir_output_tmp = os.path.join(self.dir_bundle, '_tmp')
        if not os.path.exists(self.dir_output_tmp):
            os.makedirs(self.dir_output_tmp)
        self.dir_index = os.path.join(self.dir_output_tmp, 'index')
        self.dir_toc = os.path.join(self.dir_output_tmp, 'toc')
        self.dir_index_all = os.path.join(self.dir_output_tmp, 'index_all')
        self.fname_entries_text = 'entries_text.txt'
        self.fname_entries_img = 'entries_img.txt'
        self.fname_entry_toc = 'entry_toc.txt'
        self.fname_entries_with_navi = 'entries_with_navi.txt'
        self.fname_entries_text_with_navi = 'entries_text_with_navi.txt'
        self.fname_relinks_syn = 'relinks_syn.txt'
        self.fname_relinks_st = 'relinks_st.txt'
        self.fname_relinks_headword = 'relinks_headword.txt'
        self.file_log = os.path.join(self.dir_bundle, '_log.log')

        # 文本格式
        # index/index_all
        self.pat_stem = re.compile(r'【L(\d+)】([^\t]+)\t(\-\d+|\d*)[\r\n]*$')               # 匹配图像词典全索引的主干条目 (有页码/无页码)
        self.pat_stem_vol = re.compile(r'【L(\d+)】([^\t]+)\t\[(\d+)\](\-\d+|\d*)[\r\n]*$')  # [有卷标]匹配图像词典全索引的主干条目 (有页码/无页码)
        self.pat_stem_text = re.compile(r'【L(\d+)】([^\t]+)\t([^\t\r\n]*)[\r\n]*$')         # 匹配文本词典全索引的主干条目 (有内容/无内容)
        self.pat_index = re.compile(r'([^\t]+)\t(\-?\d+)[\r\n]*$')                         # 匹配图像词典索引 (有页码)
        self.pat_index_vol = re.compile(r'([^\t]+)\t\[(\d+)\](\-?\d+)[\r\n]*$')            # [有卷标]匹配图像词典索引 (有页码)
        # toc
        self.pat_toc = re.compile(r'(\t*)([^\t]+)\t(\-?\d+)[\r\n]*$')               # 匹配图像词典目录 (有页码)
        self.pat_toc_vol = re.compile(r'(\t*)([^\t]+)\t\[(\d+)\](\-?\d+)[\r\n]*$')  # [有卷标]匹配图像词典目录 (有页码)
        self.pat_toc_blank = re.compile(r'(\t*)([^\t\r\n]+)[\t\r\n]*$')             # 匹配图像词典目录 (无页码)
        # TAB分隔(通用)
        self.pat_tab = re.compile(r'([^\t]+)\t([^\t\r\n]+)[\r\n]*$')
        # 提取
        self.pat_relink = re.compile(r'^([^\r\n]+)[\r\n]+@@@LINK=([^\r\n]+)[\r\n]+</>[\r\n]*$', flags=re.M)

        # 预设样式/模板
        self.dir_lib = os.path.join(self.dir_bundle, 'lib')
        self.build_tmpl = 'build.toml'
        self.css_atmpl = 'atmpl.css'
        self.css_btmpl = 'btmpl.css'
        self.css_ctmpl = 'ctmpl.css'
        self.css_dtmpl = 'dtmpl.css'
        self.css_split_2 = 'auto_split_2.css'

        # 预设值
        self.split_columns = 1
        self.body_end_page = [99999]
        self.add_headwords = True
        self.multi_volume = False
        self.volume_num = 1
        self.vol_names = []

    def load_build_toml(self, file_toml, pdf_flg=False, outside_flg=True):
        build_flg = True
        # 输入文件夹
        self.dir_input = os.path.split(file_toml)[0]
        self.dir_input_tmp = os.path.join(self.dir_input, '_tmp')
        with open(file_toml, 'rb') as fr:
            try:
                build = load(fr)
                # --- 通用设置 ---
                self.name = build["global"]["name"]  # 书名
                self.name_abbr = build["global"]["name_abbr"].upper()  # 书名首字母缩写
                self.simp_trad_flg = build["global"]["simp_trad_flg"]  # 是否要繁简通搜
                # --- 区别设置 ---
                self.templ_choice = build["global"]["templ_choice"].upper()  # 模板选择
                # 模板 A, B
                if self.templ_choice in ('A', 'B'):
                    # --- 1.独有部分 ----
                    if self.templ_choice == 'A':
                        label = 'a'
                        self.navi_items = build["template"][label].get("navi_items", [])
                        for item in self.navi_items:
                            if item["ref"] == "":
                                item["ref"] = item["a"]
                    else:
                        label = 'b'
                    # --- 2.共有部分 ----
                    self.body_start = build["template"][label]["body_start"]  # 正文起始页为第几张图(>=1)
                    if isinstance(self.body_start, int):
                        self.body_start = [self.body_start]
                    # 是否分卷, 卷数, 卷名(可选)
                    self.multi_volume = build["template"][label].get("multi_volume", False)
                    self.vol_names = build["template"][label].get("vol_names", [])
                    if self.multi_volume and len(self.vol_names) not in (0, len(self.body_start)):
                        build_flg = False
                        print(Fore.RED + "ERROR: " + Fore.RESET + "build.toml 中 body_start 和 vol_names 数目不匹配")
                    elif self.multi_volume:
                        self.volume_num = len(self.body_start)
                    # 分栏 (可选)
                    self.split_columns = build["template"][label].get("auto_split_columns", 1)
                    if self.multi_volume:
                        self.body_end_page = build["template"][label].get("body_end_page", [self.body_end_page for i in range(self.volume_num)])
                        if isinstance(self.body_end_page, int):
                            self.body_end_page = [self.body_end_page for i in range(self.volume_num)]
                    else:
                        self.body_end_page = build["template"][label].get("body_end_page", self.body_end_page)
                        if isinstance(self.body_end_page, int):
                            self.body_end_page = [self.body_end_page]
                # 模板 C
                elif self.templ_choice == 'C':
                    self.add_headwords = build["template"]["c"].get("add_headwords", True)
                # 模板 D
                elif self.templ_choice == 'D':
                    self.add_headwords = build["template"]["d"].get("add_headwords", True)
                    # 是否分卷, 卷数, 卷名(可选)
                    self.multi_volume = build["template"]["d"].get("multi_volume", False)
                    self.vol_names = build["template"]["d"].get("vol_names", [])
                # 设定其他变量
                self.fname_final_txt = f"{self.name}.txt"
                self.fname_css = f"{self.name_abbr.lower()}.css"
                # 确定输出文件夹
                if pdf_flg:
                    pass
                elif outside_flg:
                    self.dir_output = os.path.join(os.path.split(self.dir_input)[0], self.name) + '_mdict'
                else:
                    self.dir_output = os.path.join(self.dir_input, self.name) + '_mdict'
            except:
                build_flg = False
                print(Fore.RED + "ERROR: " + Fore.RESET + "读取 build.toml 文件失败, 请检查格式是否规范、选项是否遗漏")
        # 生成 TOML 对象
        if build_flg:
            with open(file_toml, 'r', encoding='utf-8') as fr:
                self.build = loads(fr.read())
        return build_flg
