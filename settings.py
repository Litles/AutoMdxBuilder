#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-16 00:00:58
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.5

import os
import sys
from tomli import load
from tomlkit import loads
from colorama import init, Fore


class Settings:
    """ 词典设置 """
    # 【提示】 AMB 1.4 及以后的版本已不在此处配置词典, 请移步 build.toml 文件
    def __init__(self):
        # 程序版本
        self.version = '1.5'

        # 输入文件
        self.dname_imgs = 'imgs'
        self.dname_data = 'data'
        self.fname_index = 'index.txt'
        self.fname_index_all = 'index_all.txt'
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
        self.fname_entries_text = 'entries_text.txt'
        self.fname_entries_img = 'entries_img.txt'
        self.fname_entry_toc = 'entry_toc.txt'
        self.fname_entries_with_navi = 'entries_with_navi.txt'
        self.fname_entries_text_with_navi = 'entries_text_with_navi.txt'
        self.fname_redirects_syn = 'redirects_syn.txt'
        self.fname_redirects_st = 'redirects_st.txt'
        self.fname_redirects_headword = 'redirects_headword.txt'

        # 其他文件
        self.fname_toc_all = 'toc_all.txt'

        # 预设样式/模板
        self.dir_lib = os.path.join(self.dir_bundle, 'lib')
        self.build_tmpl = 'build.toml'
        self.css_atmpl = 'atmpl.css'
        self.css_btmpl = 'btmpl.css'
        self.css_ctmpl = 'ctmpl.css'
        self.css_dtmpl = 'dtmpl.css'

    def load_build_toml(self, file_toml, pdf_flg=False, outside_flg=True):
        build_flg = False
        # 输入文件夹
        self.dir_input = os.path.split(file_toml)[0]
        with open(file_toml, 'rb') as fr:
            try:
                build = load(fr)
                # 通用设置
                self.name = build["global"]["name"]  # 书名
                self.name_abbr = build["global"]["name_abbr"]  # 书名首字母缩写
                self.simp_trad_flg = build["global"]["simp_trad_flg"]  # 是否要繁简通搜
                # 区别设置
                self.templ_choice = build["global"]["templ_choice"].upper()  # 模板选择
                if self.templ_choice == 'A':
                    self.body_start = build["template"]["a"]["body_start"]  # 正文起始页为第几张图(>=1)
                    self.navi_items = build["template"]["a"].get("navi_items", [])
                elif self.templ_choice == 'B':
                    self.body_start = build["template"]["b"]["body_start"]  # 正文起始页为第几张图(>=1)
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
                build_flg = True
            except:
                print(Fore.RED + "ERROR: " + Fore.RESET + "读取 build.toml 文件失败, 请检查格式是否规范、选项是否遗漏")
        # 生成 TOML 对象
        if build_flg:
            with open(file_toml, 'r', encoding='utf-8') as fr:
                self.build = loads(fr.read())
        return build_flg
