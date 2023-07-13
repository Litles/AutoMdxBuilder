#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-07-13 19:49:56
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.3

import os
import re
from colorama import init, Fore, Back, Style
from settings import Settings
from func_lib import FuncLib


class ImgDictAtmpl:
    """ 图像词典（模板A） """
    def __init__(self):
        self.settings = Settings()
        self.func = FuncLib()
        # 初始化, 检查原材料
        self.proc_flg, self.proc_flg_toc, self.proc_flg_syns = self._check_raw_files()

    def make_source_file(self):
        """ 制作预备 txt 源文本 """
        if self.proc_flg:
            print('\n材料检查通过, 开始制作词典……\n')
            # 创建临时输出目录, 清空目录下所有文件
            if not os.path.exists(self.settings.dir_output_tmp):
                os.makedirs(self.settings.dir_output_tmp)
            for fname in os.listdir(self.settings.dir_output_tmp):
                fpath = os.path.join(self.settings.dir_output_tmp, fname)
                if os.path.isfile(fpath):
                    os.remove(fpath)
            step = 0
            # (一) 生成主体(图像)词条
            file_1 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entries_img)
            dir_imgs_out, p_total, n_len = self._make_entries_img(file_1)
            step += 1
            print(f'\n{step}.文件 "{self.settings.fname_entries_img}" 已生成；')
            # (二) 生成总目词条
            file_2 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entry_toc)
            if self.proc_flg_toc:
                self._make_entry_toc(file_2)
                step += 1
                print(f'{step}.文件 "{self.settings.fname_entry_toc}" 已生成；')
            # (三) 生成词目重定向
            file_3 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_headword)
            self._make_redirects_headword(n_len, file_3, self.proc_flg_toc)
            step += 1
            print(f'{step}.文件 "{self.settings.fname_redirects_headword}" 已生成；')
            # (四) 生成近义词重定向
            file_4 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_syn)
            if self.proc_flg_syns:
                self._make_redirects_syn(file_4)
                step += 1
                print(f'{step}.文件 "{self.settings.fname_redirects_syn}" 已生成；')
            # (五) 合并成最终 txt 源文本
            file_final_txt = os.path.join(self.settings.dir_output_tmp, self.settings.fname_final_txt)
            entry_total = self.func.merge_and_count([file_1, file_2, file_3, file_4], file_final_txt)
            print(f'\n最终源文本 "{self.settings.fname_final_txt}"（共 {entry_total} 词条）生成完毕！')
            # (六) 生成 css 文件
            file_css = os.path.join(self.settings.dir_css, self.settings.css_atmpl)
            file_css_out = os.path.join(self.settings.dir_output_tmp, self.settings.fname_css)
            os.system(f"copy /y {file_css} {file_css_out}")
            # (七) 生成 info.html
            file_info_raw = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
            file_dict_info = self.func.generate_info_html(self.settings.name, file_info_raw, entry_total, p_total)
            return self.proc_flg, file_final_txt, dir_imgs_out, file_dict_info
        else:
            print(Fore.RED + "\n材料检查不通过, 请确保材料准备无误再执行程序")
            return self.proc_flg, None, None, None

    def _check_raw_files(self):
        """ 检查原材料
        * 必要文本存在(文本编码均要是 utf-8 无 bom)
        * 图像文件夹存在, 正文起始数要大于1, 图像个数要大于正文起始数
        * 图像个数与索引范围匹配, 不冲突
        * 检查 info.html 的编码
        """
        proc_flg = True
        proc_flg_toc = True
        proc_flg_syns = True
        dir_imgs = os.path.join(self.settings.dir_input, self.settings.dname_imgs)
        file_index = os.path.join(self.settings.dir_input, self.settings.fname_index)
        file_syns = os.path.join(self.settings.dir_input, self.settings.fname_syns)
        file_toc = os.path.join(self.settings.dir_input, self.settings.fname_toc)
        file_dict_info = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
        min_index = 0
        max_index = 0
        # 1.检查索引文件: 必须存在且合格
        if self.func.text_file_check(file_index) == 2:
            # 读取词条索引
            with open(file_index, 'r', encoding='utf-8') as fr:
                lines = fr.readlines()
                pat = re.compile(r'^([^\t]+)\t([\-\d]+)[\r\n]*$')
                for line in lines:
                    if pat.match(line):
                        i = int(pat.match(line).group(2))
                        max_index = max(max_index, i)
        else:
            proc_flg = False
        # 2.检查目录文件: 若存在就要合格
        toc_check_result = self.func.text_file_check(file_toc)
        if toc_check_result == 0:
            proc_flg_toc = False
        elif toc_check_result == 1:
            proc_flg = False
        else:
            # 读取目录索引
            with open(file_toc, 'r', encoding='utf-8') as fr:
                lines = fr.readlines()
                pat = re.compile(r'^(\t*)([^\t]+)\t([\-\d]+)[\r\n]*$')
                for line in lines:
                    if pat.match(line):
                        i = int(pat.match(line).group(3))
                        min_index = min(min_index, i)
            if self.settings.body_start < abs(min_index) + 1:
                print(Fore.RED + "ERROR: " + Fore.RESET + f"正文起始页设置有误(小于最小索引)")
                proc_flg = False
        # 3.检查同义词文件: 若存在就要合格
        syns_check_result = self.func.text_file_check(file_syns)
        if syns_check_result == 0:
            proc_flg_syns = False
        elif syns_check_result == 1:
            proc_flg = False
        else:
            pass
        # 4.检查图像
        n = 0
        if os.path.exists(dir_imgs):
            for fname in os.listdir(dir_imgs):
                n += 1
        if n == 0:
            print(Fore.RED + "ERROR: " + Fore.RESET + f"图像文件夹 {dir_imgs} 不存在或为空")
            proc_flg = False
        elif n < self.settings.body_start:
            print(Fore.RED + "ERROR: " + Fore.RESET + "图像数量不足(少于起始页码)")
            proc_flg = False
        elif n < max_index - min_index:
            print(Fore.RED + "ERROR: " + Fore.RESET + "图像数量不足(少于索引范围)")
            proc_flg = False
        # 5.检查 info.html: 若存在就要合格
        if self.func.text_file_check(file_dict_info) == 1:
            proc_flg = False
        return proc_flg, proc_flg_toc, proc_flg_syns

    def _make_entries_img(self, file_out):
        """ (一) 生成主体(图像)词条 """
        dir_imgs_out, imgs, n_len = self._prepare_imgs()
        print('图像处理完毕。')
        # 开始生成词条
        p_total = len(imgs)
        with open(file_out, 'w', encoding='utf-8') as fw:
            part_css = f'<link rel="stylesheet" type="text/css" href="{self.settings.name_abbr.lower()}.css"/>\n'
            part_middle = self._generate_navi_middle()
            for i in range(p_total):
                img = imgs[i]
                part_title = f'{img["title"]}\n'
                part_img = f'<div class="main-img"><img src="/{img["name"]}"></div>\n'
                # 生成翻页部分(首末页特殊)
                # 备用: [☚,☛] [☜,☞] [◀,▶] [上一页,下一页] [☚&#12288;&#8197;,&#8197;&#12288;☛]
                if i == 0:
                    part_left = ''
                    part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i+1]["title"]}">&#8197;&#12288;☛</a></span>'
                elif i == p_total-1:
                    part_left = f'<span class="navi-item-left"><a href="entry://{imgs[i-1]["title"]}">☚&#12288;&#8197;</a></span>'
                    part_right = ''
                else:
                    part_left = f'<span class="navi-item-left"><a href="entry://{imgs[i-1]["title"]}">☚&#12288;&#8197;</a></span>'
                    part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i+1]["title"]}">&#8197;&#12288;☛</a></span>'
                # 组合
                part_top = '<div class="top-navi">' + part_left + part_middle + part_right + '</div>\n'
                part_bottom = '<div class="bottom-navi">' + part_left + part_middle + part_right + '</div>\n'
                # 将完整词条写入文件
                fw.write(part_title+part_css+part_top+part_img+part_bottom+'</>\n')
        return dir_imgs_out, p_total, n_len

    def _prepare_imgs(self):
        """ 图像预处理(重命名等) """
        # 图像处理判断
        copy_flg = True
        dir_imgs_in = os.path.join(self.settings.dir_input, self.settings.dname_imgs)
        dir_imgs_out = os.path.join(self.settings.dir_output_tmp, self.settings.dname_imgs)
        if os.path.exists(dir_imgs_out):
            size_in = sum(os.path.getsize(os.path.join(dir_imgs_in, f)) for f in os.listdir(dir_imgs_in) if os.path.isfile(os.path.join(dir_imgs_in, f)))
            size_out = sum(os.path.getsize(os.path.join(dir_imgs_out, f)) for f in os.listdir(dir_imgs_out) if os.path.isfile(os.path.join(dir_imgs_out, f)))
            if size_out == 0:
                pass
            elif size_out == size_in:
                copy_flg = False
            else:
                for fname in os.listdir(dir_imgs_out):
                    fpath = os.path.join(dir_imgs_out, fname)
                    if os.path.isfile(fpath):
                        os.remove(fpath)
        else:
            os.makedirs(dir_imgs_out)
        # 获取图像文件列表
        img_files = []
        for fname in os.listdir(dir_imgs_in):
            fpath = os.path.join(dir_imgs_in, fname)
            if os.path.isfile(fpath):
                img_files.append(fpath)
        # 按旧文件名排序
        img_files.sort()  # 正序排
        n_len = len(str(len(img_files)))  # 获取序号位数
        # 重命名
        imgs = []
        i = 0
        for img_file in img_files:
            i += 1
            f_dir, f_name = os.path.split(img_file)
            f_ext = os.path.splitext(f_name)[1]
            # 区分正文和辅页, 辅页多加前缀'B'
            if i < self.settings.body_start:
                i_str = str(i).zfill(n_len)
                f_title_new = f'{self.settings.name_abbr}_B{i_str}'
            else:
                i_str = str(i-self.settings.body_start+1).zfill(n_len)
                f_title_new = f'{self.settings.name_abbr}_{i_str}'
            imgs.append({'title': f_title_new, 'name': f_title_new+f_ext})
            # 复制新文件到输出文件夹
            img_file_new = os.path.join(dir_imgs_out, f_title_new+f_ext)
            if copy_flg:
                os.system(f"copy /y {img_file} {img_file_new}")
        return dir_imgs_out, imgs, n_len

    def _generate_navi_middle(self):
        """ 生成导航栏中间(链接)部分 """
        html = '<span class="navi-item-middle">'
        if self.proc_flg_toc:
            html += f'<span class="navi-item"><a href="entry://TOC_{self.settings.name_abbr}">🕮</a></span>'
            for item in self.settings.navi_items:
                html += f'<span class="navi-item"><a href="entry://{self.settings.name_abbr}_{item["ref"]}">{item["a"]}</a></span>'
        else:
            html += '&#8197;&#12288;&#8197;'
        html += '</span>'
        return html

    def _make_entry_toc(self, file_out):
        """ (二) 生成总目词条 """
        # 1.读取目录书签文件
        file_toc = os.path.join(self.settings.dir_input, self.settings.fname_toc)
        pairs = self.func.read_toc_file(file_toc)
        # 2.生成总目词条
        with open(file_out, 'w', encoding='utf-8') as fw:
            # 开头
            fw.write(f'TOC_{self.settings.name_abbr}\n<link rel="stylesheet" type="text/css" href="/{self.settings.name_abbr.lower()}.css"/>\n')
            fw.write('<div class="toc-title">目录</div>\n<div class="toc-text">\n<ul>\n')
            # 主体部分
            n_total = len(pairs)
            tab = '\t'
            prefix = '<ul>'
            suffix = '</ul></li>'
            # 根据层级生成 html 列表结构
            for i in range(n_total):
                try:
                    l_after = pairs[i+1]["level"]
                except IndexError:
                    l_after = 0
                pair = pairs[i]
                # 与后同
                if pair["level"] == l_after:
                    fw.write(f'{tab*pair["level"]}<li><a href="entry://{self.settings.name_abbr}_{pair["title"]}">{pair["title"]}</a></li>\n')
                # 比后高(说明将要展开)
                elif pair["level"] < l_after:
                    fw.write(f'{tab*pair["level"]}<li><a href="entry://{self.settings.name_abbr}_{pair["title"]}">{pair["title"]}</a>{prefix}\n')
                # 比后低(说明展开到此结束)
                else:
                    gap = pair["level"] - l_after
                    fw.write(f'{tab*pair["level"]}<li><a href="entry://{self.settings.name_abbr}_{pair["title"]}">{pair["title"]}</a></li>{suffix*gap}\n')
            # 结尾
            fw.write('</ul>\n</div>\n</>\n')

    def _make_redirects_headword(self, n_len, file_out, proc_flg_toc):
        """ (三) 生成词目重定向 """
        # 1a.读取词条索引
        file_index = os.path.join(self.settings.dir_input, self.settings.fname_index)
        pairs = []
        with open(file_index, 'r', encoding='utf-8') as fr:
            lines = fr.readlines()
            pat = re.compile(r'^([^\t]+)\t([\-\d]+)[\r\n]*$')
            i = 1
            for line in lines:
                if pat.match(line):
                    part_1 = pat.match(line).group(1)
                    part_2 = pat.match(line).group(2)
                    pair = {
                        "title": part_1,
                        "page": int(part_2)
                    }
                    pairs.append(pair)
                else:
                    print(Fore.YELLOW + "INFO: " + Fore.RESET + f"第 {i} 行未匹配, 已忽略")
                i += 1
        # 1b.读取目录索引
        if proc_flg_toc:
            file_toc = os.path.join(self.settings.dir_input, self.settings.fname_toc)
            pairs_toc = self.func.read_toc_file(file_toc)
        # 2.生成重定向
        with open(file_out, 'w', encoding='utf-8') as fw:
            # a.词条部分
            for pair in pairs:
                fw.write(f'{pair["title"]}\n@@@LINK={self.settings.name_abbr}_{str(pair["page"]).zfill(n_len)}\n</>\n')
            # b.目录部分
            if proc_flg_toc:
                for pair in pairs_toc:
                    if pair["page"] < 0:
                        fw.write(f'{self.settings.name_abbr}_{pair["title"]}\n@@@LINK={self.settings.name_abbr}_B{str(pair["page"]+self.settings.body_start).zfill(n_len)}\n</>\n')
                    else:
                        fw.write(f'{self.settings.name_abbr}_{pair["title"]}\n@@@LINK={self.settings.name_abbr}_{str(pair["page"]).zfill(n_len)}\n</>\n')

    def _make_redirects_syn(self, file_out):
        """ (四) 生成近义词重定向 """
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
