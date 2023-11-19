## AutoMdxBuilder
**自动化制作 mdx 词典工具，人人都可以制作电子词典**

AutoMdxBuilder 是 [[Mdict]](https://www.mdict.cn/wp/?lang=en) 词典制作相关的工具，旨在自动化词典制作过程，同时降低制作门槛，该工具目前具备以下功能：

**(一) 打包/解包**

* 解包 mdx/mdd 文件。功能同 `MdxExport.exe`，支持自动解 mdd 分包，支持保留原始词条顺序。
* 打包成 mdx/mdd 文件。功能同 `MdxBuilder.exe`，支持 mdd 自动分包，支持保留原始词条顺序。

**(二) 制作词典**

* 自动化制作词典 (目前有A-D四个可选模板）
* 一键从 PDF/pdg 等原料制作词典

**(三) 还原词典**

* 将 Mdict 词典逆向还原成原材料，方便词典的二次编辑
* 将 Mdict 词典逆向还原成 PDF

**(四) 其他实用工具**

* PDF 与图片互转
* PDF 书签管理

## 词典制作

### 成品预览
#### 图像词典 (模板A，朴素版)
![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/img_dict_atmpl.gif)

#### 图像词典 (模板B，导航版)
![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/img_dict_btmpl.gif)

#### 文本词典 (模板C，朴素版)
![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/text_dict_ctmpl.png)

#### 文本词典 (模板D，导航版)
![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/text_dict_dtmpl.gif)

### 词典制作概述

使用词典制作功能时，需要准备好原材料，将所需要的材料单独用一个文件夹收纳（不妨称它为 amb 文件夹）。词典制作的配置信息写在 build.toml 文件中，同样也放置在该文件夹中。下面是一个示例的 amb 文件夹结构：

> AutoMdxBuilder 1.4 及以上版本已不再需要修改 settings.py（取而代之的是 build.toml），原材料文件夹也独立于程序之外，也无名称要求

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/amb_folder.png)

### 原材料准备具体说明

制作不同模板的词典，所需的原材料也不尽相同，下面分模板列举：

#### 图像词典 (模板A)

* （必须）`imgs` 文件夹：存放图像文件，不限定图片格式，png、jpg 等均可，也无特定的名称要求（顺序是对的就行）；
* （必须）`index.txt` 文件：索引文件
* （可选）`toc.txt` 文件：目录文件

#### 图像词典 (模板B)

* （必须）`imgs` 文件夹：存放图像文件，同模板A
* （必须）`index_all.txt` 文件：全索引文件

#### 文本词典 (模板C)

* （必须）`index.txt` 文件：索引文件

#### 文本词典 (模板D)

* （必须）`index_all.txt` 文件：全索引文件

**【通用可选】** 除上述各模板的材料准备之外，下面两个是通用材料，制作词典可按需添加：

* （可选）`syns.txt` 文件：同义词文件；
* （可选）`info.html` 文件：词典介绍等描述。

**【注意事项】**

* 凡涉及的文本文件（如`.txt`、`.html`），一律要求 **UTF-8 无 BOM** 的编码格式；
* 原材料文件夹中只放置需要用到的文件/文件夹，**为避免误读取，不用到的不要出现在原材料文件夹内**；
* 文件夹和文件的名称就按本说明所提的，不建议自定义名称。

## 相关文件说明

### 配置文件 `build.toml`

参见 demo 中的样板，已有详细说明。对于模板 A 的 `self.navi_items`，其中 `a` 的值是显示文字，`ref`的值是与 `toc.txt` 中词目对应的：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/settings.png)

### 索引文件 `index.txt`

格式`词目<TAB>页码`（页码数是相对正文起始页的，而不是图片序号）：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/index.png)

如果是制作文本词典 (模板C)，用到的文件也叫 `index.txt`，只不过其中的 **页码** 换成了 **词条正文**，格式为 `词目<TAB>词条正文` 。

### 目录文件 `toc.txt`

格式`[<TAB>*]词目<TAB>页码`，格式大概像这样（行首 TAB 缩进表层级）：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/toc.png)

格式同程序 `FreePic2Pdf.exe` 的书签文件`FreePic2Pdf_bkmk.txt`，因此也可以直接用 `FreePic2Pdf.exe` 程序从 pdf 文件中导出。

### 全索引文件 `index_all.txt`

是 `index.txt` 的拓展，格式同样是 `词目<TAB>页码` ，只不过 `index_all.txt` 是把 `toc.txt` 也并入进来，并且是严格有序的。

其中目录（章节）的词目要加 `【L<层级>】` 前缀标识，比如顶级章节“正文”前缀就是 `【L0】正文` ，“正文”的下一级“史前篇”的前缀就是 `【L1】史前篇` 。

> 章节词目可以没有对应页码，但要保留 `<TAB>` 

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/index_all.png)

如果是制作文本词典 (模板D)，用到的文件也叫 `index_all.txt`，只不过其中的 **页码** 换成了 **词条正文**，格式为 `词目<TAB>词条正文` 。

### 同义词文件 `syns.txt`

或说重定向文件，格式`同义词<TAB>词目`：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/syns.png)

## 参考

+ https://github.com/liuyug/mdict-utils
+ https://github.com/VimWei/MdxSourceBuilder
