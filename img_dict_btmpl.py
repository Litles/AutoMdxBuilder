#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-16 00:00:34
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.6

import os
import re
import shutil
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
        # 清空临时目录下所有文件
        for fname in os.listdir(self.settings.dir_output_tmp):
            fpath = os.path.join(self.settings.dir_output_tmp, fname)
            if os.path.isfile(fpath):
                os.remove(fpath)
        # 检查原材料: index_all, imgs, syns, info
        check_result = self._check_raw_files()
        # 开始制作
        if check_result:
            print('\n材料检查通过, 开始制作词典……\n')
            # 预定义输出文件名
            file_final_txt = os.path.join(self.settings.dir_output_tmp, self.settings.fname_final_txt)
            file_dict_info = os.path.join(self.settings.dir_output_tmp, self.settings.fname_dict_info)
            dir_imgs_tmp = os.path.join(self.settings.dir_output_tmp, self.settings.dname_imgs)
            # 1.分步生成各部分源文本
            file_1 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entries_with_navi)  # 带导航图像词条
            file_2 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_relinks_syn)  # 同义词重定向
            file_3 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_relinks_st)  # 繁简重定向
            # 0.准备图像
            if self.settings.multi_volume:
                imgs, img_lens = self.func.prepare_imgs(check_result[1], dir_imgs_tmp, self.settings.volume_num)
            else:
                imgs, img_lens = self.func.prepare_imgs(check_result[1], dir_imgs_tmp)
                # self.book_dicts = []
            # 1.开始生成各部分源文本
            dcts = self.func.read_index_all(check_result[0])
            # (1) 生成主体词条, 带层级导航
            headwords = self._make_entries_with_navi(imgs, img_lens, dcts, file_1)
            # (2) 生成同义词重定向
            if check_result[2]:
                headwords += self.func.make_relinks_syn(check_result[2], file_2)
            # (3) 生成繁简通搜重定向
            if self.settings.simp_trad_flg:
                self.func.make_relinks_st(headwords, file_3)
            # 2.合并成完整 txt 源文本
            entry_total = self.func.merge_and_count([file_1, file_2, file_3], file_final_txt)
            print(f'\n源文本 "{self.settings.fname_final_txt}"（共 {entry_total} 词条）生成完毕！')
            # 3.生成 info.html
            if self.settings.multi_volume:
                self.func.generate_info_html(check_result[3], file_dict_info, self.settings.name, 'B', self.settings.volume_num)
            else:
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
            with open(os.path.join(out_dir, 'syns.txt'), 'w', encoding='utf-8') as fw:
                for t in self.settings.pat_relink.findall(text):
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
                    self.settings.build["template"]["b"]["auto_split_columns"] = 2
        # 判断 navi_items
        with open(os.path.join(out_dir, 'build.toml'), 'w', encoding='utf-8') as fw:
            fw.write(dumps(self.settings.build))

    def _pre_navi_link(self, imgs, dcts, vpage_dcts):
        """ 匹配图片序号, 生成页面词条代表 """
        # 0.准备各卷卷首图片序号
        lst_vpi = [d["page_index"] for d in vpage_dcts]
        # 1.匹配图片序号
        for x in range(len(dcts)):
            vol_i = dcts[x]["vol_n"]-1
            if dcts[x]["body"] < 0:
                dcts[x]["page_index"] = lst_vpi[vol_i]+self.settings.body_start[vol_i]+dcts[x]["body"]-1
            elif dcts[x]["body"] > 0:
                dcts[x]["page_index"] = lst_vpi[vol_i]+self.settings.body_start[vol_i]+dcts[x]["body"]-2
            else:
                # 如果为空向后检索页码来填充
                for d in dcts[x+1:]:
                    vol_i = d["vol_n"]-1
                    if d["body"] < 0:
                        dcts[x]["page_index"] = lst_vpi[vol_i]+self.settings.body_start[vol_i]+d["body"]-1
                        break
                    elif d["body"] > 0:
                        dcts[x]["page_index"] = lst_vpi[vol_i]+self.settings.body_start[vol_i]+d["body"]-2
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
            elif i in lst_vpi:
                # 取卷首图片
                imgs[i]["dct"] = list(filter(lambda d: d["page_index"] == i, vpage_dcts))[0]
                n = 1
            else:
                # 同上条
                imgs[i]["dct"] = imgs[i-1]["dct"]
                n += 1
            imgs[i]["mark"] = f'[P{str(n)}]'

    def _make_entries_with_navi(self, imgs, img_lens, dcts, file_out):
        """ (二) 生成主体词条, 带层级导航 """
        headwords = []
        # 0.生成每卷首页词条
        vpage_dcts = []
        for x in range(len(self.settings.body_start)):
            vpage_dct = {
                "id": None,
                "level": -1,
                "body": 1-self.settings.body_start[x],
                "vol_n": x+1,
                "page_index": sum(img_lens[i] for i in range(x))
            }
            if self.settings.multi_volume:
                vpage_dct["title"] = f'{self.settings.name_abbr}[{str(x+1).zfill(2)}]'
                vpage_dct["navi_bar"] = [f'{self.settings.name_abbr}[{str(x+1).zfill(2)}]']
            else:
                vpage_dct["title"] = f'{self.settings.name_abbr}'
                vpage_dct["navi_bar"] = [f'{self.settings.name_abbr}']
            vpage_dcts.append(vpage_dct)
        # 1.整理 dcts, imgs
        self._pre_navi_link(imgs, dcts, vpage_dcts)
        # 2.开始制作
        with open(file_out, 'w', encoding='utf-8') as fw:
            # 1.卷首词条
            for dct in vpage_dcts:
                fw.write(self._get_entry_with_navi(dct, imgs))
            # 2.全索引章节和词条部分
            tops = []
            headwords_stem = []
            for dct in dcts:
                headwords.append(dct["title"])
                entry = self._get_entry_with_navi(dct, imgs)
                fw.write(entry)
                # 收集顶级章节
                if dct["level"] != -1:
                    if dct["level"] == 0:
                        tops.append(dct["title"])
                    elif dct["level"] == 1 and self.settings.multi_volume:
                        pass
                    else:
                        headwords_stem.append(dct["title"])
            # 3.总目词条
            toc_entry = f'TOC_{self.settings.name_abbr}\n'
            toc_entry += f'<link rel="stylesheet" type="text/css" href="{self.settings.name_abbr.lower()}.css"/>\n'
            toc_entry += f'<div class="top-navi-level"><span class="navi-item"><a href="entry://TOC_{self.settings.name_abbr}">🕮</a></span></div>\n'
            toc_entry += '<div class="toc-list"><ul>'
            for top in tops:
                toc_entry += f'<li><a href="entry://{self.settings.name_abbr}_{top}">{top}</a></li>'
            toc_entry += '</ul><div class="bottom-navi">' + '<span class="navi-item-middle">&#8197;&#12288;&#8197;</span>' + '</div>\n'
            toc_entry += '</div>\n</>\n'
            fw.write(toc_entry)
            # 4.补页面词条
            for x in range(len(imgs)):
                entry = self._get_entry_with_navi(imgs[x]["dct"], imgs, x)
                fw.write(entry)
            # 5.章节重定向
            for word in headwords_stem:
                fw.write(f'{word}\n@@@LINK={self.settings.name_abbr}_{word}\n</>\n')
        print("图像词条(有导航栏)已生成")
        return headwords

    def _get_entry_with_navi(self, dct, imgs, pi=None):
        # 1.词头部分
        if pi is not None:
            i = pi
            part_title = f'{imgs[i]["title"]}\n'
            part_index = ''
        else:
            i = dct["page_index"]  # 对应图片序号
            # 词头, 索引备份
            if dct["level"] == -1:
                part_title = f'{dct["title"]}\n'
                if dct["id"]:
                    part_index = f'<div class="index-all" style="display:none;">{str(dct["id"]).zfill(10)}|{dct["title"]}|{dct["body"]}</div>\n'
                else:
                    part_index = ''
            else:
                part_title = f'{self.settings.name_abbr}_{dct["title"]}\n'
                part_index = f'<div class="index-all" style="display:none;">{str(dct["id"]).zfill(10)}|【L{str(dct["level"])}】{dct["title"]}|{dct["body"]}</div>\n'
        # 2.css 引用部分
        part_css = f'<link rel="stylesheet" type="text/css" href="{self.settings.name_abbr.lower()}.css"/>\n'
        # 3.top-navi-level 部分
        part_top = '<div class="top-navi-level">'
        part_top += f'<span class="navi-item"><a href="entry://TOC_{self.settings.name_abbr}">🕮</a></span>'
        for x in range(len(dct["navi_bar"])):
            cname = 'navi-item'
            link_name = f'{self.settings.name_abbr}_{dct["navi_bar"][x]}'
            if x == len(dct["navi_bar"])-1 and dct["level"] == -1:
                cname = 'navi-item-entry'
                link_name = dct["navi_bar"][x]
            aname = dct["navi_bar"][x]
            part_top += f'<span class="sep-navi">»</span><span class="{cname}"><a href="entry://{link_name}">{aname}</a></span>'
        if pi is not None and imgs[i]["mark"] != '[P1]':
            # 图像页面的导航(补[P2]后缀)
            part_top = re.sub(r'(">)(.*?)(</a></span>)$', r'\1\2'+imgs[i]["mark"]+r'\3', part_top)
        part_top += '</div>\n'
        # 4.item-list 部分
        part_list = self.func.get_item_list(dct)
        # 5.图像(正文)部分
        if dct["level"] != -1 and dct["body"] == 0:
            part_img = ''
        else:
            # 有图像, 判断是否要分栏
            part_img = '<div class="main-img">'
            body_start = self.settings.body_start[dct["vol_n"]-1]
            body_end_page = self.settings.body_end_page[dct["vol_n"]-1]
            if self.settings.split_columns == 2 and (i >= body_start-1 and i <= body_end_page+body_start-2):
                part_img += f'<div class="left"><div class="pic"><img src="/{imgs[i]["path"]}"></div></div>'
                part_img += f'<div class="right"><div class="pic"><img src="/{imgs[i]["path"]}"></div></div>'
            else:
                part_img += f'<div class="pic"><img src="/{imgs[i]["path"]}"></div>'
            part_img += '</div>\n'
        # 6.bottom-navi 部分
        if i == 0:
            part_left = ''
            # [非图片词条]无页面的章节目录的下一页展示自己
            if pi is None and (dct["level"] != -1 and dct["body"] == 0):
                part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i]["title"]}">{imgs[i]["dct"]["title"]}</a>&#8197;☛</span>'
            # 其他情况
            elif imgs[i+1]["mark"] == '[P1]':
                part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i+1]["title"]}">{imgs[i+1]["dct"]["title"]}</a>&#8197;☛</span>'
            else:
                part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i+1]["title"]}">{imgs[i+1]["dct"]["title"]}{imgs[i+1]["mark"]}</a>&#8197;☛</span>'
        elif i == len(imgs)-1:
            if imgs[i-1]["mark"] == '[P1]':
                part_left = f'<span class="navi-item-left">☚&#8197;<a href="entry://{imgs[i-1]["title"]}">{imgs[i-1]["dct"]["title"]}</a></span>'
            else:
                part_left = f'<span class="navi-item-left">☚&#8197;<a href="entry://{imgs[i-1]["title"]}">{imgs[i-1]["dct"]["title"]}{imgs[i-1]["mark"]}</a></span>'
            part_right = ''
        else:
            if imgs[i-1]["mark"] == '[P1]':
                part_left = f'<span class="navi-item-left">☚&#8197;<a href="entry://{imgs[i-1]["title"]}">{imgs[i-1]["dct"]["title"]}</a></span>'
            else:
                part_left = f'<span class="navi-item-left">☚&#8197;<a href="entry://{imgs[i-1]["title"]}">{imgs[i-1]["dct"]["title"]}{imgs[i-1]["mark"]}</a></span>'
            # [非图片词条]无页面的章节目录的下一页展示自己
            if pi is None and (dct["level"] != -1 and dct["body"] == 0):
                part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i]["title"]}">{imgs[i]["dct"]["title"]}</a>&#8197;☛</span>'
            # 其他情况
            elif imgs[i+1]["mark"] == '[P1]':
                part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i+1]["title"]}">{imgs[i+1]["dct"]["title"]}</a>&#8197;☛</span>'
            else:
                part_right = f'<span class="navi-item-right"><a href="entry://{imgs[i+1]["title"]}">{imgs[i+1]["dct"]["title"]}{imgs[i+1]["mark"]}</a>&#8197;☛</span>'
        part_bottom = '<div class="bottom-navi">' + part_left + '<span class="navi-item-middle">&#8197;&#12288;&#8197;</span>' + part_right + '</div>\n'
        # 合并
        entry = part_title+part_css+part_index+part_top+part_list+part_img+part_bottom+'</>\n'
        return entry

    def _check_img_vol(self, file_index_all, dir_imgs, vol_i=0):
        """ 检查一个分卷的图像数目和索引是否相容 """
        pass_flg = False
        min_index = 0
        max_index = 0
        body_end_page = 0
        dname = os.path.split(dir_imgs)[1]
        # 1.从 index_all 读取页码信息
        with open(file_index_all, 'r', encoding='utf-8') as fr:
            p_last = -100000
            mess_items = []
            pat_stem = re.compile(r'【L\d+】')
            pat_end = re.compile(r'([\-\d]*)[\r\n]*$')
            for line in fr:
                mth_stem = pat_stem.match(line)
                mth_page = pat_end.search(line)
                if mth_page.group(1) != '':
                    p = int(mth_page.group(1))
                    min_index = min(min_index, p)
                    max_index = max(max_index, p)
                    if p < p_last:
                        mess_items.append(line)
                    p_last = p
                    if not mth_stem:
                        body_end_page = max(body_end_page, p)
            if self.settings.body_end_page[vol_i] == 99999:
                self.settings.body_end_page[vol_i] = copy(body_end_page)
        # 开始检查
        if self.settings.body_start[vol_i] < abs(min_index) + 1:
            print(Fore.RED + "ERROR: " + Fore.RESET + f"{dname} 对应正文起始页设置有误(小于最小索引)")
        else:
            # 2.检查图像文件夹
            n = 0
            for fname in os.listdir(dir_imgs):
                if os.path.splitext(fname)[1] in self.settings.img_exts:
                    n += 1
            if n == 0:
                print(Fore.RED + "ERROR: " + Fore.RESET + f"图像文件夹 {dname} 为空")
            elif n < self.settings.body_start[vol_i]:
                print(Fore.RED + "ERROR: " + Fore.RESET + f"{dname} 图像数量不足(少于起始页码)")
            elif n < max_index - min_index:
                print(Fore.RED + "ERROR: " + Fore.RESET + f"{dname} 图像数量不足(少于索引范围)")
            elif n < max_index+self.settings.body_start[vol_i]-1:
                print(Fore.RED + "ERROR: " + Fore.RESET + f"{dname} 图像数量不足(少于设定范围)")
            else:
                # 收集乱序词条
                if len(mess_items) > 0:
                    if not os.path.exists(self.settings.dir_input_tmp):
                        os.makedirs(self.settings.dir_input_tmp)
                    with open(os.path.join(self.settings.dir_input_tmp, '_need_checking['+str(vol_i+1).zfill(2)+'].log'), 'w', encoding='utf-8') as fw:
                        for mi in mess_items:
                            fw.write(mi)
                    print(Fore.MAGENTA + "WARN: " + Fore.RESET + "索引中存在乱序的词条, 已输出在日志 _need_checking.log 中, 建议检查")
                pass_flg = True
        return pass_flg

    def _check_txt_vols(self, dir_input, dir_out):
        """ 检查分卷的 index_all/toc_all 文本 """
        done_flg = True
        lst_file_index_all = [None for i in range(self.settings.volume_num)]
        final_index_all = os.path.join(dir_out, self.settings.fname_index_all)
        # (1) 遍历 index_all
        pat1 = re.compile(r'index_all_(\d+)', flags=re.I)
        for fname in os.listdir(dir_input):
            if fname.endswith('.txt') and pat1.match(fname):
                vol_n = int(pat1.match(fname).group(1))
                fp = os.path.join(dir_input, fname)
                fp_new = os.path.join(dir_out, 'index_all_'+str(vol_n).zfill(2)+'.txt')
                if not os.path.exists(fp_new) and vol_n <= self.settings.volume_num:
                    index_check_num = self.func.text_file_check(fp)
                    if index_check_num == 1:
                        done_flg = False
                        break
                    elif index_check_num == 2:
                        shutil.copy(fp, fp_new)
                        lst_file_index_all[vol_n-1] = fp_new
                elif not os.path.exists(fp_new):
                    print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"{fname} 不在分卷范围, 已忽略")
        # (2) 遍历 toc_all
        pat2 = re.compile(r'toc_all_(\d+)', flags=re.I)
        for fname in os.listdir(dir_input):
            if fname.endswith('.txt') and pat2.match(fname):
                vol_n = int(pat2.match(fname).group(1))
                fp = os.path.join(dir_input, fname)
                fp_new = os.path.join(dir_out, 'index_all_'+str(vol_n).zfill(2)+'.txt')
                if not os.path.exists(fp_new) and vol_n <= self.settings.volume_num:
                    toc_check_num = self.func.text_file_check(fp)
                    if toc_check_num == 1:
                        done_flg = False
                        break
                    elif toc_check_num == 2:
                        if self.func.toc_all_to_index(fp, fp_new):
                            lst_file_index_all[vol_n-1] = fp_new
                        else:
                            done_flg = False
                            break
                elif not os.path.exists(fp_new):
                    print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"{fname} 不在分卷范围, 已忽略")
        # (3) 合并各 index_all 文本, 顺便检查格式
        if done_flg and list(filter(lambda fp: fp is not None, lst_file_index_all)):
            with open(final_index_all, 'w', encoding='utf-8') as fw:
                break_flg = False
                for x in range(len(lst_file_index_all)):
                    if x == 0:
                        str_v = ''
                    else:
                        str_v = '['+str(x+1)+']'
                    if lst_file_index_all[x]:
                        with open(lst_file_index_all[x], 'r', encoding='utf-8') as fr:
                            # 写入卷标
                            if self.settings.vol_names:
                                fw.write('【L0】'+self.settings.vol_names[x]+'\t\n')
                            else:
                                fw.write('【L0】第'+str(x+1).zfill(2)+'卷\t\n')
                            # 整合开始
                            i = 0
                            for line in fr:
                                i += 1
                                mth_stem = self.settings.pat_stem.match(line)
                                if mth_stem:
                                    # 无卷标章节
                                    if mth_stem.group(3) == '':
                                        fw.write(f'【L{str(int(mth_stem.group(1))+1)}】{mth_stem.group(2)}\t\n')
                                    else:
                                        fw.write(f'【L{str(int(mth_stem.group(1))+1)}】{mth_stem.group(2)}\t{str_v}{mth_stem.group(3)}\n')
                                elif self.settings.pat_stem_vol.match(line):
                                    # 有卷标章节
                                    mth_vol_stem = self.settings.pat_stem_vol.match(line)
                                    if int(mth_vol_stem.group(3)) == x+1:
                                        if mth_vol_stem.group(4) == '':
                                            fw.write(f'【L{str(int(mth_vol_stem.group(1))+1)}】{mth_vol_stem.group(2)}\t\n')
                                        else:
                                            fw.write(f'【L{str(int(mth_vol_stem.group(1))+1)}】{mth_vol_stem.group(2)}\t{str_v}{mth_vol_stem.group(4)}\n')
                                    else:
                                        print(Fore.RED + "ERROR: " + Fore.RESET + f"第 {x+1} 卷第 {i} 行卷标与文件名不符, 请检查")
                                        done_flg = False
                                        break_flg = True
                                        break
                                elif self.settings.pat_index.match(line):
                                    # 无卷标词条
                                    mth = self.settings.pat_index.match(line)
                                    fw.write(f'{mth.group(1)}\t{str_v}{mth.group(2)}\n')
                                elif self.settings.pat_index_vol.match(line):
                                    # 有卷标词条
                                    mth_vol = self.settings.pat_index_vol.match(line)
                                    if int(mth_vol.group(2)) == x+1:
                                        fw.write(f'{mth_vol.group(1)}\t{str_v}{mth_vol.group(3)}\n')
                                    else:
                                        print(Fore.RED + "ERROR: " + Fore.RESET + f"第 {x+1} 卷第 {i} 行卷标与文件名不符, 请检查")
                                        done_flg = False
                                        break_flg = True
                                        break
                                else:
                                    print(Fore.RED + "ERROR: " + Fore.RESET + f"第 {x+1} 卷第 {i} 行未匹配, 请检查")
                                    done_flg = False
                                    break_flg = True
                                    break
                    if break_flg:
                        break
        return done_flg

    def _check_txt_top(self, dir_input, dir_out):
        """ 检查总 index_all/toc_all 文本 """
        done_flg = True
        proc_flg = False
        file_index_all = os.path.join(dir_input, self.settings.fname_index_all)
        file_toc_all = os.path.join(dir_input, self.settings.fname_toc_all)  # index_all 的替代
        # 1.扫描识别 index_all 文件
        final_index_all = os.path.join(dir_out, self.settings.fname_index_all)
        index_check_num = self.func.text_file_check(file_index_all)
        toc_check_num = self.func.text_file_check(file_toc_all)
        if index_check_num == 2:
            shutil.copy(file_index_all, final_index_all)
            proc_flg = True
        elif toc_check_num == 2:
            # index_all 不存在则使用 toc_all
            done_flg = self.func.toc_all_to_index(file_toc_all, final_index_all)
            proc_flg = copy(done_flg)
        elif index_check_num == 1 or toc_check_num == 1:
            done_flg = False
        # 2.读取检查 index_all 文件
        if proc_flg:
            lst_sup = [[] for i in range(self.settings.volume_num)]
            with open(final_index_all, 'r', encoding='utf-8') as fr:
                i = 0
                for line in fr:
                    i += 1
                    mth_stem = self.settings.pat_stem.match(line)
                    if mth_stem:
                        # 无卷标章节
                        if mth_stem.group(3) != '':
                            lst_sup[0].append(f'【{mth_stem.group(1)}】{mth_stem.group(2)}\t{mth_stem.group(3)}\n')
                    elif self.settings.pat_stem_vol.match(line):
                        # 有卷标章节
                        mth_vol_stem = self.settings.pat_stem_vol.match(line)
                        if int(mth_vol_stem.group(3)) <= self.settings.volume_num:
                            lst_sup[int(mth_vol_stem.group(3))-1].append(f'【{mth_vol_stem.group(1)}】{mth_vol_stem.group(2)}\t{mth_vol_stem.group(4)}\n')
                        else:
                            print(Fore.RED + "ERROR: " + Fore.RESET + f"index_all.txt 第 {i} 行分卷号超出范围, 请检查")
                            done_flg = False
                            break
                    elif self.settings.pat_index.match(line):
                        # 无卷标词条
                        mth = self.settings.pat_index.match(line)
                        lst_sup[0].append(f'{mth.group(1)}\t{mth.group(2)}\n')
                    elif self.settings.pat_index_vol.match(line):
                        # 有卷标词条
                        mth_vol = self.settings.pat_index_vol.match(line)
                        if int(mth_vol.group(2)) <= self.settings.volume_num:
                            lst_sup[int(mth_vol.group(2))-1].append(f'{mth_vol.group(1)}\t{mth_vol.group(3)}\n')
                        else:
                            print(Fore.RED + "ERROR: " + Fore.RESET + f"index_all.txt 第 {i} 行分卷号超出范围, 请检查")
                            done_flg = False
                            break
                    else:
                        print(Fore.RED + "ERROR: " + Fore.RESET + f"index_all.txt 第 {i} 行未匹配, 请检查")
                        done_flg = False
                        break
            # 3.生成临时分卷
            if done_flg:
                for i in range(len(lst_sup)):
                    if lst_sup[i]:
                        fp = os.path.join(dir_out, f'index_all_{str(i+1).zfill(2)}.txt')
                        with open(fp, 'w', encoding='utf-8') as fw:
                            for item in lst_sup[i]:
                                fw.write(item)
        return done_flg

    def _check_raw_files(self):
        """ 检查原材料
        * 必要文本存在(文本编码均要是 utf-8 无 bom)
        * 图像文件夹存在, 正文起始数要大于1, 图像个数要大于正文起始数
        * 图像个数与索引范围匹配, 不冲突
        * 检查 info.html 的编码
        """
        check_result = []
        # (一) 初步检查, 确定输入文件路径
        prepare_flg = True
        dir_input = self.settings.dir_input
        dir_imgs = os.path.join(dir_input, self.settings.dname_imgs)
        # 准备临时文件夹
        dir_index_all = self.settings.dir_index_all
        if os.path.exists(dir_index_all):
            shutil.rmtree(dir_index_all)
            os.makedirs(dir_index_all)
        else:
            os.makedirs(dir_index_all)
        file_index_all = os.path.join(dir_index_all, self.settings.fname_index_all)
        # 场景一: 多卷 (imgs 文件夹存在是先决条件)
        if os.path.exists(dir_imgs) and self.settings.multi_volume:
            # --- 1.index_all/toc_all ---
            lst_file_index_all = [None for i in range(self.settings.volume_num)]
            # 检查总索引
            prepare_flg = self._check_txt_top(dir_input, dir_index_all)
            if prepare_flg and list(filter(lambda fn: re.match(r'index_all_\d+', fn), os.listdir(dir_index_all))) == []:
                # 不存在则检查分索引
                prepare_flg = self._check_txt_vols(dir_input, dir_index_all)
            if prepare_flg:
                if list(filter(lambda fn: re.match(r'index_all_\d+', fn), os.listdir(dir_index_all))) == []:
                    print(Fore.RED + "ERROR: " + Fore.RESET + "未读取到 index_all/toc_all")
                    prepare_flg = False
                elif os.path.exists(file_index_all):
                    pat = re.compile(r'index_all_(\d+)', flags=re.I)
                    for fname in os.listdir(dir_index_all):
                        mth = pat.match(fname)
                        if mth:
                            lst_file_index_all[int(mth.group(1))-1] = os.path.join(dir_index_all, fname)
                else:
                    print(Fore.RED + "ERROR: " + Fore.RESET + "读取 index_all/toc_all 失败")
                    prepare_flg = False
            # --- 2.dir_imgs ---
            if prepare_flg:
                # 检查图像文件夹
                lst_dir_imgs = [None for i in range(self.settings.volume_num)]
                dct_dir_imgs = {"main": lst_dir_imgs, "others": []}
                pat_imgs = re.compile(r'vol_(\d+)', flags=re.I)
                for fname in os.listdir(dir_imgs):
                    fp = os.path.join(dir_imgs, fname)
                    if os.path.isdir(fp) and pat_imgs.match(fname):
                        vol_n = int(pat_imgs.match(fname).group(1))
                        if vol_n <= self.settings.volume_num:
                            dct_dir_imgs["main"][vol_n-1] = fp
                        else:
                            print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"图像文件夹 {fname} 未设置 body_start, 将不纳入检索范围, 仅打包")
                            dct_dir_imgs["others"].append(fp)
                    elif os.path.isdir(fp):
                        print(Fore.YELLOW + "INFO: " + Fore.RESET + f"图像文件夹 {fname} 非分卷名称, 将不纳入检索范围, 仅打包")
                        dct_dir_imgs["others"].append(fp)
                # check
                if None in dct_dir_imgs["main"]:
                    print(Fore.RED + "ERROR: " + Fore.RESET + "分卷图像文件夹数目不足")
                    prepare_flg = False
        # 场景二: 单卷 (imgs 文件夹存在是先决条件)
        elif os.path.exists(dir_imgs):
            # index_all/toc_all
            prepare_flg = self._check_txt_top(dir_input, dir_index_all)
            if prepare_flg and not os.path.exists(file_index_all):
                print(Fore.RED + "ERROR: " + Fore.RESET + "未读取到 index_all/toc_all")
                prepare_flg = False
        else:
            print(Fore.RED + "ERROR: " + Fore.RESET + f"{self.settings.dname_imgs} 图像文件夹不存在")
            prepare_flg = False
        # (二) 开始进一步检查
        if prepare_flg:
            # 1,2.开始检查全索引文件和图像文件夹
            if self.settings.multi_volume:
                check_result = [file_index_all, dct_dir_imgs]
                if None in lst_file_index_all:
                    print(Fore.MAGENTA + "WARN: " + Fore.RESET + "索引未覆盖全部分卷")
                for i in range(self.settings.volume_num):
                    if lst_file_index_all[i]:
                        if not self._check_img_vol(lst_file_index_all[i], dct_dir_imgs["main"][i], i):
                            check_result = []
                            break
            else:
                if self._check_img_vol(file_index_all, dir_imgs):
                    check_result = [file_index_all, dir_imgs]
            # 3.检查同义词文件: 若存在就要合格
            file_syns = os.path.join(self.settings.dir_input, self.settings.fname_syns)
            syns_check_num = self.func.text_file_check(file_syns)
            if syns_check_num == 0:
                check_result.append(None)
            elif syns_check_num == 2:
                check_result.append(file_syns)
            # 4.检查 info.html: 若存在就要合格
            file_dict_info = os.path.join(self.settings.dir_input, self.settings.fname_dict_info)
            info_check_num = self.func.text_file_check(file_dict_info)
            if info_check_num == 0:
                check_result.append(None)
            elif info_check_num == 2:
                check_result.append(file_dict_info)
        # (三) 返回最终检查结果
        if len(check_result) == 4:
            return check_result
        else:
            return None
