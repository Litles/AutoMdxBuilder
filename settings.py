#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-07-13 19:50:34
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.3

class Settings:
    """ 词典设置 """
    def __init__(self):
        # 模板 A,B,C,D
        self.name = '汉语委婉语词典'
        # 模板 A,B,C,D
        self.name_abbr = 'HYWWYCD'  # 书名首字母缩写
        # 模板 A,B
        self.body_start = 38  # 正文起始页为第几张图(>=1)
        # 模板 A,B,C,D
        self.simp_trad_flg = False  # 是否要繁简通搜

        # 模板 A
        # 导航栏链接(除TOC外)
        # 可选, 如果词典有目录就需要设置
        self.navi_items = [
            {"a": "凡例", "ref": "凡例"},
            {"a": "北京", "ref": "一、北京话声韵调"},
            {"a": "苏州", "ref": "九、苏州话声韵调"},
            {"a": "武汉", "ref": "五、武汉话声韵调"},
            {"a": "成都", "ref": "六、成都话声韵调"},
            {"a": "潮州", "ref": "十八、潮州话声韵调"},
            {"a": "广州", "ref": "十五、广州话声韵调"}
        ]

        # ==== 以下设置不需要更改 ====
        # 输入文件
        self.dir_input = 'raw'  # [根目录] 模板 A,B,C,D 必要
        self.dname_imgs = 'imgs'  # 模板 A,B 必要目录
        self.dname_data = 'data'
        self.fname_index = 'index.txt'  # 模板 A,C 必要文件
        self.fname_index_all = 'index_all.txt'  # 模板 B,D 必要文件
        self.fname_toc = 'toc.txt'
        self.fname_syns = 'syns.txt'
        self.fname_dict_info = 'info.html'

        # 输出文件
        self.dir_output_tmp = '_tmp'
        self.fname_entries_text = 'entries_text.txt'
        self.fname_entries_img = 'entries_img.txt'
        self.fname_entry_toc = 'entry_toc.txt'
        self.fname_entries_with_navi = 'entries_with_navi.txt'
        self.fname_entries_text_with_navi = 'entries_text_with_navi.txt'
        self.fname_redirects_syn = 'redirects_syn.txt'
        self.fname_redirects_st = 'redirects_st.txt'
        self.fname_redirects_headword = 'redirects_headword.txt'
        self.fname_final_txt = f"{self.name}.txt"
        self.dir_output = 'out'
        self.fname_css = f"{self.name_abbr.lower()}.css"

        # 其他文件
        self.fname_toc_all = 'toc_all.txt'

        # 预设 css 样式
        self.dir_css = 'css'
        self.css_atmpl = 'atmpl.css'
        self.css_btmpl = 'btmpl.css'
        self.css_ctmpl = 'ctmpl.css'
        self.css_dtmpl = 'dtmpl.css'
