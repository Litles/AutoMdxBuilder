#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-16 00:00:34
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.6

import os
import re
from copy import copy
from tomlkit import dumps
from colorama import Fore


class ImgDictBtmpl:
    """ 图像词典（模板B） """
    def __init__(self, amb):
        self.settings = amb.settings
        self.func = amb.func

    def make_source_file(self):
        """ 制作预备 txt 源文本 """
        # 检查原材料
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
            dir_imgs_tmp = os.path.join(self.settings.dir_output_tmp, self.settings.dname_imgs)
            # 1.分步生成各部分源文本
            file_1 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entries_with_navi)  # 带导航图像词条
            file_2 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_syn)  # 同义词重定向
            file_3 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_redirects_st)  # 繁简重定向
            # 获取图像信息
            imgs, n_len = self.func.prepare_imgs(check_result[1], dir_imgs_tmp)
            # (1) 生成主体词条, 带层级导航
            headwords = self._make_entries_with_navi(imgs, check_result[0], file_1)
            # (2) 生成同义词重定向
            if check_result[2]:
                headwords += self.func.make_redirects_syn(check_result[2], file_2)
            # (3) 生成繁简通搜重定向
            if self.settings.simp_trad_flg:
                self.func.make_redirects_st(headwords, file_3)
            # 2.合并成完整 txt 源文本
            entry_total = self.func.merge_and_count([file_1, file_2, file_3], file_final_txt)
            print(f'\n源文本 "{self.settings.fname_final_txt}"（共 {entry_total} 词条）生成完毕！')
            # 3.生成 info.html
            self.func.generate_info_html(check_result[3], file_dict_info, self.settings.name, 'B')
            # 返回制作结果
            return [file_final_txt, dir_imgs_tmp, file_dict_info]
        else:
            print(Fore.RED + "\n材料检查不通过, 请确保材料准备无误再执行程序" + Fore.RESET)
            return None

    def extract_final_txt(self, file_final_txt, out_dir, dict_name, file_css=None):
        """ 从模板B词典的源 txt 文本中提取 index_all, syns 信息 """
        dcts = []
        with open(file_final_txt, 'r', encoding='utf-8') as fr:
            text = fr.read()
            # 1.提取 index_all
            pat_index = re.compile(r'^<div class="index-all" style="display:none;">(\d+)\|(.*?)\|([\d|\-]+)</div>$', flags=re.M)
            for t in pat_index.findall(text):
                dct = {
                    "id": t[0],
                    "name": t[1],
                    "page": int(t[2])
                }
                dcts.append(dct)
            # 2.提取 syns, 并同时输出 syns.txt
            syns_flg = False
            pat_syn = re.compile(r'^([^\r\n]+)[\r\n]+@@@LINK=([^\r\n]+)[\r\n]+</>$', flags=re.M)
            with open(os.path.join(out_dir, 'syns.txt'), 'w', encoding='utf-8') as fw:
                for t in pat_syn.findall(text):
                    fw.write(f'{t[0]}\t{t[1]}\n')
                    syns_flg = True
            if not syns_flg:
                os.remove(os.path.join(out_dir, 'syns.txt'))
            # 3.识别 name_abbr, body_start
            body_start = 1
            names = []
            for m in re.findall(r'^([A-Z|\d]+)_A(\d+)[\r\n]+<link rel="stylesheet"', text, flags=re.M):
                if m[0].upper() not in names:
                    names.append(m[0].upper())
                if int(m[1])+1 > body_start:
                    body_start = int(m[1])+1
            if len(names) > 0:
                name_abbr = names[0]
            else:
                print(Fore.MAGENTA + "WARN: " + Fore.RESET + "未识别到词典首字母缩写, 已设置默认值")
                name_abbr = 'XXXXCD'
        # 整理 index, 输出 index_all.txt
        dcts.sort(key=lambda dct: dct["id"], reverse=False)
        with open(os.path.join(out_dir, 'index_all.txt'), 'w', encoding='utf-8') as fw:
            for dct in dcts:
                if dct["page"] == 0:
                    fw.write(f'{dct["name"]}\t\n')
                else:
                    fw.write(f'{dct["name"]}\t{str(dct["page"])}\n')
        # 输出 build.toml 文件
        self.settings.load_build_toml(os.path.join(self.settings.dir_lib, self.settings.build_tmpl), False)
        self.settings.build["global"]["templ_choice"] = "B"
        self.settings.build["global"]["name"] = dict_name
        self.settings.build["global"]["name_abbr"] = name_abbr
        self.settings.build["template"]["b"]["body_start"] = body_start
        # 判断分栏选项
        if file_css and os.path.split(file_css)[1].lower() == name_abbr.lower()+'.css':
            with open(file_css, 'r', encoding='utf-8') as fr:
                if not re.search(r'/\*<insert_css: auto_split>\*/', fr.read(), flags=re.I):
                    self.settings.build["template"]["b"]["auto_split_column"] = 2
        # 判断 navi_items
        with open(os.path.join(out_dir, 'build.toml'), 'w', encoding='utf-8') as fw:
            fw.write(dumps(self.settings.build))

    def _pre_navi_link(self, imgs, dcts):
        """ 匹配图片序号, 生成页面词条代表 """
        # 1.匹配图片序号
        dcts.sort(key=lambda dct: dct["id"], reverse=False)
        for x in range(len(dcts)):
            if dcts[x]["body"] < 0:
                dcts[x]["page_index"] = dcts[x]["body"]+self.settings.body_start-1
            elif dcts[x]["body"] > 0:
                dcts[x]["page_index"] = dcts[x]["body"]+self.settings.body_start-2
            else:
                # 如果为空向后检索页码来填充
                for d in dcts[x+1:]:
                    if d["body"] < 0:
                        dcts[x]["page_index"] = d["body"]+self.settings.body_start-1
                        break
                    elif d["body"] > 0:
                        dcts[x]["page_index"] = d["body"]+self.settings.body_start-2
                        break
        # 2.生成页面词条代表
        n = 1
        for i in range(len(imgs)):
            # 查找页面的最后一个词条
            lst = list(filter(lambda d: d["page_index"] == i, dcts))
            # 把该词条作为代表
            if lst:
                imgs[i]["dct"] = lst[-1]
                n = 1
            elif i == 0:
                imgs[i]["dct"] = dcts[0]
                n = 1
            else:
                imgs[i]["dct"] = imgs[i-1]["dct"]
                n += 1
            imgs[i]["mark"] = f'[P{str(n)}]'

    def _make_entries_with_navi(self, imgs, file_index_all, file_out):
        """ (二) 生成主体词条, 带层级导航 """
        headwords = []
        # 1.读取全索引文件
        proc_flg, dcts = self.func.read_index_all(True, file_index_all)
        # 2.生成主体词条
        if proc_flg:
            # 整理 dcts, imgs
            self._pre_navi_link(imgs, dcts)
            # 开始制作
            with open(file_out, 'w', encoding='utf-8') as fw:
                # 1.全索引词条部分
                tops = []
                for dct in dcts:
                    headwords.append(dct["title"])
                    entry = self._get_entry_with_navi(dct, imgs)
                    fw.write(entry)
                    # 收集顶级章节
                    if dct["level"] == 0:
                        tops.append(dct["title"])
                # 2.总目词条
                toc_entry = f'TOC_{self.settings.name_abbr}\n'
                toc_entry += f'<link rel="stylesheet" type="text/css" href="{self.settings.name_abbr.lower()}.css"/>\n'
                toc_entry += f'<div class="top-navi-level"><span class="navi-item"><a href="entry://TOC_{self.settings.name_abbr}">🕮</a></span></div>\n'
                toc_entry += '<div class="toc-list"><ul>'
                for top in tops:
                    toc_entry += f'<li><a href="entry://{top}">{top}</a></li>'
                toc_entry += '</ul><div class="bottom-navi">' + '<span class="navi-item-middle">&#8197;&#12288;&#8197;</span>' + '</div>\n'
                toc_entry += '</div>\n</>\n'
                fw.write(toc_entry)
                # 3.补页面词条
                for x in range(len(imgs)):
                    entry = self._get_entry_with_navi(imgs[x]["dct"], imgs, x, imgs[x]["mark"])
                    fw.write(entry)
            print("图像词条(有导航栏)已生成")
        else:
            print(Fore.RED + "全索引 index_all.txt 读取失败" + Fore.RESET)
        return headwords

    def _get_entry_with_navi(self, dct, imgs, pi=None, mark=None):
        # 1.词头部分
        if mark:
            i = pi
            part_title = f'{imgs[i]["title"]}\n'
            part_index = ''
        else:
            i = dct["page_index"]  # 对应图片序号
            part_title = f'{dct["title"]}\n'
            # 索引备份
            if dct["level"] == -1:
                part_index = f'<div class="index-all" style="display:none;">{str(dct["id"]).zfill(10)}|{dct["title"]}|{dct["body"]}</div>\n'
            else:
                part_index = f'<div class="index-all" style="display:none;">{str(dct["id"]).zfill(10)}|【L{str(dct["level"])}】{dct["title"]}|{dct["body"]}</div>\n'
        # 2.css 引用部分
        part_css = f'<link rel="stylesheet" type="text/css" href="{self.settings.name_abbr.lower()}.css"/>\n'
        # 3.top-navi-level 部分
        part_top = '<div class="top-navi-level">'
        part_top += f'<span class="navi-item"><a href="entry://TOC_{self.settings.name_abbr}">🕮</a></span>'
        for x in range(len(dct["navi_bar"])):
            if x == len(dct["navi_bar"])-1 and dct["level"] == -1:
                part_top += f'<span class="sep-navi">»</span><span class="navi-item-entry"><a href="entry://{dct["navi_bar"][x]}">{dct["navi_bar"][x]}</a></span>'
            else:
                part_top += f'<span class="sep-navi">»</span><span class="navi-item"><a href="entry://{dct["navi_bar"][x]}">{dct["navi_bar"][x]}</a></span>'
        if mark and mark != '[P1]':
            part_top = re.sub(r'(">)(.*?)(</a></span>)$', r'\1\2'+mark+r'\3', part_top)
        part_top += '</div>\n'
        # 4.item-list 部分
        part_list = self.func.get_item_list(dct)
        # 5.图像(正文)部分
        if dct["level"] != -1 and dct["body"] == 0:
            part_img = ''
        else:
            part_img = '<div class="main-img">'
            if self.settings.split_column == 2 and (i >= self.settings.body_start-1 and i <= self.settings.max_body+self.settings.body_start-2):
                part_img += f'<div class="left"><div class="pic"><img src="/{imgs[i]["name"]}"></div></div>'
                part_img += f'<div class="right"><div class="pic"><img src="/{imgs[i]["name"]}"></div></div>'
            else:
                part_img += f'<div class="pic"><img src="/{imgs[i]["name"]}"></div>'
            part_img += '</div>\n'
        # 6.bottom-navi 部分
        if i == 0:
            part_left = ''
            # 无页面章节的下一页展示自己
            if not mark and (dct["level"] != -1 and dct["body"] == 0):
                part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i]["title"]}">&#8197;&#12288;☛</a></span>'
            else:
                part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i+1]["title"]}">&#8197;&#12288;☛</a></span>'
        elif i == len(imgs)-1:
            part_left = f'<span class="navi-item-left"><a href="entry://{imgs[i-1]["title"]}">☚&#12288;&#8197;</a></span>'
            part_right = ''
        else:
            part_left = f'<span class="navi-item-left"><a href="entry://{imgs[i-1]["title"]}">☚&#12288;&#8197;</a></span>'
            # 无页面章节的下一页展示自己
            if not mark and (dct["level"] != -1 and dct["body"] == 0):
                part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i]["title"]}">&#8197;&#12288;☛</a></span>'
            else:
                part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i+1]["title"]}">&#8197;&#12288;☛</a></span>'
        part_bottom = '<div class="bottom-navi">' + part_left + '<span class="navi-item-middle">&#8197;&#12288;&#8197;</span>' + part_right + '</div>\n'
        # 合并
        entry = part_title+part_css+part_index+part_top+part_list+part_img+part_bottom+'</>\n'
        return entry

    def _check_raw_files(self):
        """ 检查原材料
        * 必要文本存在(文本编码均要是 utf-8 无 bom)
        * 图像文件夹存在, 正文起始数要大于1, 图像个数要大于正文起始数
        * 图像个数与索引范围匹配, 不冲突
        * 检查 info.html 的编码
        """
        check_result = []
        # 预定义输入文件路径
        dir_imgs = os.path.join(self.settings.dir_input, self.settings.dname_imgs)
        file_index_all = os.path.join(self.settings.dir_input, self.settings.fname_index_all)
        file_toc_all = os.path.join(self.settings.dir_input, self.settings.fname_toc_all)  # index_all 的替代
        file_syns = os.path.join(self.settings.dir_input, self.settings.fname_syns)
        file_dict_info = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
        min_index = 0
        max_index = 0
        max_body = 0
        max_remain = 0
        # 初步检查索引文件: 必须存在且合格
        if self.func.text_file_check(file_index_all) == 2:
            index_all_flg = True
        elif self.func.text_file_check(file_toc_all) == 2:
            file_index_all = os.path.join(self.settings.dir_output_tmp, self.settings.fname_index_all)
            index_all_flg = self.func.toc_all_to_index(file_toc_all, file_index_all)
        else:
            index_all_flg = False
        # 若全索引文件初步合格, 则开始进一步检查
        if index_all_flg:
            # 1.从 index_all 读取页码信息
            p_last = -100000
            mess_items = []
            with open(file_index_all, 'r', encoding='utf-8') as fr:
                lines = fr.readlines()
                pat1 = re.compile(r'^(【L\d+】[^\t]+)\t([\-\d]*)[\r\n]*$')  # 匹配章节词头
                pat2 = re.compile(r'^([^【][^\t]*)\t([\-\d]+)[\r\n]*$')  # 匹配词条词头
                # pat = re.compile(r'^([^\t]+)\t([\-\d]+)[\r\n]*$')
                for line in lines:
                    mth1 = pat1.match(line)
                    mth2 = pat2.match(line)
                    if mth1 and mth1.group(2) not in ('', '-'):
                        i = int(mth1.group(2))
                        max_remain = max(max_remain, i)
                        min_index = min(min_index, i)
                        if i < p_last:
                            mess_items.append(f"{mth1.group(1)}\t{mth1.group(2)}\n")
                        p_last = i
                    elif mth2 and mth2.group(2) not in ('', '-'):
                        i = int(mth2.group(2))
                        max_body = max(max_body, i)
                        min_index = min(min_index, i)
                        if i < p_last:
                            mess_items.append(f"{mth2.group(1)}\t{mth2.group(2)}\n")
                        p_last = i
                if self.settings.max_body == 99999:
                    self.settings.max_body = copy(max_body)
                max_index = max(max_body, max_remain)
            if self.settings.body_start < abs(min_index) + 1:
                print(Fore.RED + "ERROR: " + Fore.RESET + "正文起始页设置有误(小于最小索引)")
            else:
                check_result.append(file_index_all)
            # 收集乱序词条
            if len(mess_items) > 0:
                with open(os.path.join(self.settings.dir_input, '_need_checking.log'), 'w', encoding='utf-8') as fw:
                    for mi in mess_items:
                        fw.write(mi)
                print(Fore.MAGENTA + "WARN: " + Fore.RESET + "索引中存在乱序的词条, 已输出在日志 _need_checking.log 中, 建议检查")
                # proc_flg, dcts = self.func.read_index_all(True, file_index_all)
            # 2.检查图像文件夹: 图像数目要与页码数不冲突
            n = 0
            if os.path.exists(dir_imgs):
                for fname in os.listdir(dir_imgs):
                    if os.path.splitext(fname)[1] in self.settings.img_exts:
                        n += 1
            if n == 0:
                print(Fore.RED + "ERROR: " + Fore.RESET + f"图像文件夹 {dir_imgs} 不存在或为空")
            elif n < self.settings.body_start:
                print(Fore.RED + "ERROR: " + Fore.RESET + "图像数量不足(少于起始页码)")
            elif n < max_index - min_index:
                print(Fore.RED + "ERROR: " + Fore.RESET + "图像数量不足(少于索引范围)")
            elif n < max_index+self.settings.body_start-1:
                print(Fore.RED + "ERROR: " + Fore.RESET + "图像数量不足(少于设定范围)")
            else:
                check_result.append(dir_imgs)
            # 3.检查同义词文件: 若存在就要合格
            syns_check_num = self.func.text_file_check(file_syns)
            if syns_check_num == 0:
                check_result.append(None)
            elif syns_check_num == 2:
                check_result.append(file_syns)
            # 4.检查 info.html: 若存在就要合格
            info_check_num = self.func.text_file_check(file_dict_info)
            if info_check_num == 0:
                check_result.append(None)
            elif info_check_num == 2:
                check_result.append(file_dict_info)
        # 返回最终检查结果
        if len(check_result) == 4:
            return check_result
        else:
            return None
