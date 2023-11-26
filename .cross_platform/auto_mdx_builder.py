#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-16 00:00:17
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.5

import logging
import traceback
import os
import re
import shutil
from colorama import Fore, just_fix_windows_console
from settings import Settings
from func_lib import FuncLib
from img_dict_atmpl import ImgDictAtmpl
from img_dict_btmpl import ImgDictBtmpl
from text_dict_ctmpl import TextDictCtmpl
from text_dict_dtmpl import TextDictDtmpl
from ebook_utils import EbookUtils


class AutoMdxBuilder:
    """图像词典制作程序"""
    def __init__(self):
        self.settings = Settings()
        self.func = FuncLib(self)
        self.utils = EbookUtils(self)

    def auto_processing(self, sel):
        """ 根据选择自动处理 """
        if sel == 1:
            # --- 解包 mdx/mdd 文件 ---
            mfile = input("请输入要解包的 mdx/mdd 文件路径: ").strip('"')
            if self.utils.export_mdx(mfile):
                print(Fore.GREEN + "\n已输出在同目录下: " + Fore.RESET + os.path.splitext(mfile)[0])
        elif sel == 2:
            # --- 将源 txt 文件打包成 mdx 文件 ---
            file_final_txt = input("请输入要打包的 txt 文件路径: ").strip('"')
            if self.func.text_file_check(file_final_txt) == 2:
                # 检查数据文件夹
                dir_curr, fname_txt = os.path.split(file_final_txt)
                dir_data = os.path.join(dir_curr, 'data')
                if not os.path.exists(dir_data):
                    print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"文件夹 {dir_data} 不存在, 已默认不打包 mdd")
                    dir_data = None
                elif os.path.exists(dir_data) and len(os.listdir(dir_data)) == 0:
                    print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"文件夹 {dir_data} 为空, 已默认不打包 mdd")
                    dir_data = None
                # 生成 info.html
                file_info_raw = None
                for fname in os.listdir(dir_curr):
                    if fname == 'info.html':
                        file_info_raw = os.path.join(dir_curr, fname)
                    elif fname.endswith('.html') and fname.startswith(os.path.splitext(fname_txt)[0]):
                        file_info_raw = os.path.join(dir_curr, fname)
                        break
                file_dict_info = self.func.generate_info_html(os.path.splitext(fname_txt)[0], file_info_raw, None)
                # 打包
                print('\n------------------\n开始打包……\n')
                done_flg = self.utils.pack_to_mdict(file_final_txt, file_dict_info, dir_data, dir_curr)
                if done_flg:
                    print(Fore.GREEN + "\n打包完毕。" + Fore.RESET)
            else:
                print(Fore.RED + "\n材料检查不通过, 请确保材料准备无误再执行程序" + Fore.RESET)
        elif sel == 3:
            # --- 将资料包文件夹打包成 mdd 文件 ---
            dir_data = input("请输入要打包的资料文件夹路径: ").strip('"\\').rstrip('/')
            dir_data = dir_data.rstrip('\\')
            dir_data = dir_data.rstrip('/')
            print('\n------------------\n开始打包……\n')
            done_flg = self.utils.pack_to_mdd(dir_data, None)
            if done_flg:
                print(Fore.GREEN + "\n打包完毕。" + Fore.RESET)
        # elif sel == 10:
        #     # --- 从 PDF文件/pdg文件夹 生成预备原材料 ---
        #     p = input("请输入 pdf文件/pdg文件夹 路径: ").strip('"\\').rstrip('/')
        #     if os.path.isfile(p) and os.path.splitext(p)[1] == '.pdf':
        #         self.pdf_to_amb(p)
        #     elif os.path.isdir(p):
        #         self.pdf_to_amb(p, False)
        #     else:
        #         print(Fore.RED + "ERROR: " + Fore.RESET + "路径输入有误")
        elif sel == 11:
            # --- 从 toc_all.txt 生成 index_all.txt ---
            file_toc_all = input("请输入 toc_all.txt 的文件路径: ").strip('"')
            file_index_all = os.path.join(os.path.split(file_toc_all)[0], 'index_all.txt')
            if self.func.toc_all_to_index(file_toc_all, file_index_all):
                print(Fore.GREEN + "\n处理完成, 生成在同目录下" + Fore.RESET)
            else:
                print(Fore.RED + "\n文件检查不通过, 请确保文件准备无误再执行程序" + Fore.RESET)
        elif sel == 12:
            # --- 合并 toc.txt 和 index.txt 为 index_all.txt ---
            file_toc = input("(1) 请输入 toc.txt 的文件路径: ").strip('"')
            file_index = input("(2) 请输入 index.txt 的文件路径: ").strip('"')
            file_index_all = os.path.join(os.path.split(file_index)[0], 'index_all.txt')
            self.func.merge_to_index_all(file_toc, file_index, file_index_all)
        elif sel == 20:
            # --- 生成词典 ---
            p = input("请输入原材料文件夹路径或 build.toml 文件路径: ").strip('"\\').rstrip('/')
            if os.path.split(p)[1] == 'build.toml':
                if self.settings.load_build_toml(p, False, False):
                    self._build_mdict()
            elif os.path.isdir(p):
                file_toml = os.path.join(p, 'build.toml')
                if os.path.isfile(file_toml):
                    if self.settings.load_build_toml(file_toml, False, True):
                        self._build_mdict()
                else:
                    print(Fore.RED + "ERROR: " + Fore.RESET + "文件夹内未找到 build.toml 文件")
            else:
                print(Fore.RED + "ERROR: " + Fore.RESET + "路径输入有误")
        elif sel == 30:
            # --- 从词典还原原材料 ---
            p = input("请输入词典的文件夹或 mdx/mdd 文件路径: ").strip('"\\').rstrip('/')
            if os.path.isfile(p) and os.path.splitext(p)[1] == '.mdx':
                self._restore_raw(p, False)
            elif os.path.isfile(p) and os.path.splitext(p)[1] == '.mdd':
                if os.path.isfile(p[:-1]+'x'):
                    self._restore_raw(p[:-1]+'x', False)
            elif os.path.isdir(p):
                for m in os.listdir(p):
                    if m.endswith('.mdx'):
                        self._restore_raw(os.path.join(p, m), True)
                        break
                else:
                    print(Fore.RED + "ERROR: " + Fore.RESET + "文件夹内未找到 mdx 文件")
            else:
                print(Fore.RED + "ERROR: " + Fore.RESET + "路径输入有误")
        # elif sel == 31:
        #     # --- 从原材料还原 PDF ---
        #     p = input("请输入原材料文件夹路径或 build.toml 文件路径: ").strip('"\\').rstrip('/')
        #     if os.path.split(p)[1] == 'build.toml':
        #         if self.settings.load_build_toml(p, True):
        #             self.amb_to_pdf(file_toml, False)
        #     elif os.path.isdir(p):
        #         file_toml = os.path.join(p, 'build.toml')
        #         if os.path.isfile(file_toml):
        #             if self.settings.load_build_toml(file_toml, True):
        #                 self.amb_to_pdf(file_toml, True)
        #         else:
        #             print(Fore.RED + "ERROR: " + Fore.RESET + "文件夹内未找到 build.toml 文件")
        #     else:
        #         print(Fore.RED + "ERROR: " + Fore.RESET + "路径输入有误")
        elif sel == 32:
            # --- 从 index_all.txt 还原 toc_all.txt ---
            file_index_all = input("请输入 index_all.txt 的文件路径: ").strip('"')
            file_toc_all = os.path.join(os.path.split(file_index_all)[0], 'toc_all.txt')
            if self.func.index_to_toc(file_index_all, file_toc_all):
                print(Fore.GREEN + "\n处理完成, 生成在同目录下" + Fore.RESET)
            else:
                print(Fore.RED + "\n文件检查不通过, 请确保所有词目都有对应页码" + Fore.RESET)
        elif sel == 41:
            # --- 从 PDF 提取图片 (MuPDF) ---
            p = input("请输入 PDF 文件路径: ").strip('"\\').rstrip('/')
            if os.path.isfile(p) and p.lower().endswith('.pdf'):
                fname = os.path.split(p)[1]
                out_dir = os.path.join(os.path.split(p)[0], fname.split('.')[0])
                self.utils.extract_pdf_to_imgs_fitz(p, out_dir)
            else:
                print(Fore.RED + "\n输入的路径有误" + Fore.RESET)
        elif sel == 42:
            # --- 将 PDF 转换成图片 (MuPDF) ---
            p = input("请输入 PDF 文件路径: ").strip('"\\').rstrip('/')
            if os.path.isfile(p) and p.lower().endswith('.pdf'):
                fname = os.path.split(p)[1]
                out_dir = os.path.join(os.path.split(p)[0], fname.split('.')[0])
                dpi = input("请输入要生成图片的 DPI（回车则默认300）: ")
                if re.match(r'^\d+$', dpi):
                    self.utils.convert_pdf_to_imgs_fitz(p, out_dir, int(dpi))
                else:
                    self.utils.convert_pdf_to_imgs_fitz(p, out_dir)
            else:
                print(Fore.RED + "\n输入的路径有误" + Fore.RESET)
        # elif sel == 43:
        #     # --- 将 图片 合成 PDF (MuPDF) ---
        #     p = input("请输入图片所在文件夹路径: ").strip('"\\').rstrip('/')
        #     if os.path.isdir(p):
        #         out_file = p+'.pdf'
        #         self.utils.combine_img_to_pdf(p, out_file)
        #     else:
        #         print(Fore.RED + "\n输入的路径有误" + Fore.RESET)
        # elif sel == 44:
        #     # --- PDF 书签导出/导入（FreePic2Pdf） ---
        #     file_pdf = input("请输入 PDF 文件路径: ").strip('"\\').rstrip('/')
        #     dir_bkmk = input("请输入书签文件夹路径（导出则直接回车）: ").strip('"\\').rstrip('/')
        #     if os.path.isdir(dir_bkmk):
        #         self.utils.eximport_bkmk_fp2p(file_pdf, dir_bkmk, False)
        #     elif dir_bkmk is None or len(dir_bkmk) == 0:
        #         fname = os.path.split(file_pdf)[1]
        #         dir_bkmk = os.path.join(os.path.split(file_pdf)[0], fname.split('.')[0]+'_bkmk')
        #         self.utils.eximport_bkmk_fp2p(file_pdf, dir_bkmk)
        #     else:
        #         print(Fore.RED + "\n输入的路径有误" + Fore.RESET)
        else:
            pass

    def _build_mdict(self):
        done_flg = False
        if self.settings.templ_choice in ('a', 'A'):
            """ 制作图像词典 (模板A) """
            # 生成 txt 源文本
            proc_flg, file_final_txt, dir_imgs_out, file_dict_info = ImgDictAtmpl(self).make_source_file()
            if proc_flg:
                # 创建输出文件夹
                if not os.path.exists(self.settings.dir_output):
                    os.makedirs(self.settings.dir_output)
                # 拷贝模板 css 文件
                file_css_tmpl = os.path.join(self.settings.dir_lib, self.settings.css_atmpl)
                file_css = os.path.join(self.settings.dir_output, self.settings.fname_css)
                shutil.copy(file_css_tmpl, file_css)
                # 开始打包
                print('\n------------------\n开始打包……\n')
                done_flg = self.utils.pack_to_mdict(file_final_txt, file_dict_info, dir_imgs_out, self.settings.dir_output)
        elif self.settings.templ_choice in ('b', 'B'):
            """ 制作图像词典 (模板B) """
            # 生成 txt 源文本
            proc_flg, file_final_txt, dir_imgs_out, file_dict_info = ImgDictBtmpl(self).make_source_file()
            if proc_flg:
                # 创建输出文件夹
                if not os.path.exists(self.settings.dir_output):
                    os.makedirs(self.settings.dir_output)
                # 拷贝模板 css 文件
                file_css_tmpl = os.path.join(self.settings.dir_lib, self.settings.css_btmpl)
                file_css = os.path.join(self.settings.dir_output, self.settings.fname_css)
                shutil.copy(file_css_tmpl, file_css)
                # 开始打包
                print('\n------------------\n开始打包……\n')
                done_flg = self.utils.pack_to_mdict(file_final_txt, file_dict_info, dir_imgs_out, self.settings.dir_output)
        elif self.settings.templ_choice in ('c', 'C'):
            """ 制作文本词典 (模板C) """
            # 生成 txt 源文本
            proc_flg, file_final_txt, file_dict_info = TextDictCtmpl(self).make_source_file()
            if proc_flg:
                # 创建输出文件夹
                if not os.path.exists(self.settings.dir_output):
                    os.makedirs(self.settings.dir_output)
                # 拷贝模板 css 文件
                file_css_tmpl = os.path.join(self.settings.dir_lib, self.settings.css_ctmpl)
                file_css = os.path.join(self.settings.dir_output, self.settings.fname_css)
                shutil.copy(file_css_tmpl, file_css)
                # 开始打包
                print('\n------------------\n开始打包……\n')
                dir_data = os.path.join(self.settings.dir_input, self.settings.dname_data)
                if not os.path.exists(dir_data) or len(os.listdir(dir_data)) == 0:
                    dir_data = None
                done_flg = self.utils.pack_to_mdict(file_final_txt, file_dict_info, dir_data, self.settings.dir_output)
        elif self.settings.templ_choice in ('d', 'D'):
            """ 制作文本词典 (模板D) """
            # 生成 txt 源文本
            proc_flg, file_final_txt, file_dict_info = TextDictDtmpl(self).make_source_file()
            if proc_flg:
                # 创建输出文件夹
                if not os.path.exists(self.settings.dir_output):
                    os.makedirs(self.settings.dir_output)
                # 拷贝模板 css 文件
                file_css_tmpl = os.path.join(self.settings.dir_lib, self.settings.css_dtmpl)
                file_css = os.path.join(self.settings.dir_output, self.settings.fname_css)
                shutil.copy(file_css_tmpl, file_css)
                # 开始打包
                print('\n------------------\n开始打包……\n')
                dir_data = os.path.join(self.settings.dir_input, self.settings.dname_data)
                if not os.path.exists(dir_data) or len(os.listdir(dir_data)) == 0:
                    dir_data = None
                done_flg = self.utils.pack_to_mdict(file_final_txt, file_dict_info, dir_data, self.settings.dir_output)
        else:
            pass
        if done_flg:
            print("\n打包完毕。" + Fore.GREEN + "\n\n恭喜, 词典已生成！" + Fore.RESET)

    def _restore_raw(self, xfile, outside_flg):
        """ 将词典还原为原材料 """
        # 1.准备参数
        extract_flg = False
        dict_name = None
        templ_choice = None
        dir_input, fname = os.path.split(xfile)
        # 2.分析 mdx 文件
        tmp_restore = os.path.join(self.settings.dir_output_tmp, 'restore')
        if not os.path.exists(tmp_restore):
            os.makedirs(tmp_restore)
        tmp_xfile = os.path.join(tmp_restore, fname)
        tmp_xdir = os.path.splitext(tmp_xfile)[0]
        if os.path.exists(tmp_xdir):
            shutil.rmtree(tmp_xdir)
        shutil.copy(xfile, tmp_xfile)
        if self.utils.export_mdx(tmp_xfile):
            tmp_final_txt = os.path.join(tmp_xdir, fname.split('.')[0]+'.txt')
        # 分析 info 信息, 确定是否支持还原
        for f in os.listdir(tmp_xdir):
            fp = os.path.join(tmp_xdir, f)
            text = ''
            if fp.endswith('.info.html'):
                with open(fp, 'r', encoding='utf-8') as fr:
                    pat = re.compile(r'<div><br/>([^><]*?), built with AutoMdxBuilder[^><]*?based on template ([A-D])\.<br/></div>', flags=re.I)
                    text = fr.read()
                    if pat.search(text):
                        # 符合条件, 支持还原
                        dict_name = pat.search(text).group(1)
                        templ_choice = pat.search(text).group(2)
                        text = pat.sub('', text)
                        extract_flg = True
                        break
        # 3.开始提取
        if extract_flg:
            # 创建目标文件夹
            if outside_flg:
                out_dir = os.path.join(os.path.split(dir_input)[0], fname.split('.')[0]) + '_amb'
            else:
                out_dir = os.path.splitext(xfile)[0] + '_amb'
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            # 提取 info.html
            if not re.match(r'^\s*$', text):
                with open(os.path.join(out_dir, 'info.html'), 'w', encoding='utf-8') as fw:
                    fw.write(text)
            # 提取 index, index_all, syns 等信息
            if tmp_final_txt:
                # 选择函数进行处理
                if templ_choice == 'A':
                    ImgDictAtmpl(self).extract_final_txt(tmp_final_txt, out_dir, dict_name)
                elif templ_choice == 'B':
                    ImgDictBtmpl(self).extract_final_txt(tmp_final_txt, out_dir, dict_name)
                elif templ_choice == 'C':
                    TextDictCtmpl(self).extract_final_txt(tmp_final_txt, out_dir, dict_name)
                elif templ_choice == 'D':
                    TextDictDtmpl(self).extract_final_txt(tmp_final_txt, out_dir, dict_name)
            # 处理 mdd
            file_mdd = os.path.splitext(xfile)[0] + '.mdd'
            if os.path.isfile(file_mdd) and templ_choice in ('A', 'B'):
                dir_data = os.path.join(out_dir, "imgs")
                if os.path.exists(dir_data):
                    shutil.rmtree(dir_data)
                self.utils.mdict(['-x', file_mdd, '-d', dir_data])
            elif os.path.isfile(file_mdd) and templ_choice in ('C', 'D'):
                dir_data = os.path.join(out_dir, "data")
                if os.path.exists(dir_data):
                    shutil.rmtree(dir_data)
                self.utils.mdict(['-x', file_mdd, '-d', dir_data])
            else:
                print(Fore.YELLOW + "WARN: " + Fore.RESET + "同路径下未找到相应的 mdd 文件, 将不会生成 imgs/data 文件夹")
            print(Fore.GREEN + "\n已提取原材料至目录: " + Fore.RESET + out_dir)
        else:
            print(Fore.RED + "ERROR: " + Fore.RESET + "词典并非由 AutoMdxBuilder 制作, 不支持还原")
        shutil.rmtree(tmp_restore)

    # def pdf_to_amb(self, input_path, pdf_flg=True):
    #     """ 从 PDF文件/pdg文件夹 生成 amb 文件夹 """
    #     # 0.准备路径相关
    #     dir_bkmk = os.path.join(self.settings.dir_output_tmp, 'bkmk')
    #     if not os.path.exists(dir_bkmk):
    #         os.makedirs(dir_bkmk)
    #     # 开始处理
    #     if pdf_flg:
    #         fname = os.path.split(input_path)[1]
    #         out_dir = os.path.join(os.path.split(input_path)[0], fname.split('.')[0]+'_amb')
    #         if not os.path.exists(out_dir):
    #             os.makedirs(out_dir)
    #         # 1.导出书签
    #         cur_path = os.getcwd()
    #         self.utils.eximport_bkmk_fp2p(input_path, os.path.join(cur_path, dir_bkmk))
    #         try:
    #             with open(os.path.join(dir_bkmk, 'FreePic2Pdf_bkmk.txt'), 'r', encoding='utf-16le') as fr:
    #                 text = fr.read()
    #                 line_num = len(re.findall(r'^', text, flags=re.M))
    #                 if line_num <= 3:
    #                     print(Fore.YELLOW + "INFO: " + Fore.RESET + "未识别到目录, 将不会生成 toc.txt")
    #                 else:
    #                     with open(os.path.join(out_dir, 'toc.txt'), 'w', encoding='utf-8') as fw:
    #                         fw.write(text)
    #                     if line_num > 500:
    #                         print(Fore.YELLOW + "INFO: " + Fore.RESET + "书签超过 500 行, 请后续确认是否包含索引, 是的话建议改名为 toc_all.txt")
    #         except UnicodeDecodeError:
    #             shutil.copy(os.path.join(dir_bkmk, "FreePic2Pdf_bkmk.txt"), os.path.join(out_dir, "[utf-16]toc.txt"))
    #             print(Fore.YELLOW + "WARN: " + Fore.RESET + "书签中存在无法识别的字符, 已输出为 utf-16 编码")
    #         with open(os.path.join(dir_bkmk, 'FreePic2Pdf.itf'), 'r', encoding='utf-16le') as fr:
    #             mt = re.search(r'(?<=BasePage=)(\d+)', fr.read())
    #             if mt:
    #                 body_start = mt.group(0)
    #             else:
    #                 body_start = 1
    #                 print(Fore.YELLOW + "INFO: " + Fore.RESET + "未识别到正文起始页码, 已设置默认值 1")
    #         # 2.生成 build.toml
    #         shutil.copy(os.path.join(self.settings.dir_lib, "build.toml"), os.path.join(out_dir, "build.toml"))
    #         with open(os.path.join(out_dir, "build.toml"), 'r+', encoding='utf-8') as fr:
    #             text = fr.read()
    #             text = re.sub(r'^templ_choice = "\w"', 'templ_choice = "A"', text, flags=re.I+re.M)
    #             text = re.sub(r'^name = "[^"]+?"', f'name = "{fname.split(".")[0]}"', text, flags=re.I+re.M)
    #             text = re.sub(r'^name_abbr = "[^"]+?"', 'name_abbr = "XXXXXX"', text, flags=re.I+re.M)
    #             text = re.sub(r'^body_start = \d+', f'body_start = {str(body_start)}', text, flags=re.I+re.M)
    #             fr.seek(0)
    #             fr.truncate()
    #             fr.write(text)
    #         # 3.导出图片
    #         if not os.path.exists(os.path.join(out_dir, 'imgs')):
    #             os.makedirs(os.path.join(out_dir, 'imgs'))
    #         self.utils.pdf_to_imgs(input_path, os.path.join(out_dir, 'imgs'))
    #     else:
    #         out_dir = input_path+'_amb'
    #         if not os.path.exists(out_dir):
    #             os.makedirs(out_dir)
    #         # 1.pdg 转 img
    #         if not os.path.exists(os.path.join(out_dir, 'imgs')):
    #             os.makedirs(os.path.join(out_dir, 'imgs'))
    #         print(os.path.join(out_dir, 'imgs'))
    #         self.utils.convert_pdg_to_img(input_path, os.path.join(out_dir, 'imgs'))
    #         # 2.识别词典信息
    #         bkmk_itf = os.path.join(os.path.join(out_dir, 'imgs'), 'FreePic2Pdf.itf')
    #         if os.path.isfile(bkmk_itf):
    #             with open(bkmk_itf, 'r', encoding='utf-16le') as fr:
    #                 text = fr.read()
    #                 mt_body_start = re.search(r'(?<=TextPage=)(\d+)', text)
    #                 mt_name = re.search(r'(?<=Title=)(.+)', text)
    #                 if mt_body_start:
    #                     body_start = mt_body_start.group(0)
    #                 else:
    #                     body_start = 1
    #                     print(Fore.YELLOW + "INFO: " + Fore.RESET + "未识别到正文起始页码, 已设置默认值 1")
    #                 if mt_name:
    #                     name = mt_name.group(0)
    #                 else:
    #                     name = os.path.split(input_path)[1]
    #             os.remove(bkmk_itf)
    #         else:
    #             print(Fore.YELLOW + "INFO: " + Fore.RESET + "未识别到书籍信息")
    #         # 3.生成 build.toml
    #         shutil.copy(os.path.join(self.settings.dir_lib, "build.toml"), os.path.join(out_dir, "build.toml"))
    #         with open(os.path.join(out_dir, "build.toml"), 'r+', encoding='utf-8') as fr:
    #             text = fr.read()
    #             text = re.sub(r'^templ_choice = "\w"', 'templ_choice = "A"', text, flags=re.I+re.M)
    #             text = re.sub(r'^name = "[^"]+?"', f'name = "{name}"', text, flags=re.I+re.M)
    #             text = re.sub(r'^name_abbr = "[^"]+?"', 'name_abbr = "XXXXXX"', text, flags=re.I+re.M)
    #             text = re.sub(r'^body_start = \d+', f'body_start = {str(body_start)}', text, flags=re.I+re.M)
    #             fr.seek(0)
    #             fr.truncate()
    #             fr.write(text)
    #     shutil.rmtree(dir_bkmk)
    #     print(Fore.GREEN + "\n\n预备原材料生成完毕！" + Fore.RESET)

    # def amb_to_pdf(self, file_toml, outside_flg):
    #     """ 从 amb 文件夹合成 PDF 文件 """
    #     # 0.准备路径相关
    #     dir_amb = os.path.split(file_toml)[0]
    #     if outside_flg:
    #         out_file = os.path.join(os.path.split(dir_amb)[0], self.settings.name+'.pdf')
    #     else:
    #         out_file = os.path.join(dir_amb, self.settings.name+'.pdf')
    #     dir_bkmk_bk = os.path.join(self.settings.dir_lib, 'bkmk')
    #     dir_bkmk = os.path.join(self.settings.dir_output_tmp, 'bkmk')
    #     if not os.path.exists(dir_bkmk):
    #         os.makedirs(dir_bkmk)
    #         shutil.copy(os.path.join(dir_bkmk_bk, "FreePic2Pdf.itf"), os.path.join(dir_bkmk, "FreePic2Pdf.itf"))
    #         shutil.copy(os.path.join(dir_bkmk_bk, "FreePic2Pdf_bkmk.txt"), os.path.join(dir_bkmk, "FreePic2Pdf_bkmk.txt"))
    #     # 1.生成临时书签
    #     with open(os.path.join(dir_bkmk, 'FreePic2Pdf.itf'), 'r+', encoding='utf-8') as fr:
    #         text = re.sub(r'(?<=BasePage=|TextPage=)\d+', str(self.settings.body_start), fr.read())
    #         fr.seek(0)
    #         fr.truncate()
    #         fr.write(text)
    #     toc_flg = False
    #     for fname in os.listdir(dir_amb):
    #         if fname == 'toc.txt':
    #             with open(os.path.join(dir_amb, fname), 'r', encoding='utf-8') as fr:
    #                 text = fr.read()
    #             with open(os.path.join(dir_bkmk, 'FreePic2Pdf_bkmk.txt'), 'r+', encoding='utf-8') as fr:
    #                 fr.seek(0)
    #                 fr.truncate()
    #                 fr.write(text)
    #             toc_flg = True
    #             break
    #         elif fname == 'index_all.txt':
    #             toc_tmp = os.path.join(self.settings.dir_output_tmp, 'toc_all.txt')
    #             if self.func.index_to_toc(os.path.join(dir_amb, fname), toc_tmp):
    #                 with open(toc_tmp, 'r', encoding='utf-8') as fr:
    #                     text = fr.read()
    #                 with open(os.path.join(dir_bkmk, 'FreePic2Pdf_bkmk.txt'), 'r+', encoding='utf-8') as fr:
    #                     fr.seek(0)
    #                     fr.truncate()
    #                     fr.write(text)
    #             toc_flg = True
    #             break
    #         else:
    #             pass
    #     if not toc_flg:
    #         print(Fore.YELLOW + "WARN: " + Fore.RESET + "未找到 toc.txt/index_all.txt, 生成的 PDF 将不带书签")
    #     # 2.将图片合成PDF
    #     if os.path.isdir(os.path.join(dir_amb, 'imgs')):
    #         self.utils.combine_img_to_pdf_fp2p(os.path.join(dir_amb, 'imgs'), out_file)
    #         # 3.给PDF挂书签
    #         cur_path = os.getcwd()
    #         self.utils.eximport_bkmk_fp2p(out_file, os.path.join(cur_path, dir_bkmk), False)
    #         shutil.rmtree(dir_bkmk)
    #         print(Fore.GREEN + "\n\nPDF生成完毕！" + Fore.RESET)
    #     else:
    #         print(Fore.RED + "ERROR: " + Fore.RESET + "未找到 imgs 文件夹")


def print_menu():
    """ 打印选单 """
    # 功能选单
    print("\n(〇) 打包/解包")
    print(Fore.CYAN + "  1" + Fore.RESET + ".解包 mdx/mdd 文件")
    print(Fore.CYAN + "  2" + Fore.RESET + ".将源 txt 文件打包成 mdx 文件")
    print(Fore.CYAN + "  3" + Fore.RESET + ".将资料包文件夹打包成 mdd 文件")
    print("\n(一) 准备原材料")
    # print(Fore.CYAN + "  10" + Fore.RESET + ".从 PDF文件/pdg文件夹 生成预备原材料" + Fore.YELLOW + " (还需手动检查完善)" + Fore.RESET)
    print(Fore.CYAN + "  11" + Fore.RESET + ".从 toc_all.txt 生成 index_all.txt")
    print(Fore.CYAN + "  12" + Fore.RESET + ".合并 toc.txt 和 index.txt 为 index_all.txt")
    print("\n(二) 制作词典")
    print(Fore.CYAN + "  20" + Fore.RESET + ".生成词典" + Fore.YELLOW + " (需准备好原材料)" + Fore.RESET)
    print("\n(三) 还原词典")
    print(Fore.CYAN + "  30" + Fore.RESET + ".从词典还原原材料" + Fore.YELLOW + " (仅支持 AMB 1.4 以上版本)" + Fore.RESET)
    # print(Fore.CYAN + "  31" + Fore.RESET + ".从原材料还原 PDF")
    print(Fore.CYAN + "  32" + Fore.RESET + ".从 index_all.txt 还原 toc_all.txt")
    print("\n(四) 其他工具")
    print(Fore.CYAN + "  41" + Fore.RESET + ".从 PDF 提取图片 (MuPDF)")
    print(Fore.CYAN + "  42" + Fore.RESET + ".将 PDF 转换成图片 (MuPDF)")
    # print(Fore.CYAN + "  43" + Fore.RESET + ".将 图片 合成 PDF (MuPDF)")
    # print(Fore.CYAN + "  44" + Fore.RESET + ".PDF书签导出/导入 (FreePic2Pdf)")


def main():
    just_fix_windows_console()
    # 程序开始
    print(Fore.CYAN + "欢迎使用 AutoMdxBuilder 1.5, 下面是功能选单:" + Fore.RESET)
    while True:
        print_menu()
        sel = input('\n请输入数字（回车或“0”退出程序）: ')
        # 执行选择
        if re.match(r'^\d+$', sel) and int(sel) in range(1, 50):
            print('\n------------------')
            amb = AutoMdxBuilder()
            amb.auto_processing(int(sel))
            print('\n\n------------------------------------')
            # 判断是否继续
            ctn = input(Fore.CYAN + "回车退出程序, 或输入 Y/y 继续使用 AMB: " + Fore.RESET)
            if ctn not in ['Y', 'y']:
                break
        else:
            break


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s | %(message)s', filename=Settings().file_log, filemode='w', level=logging.INFO)
    try:
        main()
        logging.info('The program worked fine.')
    except:
        logging.error(traceback.format_exc())
