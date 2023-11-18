#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-15 18:43:07
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.5

import os
import re
import shutil
import time
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from pywinauto.timings import Timings
from PIL import Image
# import sys
# import fitz
# from fitz.__main__ import main as fitz_command


# ========== (一) From PDF to Images ==========
def pdf_to_imgs(file_pdf, dir_out):
    """ 自动判断文字版/图片版PDF, 并选择最优方法导出图像 """
    # 准备环境
    cur_path = os.getcwd()
    file_exe = os.path.join(os.path.join(os.path.join(cur_path, 'tools'), 'MuPDF'), 'mutool.exe')
    dir_tmp = os.path.join(cur_path, '_tmp')
    if not os.path.exists(dir_tmp):
        os.makedirs(dir_tmp)
    dir_tmp_mp = os.path.join(dir_tmp, 'MuPDF_tmp')
    if not os.path.exists(dir_tmp_mp):
        os.makedirs(dir_tmp_mp)
    tmp_txt = os.path.join(dir_tmp_mp, 'text.txt')
    # 判断是文字版还是图片版PDF
    img_pdf_flg = True
    os.system(f'{file_exe} draw -o {tmp_txt} -F text {file_pdf} 2-11')
    with open(tmp_txt, 'r', encoding='utf-8') as fr:
        word = re.sub(r'[\r\n\s]', '', fr.read(), flags=re.I)
        if len(word) > 50:
            img_pdf_flg = False
    # 开始处理
    if img_pdf_flg:
        extract_pdf_to_imgs(file_pdf, dir_out)
    else:
        convert_pdf_to_imgs(file_pdf, dir_out)
    shutil.rmtree(dir_tmp_mp)


def convert_pdf_to_imgs(file_pdf, dir_out, dpi=300):
    """ 使用 mutool.exe 按 DPI 参数转换成图片 (推荐用于文字版PDF) """
    # 准备文件夹
    cur_path = os.getcwd()
    file_exe = os.path.join(os.path.join(os.path.join(cur_path, 'tools'), 'MuPDF'), 'mutool.exe')
    if not os.path.exists(dir_out):
        os.makedirs(dir_out)
    file_png = os.path.join(dir_out, '%06d.png')
    # 开始转换
    os.system(f'{file_exe} draw -o {file_png} -F png -r {str(dpi)} {file_pdf} 1-10')

# def convert_pdf_to_imgs_fitz(file_pdf, dir_out):
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
#     for i in range(count):
#         fname = f"{str(i+1).zfill(8)}.png"
#         page = doc.load_page(i)
#         pix = page.get_pixmap(matrix=mat, dpi=300, colorspace=fitz.csGRAY, alpha=False)
#         pix.save(os.path.join(dir_out, fname))
#     doc.close()


def extract_pdf_to_imgs(file_pdf, dir_out):
    """ Extracting images with mutool.exe (Windows only) """
    # 1.extract to tmp folder
    cur_path = os.getcwd()
    file_exe = os.path.join(os.path.join(os.path.join(cur_path, 'tools'), 'MuPDF'), 'mutool.exe')
    dir_tmp = os.path.join(cur_path, '_tmp')
    if not os.path.exists(dir_tmp):
        os.makedirs(dir_tmp)
    dir_tmp_me = os.path.join(dir_tmp, 'MuPDF_extract')
    if not os.path.exists(dir_tmp_me):
        os.makedirs(dir_tmp_me)
    os.chdir(dir_tmp_me)
    os.system(f'{file_exe} extract "{file_pdf}"')
    os.chdir(cur_path)
    # 2.remove to destination
    img_exts = ['jpg', 'jpeg', 'jp2', 'png', 'gif', 'bmp', 'tif', 'tiff']
    imgs = []
    for fname in os.listdir(dir_tmp_me):
        ext = fname.split('.')[1].lower()
        if ext in img_exts:
            imgs.append({"path": os.path.join(dir_tmp_me, fname), "ext": '.'+ext})
    if not os.path.exists(dir_out):
        os.makedirs(dir_out)
    imgs.sort(key=lambda x: x["path"], reverse=False)
    n = 0
    for img in imgs:
        n += 1
        os.rename(img["path"], os.path.join(dir_out, str(n).zfill(6)+img["ext"]))
    shutil.rmtree(dir_tmp_me)


def extract_pdf_to_imgs_pdfpatcher(file_pdf, dir_out):
    """ Extracting images with PDFPatcher.exe (Windows only) """
    # 0.配置程序选项
    dir_program = './tools/PDFPatcher/'
    file_conf_bak = './lib/PDFPatcher_AppConfig.json'
    file_conf = os.path.join(dir_program, 'AppConfig.json')
    os.system(f'copy /y "{file_conf_bak}" "{file_conf}"')
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


# def extract_pdf_to_imgs_fitz(file_pdf, dir_out):
#     """ 使用 fitz(mupdf), 如果生成了JBIG2加密的 jb2，则还需要使用 jbig2dec 解密成 png """
#     # 准备参数
#     cmd = ['extract', str(file_pdf), '-images', '-output', str(dir_out)]
#     saved_parms = sys.argv[1:]
#     sys.argv[1:] = cmd
#     # 开始导出
#     if not os.path.exists(dir_out):
#         os.makedirs(dir_out)
#     fitz_command()
#     sys.argv[1:] = saved_parms


# ========== (二) From Images to PDF ==========
def combine_img_to_pdf(dir_imgs, file_pdf):
    """ use mutool.exe to combine images to pdf file (Windows only) """
    # prepare paths
    cur_path = os.getcwd()
    file_exe = os.path.join(os.path.join(os.path.join(cur_path, 'tools'), 'MuPDF'), 'mutool.exe')
    dir_tmp = os.path.join(cur_path, '_tmp')
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
    file_pcs = os.path.join(os.path.join(cur_path, 'lib'), 'MuPDF_pcs.txt')
    # read image files to get sizes
    img_exts = ['.jpg', 'jpeg', '.jp2', '.png', '.gif', '.bmp', '.tif', '.tiff']
    imgs = []
    for fname in os.listdir(dir_imgs):
        fp = os.path.join(dir_imgs, fname)
        if os.path.splitext(fp)[1].lower() in img_exts:
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
    os.system(f'{file_exe} merge -o {file_pdf} {pdf_str}')
    shutil.rmtree(dir_pcs)
    shutil.rmtree(dir_pdf_frag)
    shutil.rmtree(dir_pdf_merge)


def combine_img_to_pdf_fp2p(dir_imgs, file_pdf):
    """ 使用 FreePic2Pdf.exe 图像合成 pdf """
    # 0.配置转换选项, 设定图像文件夹
    dir_program = './tools/FreePic2Pdf/'
    file_ini_bak = './lib/FreePic2Pdf.ini'
    file_ini = os.path.join(dir_program, 'FreePic2Pdf.ini')
    with open(file_ini_bak, 'r', encoding='utf-16') as fr:
        para_item = 'PARA_DIR_SRC='+dir_imgs.replace('\\', '\\\\')
        text = re.sub(r'^PARA_DIR_SRC=.+$', para_item, fr.read(), flags=re.M+re.I)
        with open(file_ini, 'w', encoding='utf-16') as fw:
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
def convert_pdg_to_img(dir_pdg, dir_out):
    """ 使用 Pdg2Pic.exe 转换 pdgs 为 imgs """
    # 0.配置转换选项, 设定输出文件夹
    dir_program = './tools/Pdg2Pic/'
    file_ini_bak = './lib/Pdg2Pic.ini'
    file_ini = os.path.join(dir_program, 'Pdg2Pic.ini')
    with open(file_ini_bak, 'r', encoding='utf-16') as fr:
        para_item = 'PARA_DIR_TGT='+dir_out.replace('\\', '\\\\')
        text = re.sub(r'^PARA_DIR_TGT=.+$', para_item, fr.read(), flags=re.M+re.I)
        with open(file_ini, 'w', encoding='utf-16') as fw:
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
def eximport_bkmk_fp2p(file_pdf, dir_bkmk, export_flg=True):
    """ 使用 FreePic2Pdf.exe 向/从 pdf 文件中导入/导出书签 """
    dir_program = './tools/FreePic2Pdf/'
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
        print('书签导出完成！')
    else:
        print('书签导入完成！')


# convert pdg to image
# file_pdf = "C:\\Users\\shuji\\Desktop\\汉语方言词汇_out_jb2.pdf"
# dir_out = "C:\\Users\\shuji\\Desktop\\patch_out"
# extract_pdf_to_imgs_pdfpatcher(file_pdf, dir_out)

# convert pdg to image
# dir_pdg = "C:\\Users\\shuji\\Downloads\\汉语方言词汇_pdg"
# dir_out = "C:\\Users\\shuji\\Downloads\\汉语方言词汇_img"
# convert_pdg_to_img(dir_pdg, dir_out)

# file_pdf = "C:\\Users\\shuji\\Desktop\\汉语方言词汇_out_tiff.pdf"
# dir_bkmk = "C:\\Users\\shuji\\Desktop\\bkmk"
# eximport_bkmk_fp2p(file_pdf, dir_bkmk)

# convert method
# file_pdf = "C:\\Users\\shuji\\Desktop\\生物学大辞典.pdf"
# dir_out = "C:\\Users\\shuji\\Desktop\\mutool_out1_draw_300dpi"
# convert_pdf_to_imgs(file_pdf, dir_out)

# extract method
# file_pdf = "C:\\Users\\shuji\\Desktop\\mutool_out1.pdf"
# dir_out = "C:\\Users\\shuji\\Desktop\\mutool_out1"
# extract_pdf_to_imgs(file_pdf, dir_out)

# auto extract/convert
# file_pdf = "C:\\Users\\shuji\\Desktop\\生物学大辞典_part.pdf"
# dir_out = "C:\\Users\\shuji\\Desktop\\生物学大辞典_part"
# pdf_to_imgs(file_pdf, dir_out)

# combine images to pdf
# dir_imgs = "C:\\Users\\shuji\\Desktop\\mutool_out"
# file_pdf = "C:\\Users\\shuji\\Desktop\\mutool_out.pdf"
# combine_img_to_pdf(dir_imgs, file_pdf)

# dir_imgs = "C:\\Users\\shuji\\Desktop\\汉语方言词汇_out"
# combine_img_to_pdf_fp2p(dir_imgs, file_pdf)