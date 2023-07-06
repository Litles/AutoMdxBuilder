## 功能
自动化制作 mdx 词典

> 目前只有制作图像词典（两种模板）的功能，后续有时间还会添加功能：第三种模板的图像词典，以及文本词典

## 成品预览
![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/MDict_SsKrKKq8A2.gif)

## 使用方法

### 使用步骤

这里只介绍 Windows 下使用方法（程序在其他如 Linux 平台也没测试过），有需要可自行摸索调整。

1. 安装 Python。[Python官网](https://www.python.org) 下载安装 Python 的 `.exe` 包，运行按提示安装即可；
2. 解压本工具 `AutoMdxBuilder_xx.zip` 作为工作文件夹（假如文件夹名就为 AutoMdxBuilder）；
3. 安装 Python 模块包。`cmd` 在 AutoMdxBuilder 内执行 `pip install -r requirements.txt`即可（或手动挨个安装 `requirements.txt` 中所列包也行）；
4. 准备词典制作的原材料。在 AutoMdxBuilder 文件夹内创建子文件夹 `raw`，将原材料按要求放置其内（**具体参见下面说明**）；
5. 修改好 `settings.py` 配置文件（**具体参见下面说明**）；
6. 运行 auto_mdx_builder.py （可直接双击）。词典成品产生在 `out` 子文件夹内，过程文件存放在 `_tmp` 子文件夹内以备用。

### 原材料准备说明

原材料要求全部放置在子文件夹 `raw` 内，图像词典制作需要以下材料：

* （必须）`imgs` 文件夹：存放图像文件，不限定图片格式，png、jpg 等均可；
* （必须）`index.txt` 文件：索引文件，格式`词目<TAB>页码数`（页码数是相对正文起始页的，而不是图片序号）；
* （可选）`toc.txt` 文件：目录文件，格式同`FreePic2Pdf.exe`程序的书签文件`FreePic2Pdf_bkmk.txt`；
* （可选）`syns.txt` 文件：同义词文件，或说重定向文件，格式`同义词<TAB>词目`；

> 以上 `.txt` 文本文件一律要求 **UTF-8 无 BOM** 的编码格式；

> 以上三个 `.txt` 文件需要哪几个就留哪几个，**不用到的不要出现在 raw 文件夹内**；

> 以上文件夹和文件的名称建议就按上述默认，不建议修改名称（如果一定要自定义的话下面 `settings.py` 文件也要相应修改）；

### 配置文件 `settings.py` 说明

一般修改图中绿框中的部分便可

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/sublime_text_k4SnaNJMle.png)

> 有 `toc.txt` 文件才需要设置 `self.navi_items`。`"a"`是显示文字，`"ref"`是与 `toc.txt` 中词目对应的。

## 参考

+ https://github.com/liuyug/mdict-utils
+ https://github.com/VimWei/MdxSourceBuilder
