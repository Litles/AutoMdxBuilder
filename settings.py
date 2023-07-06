#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-07-05 14:49:12
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.0

class Settings:
    """词典属性, css个性化设置"""
    def __init__(self):
        # 词典属性
        self.name = '现代汉语规范词典（第4版）'
        self.name_abbr = 'XDHYGFCD4'  # 书名首字母缩写
        self.body_start = 105  # 正文起始页为第几张图(>=1)

        # 导航栏链接(除TOC外)
        # 可选, 如果词典有目录就需要设置
        self.navi_items = [
            {"a":"凡例", "ref":"凡例"},
            {"a":"音节表", "ref":"音节表"},
            {"a":"部首表", "ref":"部首目录"},
            {"a":"插图", "ref":"彩色插图"},
            {"a":"纪元简表", "ref":"中国历史纪元简表"}
        ]

        # ==== 以下设置不需要更改 ====
        # 输入文件
        self.dir_input = '.\\raw' # 必要目录
        self.dname_imgs = 'imgs' # 必要目录
        self.fname_index = 'index.txt' # 必要文件
        self.fname_toc = 'toc.txt'
        self.fname_syns = 'syns.txt'
        self.fname_dict_info = 'info.html'

        # 输出文件
        self.dir_output_tmp = '.\\_tmp'
        self.fname_entries_main = 'entries_main.txt'
        self.fname_entries_toc = 'entries_toc.txt'
        self.fname_redirects_syn = 'redirects_syn.txt'
        self.fname_redirects_headword = 'redirects_headword.txt'
        self.fname_final_txt = f'{self.name}.txt'
        self.dir_output = '.\\out'
        self.fname_css = f'{self.name_abbr.lower()}.css'

        # 预设 css 样式
        self.css_text = """/*预定义*/
ul {
    margin-right: 0px;
    margin-left: 32px;
    margin-top: 4px;
    margin-bottom: 4px;
    padding: 0px;
}
p {
    text-indent: 2em;
    margin:4px auto;
}
a {text-decoration:none}

/*----------导航------------*/
/*导航框*/
div.top-navi{
    margin: 0px 0px 0px 0px;
    padding: 3px 0px;
    border-top: 3px solid #3b264d;
    background-color: #CD284C; /* ea8790 */
    text-align: center;
}
div.bottom-navi{
    margin: 0px 0px 0px 0px;
    padding: 3px 0px;
    border-bottom: 1px solid #3b264d;/*#ef8b14; #8470FF*/
    background-color: #EAEAEA;
    text-align: center;
}
/*导航链接*/
div.top-navi a:link {color: #ffffff;}
div.top-navi a:hover {background:green;}
div.top-navi a:visited {color: #ffffff}
div.bottom-navi a:link {color: blue;}
div.bottom-navi a:hover {background:yellow;}
span.navi-item-left{
    margin: 0px 0px 0px 4px;
    float: left;
    color: green;
}
span.navi-item-middle span.navi-item{
    margin: 0px 6px 0px 6px;
    color: #ffffff;/*#a50000; #ef8b14; #4a0007; Bule*/
}
span.navi-item-right{
    margin: 0px 4px 0px 0px;
    float: right;
    color: #ffffff;/*#a50000; #ef8b14; #4a0007; Bule*/
}

/*----------词条------------*/
/*图片*/
div.main-img img{
    text-align: center;
    width: 100%;
}
/*目录标题*/
div.toc-title {
    text-align: center;
    margin-bottom: 8px;
    font-weight: bold;
    font-size: 120%;
}
/*目录链接*/
div.toc-text a:link {color: blue;}
div.toc-text a:hover {background:yellow;}
"""