#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-07-08 23:33:51
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.1

import os
from colorama import init, Fore, Back, Style
from settings import Settings
from img_dict import ImgDict
from func_lib import FuncLib


class AutoMdxBuilder:
    """图像词典制作程序"""
    def __init__(self):
        self.settings = Settings()
        self.func = FuncLib()

    def auto_processing(self, sel):
        """ 根据选择自动处理 """
        if sel == 1:
            mfile = input(f"请输入要解包的 mdx/mdd 文件路径: ").strip('"')
            self._export_mdx(mfile)
        elif sel == 2:
            file_final_txt = input(f"请输入要打包的 txt 文件路径: ").strip('"')
            if os.path.isfile(file_final_txt) and self.func.text_file_check(file_final_txt) == 2:
                # 读取词条数
                entry_total = self.func.merge_and_count([file_final_txt], file_final_txt)
                # 检查数据文件夹
                dir_curr = os.path.split(file_final_txt)[0]
                dir_data = os.path.join(dir_curr, 'data')
                if not os.path.exists(dir_data):
                    print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"文件夹 {dir_data} 不存在, 已默认不打包 mdd")
                    dir_data = None
                elif os.path.exists(dir_data) and len(os.listdir(dir_data)) == 0:
                    print(Fore.MAGENTA + "WARN: " + Fore.RESET + f"文件夹 {dir_data} 为空, 已默认不打包 mdd")
                    dir_data = None
                # 生成 info.html
                file_dict_info = self.func.generate_info_html(entry_total, 0)
                # 打包
                self._build_mdx(file_final_txt, file_dict_info, dir_data, dir_curr)
            else:
                print(Fore.RED + f"\n材料检查不通过, 请确保材料准备无误再执行程序")
        elif sel == 3:
            mdir = input(f"请输入要打包的资料文件夹路径: ").strip('"')
            self._build_mdd_only(mdir)
        elif sel == 4:
            self.imgdict = ImgDict()
            # 生成 txt 源文本
            proc_flg, file_final_txt, dir_imgs_out, file_dict_info = self.imgdict.make_source_file()
            if proc_flg:
                # 创建输出文件夹, 开始打包
                if not os.path.exists(self.settings.dir_output):
                    os.makedirs(self.settings.dir_output)
                self._build_mdx(file_final_txt, file_dict_info, dir_imgs_out, self.settings.dir_output)
                # 如果有 css 文件就拷贝过来
                file_css_tmp = os.path.join(self.settings.dir_output_tmp, self.settings.fname_css)
                file_css = os.path.join(self.settings.dir_output, self.settings.fname_css)
                if os.path.exists(file_css_tmp):
                    text = ''
                    with open(file_css_tmp, 'r', encoding='utf-8') as fr:
                        text = fr.read()
                    with open(file_css, 'w', encoding='utf-8') as fw:
                        fw.write(text)
        else:
            pass
        input('\n------------------\n回车退出程序：')


    def _export_mdx(self, mfile):
        """ 解包 mdx/mdd (取代 MdxExport.exe) """
        if os.path.isfile(mfile) and mfile.endswith('.mdx'):
            out_dir = os.path.splitext(mfile)[0]
            os.system(f"mdict -x {mfile} -d {out_dir}")
            for fname in os.listdir(out_dir):
                fp = os.path.join(out_dir, fname)
                if os.path.isfile(fp):
                    fp_new = fp.replace('.mdx', '')
                    os.rename(fp, fp_new)
            print(Fore.GREEN + f"\n已输出在同目录下: " + Fore.BLUE + out_dir)
        elif os.path.isfile(mfile) and mfile.endswith('.mdd'):
            out_dir = os.path.join(os.path.splitext(mfile)[0], 'data')
            os.system(f"mdict -x {mfile} -d {out_dir}")
            print(Fore.GREEN + f"\n已输出在同目录下: " + Fore.BLUE + out_dir)
        else:
            print(Fore.RED + "ERROR: " + Fore.RESET + "路径输入有误")


    def _build_mdx(self, file_final_txt, file_dict_info, dir_data, dir_output):
        """ 打包 mdx/mdd (取代 MdxBuilder.exe) """
        done_flg = True
        # 打包 mdx
        ftitle = os.path.join(dir_output, os.path.splitext(os.path.split(file_final_txt)[1])[0])
        print('\n------------------\n开始打包:')
        if os.path.exists(file_final_txt) and os.path.exists(file_dict_info):
            os.system(f"mdict --description {file_dict_info} --encoding utf-8 -a {file_final_txt} {ftitle}.mdx")
        else:
            print(Fore.RED + "ERROR: " + Fore.RESET + f"文件 {file_final_txt} 或 {file_dict_info} 不存在")
            done_flg = False
        # 打包 mdd
        if dir_data:
            pack_mdd_flg = True
            if os.path.exists(ftitle+'.mdd'):
                a = input(f'文件 "{ftitle}.mdd" 已存在, 是否重新打包 mdd (Y/N): ')
                if a not in ('Y', 'y'):
                    pack_mdd_flg = False
                elif a in ('Y', 'y') and (not os.path.exists(dir_data) or len(os.listdir(dir_data))==0):
                    print(Fore.RED + "ERROR: " + Fore.RESET + f"文件夹 {dir_data} 不存在或为空")
                    pack_mdd_flg = False
                    done_flg = False
            if pack_mdd_flg:
                os.system(f"mdict -a {dir_data} {ftitle}.mdd")
        if done_flg:
            print("\n打包完毕。"+ Fore.GREEN + "\n\n恭喜, 词典已生成！")

    def _build_mdd_only(self, dir_data):
        done_flg = True
        if os.path.exists(dir_data):
            print('\n------------------\n开始打包:')
            ftitle = dir_data.rstrip('\\')
            os.system(f"mdict -a {dir_data} {ftitle}.mdd")
        else:
            print(Fore.RED + "ERROR: " + Fore.RESET + f"文件夹 {dir_data} 不存在")
            done_flg = False
        if done_flg:
            print('\n打包完毕。')

if __name__ == '__main__':
    init(autoreset=True)
    # 功能选单
    print(Fore.GREEN + "欢迎使用 AutoMdxBuilder, 下面是功能选单:")
    print("\n(一) 打包/解包")
    print(Fore.CYAN + "  1" + Fore.RESET + ".解包 mdx/mdd 文件")
    print(Fore.CYAN + "  2" + Fore.RESET + ".打包成 mdx/mdd 文件")
    print(Fore.CYAN + "  3" + Fore.RESET + ".仅打包成 mdd 文件")
    print("\n(二) 制作词典 (需于 raw 文件夹放置好原材料)")
    print(Fore.CYAN + "  4" + Fore.RESET + ".制作图像词典 (模板A)")
    print("\n(三) 其他")
    print(Fore.CYAN + "  0" + Fore.RESET + ".退出程序")
    sel = int(input('\n请输入数字: '))
    # 执行选择
    if sel in range(1,5):
        print('\n------------------')
        amb = AutoMdxBuilder()
        amb.auto_processing(sel)
