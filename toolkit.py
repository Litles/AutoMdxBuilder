#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-11-15 18:43:07
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.5

import time
import os
import re
from pywinauto.application import Application
from pywinauto.timings import Timings


def p2p_convert(dir_pdg, dir_out):
    """ 转换 pdgs 为 imgs """
    # 0.配置转换选项, 设定输出文件夹
    dir_p2p = './tools/Pdg2Pic/'
    fp_ini = os.path.join(dir_p2p, 'Pdg2Pic.ini')
    with open(fp_ini, 'r+', encoding='utf-16le') as fr:
        para_item = 'PARA_DIR_TGT='+dir_out.replace('\\', '\\\\')
        text = re.sub(r'^PARA_DIR_TGT=.+$', para_item, fr.read(), flags=re.M+re.I)
        fr.seek(0)
        fr.truncate()
        fr.write(text)
    # 1.启动 Pdg2Pic 程序
    Timings.fast()
    app = Application(backend='win32').start(os.path.join(dir_p2p, 'Pdg2Pic.exe'))
    dlg_main = app.Pdg2Pic
    # 2.读取输入的 PDG 文件夹
    dlg_main.wait('ready', timeout=10).children()[3].click()  # 打开文件夹选择框
    dlg_sel = app.window(title=u'选择存放PDG文件的文件夹')
    dlg_sel.wait('ready', timeout=5).children()[6].set_text(dir_pdg)
    dlg_sel.children()[9].click()
    app.window(title=u'格式统计').wait('ready', timeout=10).children()[0].click()
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


def fp2p_export_bkmk(file_pdf, dir_out):
    """ 从 pdf 文件中导出书签 """
    dir_fp2p = './tools/FreePic2Pdf/'
    # 1.启动 FreePic2Pdf 程序
    Timings.fast()
    app = Application(backend='win32').start(os.path.join(dir_fp2p, 'FreePic2Pdf.exe'))
    dlg_main = app.FreePic2Pdf
    dlg_main.wait('ready', timeout=10).children()[30].click()  # 点击进入书签导入/导出窗口
    dlg_iebkmk = app.window(title=u'Import/Export PDF Bookmark')
    dlg_iebkmk.wait('ready', timeout=5).children()[26].select(1)  # 切换到书签导出栏
    # 2.选定输入的 pdf 文件
    time.sleep(0.1)
    dlg_iebkmk.children()[4].click()  # 打开文件选择框
    dlg_sel_pdf = app.window(title=u'Select File')
    dlg_sel_pdf.wait('ready', timeout=5).children()[12].set_text(file_pdf)
    dlg_sel_pdf.children()[16].click()  # 选中待处理的 pdf 文件
    # 3.选定输出的书签目录
    if not os.path.exists(dir_out):
        os.makedirs(dir_out)
    while True:
        if not app.window(title=u'Select File').exists():
            break
        else:
            time.sleep(0.05)
    dlg_iebkmk.children()[9].click()  # 打开输出文件夹选择框
    dlg_sel_folder = app.window(title=u'Source Folder')
    dlg_sel_folder.wait('ready', timeout=5).children()[6].set_edit_text(dir_out)
    dlg_sel_folder.children()[9].click()
    # 3.开始导出
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

def fp2p_import_bkmk(file_pdf, dir_bkmk):
    """ 向 pdf 文件导入书签 """
    pass

def fp2p_bkmk_to_amb():
    pass

def fp2p_amb_to_bkmk():
    pass


# dir_pdg = "C:\\Users\\shuji\\Downloads\\汉语方言词汇 第2版_11737900"
# dir_out = "C:\\Users\\shuji\\Downloads\\汉语方言词汇_out"
# p2p_convert(dir_pdg, dir_out)


file_pdf = "C:\\Users\\shuji\\Desktop\\A Global History From Prehistory To The 21st Century, 7th Edition.pdf"
dir_out = "C:\\Users\\shuji\\Downloads\\bkmk_out"
fp2p_export_bkmk(file_pdf, dir_out)
