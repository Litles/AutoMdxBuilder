#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-15 18:43:07
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.5

import os
import re
import shutil
from colorama import Fore
# from PIL import Image
import sys
from mdict_utils.__main__ import run as mdict_cmd
import fitz
from fitz.__main__ import main as fitz_command


class EbookUtils:
    """ 电子书(PDF等)实用工具 """
    def __init__(self, amb):
        self.settings = amb.settings

    # ========== (〇) mdict-utils ==========
    def mdict(self, parms):
        """ 执行 mdict-utils 程序 """
        saved_parms = sys.argv[1:]
        sys.argv[1:] = parms
        mdict_cmd()
        sys.argv[1:] = saved_parms

    def export_mdx(self, mfile):
        """ 解包 mdx/mdd (取代 MdxExport.exe) """
        done_flg = True
        if os.path.isfile(mfile) and mfile.endswith('.mdx'):
            out_dir = os.path.splitext(mfile)[0]
            self.mdict(['-x', mfile, '-d', out_dir])
            for fname in os.listdir(out_dir):
                fp = os.path.join(out_dir, fname)
                if os.path.isfile(fp) and ('description' in fname.split('.')):
                    fp_new = fp.replace('.description', '.info').replace('.mdx', '')
                    os.rename(fp, fp_new)
                elif os.path.isfile(fp):
                    fp_new = fp.replace('.mdx', '')
                    os.rename(fp, fp_new)
            # 分析 info 信息, 确定是否支持词条顺序的还原
            order_flg = False
            for f in os.listdir(out_dir):
                fp = os.path.join(out_dir, f)
                text = ''
                if fp.endswith('.info.html'):
                    with open(fp, 'r', encoding='utf-8') as fr:
                        if re.search(r'<div><br/>[^><]*?, (packed|built) with AutoMdxBuilder[^><]*?\.<br/></div>', fr.read(), flags=re.I):
                            # 符合条件, 支持词条顺序的还原
                            order_flg = True
                            break
            if order_flg:
                # 按编号精准还原源 txt
                xname = os.path.split(mfile)[1]
                file_final_txt = os.path.join(out_dir, xname.split('.')[0]+'.txt')
                entries = []
                eid = '99999999'
                with open(file_final_txt, 'r', encoding='utf-8') as fr:
                    text = ''
                    for line in fr:
                        if re.match(r'^<div class="entry-id" style="display:none;">(\d+)</div>', line):
                            eid = re.match(r'^<div class="entry-id" style="display:none;">(\d+)</div>', line).group(1)
                        elif not re.match(r'^</>\s*$', line):
                            text += line
                        else:
                            text += line
                            entries.append({"eid": eid, "text": text})
                            eid = '99999999'
                            text = ''
                if eid != '':
                    entries.sort(key=lambda x: x["eid"], reverse=False)
                    with open(file_final_txt, 'w', encoding='utf-8') as fw:
                        for entry in entries:
                            fw.write(entry["text"])
            else:
                print(Fore.YELLOW + "WARN: " + Fore.RESET + "检测到词典并非由 AMB 生成, 不保证词条顺序的准确还原")
        elif os.path.isfile(mfile) and mfile.endswith('.mdd'):
            cur_dir, mname = os.path.split(mfile)
            out_dir = os.path.join(os.path.splitext(mfile)[0], 'data')
            if os.path.exists(out_dir):
                shutil.rmtree(out_dir)
            # 检查是否存在 mdd 分包
            multi_mdd_flg = False
            mdd_names = [mname]
            for fname in os.listdir(cur_dir):
                if re.search(r'\.\d+\.mdd$', fname.lower()):
                    multi_mdd_flg = True
                    mdd_names.append(fname)
            # 按检查结果区分处理
            if multi_mdd_flg and input('检查到目录下存在 mdd 分包, 是否全部解包 (Y/N): ') in ('Y', 'y'):
                mdd_names = list(set(mdd_names))
                mdd_names.sort()
                for mdd_name in mdd_names:
                    print(f"开始解压 '{mdd_name}' :\n")
                    self.mdict(['-x', os.path.join(cur_dir, mdd_name), '-d', out_dir])
            else:
                self.mdict(['-x', mfile, '-d', out_dir])
        else:
            print(Fore.RED + "ERROR: " + Fore.RESET + "路径输入有误")
            done_flg = False
        return done_flg

    def pack_to_mdict(self, file_final_txt, file_dict_info, dir_data, dir_output):
        """ 打包 mdx/mdd (取代 MdxBuilder.exe) """
        mdx_flg = True
        mdd_flg = True
        # 打包 mdx
        print('正在生成 mdx 文件……\n')
        ftitle = os.path.join(dir_output, os.path.splitext(os.path.split(file_final_txt)[1])[0])
        if os.path.exists(file_final_txt) and os.path.exists(file_dict_info):
            # 给词条添加编号信息
            tmp_final_txt = os.path.join(os.path.join(self.settings.dir_bundle, '_tmp'), 'tmp_final.txt')
            with open(file_final_txt, 'r', encoding='utf-8') as fr:
                with open(tmp_final_txt, 'w', encoding='utf-8') as fw:
                    n = 0
                    link_flg = False
                    for line in fr:
                        if re.match(r'^@@@LINK=', line, flags=re.I):
                            link_flg = True
                        if (not link_flg) and re.match(r'^</>\s*$', line):
                            n += 1
                            fw.write(f'<div class="entry-id" style="display:none;">{str(n).zfill(8)}</div>\n')
                            link_flg = False
                        fw.write(line)
            self.mdict(['--description', file_dict_info, '--encoding', 'utf-8', '-a', tmp_final_txt, ftitle+'.mdx'])
        else:
            print(Fore.RED + "ERROR: " + Fore.RESET + f"文件 {file_final_txt} 或 {file_dict_info} 不存在")
            mdx_flg = False
        # 打包 mdd
        if dir_data is not None:
            mdd_flg = self.pack_to_mdd(dir_data, ftitle)
        if mdx_flg and mdd_flg:
            return True
        else:
            return False

    def pack_to_mdd(self, dir_data, ftitle):
        """ 仅打包 mdd (取代 MdxBuilder.exe) """
        done_flg = True
        pack_flg = True
        if ftitle is None:
            ftitle = dir_data
        # 判断是否打包
        if os.path.exists(dir_data) and len(os.listdir(dir_data)) > 0:
            if os.path.exists(ftitle+'.mdd'):
                a = input(f'文件 "{ftitle}.mdd" 已存在, 是否重新打包 mdd (Y/N): ')
                if a not in ('Y', 'y'):
                    pack_flg = False
        else:
            print(Fore.RED + "ERROR: " + Fore.RESET + f"文件夹 {dir_data} 不存在或为空")
            pack_flg = False
            done_flg = False
        # 开始打包
        if pack_flg:
            print('正在生成 mdd 文件……\n')
            # 检查子文件夹的数量
            sub_dirs = []
            for item in os.listdir(dir_data):
                if os.path.isdir(os.path.join(dir_data, item)):
                    sub_dirs.append(os.path.join(dir_data, item))
            # 如果有2个子文件夹以上, 再计算子文件夹大小, 如果大小超过 1.5G, 将分包
            split_flg = False
            size_sum = 0
            if len(sub_dirs) > 1:
                # 判断子文件夹大小
                for sub_dir in sub_dirs:
                    for fname in os.listdir(sub_dir):
                        if os.path.isfile(os.path.join(sub_dir, fname)):
                            size_sum += os.path.getsize(os.path.join(sub_dir, fname))
                        if size_sum > 1536000000:
                            split_flg = True
                            break
            # 按检查结果开始处理
            if split_flg:
                size_sum = 0
                print(Fore.YELLOW + "INFO: " + Fore.RESET + "资料文件夹超过 1.5G, 将自动分包")
                # 创建临时文件夹
                tmp_dir = os.path.join(os.path.split(dir_data)[0], '_packing')
                if not os.path.exists(tmp_dir):
                    os.makedirs(tmp_dir)
                pack_list = []
                pack = []
                n = 0
                # 对每个子文件夹作判断
                for i in range(len(sub_dirs)):
                    for fname in os.listdir(sub_dirs[i]):
                        if os.path.isfile(os.path.join(sub_dirs[i], fname)):
                            size_sum += os.path.getsize(os.path.join(sub_dirs[i], fname))
                        if size_sum > 1024000000:
                            size_sum = 0
                            pack.append(sub_dirs[i])
                            pack_list.append(pack)
                            pack = []
                            break
                    pack.append(sub_dirs[i])
                    n = i
                # 1.打包子文件夹
                mdd_rk = 0
                for sds in pack_list:
                    for sd in sds:
                        # 移动到临时文件夹中
                        os.rename(sd, os.path.join(tmp_dir, os.path.split(sd)[1]))
                    # 移完之后打包
                    if mdd_rk == 0:
                        self.mdict(['-a', tmp_dir, ftitle+'.mdd'])
                    else:
                        self.mdict(['-a', tmp_dir, f'{ftitle}.{str(mdd_rk)}.mdd'])
                    # 打包完再移回去
                    for fname in os.listdir(tmp_dir):
                        os.rename(os.path.join(tmp_dir, fname), os.path.join(dir_data, fname))
                    mdd_rk += 1
                # 1.打包剩余部分
                # 移动文件夹部分(如果有)
                if n == len(sub_dirs) - 1:
                    for sd in pack:
                        os.rename(sd, os.path.join(tmp_dir, os.path.split(sd)[1]))
                # 移动文件部分(如果有)
                for item in os.listdir(dir_data):
                    if not os.path.isdir(os.path.join(dir_data, item)):
                        os.rename(os.path.join(dir_data, item), os.path.join(tmp_dir, item))
                # 打包
                if len(os.listdir(tmp_dir)) == 0:
                    pass
                else:
                    self.mdict(['-a', tmp_dir, f'{ftitle}.{str(mdd_rk)}.mdd'])
                    # 移回去
                    for fname in os.listdir(tmp_dir):
                        os.rename(os.path.join(tmp_dir, fname), os.path.join(dir_data, fname))
                # 删除临时文件夹
                if os.path.exists(tmp_dir):
                    os.rmdir(tmp_dir)
            else:
                self.mdict(['-a', dir_data, ftitle+'.mdd'])
        return done_flg

    # ========== (一) From PDF to Images ==========
    # def pdf_to_imgs(self, file_pdf, dir_out):
    #     """ 自动判断文字版/图片版PDF, 并选择最优方法导出图像 """
    #     # 准备环境
    #     file_exe = os.path.join(os.path.join(os.path.join(self.settings.dir_bundle, 'tools'), 'MuPDF'), 'mutool.exe')
    #     dir_tmp = os.path.join(self.settings.dir_bundle, '_tmp')
    #     if not os.path.exists(dir_tmp):
    #         os.makedirs(dir_tmp)
    #     dir_tmp_mp = os.path.join(dir_tmp, 'MuPDF_tmp')
    #     if not os.path.exists(dir_tmp_mp):
    #         os.makedirs(dir_tmp_mp)
    #     tmp_txt = os.path.join(dir_tmp_mp, 'text.txt')
    #     # 判断是文字版还是图片版PDF
    #     img_pdf_flg = True
    #     os.system(f'{file_exe} draw -o {tmp_txt} -F text {file_pdf} 2-11')
    #     with open(tmp_txt, 'r', encoding='utf-8') as fr:
    #         word = re.sub(r'[\r\n\s]', '', fr.read())
    #         if len(word) > 50:
    #             img_pdf_flg = False
    #     # 开始处理
    #     if img_pdf_flg:
    #         self.extract_pdf_to_imgs_pdfpatcher(file_pdf, dir_out)
    #     else:
    #         self.convert_pdf_to_imgs(file_pdf, dir_out)
    #     shutil.rmtree(dir_tmp_mp)

    def convert_pdf_to_imgs_fitz(self, file_pdf, dir_out, dpi=300):
        """ 使用 fitz(mupdf), 按 DPI 等参数转换成图片 """
        # 读取 pdf
        doc = fitz.open(file_pdf)
        mat = fitz.Matrix(1, 1)
        count = 0
        for p in doc:
            count += 1
        # 开始导出
        if not os.path.exists(dir_out):
            os.makedirs(dir_out)
        print('转换中……')
        for i in range(count):
            fname = f"{str(i+1).zfill(8)}.png"
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=mat, dpi=dpi, colorspace=fitz.csGRAY, alpha=False)
            pix.save(os.path.join(dir_out, fname))
        doc.close()
        print('转换完成！')

    def extract_pdf_to_imgs_fitz(self, file_pdf, dir_out):
        """ 使用 fitz(mupdf), 如果生成了JBIG2加密的 jb2，则还需要使用 jbig2dec 解密成 png """
        # 准备参数
        cmd = ['extract', str(file_pdf), '-images', '-output', str(dir_out)]
        saved_parms = sys.argv[1:]
        sys.argv[1:] = cmd
        # 开始导出
        if not os.path.exists(dir_out):
            os.makedirs(dir_out)
        print('提取中……')
        fitz_command()
        sys.argv[1:] = saved_parms
        print('提取完成！')
