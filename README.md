## AutoMdxBuilder
自动化制作 mdx 词典工具，人人都可以制作电子词典

### 功能
目前具备以下功能：

**(一) 打包/解包**

* 解包 mdx/mdd 文件。功能同 `MdxExport.exe`，另支持自动批量。
* 打包成 mdx 文件。功能同 `MdxBuilder.exe` 。
* 打包成 mdd 文件。功能同 `MdxBuilder.exe`，另支持自动批量。

**(二) 制作词典**

* 制作图像词典 (模板A，朴素版)
* 制作图像词典 (模板B，导航版)
* 制作文本词典 (模板C，朴素版)
* 制作文本词典 (模板D，导航版)

## 成品预览
#### 1.图像词典 (模板A，朴素版)
![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/img_dict_atmpl.gif)

#### 2.图像词典 (模板B，导航版)
![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/img_dict_btmpl.gif)

#### 3.文本词典 (模板C，朴素版)
![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/text_dict_ctmpl.png)

#### 4.文本词典 (模板D，导航版)
![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/text_dict_dtmpl.gif)

## 使用方法

### 使用步骤

#### 1.准备工具
1. 安装 Python。（Windows）从 [Python官网](https://www.python.org) 下载安装 Python 的 `.exe` 包，运行按提示安装即可；
2. 解压本工具 [AutoMdxBuilder_xx.zip](https://github.com/Litles/AutoMdxBuilder/releases) 作为工作文件夹（假设为 AutoMdxBuilder）；
3. 安装 Python 模块包。在 AutoMdxBuilder  内执行 `pip install -r requirements.txt`即可（或手动挨个安装 `requirements.txt` 中所列包也行）；

#### 2.制作词典
4. 准备词典制作所需的原材料。在 AutoMdxBuilder 文件夹内创建子文件夹 `raw`，将原材料按要求放置其内（**具体参见下面说明**）；
5. 修改好 `settings.py` 配置文件（**具体参见下面说明**）；
6. 运行 auto_mdx_builder.py （可直接双击），按对话框提示输入。词典成品将生成在 `out` 子文件夹内，过程文件存放在 `_tmp` 子文件夹内以备用。

### 原材料准备说明

制作词典才需要在子文件夹 `raw` 内放置原材料，如果是使用程序的其他功能则不涉及。制作不同模板的词典，所需的原材料也不尽相同，下面分模板说明：

#### 通用说明

**通用可选**

* （可选）`syns.txt` 文件：同义词文件，或说重定向文件，格式`同义词<TAB>词目`；
* （可选）`info.html` 文件：词典介绍等描述；

**注意事项**

* 凡涉及的文本文件（如`.txt`、`.html`），一律要求 **UTF-8 无 BOM** 的编码格式；
* `raw` 文件夹中只放置需要用到的文件/文件夹，**不用到的不要出现在 raw 文件夹内**；
* 文件夹和文件的名称就按本说明所提的，不建议自定义名称。

#### 1.图像词典 (模板A)

* （必须）`imgs` 文件夹：存放图像文件，不限定图片格式，png、jpg 等均可，也无特定的名称要求（顺序是对的就行）；
* （必须）`index.txt` 文件：索引文件
* （可选）`toc.txt` 文件：目录文件

#### 2.图像词典 (模板B)

* （必须）`imgs` 文件夹：存放图像文件，同模板A
* （必须）`index_all.txt` 文件：全索引文件

#### 3.文本词典 (模板C)

* （必须）`index.txt` 文件：索引文件

#### 4.文本词典 (模板D)

* （必须）`index_all.txt` 文件：全索引文件

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/work_dir_tree.png)

## 相关文件具体说明

### 配置文件 `settings.py`

一般修改图中绿框中的部分便可

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/settings.png)

有 `toc.txt` 文件才需要设置 `self.navi_items`。`a`的值是显示文字，`ref`的值是与 `toc.txt` 中词目对应的。

### 索引文件 `index.txt`

格式`词目<TAB>页码`（页码数是相对正文起始页的，而不是图片序号）：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/index.png)

如果是制作文本词典 (模板C)，用到的文件也叫 `index.txt`，只不过其中的 **页码** 换成了 **词条正文**，格式为 `词目<TAB>词条正文` 。

### 全索引文件 `index_all.txt`

是 `index.txt` 的拓展，格式同样是 `词目<TAB>页码` ，只不过 `index_all.txt` 是把 `toc.txt` 也并入进来，并且是严格有序的。

其中目录（章节）的词目要加 `【L<层级>】` 前缀标识，比如顶级章节“正文”前缀就是 `【L0】正文` ，“正文”的下一级“史前篇”的前缀就是 `【L1】史前篇` 。

> 章节词目可以没有对应页码，但要保留 `<TAB>` 

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/index_all.png)

如果是制作文本词典 (模板D)，用到的文件也叫 `index_all.txt`，只不过其中的 **页码** 换成了 **词条正文**，格式为 `词目<TAB>词条正文` 。

### 目录文件 `toc.txt`

格式`[<TAB>*]词目<TAB>页码`，格式大概像这样（行首 TAB 缩进表层级）：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/toc.png)

格式同程序 `FreePic2Pdf.exe` 的书签文件`FreePic2Pdf_bkmk.txt`，因此也可以直接用 `FreePic2Pdf.exe` 程序从 pdf 文件中导出。

### 同义词文件 `syns.txt`

或说重定向文件，格式`同义词<TAB>词目`：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/syns.png)

## 参考

+ https://github.com/liuyug/mdict-utils
+ https://github.com/VimWei/MdxSourceBuilder
