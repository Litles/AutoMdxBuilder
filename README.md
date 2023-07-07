## 功能
自动化制作 mdx 词典工具，让词典制作者只需专注于索引，人人都可以制作自己的词典

目前支持制作以下词典：

* 图像词典（style01）：有目录（即成品预览所展示）
* 图像词典（style02）：无目录

后续还将支持以下词典：

* 图像词典（style03）：有目录，且任意层级导航
* 文本词典：……

## 成品预览
![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/final_product_demo.gif)

## 使用方法

### 使用步骤

1. 安装 Python。（Windows）从 [Python官网](https://www.python.org) 下载安装 Python 的 `.exe` 包，运行按提示安装即可；
2. 解压本工具 [AutoMdxBuilder_xx.zip](https://github.com/Litles/AutoMdxBuilder/releases) 作为工作文件夹（假设为 AutoMdxBuilder）；
3. 安装 Python 模块包。在 AutoMdxBuilder  内执行 `pip install -r requirements.txt`即可（或手动挨个安装 `requirements.txt` 中所列包也行）；
4. 准备词典制作的原材料。在 AutoMdxBuilder 文件夹内创建子文件夹 `raw`，将原材料按要求放置其内（**具体参见下面说明**）；
5. 修改好 `settings.py` 配置文件（**具体参见下面说明**）；
6. 运行 auto_mdx_builder.py （可直接双击）。词典成品产生在 `out` 子文件夹内，过程文件存放在 `_tmp` 子文件夹内以备用。

### 原材料准备简述

原材料要求全部放置在子文件夹 `raw` 内，图像词典制作需要以下材料：

* （必须）`imgs` 文件夹：存放图像文件，不限定图片格式，png、jpg 等均可，也无特定的名称要求（顺序是对的就行）；
* （必须）`index.txt` 文件：索引文件，格式`词目<TAB>页码`（页码数是相对正文起始页的，而不是图片序号）；
* （可选）`toc.txt` 文件：目录文件，格式`[<TAB>*]词目<TAB>页码`，同`FreePic2Pdf.exe`程序的书签文件`FreePic2Pdf_bkmk.txt`；
* （可选）`syns.txt` 文件：同义词文件，或说重定向文件，格式`同义词<TAB>词目`；
* （可选）`info.html` 文件：词典介绍等描述；

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/work_dir_tree.png)

**注意**：

* 以上 `.txt`/`.html` 文本文件一律要求 **UTF-8 无 BOM** 的编码格式；
* 以上文件/文件夹需要哪几个就留哪几个，**不用到的不要出现在 raw 文件夹内**；
* 以上文件夹和文件的名称建议就按上述默认，不建议修改名称（如果一定要自定义的话下面 `settings.py` 文件也要相应修改）；

## 相关文件具体说明

### 配置文件 `settings.py` 说明

一般修改图中绿框中的部分便可

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/settings.png)

有 `toc.txt` 文件才需要设置 `self.navi_items`。`a`的值是显示文字，`ref`的值是与 `toc.txt` 中词目对应的。

### 索引文件 `index.txt` 说明

格式`词目<TAB>页码`（页码数是相对正文起始页的，而不是图片序号）：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/index.png)

### （可选）目录文件 `toc.txt` 说明

格式`[<TAB>*]词目<TAB>页码`，该文件也可以直接用 `FreePic2Pdf.exe` 程序从 pdf 文件中导出，格式大概像这样（行首 TAB 缩进表示层级）：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/toc.png)

### （可选）同义词文件 `syns.txt` 说明

或说重定向文件，格式`同义词<TAB>词目`：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/syns.png)

## 参考

+ https://github.com/liuyug/mdict-utils
+ https://github.com/VimWei/MdxSourceBuilder
