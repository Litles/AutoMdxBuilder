#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-16 00:00:53
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.6

import os
import re
import shutil
from copy import copy
from datetime import datetime
# import chardet
from colorama import Fore
from opencc import OpenCC


class FuncLib():
    """ functions for invoking """
    def __init__(self, amb):
        self.settings = amb.settings

    def index_all_to_toc(self, file_index_all, file_toc_all, vol_i=0, fill_flg=False):
        """ index_all 文件转 toc_all 文件 """
        done_flg = True
        if self.text_file_check(file_index_all) == 2:
            # 读取
            dcts = []
            with open(file_index_all, 'r', encoding='utf-8') as fr:
                level = 0
                i = 0
                for line in fr:
                    i += 1
                    # 要先扫描章节再扫描词条
                    mth_stem = self.settings.pat_stem.match(line)
                    if mth_stem:
                        # 无卷标章节
                        level = int(mth_stem.group(1))
                        if mth_stem.group(3) == '':
                            dcts.append({"level": level, "name": mth_stem.group(2), "page": 0, "vol_n": vol_i+1})
                        else:
                            dcts.append({"level": level, "name": mth_stem.group(2), "page": int(mth_stem.group(3)), "vol_n": vol_i+1})
                    elif self.settings.pat_stem_vol.match(line):
                        # 有卷标章节
                        mth_vol_stem = self.settings.pat_stem_vol.match(line)
                        level = int(mth_vol_stem.group(1))
                        if mth_vol_stem.group(4) == '':
                            dcts.append({"level": level, "name": mth_vol_stem.group(2), "page": 0, "vol_n": int(mth_vol_stem.group(3))})
                        else:
                            dcts.append({"level": level, "name": mth_vol_stem.group(2), "page": int(mth_vol_stem.group(4)), "vol_n": int(mth_vol_stem.group(3))})
                    elif self.settings.pat_index.match(line):
                        # 无卷标词条
                        mth = self.settings.pat_index.match(line)
                        dcts.append({"level": level+1, "name": mth.group(1), "page": int(mth.group(2)), "vol_n": vol_i+1})
                    elif self.settings.pat_index_vol.match(line):
                        # 有卷标词条
                        mth_vol = self.settings.pat_index_vol.match(line)
                        dcts.append({"level": level+1, "name": mth_vol.group(1), "page": int(mth_vol.group(3)), "vol_n": int(mth_vol.group(2))})
                    else:
                        print(Fore.RED + "ERROR: " + Fore.RESET + f"第 {i} 行格式有误, 请检查")
                        done_flg = False
                        break
            # 输出
            if done_flg:
                with open(file_toc_all, 'w', encoding='utf-8') as fw:
                    p_fill = 1
                    for x in range(len(dcts)):
                        dct = dcts[x]
                        # 判断是否要加卷标
                        if dct["vol_n"] == 1:
                            s_vol = ''
                        else:
                            s_vol = '['+str(dct["vol_n"])+']'
                        # 开始写入
                        if dct["page"] != 0:
                            fw.write('\t'*dct["level"] + f'{dct["name"]}\t{s_vol}{str(dct["page"])}\n')
                        elif fill_flg:
                            # 向后检索页码来填充
                            for d in dcts[x+1:]:
                                if d["page"] != 0:
                                    p_fill = d["page"]
                                    break
                            fw.write('\t'*dct["level"] + f'{dct["name"]}\t{s_vol}{str(p_fill)}\n')
                            # 如果向后仍未检索到页码(待补充)
                        else:
                            fw.write('\t'*dct["level"] + f'{dct["name"]}\n')
        else:
            done_flg = False
        return done_flg

    def toc_all_to_index(self, file_toc_all, file_index_all):
        """ toc_all 文件转 index_all 文件 """
        if self.text_file_check(file_toc_all) == 2:
            # 读取 toc_all.txt
            pairs = self.read_toc_file(file_toc_all)
            # 识别收集非章节的词条索引
            index, entries_tmp = [], []
            child_flg = False
            for i in range(1, len(pairs)):
                if pairs[i]["level"] == pairs[i-1]["level"]:
                    if child_flg:
                        # 满足条件, 继续收集
                        entries_tmp.append(i)
                elif pairs[i]["level"] > pairs[i-1]["level"]:
                    # 是展开节点, 开启收集
                    entries_tmp = []
                    child_flg = True
                    entries_tmp.append(i)
                else:
                    # 展开结束, 归档, 清空篮子
                    index += entries_tmp
                    entries_tmp = []
                    child_flg = False
            # 补漏(因为最末一次收集可能未归档)
            if len(entries_tmp) > 0:
                index += entries_tmp
            # 生成 index_all.txt
            with open(file_index_all, 'w', encoding='utf-8') as fw:
                for i in range(len(pairs)):
                    vol_n = pairs[i]["vol_n"]  # 若 vol_n 大于 1 则标示分卷号
                    if i in index:
                        # 检查是否存在索引条无页码
                        if pairs[i]["page"] == 0:
                            str_p = '1'
                            print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"第 {i+1} 行普通索引条无页码, 已设置为默认值 1")
                        else:
                            str_p = str(pairs[i]["page"])
                        # 写入索引条
                        if vol_n > 1:
                            fw.write(f'{pairs[i]["title"]}\t[{str(vol_n)}]{str_p}\n')
                        else:
                            fw.write(f'{pairs[i]["title"]}\t{str_p}\n')
                    elif pairs[i]["page"] == 0:
                        fw.write(f'【L{str(pairs[i]["level"])}】{pairs[i]["title"]}\t\n')
                    else:
                        if vol_n > 1:
                            fw.write(f'【L{str(pairs[i]["level"])}】{pairs[i]["title"]}\t[{str(vol_n)}]{str(pairs[i]["page"])}\n')
                        else:
                            fw.write(f'【L{str(pairs[i]["level"])}】{pairs[i]["title"]}\t{str(pairs[i]["page"])}\n')
            return True
        else:
            return False

    def read_toc_file(self, file_toc, vol_i=0):
        """ 读取 toc/toc_all 文件 """
        pairs = []
        with open(file_toc, 'r', encoding='utf-8') as fr:
            i = 1
            for line in fr:
                mth = self.settings.pat_toc.match(line)
                if mth:
                    pair = {
                        "level": len(mth.group(1)),
                        "title": mth.group(2),
                        "page": int(mth.group(3)),
                        "vol_n": vol_i+1
                    }
                    pairs.append(pair)
                elif self.settings.pat_toc_blank.match(line):
                    mth_blank = self.settings.pat_toc_blank.match(line)
                    pair = {
                        "level": len(mth_blank.group(1)),
                        "title": mth_blank.group(2),
                        "page": 0,
                        "vol_n": vol_i+1
                    }
                    pairs.append(pair)
                elif self.settings.pat_toc_vol.match(line):
                    mth_vol = self.settings.pat_toc_vol.match(line)
                    pair = {
                        "level": len(mth_vol.group(1)),
                        "title": mth_vol.group(2),
                        "page": int(mth_vol.group(4)),
                        "vol_n": int(mth_vol.group(3))
                    }
                    pairs.append(pair)
                else:
                    print(Fore.RED + "ERROR: " + Fore.RESET + f"第 {i} 行未匹配, 已忽略")
                    pairs = []
                    break
                i += 1
        return pairs

    def read_index_file(self, file_index, vol_i=0):
        """ 读取 index 文件 """
        pairs = []
        with open(file_index, 'r', encoding='utf-8') as fr:
            i = 1
            for line in fr:
                mth = self.settings.pat_index.match(line)
                if mth:
                    pair = {
                        "title": mth.group(1),
                        "page": int(mth.group(2)),
                        "vol_n": vol_i+1
                    }
                    pairs.append(pair)
                elif self.settings.pat_index_vol.match(line):
                    mth_vol = self.settings.pat_index_vol.match(line)
                    pair = {
                        "title": mth_vol.group(1),
                        "page": int(mth_vol.group(3)),
                        "vol_n": int(mth_vol.group(2))
                    }
                    pairs.append(pair)
                else:
                    print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"第 {i} 行未匹配, 已忽略")
                i += 1
        return pairs

    def merge_to_index_all(self, file_toc, file_index, file_index_all):
        """ 将 toc 和 index 文件合并成 index_all 文件 """
        # 思路: 先合并为 toc_all, 再转换成 index_all
        if self.text_file_check(file_toc) == 2:
            done_flg = True
            # 1.读取 toc
            toc_pairs = self.read_toc_file(file_toc)
            if toc_pairs:
                # 判断 toc 是否是有序的(无序则不支持合并), 同时生成新页码(填充无页码章节)
                rank_last = -100000
                p_fill = 1
                for i in range(len(toc_pairs)):
                    toc_pairs[i]["page_new"] = copy(toc_pairs[i]["page"])
                    dct = toc_pairs[i]
                    if dct["page"] == 0:
                        # 向后检索页码来填充
                        for d in toc_pairs[i+1:]:
                            if d["page"] != 0:
                                p_fill = d["page"]
                                break
                        toc_pairs[i]["page_new"] = copy(p_fill)
                    elif dct["vol_n"]*100000+dct["page"] < rank_last:
                        print(Fore.RED + "ERROR: " + Fore.RESET + f"目录文件第 {i} 行页码乱序, 不支持合并")
                        done_flg = False
                        break
                    else:
                        rank_last = dct["vol_n"]*100000+dct["page"]
            else:
                done_flg = False
            # 2.读取 index
            index_pairs = self.read_index_file(file_index)
            if index_pairs:
                # 排序确保是有序的
                index_pairs.sort(key=lambda x: x["vol_n"]*100000+x["page"], reverse=False)
            else:
                print(Fore.RED + "ERROR: " + Fore.RESET + "读取索引文件失败")
                done_flg = False
            # 3.排序合并 toc 和 index
            if done_flg:
                toc_unsure = []
                toc_wrong = []
                file_tmp = os.path.join(self.settings.dir_output_tmp, self.settings.fname_toc_all)
                with open(file_tmp, 'w', encoding='utf-8') as fw:
                    i = 0
                    j = 0
                    # toc 除最后一行
                    for i in range(len(toc_pairs)-1):
                        level = toc_pairs[i]["level"]
                        # 先写入目录条
                        if toc_pairs[i]["vol_n"] > 1:
                            vol_toc = '['+str(toc_pairs[i]["vol_n"])+']'
                        else:
                            vol_toc = ''
                        if toc_pairs[i]["page"] != 0:
                            fw.write('\t'*level + f'{toc_pairs[i]["title"]}\t{vol_toc}{str(toc_pairs[i]["page"])}\n')
                        else:
                            fw.write('\t'*level + f'{toc_pairs[i]["title"]}\n')
                        # 2.写入符合的索引行
                        for x in range(j, len(index_pairs)):
                            if index_pairs[x]["vol_n"] > 1:
                                vol_index = '['+str(index_pairs[x]["vol_n"])+']'
                            else:
                                vol_index = ''
                            rk = index_pairs[x]["vol_n"]*100000+index_pairs[x]["page"]
                            # a.小于当前章节: 写入(排序错误)
                            if (rk < toc_pairs[i]["vol_n"]*100000+toc_pairs[i]["page_new"]):
                                fw.write('\t'*(level+1) + f'{index_pairs[x]["title"]}\t{vol_index}{str(index_pairs[x]["page"])}\n')
                                j = x + 1
                                if toc_pairs[i] not in toc_wrong:
                                    toc_wrong.append(toc_pairs[i])
                            elif (rk == toc_pairs[i]["vol_n"]*100000+toc_pairs[i]["page_new"]) and (rk == toc_pairs[i+1]["vol_n"]*100000+toc_pairs[i+1]["page_new"]):
                                j = x
                                break
                            # b.等于当前章节, 小于后一章节: 写入(词条和章节孰前孰后存疑,故记录)
                            elif (rk == toc_pairs[i]["vol_n"]*100000+toc_pairs[i]["page_new"]) and (rk < toc_pairs[i+1]["vol_n"]*100000+toc_pairs[i+1]["page_new"]):
                                fw.write('\t'*(level+1) + f'{index_pairs[x]["title"]}\t{vol_index}{str(index_pairs[x]["page"])}\n')
                                j = x + 1
                                if toc_pairs[i] not in toc_unsure:
                                    toc_unsure.append(toc_pairs[i])
                            # c.大于当前章节, 小于后一章节: 写入
                            elif (rk > toc_pairs[i]["vol_n"]*100000+toc_pairs[i]["page_new"]) and (rk < toc_pairs[i+1]["vol_n"]*100000+toc_pairs[i+1]["page_new"]):
                                fw.write('\t'*(level+1) + f'{index_pairs[x]["title"]}\t{vol_index}{str(index_pairs[x]["page"])}\n')
                                j = x + 1
                            # d.剩余情况: 大于当前章节,大于等于后一章节
                            else:
                                j = x
                                break
                    # 补 toc 的最后一行
                    level = toc_pairs[-1]["level"]
                    if toc_pairs[-1]["vol_n"] > 1:
                        vol_toc = '['+str(toc_pairs[-1]["vol_n"])+']'
                    else:
                        vol_toc = ''
                    if toc_pairs[-1]["page"] != 0:
                        fw.write('\t'*level + f'{toc_pairs[-1]["title"]}\t{vol_toc}{str(toc_pairs[-1]["page"])}\n')
                    else:
                        fw.write('\t'*level + f'{toc_pairs[-1]["title"]}\n')
                    # 写入剩余的索引行
                    for x in range(j, len(index_pairs)):
                        if index_pairs[x]["vol_n"] > 1:
                            vol_index = '['+str(index_pairs[x]["vol_n"])+']'
                        else:
                            vol_index = ''
                        fw.write('\t'*(level+1) + f'{index_pairs[x]["title"]}\t{vol_index}{str(index_pairs[x]["page"])}\n')
                        if index_pairs[x]["vol_n"]*100000+index_pairs[x]["page"] < toc_pairs[-1]["vol_n"]*100000+toc_pairs[-1]["page_new"]:
                            if toc_pairs[-1] not in toc_wrong:
                                toc_wrong.append(toc_pairs[-1])
                        elif index_pairs[x]["vol_n"]*100000+index_pairs[x]["page"] == toc_pairs[-1]["vol_n"]*100000+toc_pairs[-1]["page_new"]:
                            if toc_pairs[-1] not in toc_unsure:
                                toc_unsure.append(toc_pairs[-1])
                if self.toc_all_to_index(file_tmp, file_index_all):
                    print(Fore.GREEN + "\n处理完成, 生成在同 index.txt 目录下" + Fore.RESET)
                    # 输出错误和存疑的 toc 部分以便检查
                    if toc_wrong or toc_unsure:
                        fp = os.path.join(os.path.split(file_index_all)[0], '_need_checking.log')
                        with open(fp, 'w', encoding='utf-8') as fw:
                            if toc_wrong:
                                fw.write('========= 排序错误 ==========\n')
                                for t in toc_wrong:
                                    if t["vol_n"] > 1:
                                        vol_toc = '['+str(t["vol_n"])+']'
                                    else:
                                        vol_toc = ''
                                    if t["page"] == 0:
                                        fw.write(f'【L{str(t["level"])}】{t["title"]}\t\n')
                                    else:
                                        fw.write(f'【L{str(t["level"])}】{t["title"]}\t{vol_toc}{str(t["page"])}\n')
                            if toc_unsure:
                                fw.write('========= 排序存疑 ==========\n')
                                for t in toc_unsure:
                                    if t["vol_n"] > 1:
                                        vol_toc = '['+str(t["vol_n"])+']'
                                    else:
                                        vol_toc = ''
                                    if t["page"] == 0:
                                        fw.write(f'【L{str(t["level"])}】{t["title"]}\t\n')
                                    else:
                                        fw.write(f'【L{str(t["level"])}】{t["title"]}\t{vol_toc}{str(t["page"])}\n')
                        print(Fore.MAGENTA + "WARN: " + Fore.RESET + "存在排序存疑的条目, 已记录在日志 _need_checking.log 中，需手动调整完善")
        else:
            print(Fore.RED + "ERROR: " + Fore.RESET + "读取目录文件失败")

    def read_index_all_file(self, file_index_all, img_dict_flg=True, vol_i=0):
        done_flg = True
        dcts = []
        dct_chaps = []
        tail_ids = []
        # 用于收集末章节的子词条
        tail_list = []
        tail = {"id": 0, "children": []}
        with open(file_index_all, 'r', encoding='utf-8') as fr:
            if img_dict_flg:
                pat1 = re.compile(r'【L(\d+)】([^\t]+)\t([\[\d\]]*\-\d+|[\[\d\]]*\d*)[\r\n]*$')  # 匹配章节词头(有/无卷标)
                pat2 = re.compile(r'([^\t]+)\t([\[\d\]]*\-?\d+)[\r\n]*$')  # 匹配词条词头(有/无卷标)
            else:
                pat1 = self.settings.pat_stem_text  # 匹配章节词头
                pat2 = self.settings.pat_tab  # 匹配词条词头
            i = 0
            navi_bar = [None for i in range(10)]
            navi_bar_tmp = []
            for line in fr:
                i += 1
                checked_flg = False
                vol_n = vol_i+1
                # 匹配章节
                if pat1.match(line):
                    mth = pat1.match(line)
                    # 读取页码/词条内容, 分卷号
                    if img_dict_flg and mth.group(3) == '':
                        body = 0
                    elif img_dict_flg and re.match(r'\-?\d+$', mth.group(3)):
                        body = int(mth.group(3))
                    elif img_dict_flg and re.match(r'\[(\d+)\](\-?\d+)$', mth.group(3)):
                        mth_mth1 = re.match(r'\[(\d+)\](\-?\d+)$', mth.group(3))
                        vol_n, body = int(mth_mth1.group(1)), int(mth_mth1.group(2))
                    elif img_dict_flg:
                        print(Fore.RED + "ERROR: " + Fore.RESET + f"第 {i} 行未匹配, 请检查")
                        done_flg = False
                        break
                    else:
                        body = mth.group(3)
                    dct = {
                        "id": i,
                        "level": int(mth.group(1)),
                        "title": mth.group(2),
                        "body": body,
                        "vol_n": vol_n
                    }
                    # navi_bar 构造
                    navi_bar[int(mth.group(1))] = mth.group(2)
                    navi_bar_tmp = navi_bar[:int(mth.group(1))+1]
                    dct["navi_bar"] = copy(navi_bar_tmp)
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
                    if img_dict_flg and re.match(r'\-?\d+$', mth.group(2)):
                        body = int(mth.group(2))
                    elif img_dict_flg and re.match(r'\[(\d+)\](\-?\d+)$', mth.group(2)):
                        mth_mth1 = re.match(r'\[(\d+)\](\-?\d+)$', mth.group(2))
                        vol_n, body = int(mth_mth1.group(1)), int(mth_mth1.group(2))
                    elif img_dict_flg:
                        print(Fore.RED + "ERROR: " + Fore.RESET + f"第 {i} 行未匹配, 请检查")
                        done_flg = False
                        break
                    else:
                        body = mth.group(2)
                    dct = {
                        "id": i,
                        "level": -1,
                        "title": mth.group(1),
                        "body": body,
                        "vol_n": vol_n
                    }
                    dct["navi_bar"] = navi_bar_tmp + [mth.group(1)]
                    # 收集子词条
                    tail["children"].append(mth.group(1))
                else:
                    print(Fore.RED + "ERROR: " + Fore.RESET + f"第 {i} 行未匹配, 请检查")
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
        if done_flg:
            return dcts
        else:
            print(Fore.RED + "全索引文件读取失败: " + Fore.RESET + file_index_all)
            return None

    def make_relinks_syn(self, file_syns, file_out):
        """ 生成同义词重定向 """
        words = []
        # 1.读取重定向索引
        syns = []
        with open(file_syns, 'r', encoding='utf-8') as fr:
            i = 1
            for line in fr:
                mth = self.settings.pat_tab.match(line)
                if mth:
                    syns.append({"syn": mth.group(1), "origin": mth.group(2)})
                else:
                    print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"第 {i} 行未匹配, 已忽略")
                i += 1
        # 2.生成重定向
        with open(file_out, 'w', encoding='utf-8') as fw:
            for syn in syns:
                fw.write(f'{syn["syn"]}\n@@@LINK={syn["origin"]}\n</>\n')
                words.append(syn["syn"])
        print("重定向(同义词)词条已生成")
        return words

    def make_relinks_st(self, words, file_out):
        converter_s2t = OpenCC('s2t.json')
        converter_t2s = OpenCC('t2s.json')
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
        print("重定向(繁简)词条已生成")

    def simp_trad_trans(self, file_in, file_out, trans_type):
        """ 繁简转换 """
        if trans_type == 'T':
            converter_s2t = OpenCC('s2t.json')
            with open(file_out, 'w', encoding='utf-8') as fw:
                with open(file_in, 'r', encoding='utf-8') as fr:
                    for line in fr:
                        # 简转繁
                        fw.write(converter_s2t.convert(line))
        else:
            converter_t2s = OpenCC('t2s.json')
            with open(file_out, 'w', encoding='utf-8') as fw:
                with open(file_in, 'r', encoding='utf-8') as fr:
                    for line in fr:
                        # 繁转简
                        fw.write(converter_t2s.convert(line))
        print(f"\n转换结果已生成: {file_out}")

    def text_file_check(self, text_file):
        if not os.path.exists(text_file) or not os.path.isfile(text_file):
            print(Fore.YELLOW + "INFO: " + Fore.RESET + f"文件 {text_file} 不存在")
            return 0
        else:
            text = ''
            with open(text_file, 'r', encoding='utf-8') as fr:
                i = 0
                for line in fr:
                    i += 1
                    if i < 6:
                        text += line
                    else:
                        break
            if re.match(r'\s*$', text):
                print(Fore.RED + "ERROR: " + Fore.RESET + f"文件 {text_file} 内容为空")
                return 1
            else:
                return 2

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
                for line in fr:
                    if line == '</>\n':
                        entry_total += 1
        else:
            # 用临时文件存储, 完了再重命名
            file_tmp = os.path.join(self.settings.dir_output_tmp, 'tmp.xxx')
            with open(file_tmp, 'a', encoding='utf-8') as fa:
                for part in parts:
                    with open(part, 'r', encoding='utf-8') as fr:
                        for line in fr:
                            if line == '</>\n':
                                entry_total += 1
                            fa.write(line)
            if os.path.isfile(file_final):
                os.remove(file_final)
            os.rename(file_tmp, file_final)
        return entry_total

    def generate_info_html(self, file_info_raw, file_out, dict_name, templ_choice=None, volume_num=None):
        with open(file_out, 'w', encoding='utf-8') as fw:
            # 读取 info.html
            if file_info_raw and os.path.isfile(file_info_raw):
                with open(file_info_raw, 'r', encoding='utf-8') as fr:
                    fw.write(fr.read().rstrip())
            # 打上 AMB 标志 (有模板则是制作, 没有则认为是打包)
            if templ_choice and volume_num:
                fw.write(f"\n<div><br/>{dict_name}, built with AutoMdxBuilder {self.settings.version} on {datetime.now().strftime('%Y/%m/%d')}, based on template {templ_choice.upper()} in {volume_num} volumes.<br/></div>\n")
            elif templ_choice:
                fw.write(f"\n<div><br/>{dict_name}, built with AutoMdxBuilder {self.settings.version} on {datetime.now().strftime('%Y/%m/%d')}, based on template {templ_choice.upper()}.<br/></div>\n")
            else:
                fw.write(f"\n<div><br/>{dict_name}, packed with AutoMdxBuilder {self.settings.version} on {datetime.now().strftime('%Y/%m/%d')}.<br/></div>\n")
        return True

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
                html += f'<li><a href="entry://{self.settings.name_abbr}_{item}">{item}</a></li>'
            html += '</ul></div>\n'
        else:
            pass
        return html

    # def _detect_code(self, text_file):
    #     with open(text_file, 'rb') as frb:
    #         data = frb.read()
    #         dcts = chardet.detect(data)
    #     return dcts["encoding"]

    def prepare_imgs(self, dir_imgs_in, dir_imgs_out, volume_num=None):
        print('开始处理图像...')
        imgs = []
        img_lens = []
        if volume_num:
            # 整理图像
            lst_dir_imgs = []
            for i in range(volume_num):
                dir_tmp = os.path.join(dir_imgs_out, os.path.split(dir_imgs_in["main"][i])[1])
                imgs_tmp = self._proc_img_vol(dir_imgs_in["main"][i], dir_tmp, True, i)
                imgs += imgs_tmp
                img_lens.append(len(imgs_tmp))
                print(f"第 {i+1} 卷已完成")
                lst_dir_imgs.append(dir_tmp)
            for fp in dir_imgs_in["others"]:
                dir_tmp = os.path.join(dir_imgs_out, os.path.split(fp)[1])
                if os.path.exists(dir_tmp):
                    size_in = sum(os.path.getsize(os.path.join(fp, f)) for f in os.listdir(fp) if os.path.isfile(os.path.join(fp, f)))
                    size_out = sum(os.path.getsize(os.path.join(dir_tmp, f)) for f in os.listdir(dir_tmp) if os.path.isfile(os.path.join(dir_tmp, f)))
                    if size_out == 0 or size_out != size_in:
                        shutil.rmtree(dir_tmp)
                        shutil.copytree(fp, dir_tmp)
                else:
                    shutil.copytree(fp, dir_tmp)
                lst_dir_imgs.append(dir_tmp)
            # 清除 _tmp/imgs 中无关的文件,文件夹
            for fname in os.listdir(dir_imgs_out):
                fp = os.path.join(dir_imgs_out, fname)
                if os.path.isfile(fp):
                    os.remove(fp)
                elif os.path.isdir(fp) and fp not in lst_dir_imgs:
                    shutil.rmtree(fp)
        else:
            imgs = self._proc_img_vol(dir_imgs_in, dir_imgs_out)
            img_lens.append(len(imgs))
        print('\n图像处理完毕。')
        return imgs, img_lens

    def _proc_img_vol(self, dir_imgs_in, dir_imgs_out, multi_vols_flg=False, vol_i=0):
        """ 图像预处理(重命名等) """
        # 0.图像拷贝判断
        copy_flg = True
        if os.path.exists(dir_imgs_out):
            size_in = sum(os.path.getsize(os.path.join(dir_imgs_in, f)) for f in os.listdir(dir_imgs_in) if os.path.isfile(os.path.join(dir_imgs_in, f)))
            size_out = sum(os.path.getsize(os.path.join(dir_imgs_out, f)) for f in os.listdir(dir_imgs_out) if os.path.isfile(os.path.join(dir_imgs_out, f)))
            # 为空或不一样, 则重新处理
            if size_out == 0 or size_out != size_in:
                shutil.rmtree(dir_imgs_out)
                os.makedirs(dir_imgs_out)
            else:
                copy_flg = False
        else:
            os.makedirs(dir_imgs_out)
        # 1.获取图像文件列表
        num_flg = True  # 图像文件名是否纯数字
        img_files = []
        for fname in os.listdir(dir_imgs_in):
            fpath = os.path.join(dir_imgs_in, fname)
            if os.path.isfile(fpath) and fpath.endswith(tuple(self.settings.img_exts)):
                img_files.append(fpath)
            if not re.match(r'\d+', fname.split('.')[0]):
                num_flg = False
        # 按旧文件名排序
        if num_flg:
            img_files.sort(key=lambda x: int(os.path.split(x)[1].split('.')[0]), reverse=False)  # 按数字排
        else:
            img_files.sort(reverse=False)  # 按字符串排
        # 2.重命名
        dname = os.path.split(dir_imgs_out)[1].strip('\\/')
        imgs = []
        n = 0
        len_digit = self.settings.len_digit  # 获取序号位数
        for img_file in img_files:
            n += 1
            f_dir, f_name = os.path.split(img_file)
            f_ext = os.path.splitext(f_name)[1]
            # 区分正文和辅页, 辅页前缀'A', 正文前缀'B'
            if multi_vols_flg:
                # 分卷
                if n < self.settings.body_start[vol_i]:
                    i_str = str(n).zfill(len_digit)
                    f_title_new = f'{self.settings.name_abbr}[{str(vol_i+1).zfill(2)}]_A{i_str}'
                else:
                    i_str = str(n-self.settings.body_start[vol_i]+1).zfill(len_digit)
                    f_title_new = f'{self.settings.name_abbr}[{str(vol_i+1).zfill(2)}]_B{i_str}'
                imgs.append({'vol_n': vol_i+1, 'title': f_title_new, 'path': dname+'/'+f_title_new+f_ext, 'i_in_vol': n-1})
            else:
                # 非分卷
                if n < self.settings.body_start[vol_i]:
                    i_str = str(n).zfill(len_digit)
                    f_title_new = f'{self.settings.name_abbr}_A{i_str}'
                else:
                    i_str = str(n-self.settings.body_start[vol_i]+1).zfill(len_digit)
                    f_title_new = f'{self.settings.name_abbr}_B{i_str}'
                imgs.append({'vol_n': vol_i+1, 'title': f_title_new, 'path': f_title_new+f_ext, 'i_in_vol': n-1})
            # 复制新文件到输出文件夹
            if copy_flg:
                shutil.copy(img_file, os.path.join(dir_imgs_out, f_title_new+f_ext))
        return imgs
