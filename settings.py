#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-07-08 23:33:32
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.1

from os.path import join as pjoin

class Settings:
    """ 词典设置 """
    def __init__(self):
        # 选单 [3]
        self.name = '汉语方言词汇（第二版）'
        # 选单 [3]
        self.name_abbr = 'HYFYCH2'  # 书名首字母缩写
        # 选单 [3]
        self.body_start = 62  # 正文起始页为第几张图(>=1)

        # 选单 [3]
        # 导航栏链接(除TOC外)
        # 可选, 如果词典有目录就需要设置
        self.navi_items = [
            {"a":"凡例", "ref":"凡例"},
            {"a":"北京", "ref":"一、北京话声韵调"},
            {"a":"苏州", "ref":"九、苏州话声韵调"},
            {"a":"武汉", "ref":"五、武汉话声韵调"},
            {"a":"成都", "ref":"六、成都话声韵调"},
            {"a":"潮州", "ref":"十八、潮州话声韵调"},
            {"a":"广州", "ref":"十五、广州话声韵调"}
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
        self.flist_mdx_parts = [
            pjoin(self.dir_output_tmp,self.fname_entries_main),
            pjoin(self.dir_output_tmp,self.fname_entries_toc),
            pjoin(self.dir_output_tmp,self.fname_redirects_syn),
            pjoin(self.dir_output_tmp,self.fname_redirects_headword)
        ]
        self.fname_final_txt = f"{self.name}.txt"
        self.dir_output = '.\\out'
        self.fname_css = f"{self.name_abbr.lower()}.css"

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
    background-color: #CC9933; /* CD284C */
    font-weight: bold;
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
div.top-navi a:visited {color: #ffffff} /* FFFF99 */
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