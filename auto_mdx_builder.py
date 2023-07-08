#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-07-08 23:33:51
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.1

import os
from settings import Settings
from img_dict import ImgDict
from funcs_lib import FuncsLib

class AutoMdxBuilder:
    """图像词典制作程序"""
    def __init__(self):
        self.settings = Settings()
        self.funcs = FuncsLib()

    def auto_processing(self, sel):
        """ 根据选择自动处理 """
        if sel == 1:
            file_final_txt = os.path.join(self.settings.dir_input, self.settings.fname_final_txt)
            if self.funcs.text_file_check(file_final_txt) == 2:
                # 读取词条数
                entry_total = self.funcs.merge_and_count([file_final_txt], file_final_txt)
                # 检查数据文件夹
                dir_data = os.path.join(self.settings.dir_input, self.settings.dname_data)
                if not os.path.exists(dir_data):
                    print(f"INFO: 文件夹 {dir_data} 不存在, 已默认不打包 mdd")
                    dir_data = None
                elif os.path.exists(dir_data) and len(os.listdir(dir_data)) == 0:
                    print(f"WARN: 文件夹 {dir_data} 为空, 已默认不打包 mdd")
                    dir_data = None
                # 生成 info.html
                file_dict_info = self.funcs.generate_info_html(entry_total, 0)
                # 打包
                self._build_mdx(file_final_txt, file_dict_info, dir_data)
            else:
                print(f"\n材料检查不通过, 请确保材料准备无误再执行程序")
            a = input('\n------------------\n回车退出程序：')
        elif sel == 2:
            self.imgdict = ImgDict()
            # 生成 txt 源文本
            proc_flg, file_final_txt, dir_imgs_out, file_dict_info = self.imgdict.make_source_file()
            if proc_flg:
                # 打包
                self._build_mdx(file_final_txt, file_dict_info, dir_imgs_out)
                # 如果有 css 文件就拷贝过来
                file_css_tmp = os.path.join(self.settings.dir_output_tmp, self.settings.fname_css)
                file_css = os.path.join(self.settings.dir_output, self.settings.fname_css)
                if os.path.exists(file_css_tmp):
                    text = ''
                    with open(file_css_tmp, 'r', encoding='utf-8') as fr:
                        text = fr.read()
                    with open(file_css, 'w', encoding='utf-8') as fw:
                        fw.write(text)
            a = input('\n------------------\n回车退出程序：')
        else:
            pass

    def _build_mdx(self, file_final_txt, file_dict_info, dir_data):
        done_flg = True
        # 创建输出文件夹
        if not os.path.exists(self.settings.dir_output):
            os.makedirs(self.settings.dir_output)
        # 打包 mdx
        ftitle = os.path.join(self.settings.dir_output, self.settings.name)
        print('\n------------------\n开始打包:')
        if os.path.exists(file_final_txt) and os.path.exists(file_dict_info):
            os.system(f"mdict --description {file_dict_info} -a {file_final_txt} {ftitle}.mdx")
        else:
            print(f"ERROR: 文件 {file_final_txt} 或 {file_dict_info} 不存在")
            done_flg = False
        # 打包 mdd
        if dir_data:
            pack_mdd_flg = True
            if os.path.exists(ftitle+'.mdd'):
                a = input(f'文件 "{ftitle}.mdd" 已存在, 是否重新打包 mdd (Y/N): ')
                if a not in ('Y', 'y'):
                    pack_mdd_flg = False
                elif a in ('Y', 'y') and (not os.path.exists(dir_data) or len(os.listdir(dir_data))==0):
                    print(f"ERROR: 文件夹 {dir_data} 不存在或为空")
                    pack_mdd_flg = False
                    done_flg = False
            if pack_mdd_flg:
                os.system(f"mdict -a {dir_data} {ftitle}.mdd")
        if done_flg:
            print('\n打包完毕。\n\n恭喜, 词典已生成！')


if __name__ == '__main__':
    # 功能选单
    print("欢迎使用 AutoMdxBuilder, 下面是功能选单：\n")
    print("1.已准备源文本 (mdx.txt [,data]), 请直接打包成词典")
    print("2.已准备原材料 (index.txt 等), 请制作词典")
    print("9.退出程序")
    sel = int(input('\n请输入数字: '))
    # 执行选择
    if sel in (1,2):
        print('\n------------------')
        amb = AutoMdxBuilder()
        amb.auto_processing(sel)
