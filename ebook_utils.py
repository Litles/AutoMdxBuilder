#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-15 18:43:07
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.6

import os
import re
import shutil
import time
from colorama import Fore
# import codecs
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from pywinauto.timings import Timings
from PIL import Image
import sys
from mdict_utils.__main__ import run as mdict_cmd
# import fitz
# from fitz.__main__ import main as fitz_command


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
                print(Fore.YELLOW + "INFO: " + Fore.RESET + "检测到词典并非由 AMB 生成, 不保证词条顺序的准确还原")
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

    def pack_to_mdict(self, dir_output, file_final_txt, file_dict_info, dir_data):
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
    def pdf_to_imgs(self, file_pdf, dir_out):
        """ 自动判断文字版/图片版PDF, 并选择最优方法导出图像 """
        # 准备环境
        file_exe = os.path.join(os.path.join(os.path.join(self.settings.dir_bundle, 'tools'), 'MuPDF'), 'mutool.exe')
        dir_tmp = os.path.join(self.settings.dir_bundle, '_tmp')
        if not os.path.exists(dir_tmp):
            os.makedirs(dir_tmp)
        dir_tmp_mp = os.path.join(dir_tmp, 'MuPDF_tmp')
        if not os.path.exists(dir_tmp_mp):
            os.makedirs(dir_tmp_mp)
        tmp_txt = os.path.join(dir_tmp_mp, 'text.txt')
        # 判断是文字版还是图片版PDF
        img_pdf_flg = True
        os.system(f'{file_exe} draw -o {tmp_txt} -F text "{file_pdf}" 2-11')
        with open(tmp_txt, 'r', encoding='utf-8') as fr:
            word = re.sub(r'[\r\n\s]', '', fr.read())
            if len(word) > 50:
                img_pdf_flg = False
        # 开始处理
        if img_pdf_flg:
            self.extract_pdf_to_imgs_pdfpatcher(file_pdf, dir_out)
        else:
            self.convert_pdf_to_imgs(file_pdf, dir_out)
        shutil.rmtree(dir_tmp_mp)

    def convert_pdf_to_imgs(self, file_pdf, dir_out, dpi=300):
        """ 使用 mutool.exe 按 DPI 参数转换成图片 (推荐用于文字版PDF) """
        # 准备文件夹
        file_exe = os.path.join(os.path.join(os.path.join(self.settings.dir_bundle, 'tools'), 'MuPDF'), 'mutool.exe')
        if not os.path.exists(dir_out):
            os.makedirs(dir_out)
        file_png = os.path.join(dir_out, '%06d.png')
        # 开始转换
        os.system(f'{file_exe} draw -o "{file_png}" -F png -r {str(dpi)} "{file_pdf}"')
        print('转换完成！')

    # def convert_pdf_to_imgs_fitz(self, file_pdf, dir_out, dpi=300):
    #     """ 使用 fitz(mupdf), 按 DPI 等参数转换成图片 """
    #     # 读取 pdf
    #     doc = fitz.open(file_pdf)
    #     mat = fitz.Matrix(1, 1)
    #     count = 0
    #     for p in doc:
    #         count += 1
    #     # 开始导出
    #     if not os.path.exists(dir_out):
    #         os.makedirs(dir_out)
    #     print('转换中……')
    #     for i in range(count):
    #         fname = f"{str(i+1).zfill(8)}.png"
    #         page = doc.load_page(i)
    #         pix = page.get_pixmap(matrix=mat, dpi=dpi, colorspace=fitz.csGRAY, alpha=False)
    #         pix.save(os.path.join(dir_out, fname))
    #     doc.close()
    #     print('转换完成！')

    def extract_pdf_to_imgs(self, file_pdf, dir_out):
        """ Extracting images with mutool.exe (Windows only) """
        # 1.extract to tmp folder
        file_exe = os.path.join(os.path.join(os.path.join(self.settings.dir_bundle, 'tools'), 'MuPDF'), 'mutool.exe')
        dir_tmp = os.path.join(self.settings.dir_bundle, '_tmp')
        if not os.path.exists(dir_tmp):
            os.makedirs(dir_tmp)
        dir_tmp_me = os.path.join(dir_tmp, 'MuPDF_extract')
        if not os.path.exists(dir_tmp_me):
            os.makedirs(dir_tmp_me)
        os.chdir(dir_tmp_me)
        os.system(f'{file_exe} extract "{file_pdf}"')
        os.chdir(self.settings.dir_bundle)
        # 2.remove to destination
        imgs = []
        for fname in os.listdir(dir_tmp_me):
            ext = os.path.splitext(fname)[1].lower()
            if ext in self.settings.img_exts:
                imgs.append({"path": os.path.join(dir_tmp_me, fname), "ext": ext})
        if not os.path.exists(dir_out):
            os.makedirs(dir_out)
        imgs.sort(key=lambda x: x["path"], reverse=False)
        n = 0
        for img in imgs:
            n += 1
            os.rename(img["path"], os.path.join(dir_out, str(n).zfill(6)+img["ext"]))
        shutil.rmtree(dir_tmp_me)
        print('提取完成！')

    def extract_pdf_to_imgs_pdfpatcher(self, file_pdf, dir_out):
        """ Extracting images with PDFPatcher.exe (Windows only) """
        # 0.配置程序选项
        dir_program = os.path.join(os.path.join(self.settings.dir_bundle, 'tools'), 'PDFPatcher')
        file_conf_bak = os.path.join(self.settings.dir_lib, 'PDFPatcher_AppConfig.json')
        file_conf = os.path.join(dir_program, 'AppConfig.json')
        shutil.copy(file_conf_bak, file_conf)
        # 1.启动 PDFPatcher 程序, 配置提取选项
        Timings.fast()
        app = Application(backend='win32').start(os.path.join(dir_program, 'PDFPatcher.exe'))
        dlg_main = app.window(title_re='.*PDF.*补丁丁')
        dlg_main.wait('ready', timeout=10)
        send_keys('%{g}tt')
        dlg_extract = dlg_main
        dlg_extract.wait('ready', timeout=2).children()[38].set_text(file_pdf)
        dlg_extract.wait('ready', timeout=2).children()[33].set_text(dir_out)
        # 2.开始提取
        dlg_extract.wait('ready', timeout=2).children()[6].click()
        time.sleep(0.2)
        # print(dlg_extract.children()[52].GetProperties())
        while True:
            if '返回' in dlg_extract.children()[52].texts():
                dlg_extract.children()[52].click()
                app.kill()
                break
            else:
                time.sleep(0.2)
        print('提取完成！')

    # def extract_pdf_to_imgs_fitz(self, file_pdf, dir_out):
    #     """ 使用 fitz(mupdf), 如果生成了JBIG2加密的 jb2，则还需要使用 jbig2dec 解密成 png """
    #     # 准备参数
    #     cmd = ['extract', str(file_pdf), '-images', '-output', str(dir_out)]
    #     saved_parms = sys.argv[1:]
    #     sys.argv[1:] = cmd
    #     # 开始导出
    #     if not os.path.exists(dir_out):
    #         os.makedirs(dir_out)
    #     print('提取中……')
    #     fitz_command()
    #     sys.argv[1:] = saved_parms
    #     print('提取完成！')

    # ========== (二) From Images to PDF ==========
    def combine_img_to_pdf(self, dir_imgs, file_pdf):
        """ use mutool.exe to combine images to pdf file (Windows only) """
        # prepare paths
        file_exe = os.path.join(os.path.join(os.path.join(self.settings.dir_bundle, 'tools'), 'MuPDF'), 'mutool.exe')
        dir_tmp = os.path.join(self.settings.dir_bundle, '_tmp')
        if not os.path.exists(dir_tmp):
            os.makedirs(dir_tmp)
        dir_pcs = os.path.join(dir_tmp, 'MuPDF_pcs')
        dir_pdf_frag = os.path.join(dir_tmp, 'MuPDF_pdf_frag')
        dir_pdf_merge = os.path.join(dir_tmp, 'MuPDF_pdf_merge')
        if not os.path.exists(dir_pcs):
            os.makedirs(dir_pcs)
        if not os.path.exists(dir_pdf_frag):
            os.makedirs(dir_pdf_frag)
        if not os.path.exists(dir_pdf_merge):
            os.makedirs(dir_pdf_merge)
        file_pcs = os.path.join(self.settings.dir_lib, 'MuPDF_pcs.txt')
        # read image files to get sizes
        imgs = []
        for fname in os.listdir(dir_imgs):
            fp = os.path.join(dir_imgs, fname)
            if os.path.splitext(fp)[1].lower() in self.settings.img_exts:
                img = {
                    "fname": fname,
                    "path": fp,
                    "size": Image.open(fp).size
                }
                imgs.append(img)
        imgs.sort(key=lambda x: x["fname"], reverse=False)
        # generate pcs(Page content streams) txt file
        with open(file_pcs, 'r', encoding='utf-8') as fr:
            text = fr.read()
        page_num = 0
        txts = []
        for img in imgs:
            page_num += 1
            pcs = text.replace('<num>', str(page_num).zfill(6))
            pcs = pcs.replace('<path>', img["path"])
            pcs = pcs.replace('<width>', str(img["size"][0]))
            pcs = pcs.replace('<height>', str(img["size"][1]))
            txt = os.path.join(dir_pcs, str(page_num).zfill(6)+'.txt')
            with open(txt, 'w', encoding='utf-8') as fw:
                fw.write(pcs)
            txts.append(txt)
        # start to create pdf fragments
        pdfs = []
        n, k, step = 1, 1, 20
        total_step = int(page_num/step + 1)
        while k <= total_step:
            pcs_str = ''
            bound = k*step
            while n <= min(bound, page_num):
                pcs_str = pcs_str + ' ' + txts[n-1]
                n += 1
            tmp_pdf = os.path.join(dir_pdf_frag, str(k).zfill(3)+'.pdf')
            os.system(f'{file_exe} create -o {tmp_pdf} -O compress-images {pcs_str}')
            print(f'[{str(min(n,page_num))}/{str(page_num)}]PDF合成中')
            pdfs.append(tmp_pdf)
            k += 1
        # merge fragments
        pdf_str = ''
        file_num = len(pdfs)
        n, k, step = 1, 1, 10
        total_step = int(file_num/step + 1)
        while k <= total_step:
            merge_str = ''
            bound = k*step
            while n <= min(bound, file_num):
                merge_str = merge_str + ' ' + pdfs[n-1]
                n += 1
            tmp_pdf = os.path.join(dir_pdf_merge, str(k).zfill(2)+'.pdf')
            os.system(f'{file_exe} merge -o {tmp_pdf} {merge_str}')
            pdf_str = pdf_str + ' ' + tmp_pdf
            k += 1
        # output final single file
        os.system(f'{file_exe} merge -o "{file_pdf}" {pdf_str}')
        shutil.rmtree(dir_pcs)
        shutil.rmtree(dir_pdf_frag)
        shutil.rmtree(dir_pdf_merge)
        print('合成完成！')

    def combine_img_to_pdf_fp2p(self, dir_imgs, file_pdf):
        """ 使用 FreePic2Pdf.exe 图像合成 pdf """
        # 0.配置转换选项, 设定图像文件夹
        dir_program = os.path.join(os.path.join(self.settings.dir_bundle, 'tools'), 'FreePic2Pdf')
        file_ini_bak = os.path.join(self.settings.dir_lib, 'FreePic2Pdf.ini')
        file_ini = os.path.join(dir_program, 'FreePic2Pdf.ini')
        with open(file_ini_bak, 'r', encoding='utf-16le') as fr:
            para_item = 'PARA_DIR_SRC='+dir_imgs.replace('\\', '\\\\')
            text = re.sub(r'^PARA_DIR_SRC=.+$', para_item, fr.read(), flags=re.M)
            with open(file_ini, 'w', encoding='utf-16le') as fw:
                fw.write(text)
        # 1.启动 FreePic2Pdf 程序
        Timings.fast()
        app = Application(backend='win32').start(os.path.join(dir_program, 'FreePic2Pdf.exe'))
        dlg_main = app.FreePic2Pdf
        # 2.设定输出 pdf 文件路径
        dlg_main.wait('ready', timeout=10).children()[32].set_edit_text(file_pdf)
        # 3.开始合成 pdf
        dlg_main.children()[20].click()  # 点击执行
        while True:
            if app.window(title='FreePic2Pdf', predicate_func=lambda dlg: len(dlg.children()) == 3).exists():
                app.window(
                    title='FreePic2Pdf', predicate_func=lambda dlg: len(dlg.children()) == 3
                ).wait('ready', timeout=2).children()[0].click()
                app.kill()
                break
            else:
                time.sleep(0.2)
        print('PDF 生成完毕！')

    # ========== (三) From Other Formats to Images ==========
    def convert_pdg_to_img(self, dir_pdg, dir_out):
        """ 使用 Pdg2Pic.exe 转换 pdgs 为 imgs """
        # 0.配置转换选项, 设定输出文件夹
        dir_program = os.path.join(os.path.join(self.settings.dir_bundle, 'tools'), 'Pdg2Pic')
        file_ini_bak = os.path.join(self.settings.dir_lib, 'Pdg2Pic.ini')
        file_ini = os.path.join(dir_program, 'Pdg2Pic.ini')
        with open(file_ini_bak, 'r', encoding='utf-16le') as fr:
            para_item = 'PARA_DIR_TGT='+dir_out.replace('\\', '\\\\')
            text = re.sub(r'^PARA_DIR_TGT=.+$', para_item, fr.read(), flags=re.M)
            with open(file_ini, 'w', encoding='utf-16le') as fw:
                fw.write(text)
        # 1.启动 Pdg2Pic 程序
        Timings.fast()
        app = Application(backend='win32').start(os.path.join(dir_program, 'Pdg2Pic.exe'))
        dlg_main = app.Pdg2Pic
        # 2.读取输入的 PDG 文件夹
        dlg_main.wait('ready', timeout=10).children()[3].click()  # 打开文件夹选择框
        dlg_sel = app.window(title=u'选择存放PDG文件的文件夹')
        dlg_sel.wait('ready', timeout=5).children()[6].set_text(dir_pdg)
        dlg_sel.children()[9].click()
        app.window(title=u'格式统计').wait('ready', timeout=3).children()[0].click()
        # dlg_sum = app.window(title=u'格式统计').wait('ready', timeout=3)
        # while True:
        #     if 'OK' in dlg_sum.children()[0].texts():
        #         dlg_sum.children()[0].click()
        #         break
        #     else:
        #         time.sleep(0.05)
        # 3.开始转换
        while True:
            if not app.window(title=u'格式统计').exists():
                dlg_main.children()[0].click()  # 点击执行
                break
            else:
                time.sleep(0.05)
        while True:
            if app.window(title='Pdg2Pic', predicate_func=lambda dlg: len(dlg.children()) == 3).exists():
                app.window(
                    title='Pdg2Pic', predicate_func=lambda dlg: len(dlg.children()) == 3
                ).wait('ready', timeout=2).children()[0].click()
                app.kill()
                break
            else:
                time.sleep(0.2)
        print('转换完成！')

    # ========== (四) PDF Bookmark Management ==========
    def eximport_bkmk_fp2p(self, file_pdf, dir_bkmk, export_flg=True):
        """ 使用 FreePic2Pdf.exe 向/从 pdf 文件中导入/导出书签 """
        dir_program = os.path.join(os.path.join(self.settings.dir_bundle, 'tools'), 'FreePic2Pdf')
        # 1.启动 FreePic2Pdf 程序
        Timings.fast()
        app = Application(backend='win32').start(os.path.join(dir_program, 'FreePic2Pdf.exe'))
        dlg_main = app.FreePic2Pdf
        dlg_main.wait('ready', timeout=10).children()[30].click()  # 点击进入书签导入/导出窗口
        dlg_iebkmk = app.window(title=u'Import/Export PDF Bookmark')
        if export_flg:
            dlg_iebkmk.wait('ready', timeout=5).children()[26].select(1)  # 切换到书签导出栏
        # 2.选定 pdf 文件
        time.sleep(0.1)
        dlg_iebkmk.children()[4].click()  # 打开文件选择框
        dlg_sel_pdf = app.window(title=u'Select File')
        dlg_sel_pdf.wait('ready', timeout=5).children()[12].set_text(file_pdf)
        dlg_sel_pdf.children()[16].click()  # 选中待处理的 pdf 文件
        # 3.选定书签文件夹
        if not os.path.exists(dir_bkmk):
            os.makedirs(dir_bkmk)
        while True:
            if not app.window(title=u'Select File').exists():
                break
            else:
                time.sleep(0.05)
        dlg_iebkmk.children()[9].click()  # 打开文件夹选择框
        dlg_sel_folder = app.window(title=u'Source Folder')
        dlg_sel_folder.wait('ready', timeout=5).children()[6].set_edit_text(dir_bkmk)
        dlg_sel_folder.children()[9].click()
        # 3.开始导入/导出
        while True:
            if not app.window(title=u'Source Folder').exists():
                dlg_iebkmk.children()[0].click()  # 点击执行
                break
            else:
                time.sleep(0.05)
        while True:
            if app.window(title='FreePic2Pdf', predicate_func=lambda dlg: len(dlg.children()) == 3).exists():
                app.window(
                    title='FreePic2Pdf', predicate_func=lambda dlg: len(dlg.children()) == 3
                ).wait('ready', timeout=2).children()[0].click()
                app.kill()
                break
            else:
                time.sleep(0.2)
        if export_flg:
            # [备用1]utf-16判断有无BOM
            # with open(os.path.join(dir_bkmk, 'FreePic2Pdf.itf'), 'rb') as frb:
            #     encoded_text = frb.read()
            #     bom = codecs.BOM_UTF16_LE
            #     if encoded_text.startswith(bom):
            #         bkmk_itf = encoded_text[len(bom):].decode('utf-16le')
            #     else:
            #         bkmk_itf = encoded_text.decode('utf-16le')
            #     base_page = re.search(r'(?<=BasePage=)(\d+)', bkmk_itf)
            #     if base_page:
            #         bkmk_itf = re.sub(r'^TextPage=$', 'TextPage='+base_page.group(0), bkmk_itf, flags=re.M)
            # with open(os.path.join(dir_bkmk, 'FreePic2Pdf_bkmk.txt'), 'rb') as frb:
            #     encoded_text = frb.read()
            #     bom = codecs.BOM_UTF16_LE
            #     if encoded_text.startswith(bom):
            #         bkmk_text = encoded_text[len(bom):].decode('utf-16le')
            #     else:
            #         bkmk_text = encoded_text.decode('utf-16le')
            # [备用2]考虑是否一律转utf-8
            # with open(os.path.join(dir_bkmk, 'FreePic2Pdf.itf'), 'r', encoding='utf-16') as fr:
            #     bkmk_itf = fr.read()
            #     base_page = re.search(r'(?<=BasePage=)(\d+)', bkmk_itf)
            #     if base_page:
            #         bkmk_itf = re.sub(r'^TextPage=$', 'TextPage='+base_page.group(0), bkmk_itf, flags=re.M)
            # with open(os.path.join(dir_bkmk, 'FreePic2Pdf_bkmk.txt'), 'r', encoding='utf-16') as fr:
            #     bkmk_text = fr.read()
            # dir_bkmk_bk = os.path.join(self.settings.dir_lib, 'bkmk')
            # shutil.copy(os.path.join(dir_bkmk_bk, "FreePic2Pdf.itf"), os.path.join(dir_bkmk, "FreePic2Pdf.itf"))
            # shutil.copy(os.path.join(dir_bkmk_bk, "FreePic2Pdf_bkmk.txt"), os.path.join(dir_bkmk, "FreePic2Pdf_bkmk.txt"))
            # with open(os.path.join(dir_bkmk, 'FreePic2Pdf.itf'), 'w', encoding='utf-8') as fw:
            #     fw.write(bkmk_itf)
            # with open(os.path.join(dir_bkmk, 'FreePic2Pdf_bkmk.txt'), 'w', encoding='utf-8') as fw:
            #     fw.write(bkmk_text)
            with open(os.path.join(dir_bkmk, 'FreePic2Pdf.itf'), 'r+', encoding='utf-16le') as fr:
                bkmk_itf = fr.read()
                base_page = re.search(r'(?<=BasePage=)(\d+)', bkmk_itf)
                if base_page:
                    bkmk_itf = re.sub(r'^TextPage=$', 'TextPage='+base_page.group(0), bkmk_itf, flags=re.M)
                fr.seek(0)
                fr.truncate()
                fr.write(bkmk_itf)
            print('书签导出完成！')
        else:
            print('书签导入完成！')
