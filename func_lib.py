#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-16 00:00:53
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.5

import os
import re
import shutil
from datetime import datetime
# import chardet
from colorama import init, Fore
import opencc


class FuncLib():
    """ functions for usage """
    def __init__(self, amb):
        self.settings = amb.settings

    def make_entries_img(self, proc_flg_toc, file_out):
        """ (一) 生成图像词条 """
        dir_imgs_out, imgs, n_len = self._prepare_imgs()
        print('图像处理完毕。')
        # 开始生成词条
        p_total = len(imgs)
        with open(file_out, 'w', encoding='utf-8') as fw:
            part_css = f'<link rel="stylesheet" type="text/css" href="{self.settings.name_abbr.lower()}.css"/>\n'
            part_middle = self._generate_navi_middle(proc_flg_toc)
            for i in range(p_total):
                img = imgs[i]
                part_title = f'{img["title"]}\n'
                part_img = '<div class="main-img">'
                part_img += f'<div class="left"><div class="pic"><img src="/{img["name"]}"></div></div>'
                part_img += f'<div class="right"><div class="pic"><img src="/{img["name"]}"></div></div>'
                part_img += '</div>\n'
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
        return dir_imgs_out, imgs, p_total, n_len

    def index_to_toc(self, file_index_all, file_toc_all):
        """ 处理成 toc_all.txt 文件 """
        done_flg = True
        if self.text_file_check(file_index_all) == 2:
            # 读取
            pat1 = re.compile(r'^【L(\d+)】([^\t]+)\t([\-\d]*)[\r\n]*$')
            pat2 = re.compile(r'^([^【][^\t]*)\t([\-\d]*)[\r\n]*$')
            dcts = []
            with open(file_index_all, 'r', encoding='utf-8') as fr:
                lines = fr.readlines()
                level = 0
                i = 0
                for line in lines:
                    i += 1
                    if pat1.match(line):
                        mth = pat1.match(line)
                        level = int(mth.group(1))
                        dct = {
                            "level": level,
                            "name": mth.group(2),
                            "page": mth.group(3)
                        }
                    elif pat2.match(line):
                        dct = {
                            "level": level+1,
                            "name": pat2.match(line).group(1),
                            "page": pat2.match(line).group(2)
                        }
                    else:
                        print(Fore.RED + "ERROR: " + Fore.RESET + f"第 {i} 行格式有误, 请检查")
                        done_flg = False
                        break
                    dcts.append(dct)
            # 输出
            if done_flg:
                with open(file_toc_all, 'w', encoding='utf-8') as fw:
                    for x in range(len(dcts)):
                        level = dcts[x]["level"]
                        name = dcts[x]["name"]
                        page = dcts[x]["page"].strip()
                        if page == '':
                            for d in dcts[x+1:]:
                                if d["page"].strip() != '':
                                    page = d["page"].strip()
                                    break
                        fw.write('\t'*level + name + '\t' + page + '\n')
        else:
            done_flg = False
        return done_flg

    def make_redirects_st(self, words, file_out):
        converter_s2t = opencc.OpenCC('s2t.json')
        converter_t2s = opencc.OpenCC('t2s.json')
        to_words = []
        # 生成繁简通搜重定向
        with open(file_out, 'w', encoding='utf-8') as fw:
            for word in words:
                # 简转繁
                to_word = converter_s2t.convert(word)
                if to_word != word and to_word not in to_words:
                    fw.write(f'{to_word}\n@@@LINK={word}\n</>\n')
                    to_words.append(to_word)
                # 繁转简
                to_word = converter_t2s.convert(word)
                if to_word != word and to_word not in to_words:
                    fw.write(f'{to_word}\n@@@LINK={word}\n</>\n')
                    to_words.append(to_word)

    def make_redirects_syn(self, file_out):
        """ (四) 生成近义词重定向 """
        words = []
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
                words.append(syn["syn"])
        return words

    def toc_all_to_index(self, file_toc_all, file_index_all):
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

    def toc_to_index(self, file_toc, file_index_all):
        """ 处理成 index_all.txt 文件 """
        done_flg = True
        if self.text_file_check(file_toc) == 2:
            pairs = self.read_toc_file(file_toc)
            with open(file_index_all, 'w', encoding='utf-8') as fw:
                for pair in pairs:
                    fw.write('【L'+str(pair["level"])+'】'+pair["title"]+'\t'+str(pair["page"])+'\n')
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

    def merge_to_index_all(self, file_toc, file_index, file_index_all):
        # 先将 toc 转成 index, 再将 index 扩展成 index_all
        if self.toc_to_index(file_toc, file_index_all):
            pat = re.compile(r'^([^\t]+)\t([\-|\d]+)[\r\n]*$')
            # 1.读取 toc
            toc = []
            with open(file_index_all, 'r', encoding='utf-8') as fr:
                i = 1
                for line in fr.readlines():
                    if pat.match(line):
                        toc.append({"name": pat.match(line).group(1), "page": int(pat.match(line).group(2))})
                    else:
                        print(Fore.YELLOW + "WARN: " + Fore.RESET + f"toc.txt 文件的第 {i} 行未识别, 已过滤")
                    i = i + 1
            # 2.读取 index
            index = []
            with open(file_index, 'r', encoding='utf-8') as fr:
                j = 1
                p_last = -100000
                mess_flg = False
                for line in fr.readlines():
                    mth = pat.match(line)
                    if mth:
                        index.append({"name": mth.group(1), "page": int(mth.group(2))})
                        if int(mth.group(2)) < p_last:
                            mess_flg = True
                        p_last = int(mth.group(2))
                    else:
                        print(Fore.YELLOW + "WARN: " + Fore.RESET + f"index.txt 文件的第 {j} 行未识别, 已过滤")
                    j = j + 1
            if mess_flg:
                index.sort(key=lambda x: x["page"], reverse=False)
                print(Fore.YELLOW + "INFO: " + Fore.RESET + "索引存在乱序, 已按页码重排")
            # 3.排序合并 toc 和 index
            toc_sub = []
            with open(file_index_all, 'w', encoding='utf-8') as fw:
                i = 0
                j = 0
                for i in range(len(toc)-1):
                    s = f'{toc[i]["name"]}\t{str(toc[i]["page"])}\n'
                    fw.write(s)
                    for x in range(j, len(index)):
                        if index[x]["page"] > toc[i]["page"] and index[x]["page"] < toc[i+1]["page"]:
                            fw.write(f'{index[x]["name"]}\t{str(index[x]["page"])}\n')
                            j = x + 1
                        elif index[x]["page"] == toc[i]["page"] and index[x]["page"] < toc[i+1]["page"]:
                            fw.write(f'{index[x]["name"]}\t{str(index[x]["page"])}\n')
                            j = x + 1
                            if s not in toc_sub:
                                toc_sub.append(s)
                        else:
                            j = x
                            break
                # 补 toc 的最后一行
                fw.write(f'{toc[-1]["name"]}\t{str(toc[-1]["page"])}\n')
                for x in range(j, len(index)):
                    if index[x]["page"] >= toc[i]["page"]:
                        fw.write(f'{index[x]["name"]}\t{str(index[x]["page"])}\n')
                    else:
                        break
            print(Fore.GREEN + "\n处理完成, 生成在同 index.txt 目录下")
            # 需要检查
            if len(toc_sub) > 0:
                fp = os.path.join(os.path.split(file_index_all)[0], '_need_checking.log')
                with open(fp, 'w', encoding='utf-8') as fw:
                    for t in toc_sub:
                        fw.write(t)
                print(Fore.YELLOW + "INFO: " + Fore.RESET + "存在不确定的排序, 已存放在日志 _need_checking.log 中，请手动对照调整")
        else:
            print(Fore.RED + "\n文件检查不通过, 请确保文件准备无误再执行程序")

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

    def generate_info_html(self, dict_name, file_info_raw, templ_choice):
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
                    fw.write(fr.read().rstrip())
            if templ_choice:
                fw.write(f"\n<div><br/>{dict_name}, built with AutoMdxBuilder {self.settings.version} on {datetime.now().strftime('%Y/%m/%d')}, based on template {templ_choice.upper()}.<br/></div>\n")
            else:
                fw.write(f"\n<div><br/>{dict_name}, packed with AutoMdxBuilder {self.settings.version} on {datetime.now().strftime('%Y/%m/%d')}.<br/></div>\n")
        return file_info

    def get_item_list(self, dct):
        html = ''
        if dct["level"] == -1:
            pass
        elif dct["entry_list"]:
            html += '<div class="toc-list"><p>'
            i = 0
            for item in dct["children"]:
                i += 1
                if i == 1:
                    html += f'<a href="entry://{item}">{item}</a>'
                else:
                    html += f'<span class="sep-list">／</span><a href="entry://{item}">{item}</a>'
            html += '</p></div>\n'
        elif len(dct["children"]) != 0:
            html += '<div class="toc-list"><ul>'
            for item in dct["children"]:
                html += f'<li><a href="entry://{item}">{item}</a></li>'
            html += '</ul></div>\n'
        else:
            pass
        return html

    def read_index_all(self, img_dict_flg, file_index_all):
        done_flg = True
        dcts = []
        dct_chaps = []
        tail_ids = []
        # 用于收集末章节的子词条
        tail_list = []
        tail = {"id": 0, "children": []}
        with open(file_index_all, 'r', encoding='utf-8') as fr:
            if img_dict_flg:
                pat1 = re.compile(r'^【L(\d+)】([^\t]+)\t([\-\d]*)[\r\n]*$')  # 匹配章节词头
                pat2 = re.compile(r'^([^【][^\t]*)\t([\-\d]+)[\r\n]*$')  # 匹配词条词头
            else:
                pat1 = re.compile(r'^【L(\d+)】([^\t]+)\t([^\t\r\n]*)[\r\n]*$')  # 匹配章节词头
                pat2 = re.compile(r'^([^【][^\t]*)\t([^\t\r\n]+)[\r\n]*$')  # 匹配词条词头
            lines = fr.readlines()
            i = 0
            navi_bar = [None, None, None, None, None, None, None, None]
            navi_bar_tmp = []
            for line in lines:
                i += 1
                checked_flg = False
                # 匹配章节
                if pat1.match(line):
                    mth = pat1.match(line)
                    if img_dict_flg and mth.group(3) == '':
                        body = 0
                    elif img_dict_flg:
                        body = int(mth.group(3))
                    else:
                        body = mth.group(3)
                    dct = {
                        "id": i,
                        "level": int(mth.group(1)),
                        "title": mth.group(2),
                        "body": body
                    }
                    # navi_bar 构造
                    navi_bar[int(mth.group(1))] = mth.group(2)
                    navi_bar_tmp = navi_bar[:int(mth.group(1))+1]
                    dct["navi_bar"] = navi_bar_tmp
                    dct_chaps.append(dct)
                    # 子词条清“篮子”
                    if len(tail["children"]) != 0:
                        tail_list.append({"id": tail["id"], "children": tail["children"]})
                        tail_ids.append(tail["id"])
                    checked_flg = True
                    tail["id"] = i
                    tail["children"] = []
                # 匹配词条
                elif pat2.match(line):
                    mth = pat2.match(line)
                    if img_dict_flg:
                        body = int(mth.group(2))
                    else:
                        body = mth.group(2)
                    dct = {
                        "id": i,
                        "level": -1,
                        "title": mth.group(1),
                        "body": body
                    }
                    dct["navi_bar"] = navi_bar_tmp + [mth.group(1)]
                    # 收集子词条
                    tail["children"].append(mth.group(1))
                else:
                    print(f"第 {i} 行未匹配, 请检查")
                    done_flg = False
                    break
                dcts.append(dct)
            # 遍历完成后补漏
            if not checked_flg and len(tail["children"]) != 0:
                tail_list.append({"id": tail["id"], "children": tail["children"]})
                tail_ids.append(tail["id"])
        # 用于收集大章节的子章节
        stem_ids = []
        stem_list = []
        stem = {"id": 0, "children": []}
        for i in range(len(dct_chaps)-1):
            dct_obj = dct_chaps[i]
            stem["id"] = dct_obj["id"]
            stem["children"] = []
            checked_flg = False
            for dct in dct_chaps[i+1:]:
                if dct["level"] == dct_obj["level"]+1:
                    stem["children"].append(dct["title"])
                elif dct["level"] <= dct_obj["level"]:
                    # 收集子章节
                    if len(stem["children"]) != 0:
                        stem_list.append({"id": stem["id"], "children": stem["children"]})
                        stem_ids.append(stem["id"])
                    checked_flg = True
                    break
            # 补漏收
            if not checked_flg and len(stem["children"]) != 0:
                stem_list.append({"id": stem["id"], "children": stem["children"]})
                stem_ids.append(stem["id"])
        # 检查
        if len(tail_ids+stem_ids) != len(set(tail_ids+stem_ids)):
            done_flg = False
            print(Fore.RED + "ERROR: " + Fore.RESET + f"文件 {file_index_all} 解析出现矛盾, 请检查索引顺序")
        else:
            # 整合所有信息
            for dct in dcts:
                if dct["level"] == -1:
                    dct["children"] = []
                    dct["entry_list"] = False
                elif dct["id"] in tail_ids:
                    for item in tail_list:
                        if dct["id"] == item["id"]:
                            dct["children"] = item["children"]
                            dct["entry_list"] = True
                            break
                elif dct["id"] in stem_ids:
                    for item in stem_list:
                        if dct["id"] == item["id"]:
                            dct["children"] = item["children"]
                            dct["entry_list"] = False
                            break
                else:
                    dct["children"] = []
                    dct["entry_list"] = False
        return done_flg, dcts

    # def _detect_code(self, text_file):
    #     with open(text_file, 'rb') as frb:
    #         data = frb.read()
    #         dcts = chardet.detect(data)
    #     return dcts["encoding"]

    def _is_blank_file(self, text_file):
        blank_flg = False
        text = ''
        with open(text_file, 'r', encoding='utf-8') as fr:
            i = 0
            for line in fr:
                i += 1
                if i < 6:
                    text += line
                else:
                    break
        if re.match(r'^\s*$', text):
            blank_flg = True
        return blank_flg

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
            # 有非空且不一样, 清空以重新处理
            else:
                shutil.rmtree(dir_imgs_out)
                os.makedirs(dir_imgs_out)
        else:
            os.makedirs(dir_imgs_out)
        # 获取图像文件列表
        num_flg = True  # 图像文件名是否纯数字
        img_files = []
        for fname in os.listdir(dir_imgs_in):
            fpath = os.path.join(dir_imgs_in, fname)
            if os.path.isfile(fpath):
                img_files.append(fpath)
            if not re.match(r'\d+', fname.split('.')[0]):
                num_flg = False
        # 按旧文件名排序
        if num_flg:
            img_files.sort(key=lambda x: int(os.path.split(x)[1].split('.')[0]), reverse=False)  # 按数字排
        else:
            img_files.sort(reverse=False)  # 按字符串排
        n_len = len(str(len(img_files)))  # 获取序号位数
        # 重命名
        imgs = []
        i = 0
        for img_file in img_files:
            i += 1
            f_dir, f_name = os.path.split(img_file)
            f_ext = os.path.splitext(f_name)[1]
            # 区分正文和辅页, 辅页前缀'A', 正文前缀'B'
            if i < self.settings.body_start:
                i_str = str(i).zfill(n_len)
                f_title_new = f'{self.settings.name_abbr}_A{i_str}'
            else:
                i_str = str(i-self.settings.body_start+1).zfill(n_len)
                f_title_new = f'{self.settings.name_abbr}_B{i_str}'
            imgs.append({'title': f_title_new, 'name': f_title_new+f_ext})
            # 复制新文件到输出文件夹
            img_file_new = os.path.join(dir_imgs_out, f_title_new+f_ext)
            if copy_flg:
                os.system(f'copy /y "{img_file}" "{img_file_new}"')
        return dir_imgs_out, imgs, n_len

    def _generate_navi_middle(self, proc_flg_toc):
        """ 生成导航栏中间(链接)部分 """
        html = '<span class="navi-item-middle">'
        if proc_flg_toc:
            html += f'<span class="navi-item"><a href="entry://TOC_{self.settings.name_abbr}">🕮</a></span>'
            for item in self.settings.navi_items:
                html += f'<span class="navi-item"><a href="entry://{self.settings.name_abbr}_{item["ref"]}">{item["a"]}</a></span>'
        else:
            html += '&#8197;&#12288;&#8197;'
        html += '</span>'
        return html
