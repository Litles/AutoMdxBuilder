#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023-07-13 19:49:50
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.4

import os
import re
import shutil
from colorama import init, Fore, Back, Style
from settings import Settings
from func_lib import FuncLib
from img_dict_atmpl import ImgDictAtmpl
from img_dict_btmpl import ImgDictBtmpl
from text_dict_ctmpl import TextDictCtmpl
from text_dict_dtmpl import TextDictDtmpl


class AutoMdxBuilder:
    """图像词典制作程序"""
    def __init__(self):
        self.settings = Settings()
        self.func = FuncLib(self)

    def auto_processing(self, sel):
        """ 根据选择自动处理 """
        if sel == 1:
            mfile = input("请输入要解包的 mdx/mdd 文件路径: ").strip('"')
            self._export_mdx(mfile)
        elif sel == 2:
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
                done_flg = self._pack_to_mdict(file_final_txt, file_dict_info, dir_data, dir_curr)
                if done_flg:
                    print(Fore.GREEN + "\n打包完毕。")
            else:
                print(Fore.RED + "\n材料检查不通过, 请确保材料准备无误再执行程序")
        elif sel == 3:
            dir_data = input("请输入要打包的资料文件夹路径: ").strip('"/\\')
            dir_data = dir_data.rstrip('\\')
            dir_data = dir_data.rstrip('/')
            print('\n------------------\n开始打包……\n')
            done_flg = self._pack_to_mdd(dir_data, None)
            if done_flg:
                print(Fore.GREEN + "\n打包完毕。")
        elif sel == 20:
            """ 制作词典 """
            p = input("请输入原材料文件夹路径或 build.toml 文件路径: ").strip('"/\\')
            if os.path.split(p)[1] == 'build.toml':
                if self.settings.load_build_toml(p, False):
                    self._build_mdict()
            elif os.path.isdir(p):
                file_toml = os.path.join(p, 'build.toml')
                if os.path.isfile(file_toml):
                    if self.settings.load_build_toml(file_toml, True):
                        self._build_mdict()
                else:
                    print(Fore.RED + "ERROR: " + Fore.RESET + "文件夹内未找到 build.toml 文件")
            else:
                print(Fore.RED + "ERROR: " + Fore.RESET + "路径输入有误")
        elif sel == 21:
            file_toc_all = input("请输入 toc_all.txt 的文件路径: ").strip('"')
            file_index_all = os.path.join(os.path.split(file_toc_all)[0], 'index_all.txt')
            if self.func.toc_all_to_index(file_toc_all, file_index_all):
                print(Fore.GREEN + "\n处理完成, 生成在同目录下")
            else:
                print(Fore.RED + "\n文件检查不通过, 请确保文件准备无误再执行程序")
        elif sel == 22:
            file_toc = input("(1) 请输入 toc.txt 的文件路径: ").strip('"')
            file_index = input("(2) 请输入 index.txt 的文件路径: ").strip('"')
            file_index_all = os.path.join(os.path.split(file_index)[0], 'index_all.txt')
            self.func.merge_to_index_all(file_toc, file_index, file_index_all)
        elif sel == 30:
            p = input("请输入词典的文件夹或 mdx/mdd 文件路径: ").strip('"/\\')
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
        elif sel == 31:
            file_index_all = input("请输入 index_all.txt 的文件路径: ").strip('"')
            file_toc_all = os.path.join(os.path.split(file_index_all)[0], 'toc_all.txt')
            if self.func.index_to_toc(file_index_all, file_toc_all):
                print(Fore.GREEN + "\n处理完成, 生成在同目录下")
            else:
                print(Fore.RED + "\n文件检查不通过, 请确保所有词目都有对应页码")
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
                # 如果有 css 文件就拷贝过来
                file_css_tmp = os.path.join(self.settings.dir_output_tmp, self.settings.fname_css)
                file_css = os.path.join(self.settings.dir_output, self.settings.fname_css)
                if os.path.exists(file_css_tmp):
                    os.system(f'copy /y "{file_css_tmp}" "{file_css}"')
                # 开始打包
                print('\n------------------\n开始打包……\n')
                done_flg = self._pack_to_mdict(file_final_txt, file_dict_info, dir_imgs_out, self.settings.dir_output)
        elif self.settings.templ_choice in ('b', 'B'):
            """ 制作图像词典 (模板B) """
            # 生成 txt 源文本
            proc_flg, file_final_txt, dir_imgs_out, file_dict_info = ImgDictBtmpl(self).make_source_file()
            if proc_flg:
                # 创建输出文件夹
                if not os.path.exists(self.settings.dir_output):
                    os.makedirs(self.settings.dir_output)
                # 如果有 css 文件就拷贝过来
                file_css_tmp = os.path.join(self.settings.dir_output_tmp, self.settings.fname_css)
                file_css = os.path.join(self.settings.dir_output, self.settings.fname_css)
                if os.path.exists(file_css_tmp):
                    os.system(f'copy /y "{file_css_tmp}" "{file_css}"')
                # 开始打包
                print('\n------------------\n开始打包……\n')
                done_flg = self._pack_to_mdict(file_final_txt, file_dict_info, dir_imgs_out, self.settings.dir_output)
        elif self.settings.templ_choice in ('c', 'C'):
            """ 制作文本词典 (模板C) """
            # 生成 txt 源文本
            proc_flg, file_final_txt, file_dict_info = TextDictCtmpl(self).make_source_file()
            if proc_flg:
                # 创建输出文件夹
                if not os.path.exists(self.settings.dir_output):
                    os.makedirs(self.settings.dir_output)
                # 如果有 css 文件就拷贝过来
                file_css_tmp = os.path.join(self.settings.dir_output_tmp, self.settings.fname_css)
                file_css = os.path.join(self.settings.dir_output, self.settings.fname_css)
                if os.path.exists(file_css_tmp):
                    os.system(f'copy /y "{file_css_tmp}" "{file_css}"')
                # 开始打包
                print('\n------------------\n开始打包……\n')
                dir_data = os.path.join(self.settings.dir_input, self.settings.dname_data)
                if not os.path.exists(dir_data) or len(os.listdir(dir_data)) == 0:
                    dir_data = None
                done_flg = self._pack_to_mdict(file_final_txt, file_dict_info, dir_data, self.settings.dir_output)
        elif self.settings.templ_choice in ('d', 'D'):
            """ 制作文本词典 (模板D) """
            # 生成 txt 源文本
            proc_flg, file_final_txt, file_dict_info = TextDictDtmpl(self).make_source_file()
            if proc_flg:
                # 创建输出文件夹
                if not os.path.exists(self.settings.dir_output):
                    os.makedirs(self.settings.dir_output)
                # 如果有 css 文件就拷贝过来
                file_css_tmp = os.path.join(self.settings.dir_output_tmp, self.settings.fname_css)
                file_css = os.path.join(self.settings.dir_output, self.settings.fname_css)
                if os.path.exists(file_css_tmp):
                    os.system(f'copy /y "{file_css_tmp}" "{file_css}"')
                # 开始打包
                print('\n------------------\n开始打包……\n')
                dir_data = os.path.join(self.settings.dir_input, self.settings.dname_data)
                if not os.path.exists(dir_data) or len(os.listdir(dir_data)) == 0:
                    dir_data = None
                done_flg = self._pack_to_mdict(file_final_txt, file_dict_info, dir_data, self.settings.dir_output)
        else:
            pass
        if done_flg:
            print("\n打包完毕。" + Fore.GREEN + "\n\n恭喜, 词典已生成！")

    def _export_mdx(self, mfile):
        """ 解包 mdx/mdd (取代 MdxExport.exe) """
        if os.path.isfile(mfile) and mfile.endswith('.mdx'):
            out_dir = os.path.splitext(mfile)[0]
            os.system(f'mdict -x "{mfile}" -d "{out_dir}"')
            for fname in os.listdir(out_dir):
                fp = os.path.join(out_dir, fname)
                if os.path.isfile(fp):
                    fp_new = fp.replace('.mdx', '')
                    os.rename(fp, fp_new)
            print(Fore.GREEN + "\n已输出在同目录下: " + Fore.RESET + out_dir)
        elif os.path.isfile(mfile) and mfile.endswith('.mdd'):
            cur_dir, mname = os.path.split(mfile)
            out_dir = os.path.join(os.path.splitext(mfile)[0], 'data')
            # 检查是否存在 mdd 分包
            multi_mdd_flg = False
            mdd_names = [mname]
            for fname in os.listdir(cur_dir):
                if re.search(r'\.\d+\.mdd$', fname, flags=re.I):
                    multi_mdd_flg = True
                    mdd_names.append(fname)
            # 按检查结果区分处理
            if multi_mdd_flg and input('检查到目录下存在 mdd 分包, 是否全部解包 (Y/N): ') in ('Y','y'):
                mdd_names = list(set(mdd_names))
                mdd_names.sort()
                for mdd_name in mdd_names:
                    print(f"开始解压 '{mdd_name}' :\n")
                    os.system(f'mdict -x "{os.path.join(cur_dir, mdd_name)}" -d "{out_dir}"')
            else:
                os.system(f'mdict -x "{mfile}" -d "{out_dir}"')
            print(Fore.GREEN + f"\n已输出在同目录下: " + Fore.RESET + out_dir)
        else:
            print(Fore.RED + "ERROR: " + Fore.RESET + "路径输入有误")

    def _pack_to_mdict(self, file_final_txt, file_dict_info, dir_data, dir_output):
        """ 打包 mdx/mdd (取代 MdxBuilder.exe) """
        mdx_flg = True
        mdd_flg = True
        # 打包 mdx
        print('正在生成 mdx 文件……\n')
        ftitle = os.path.join(dir_output, os.path.splitext(os.path.split(file_final_txt)[1])[0])
        if os.path.exists(file_final_txt) and os.path.exists(file_dict_info):
            os.system(f'mdict --description "{file_dict_info}" --encoding utf-8 -a "{file_final_txt}" "{ftitle}.mdx"')
        else:
            print(Fore.RED + "ERROR: " + Fore.RESET + f"文件 {file_final_txt} 或 {file_dict_info} 不存在")
            mdx_flg = False
        # 打包 mdd
        if dir_data is not None:
            mdd_flg = self._pack_to_mdd(dir_data, ftitle)
        if mdx_flg and mdd_flg:
            return True
        else:
            return False

    def _pack_to_mdd(self, dir_data, ftitle):
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
                        if os.path.isfile(os.path.join(sub_dirs[i],fname)):
                            size_sum += os.path.getsize(os.path.join(sub_dirs[i],fname))
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
                        os.system(f'mdict -a "{tmp_dir}" "{ftitle}.mdd"')
                    else:
                        os.system(f'mdict -a "{tmp_dir}" "{ftitle}.{str(mdd_rk)}.mdd"')
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
                    os.system(f'mdict -a "{tmp_dir}" "{ftitle}.{str(mdd_rk)}.mdd"')
                    # 移回去
                    for fname in os.listdir(tmp_dir):
                        os.rename(os.path.join(tmp_dir, fname), os.path.join(dir_data, fname))
                # 删除临时文件夹
                if os.path.exists(tmp_dir):
                    os.rmdir(tmp_dir)
            else:
                os.system(f'mdict -a "{dir_data}" "{ftitle}.mdd"')
        return done_flg

    def _restore_raw(self, xfile, outside_flg):
        """ 将词典还原为原材料 """
        extract_flg = False
        dict_name = None
        templ_choice = None
        # 1.准备输出文件夹
        dir_input, fname = os.path.split(xfile)
        if outside_flg:
            out_dir = os.path.join(os.path.split(dir_input)[0], fname.split('.')[0]) + '_amb'
        else:
            out_dir = os.path.splitext(xfile)[0] + '_amb'
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        # 2.分析 mdx 文件
        os.system(f'mdict -x "{xfile}" -d "{out_dir}"')
        # 分析 info 信息, 确定是否支持还原
        for fname in os.listdir(out_dir):
            fp = os.path.join(out_dir, fname)
            text = None
            if fp.endswith('.mdx.description.html'):
                with open(fp, 'r+', encoding='utf-8') as fr:
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
            # 提取 info.html
            os.remove(fp)
            if not re.match(r'^\s*$', text):
                with open(os.path.join(out_dir, 'info.html'), 'w', encoding='utf-8') as fw:
                    fw.write(text)
            # 提取 index, index_all, syns 等信息
            for fname in os.listdir(out_dir):
                fp = os.path.join(out_dir, fname)
                if fp.endswith('.mdx.txt'):
                    # 选择函数进行处理
                    if templ_choice == 'A':
                        ImgDictAtmpl(self).extract_final_txt(fp, out_dir, dict_name)
                    elif templ_choice == 'B':
                        ImgDictBtmpl(self).extract_final_txt(fp, out_dir, dict_name)
                    elif templ_choice == 'C':
                        TextDictCtmpl(self).extract_final_txt(fp, out_dir, dict_name)
                    elif templ_choice == 'D':
                        TextDictDtmpl(self).extract_final_txt(fp, out_dir, dict_name)
            # 处理 mdd
            file_mdd = os.path.splitext(xfile)[0] + '.mdd'
            if os.path.isfile(file_mdd) and templ_choice in ('A', 'B'):
                os.system(f'mdict -x "{file_mdd}" -d "{os.path.join(out_dir, "imgs")}"')
            elif os.path.isfile(file_mdd) and templ_choice in ('C', 'D'):
                os.system(f'mdict -x "{file_mdd}" -d "{os.path.join(out_dir, "data")}"')
            else:
                print(Fore.YELLOW + "WARN: " + Fore.RESET + "同路径下未找到相应的 mdd 文件, 将不会生成 imgs/data 文件夹")
            print(Fore.GREEN + "\n已提取原材料至目录: " + Fore.RESET + out_dir)
        else:
            print(Fore.RED + "ERROR: " + Fore.RESET + "词典并非由 AutoMdxBuilder 制作, 不支持还原")


def print_menu():
    """ 打印选单 """
    # 功能选单
    print("\n(一) 打包/解包")
    print(Fore.CYAN + "  1" + Fore.RESET + ".解包 mdx/mdd 文件")
    print(Fore.CYAN + "  2" + Fore.RESET + ".将源 txt 文件打包成 mdx 文件")
    print(Fore.CYAN + "  3" + Fore.RESET + ".将资料包文件夹打包成 mdd 文件")
    print("\n(二) 制作词典")
    print(Fore.CYAN + "  20" + Fore.RESET + ".生成词典" + Fore.YELLOW + " (需准备好原材料)")
    print(Fore.CYAN + "  21" + Fore.RESET + ".【图像词典】将 toc_all.txt 处理成 index_all.txt 文件")
    print(Fore.CYAN + "  22" + Fore.RESET + ".【图像词典】将 toc.txt 和 index.txt 合并成 index_all.txt 文件")
    print("\n(三) 还原词典")
    print(Fore.CYAN + "  30" + Fore.RESET + ".还原词典" + Fore.YELLOW + " (仅支持还原 AMB 1.4 以上版本词典)")
    print(Fore.CYAN + "  31" + Fore.RESET + ".【图像词典】将 index_all.txt 处理成 toc_all.txt 文件")
    print("\n(四) 其他")
    print(Fore.CYAN + "  0" + Fore.RESET + ".退出程序")


if __name__ == '__main__':
    init(autoreset=True)
    # 程序开始
    print(Fore.CYAN + "欢迎使用 AutoMdxBuilder, 下面是功能选单:" + Fore.RESET)
    while True:
        print_menu()
        try:
            sel = int(input('\n请输入数字: '))
        except ValueError:
            sel = 0
        # 执行选择
        if sel in range(1, 50):
            print('\n------------------')
            amb = AutoMdxBuilder()
            amb.auto_processing(sel)
            print('\n\n------------------------------------')
            if input(Fore.CYAN + "回车退出程序, 或输入 Y/y 继续使用 AMB: " + Fore.RESET) not in ['Y','y']:
                break
        else:
            break
