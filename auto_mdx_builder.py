#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-07-05 14:49:12
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.0

import os
from settings import Settings
from img_dict import ImgDict

class AutoMdxBuilder:
    """图像词典制作程序"""
    def __init__(self):
        self.imgdict = ImgDict()
        self.settings = Settings()

    def build_mdx(self):
        """生成mdx词典"""
        # 0.生成 txt 源文本
        proc_flg, file_final_txt, dir_imgs_out = self.imgdict.make_source_file()
        if proc_flg:
            # 创建输出文件夹
            if not os.path.exists(self.settings.dir_output):
                os.makedirs(self.settings.dir_output)
            # 3.打包 mdx
            ftitle = os.path.join(self.settings.dir_output, self.settings.name)
            file_dict_info = os.path.join(self.settings.dir_output_tmp, self.settings.fname_dict_info)
            print('\n------------------\n开始打包:')
            os.system(f"mdict --description {file_dict_info} -a {file_final_txt} {ftitle}.mdx")
            # 4.打包 mdd
            if os.path.exists(ftitle+'.mdd'):
                a = input(f'文件 "{ftitle}.mdd" 已存在, 是否重新打包图像 (Y/N): ')
                if a in ('Y', 'y'):
                    os.system(f"mdict -a {dir_imgs_out} {ftitle}.mdd")
            else:
                os.system(f"mdict -a {dir_imgs_out} {ftitle}.mdd")
            print('\n打包完毕。\n\n恭喜, 词典已制作完成！')
            # 如果有 css 文件就拷贝过来
            file_css_tmp = os.path.join(self.settings.dir_output_tmp, self.settings.fname_css)
            file_css = os.path.join(self.settings.dir_output, self.settings.fname_css)
            if os.path.exists(file_css_tmp):
                text = ''
                with open(file_css_tmp, 'r', encoding='utf-8') as fr:
                    text = fr.read()
                with open(file_css, 'w', encoding='utf-8') as fw:
                    fw.write(text)

if __name__ == '__main__':
    imb = AutoMdxBuilder()
    imb.build_mdx()
    a = input('\n------------------\n回车退出程序：')
