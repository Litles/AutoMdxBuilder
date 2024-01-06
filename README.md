## AutoMdxBuilder 简介
**自动化制作 mdx 词典工具，人人都可以制作电子词典**（支持 Windows/macOS/Linux）

AutoMdxBuilder 是 [[Mdict]](https://www.mdict.cn/wp/?lang=en) 词典制作相关的工具，旨在自动化词典制作过程，同时降低制作门槛，该工具目前具备以下功能：

**(一) 打包/解包**

* 解包 mdx/mdd 文件。功能同 `MdxExport.exe`，支持自动解 mdd 分包，支持保留原始词条顺序。
* 打包成 mdx/mdd 文件。功能同 `MdxBuilder.exe`，支持 mdd 自动分包，支持保留原始词条顺序。

**(二) 制作词典**

* 自动化制作词典 (目前有A-D四个可选模板, 均支持多卷/集合类型）
* 一键从 PDF/pdg 等原料制作词典

**(三) 还原词典**

* 将 Mdict 词典逆向还原成原材料，方便词典的二次编辑
* 将 Mdict 词典逆向还原成 PDF

**(四) 其他实用工具**

* PDF 与图片互转
* PDF 书签管理

## 一、词典制作

### (〇) 成品预览
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

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/amb_folder.png)

### (一) 原材料准备说明

制作不同模板的词典，所需的原材料也不尽相同，下面分模板列举：

#### 1.图像词典 (模板A)

* (必须) `imgs` 文件夹: 存放图像文件，不限定图片格式，png、jpg 等均可，也无特定的名称要求（顺序是对的就行）；
* (可选) `index.txt`: 索引文件
* (可选) `toc.txt`: 目录文件

> index 和 toc 二者中必须至少有一个, 如果你的 toc 目录文件比较全, 建议改名 toc_all 然后使用模板 B

#### 2.图像词典 (模板B)

* （必须）`imgs` 文件夹：存放图像文件，同模板A
* （可选）`index_all.txt`: 全索引文件
* （可选）`toc_all.txt`: 全目录文件

> index_all 与 toc_all 是等价的, 按偏好使用其中一种即可

#### 3.文本词典 (模板C)

* （必须）`index.txt`: 索引文件

#### 4.文本词典 (模板D)

* （必须）`index_all.txt`: 全索引文件

**【通用可选】** 除上述各模板的材料准备之外，下面两个是通用材料，制作词典可按需添加：

* （可选）`syns.txt` 文件：同义词文件；
* （可选）`info.html` 文件：词典介绍等描述。

**【注意事项】**

* 凡涉及的文本文件（如`.txt`、`.html`），一律要求 **UTF-8 无 BOM** 的编码格式；
* 原材料文件夹中只放置需要用到的文件/文件夹，**为避免误读取，不用到的不要出现在原材料文件夹内**；
* 文件夹和文件的名称就按本说明所提的，不建议自定义名称。

### (二) 配置文件 `build.toml` 参数说明

可参见 lib/build.toml 中的初始配置，已有详细注释，制作词典时可直接拷贝修改, 也可以参考 demo 词典的配置情况。下面选取其中部分作为补充说明：

* `simp_trad_flg`: 是否需要繁简通搜, 开启后将会把所有词头都添加繁体/简体跳转, 以确保 mdx 使用时能繁简通搜。 默认是 false 即单卷模式。
* `multi_volume`: 是否是多卷的, true 则开启多卷模式（需要按多卷模式来准备原材料）。默认是 false 即单卷模式。
* `body_start`: 正文起始图片序号, 比如正文第一页是 imgs 文件夹中的第 23 张图, 那么就设置为 `body_start = 23`。（多卷模式下该值是列表，比如 `body_start = [23, 19, 1, 1]`）
* `auto_split_columns`: 是否开启自动分栏, 默认值 1 表示不开启自动分栏，该功能是为方便手机等小屏移动设备的使用而设置。
* `body_end_page`: 当自动分栏开启时，该值确定了分栏的应用范围，分栏从正文第一页开启, 默认到辞书的最后一页。（多卷模式下该值是列表，比如 `body_end_page = [463, 501, 9999, 9999]`）

对于模板 A 的 `navi_items`，其中 `a` 的值是显示文字，`ref`的值是与 `toc.txt` 中词目对应的：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/settings.png)

对于文本词典模板 C,D 中的 `add_headwords` 选项, 词条内容如果已经带有标题，可以将该项设置为 false。


## 二、相关文件格式

### 索引文件 `index.txt`

格式`词目<TAB>页码`（页码数是相对正文起始页的，而不是图片序号）：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/index.png)

> 如果是多卷模式, 则页码需要带分卷号前缀 `[n]` 以标识分卷（第一卷 `[1]` 可以省略不写），比如词条『刘备』是在第4卷第3页, 那么索引应写作 `刘备<TAB>[4]3`；

如果是制作文本词典 (模板C)，用到的文件也叫 `index.txt`，只不过其中的 **页码** 换成了 **词条正文**，格式为 `词目<TAB>词条正文` 。

### 目录文件 `toc.txt`

格式`[<TAB>*]词目<TAB>页码`，格式大概像这样（行首 TAB 缩进表层级）：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/toc.png)

格式同程序 `FreePic2Pdf.exe` 的书签文件`FreePic2Pdf_bkmk.txt`，因此也可以直接用 `FreePic2Pdf.exe` 程序从 pdf 文件中导出。

> 与索引文件一样，多卷模式下, 页码需要带分卷号前缀 `[n]` 以标识分卷（第一卷 `[1]` 可以省略不写）

### 全索引文件 `index_all.txt`

是 `index.txt` 的拓展，格式同样是 `词目<TAB>页码` ，只不过 `index_all.txt` 是把 `toc.txt` 也并入进来，并且是严格有序的。

其中目录（章节）的词目要加 `【L<层级>】` 前缀标识，比如顶级章节“正文”前缀就是 `【L0】正文` ，“正文”的下一级“史前篇”的前缀就是 `【L1】史前篇` 。

> 章节词目可以没有对应页码，但要保留 `<TAB>` 

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/index_all.png)

> 与索引文件一样，多卷模式下, 页码需要带分卷号前缀 `[n]` 以标识分卷（第一卷 `[1]` 可以省略不写）

如果是制作文本词典 (模板D)，用到的文件也叫 `index_all.txt`，只不过其中的 **页码** 换成了 **词条正文**，格式为 `词目<TAB>词条正文` 。

### 同义词文件 `syns.txt`

或说重定向文件，格式`同义词<TAB>词目`：

![img](https://github.com/Litles/AutoMdxBuilder/blob/main/images/syns.png)

## 三、多卷模式补充说明

当在 `build.toml` 中设置 `multi_volume = true` 时，将会按照多卷模式制作词典，这时原材料的命名相比一般模式会有些许不同，下面按模板列举：

图像词典模板 A,B 在多卷模式下, 首先图像文件夹结构将是 imgs/vol_01, imgs/vol_02, imgs/vol_03... 即分卷子文件夹名称需加 vol_00 前缀

* 模板 A: 除可以使用全局索引/目录文件 index.txt, toc.txt 外，也可以使用分卷文件 index_01.txt, index_02.txt ... 和 toc_01.txt, toc_02.txt ... （分卷文件中的页码无需加`[n]`前缀）
* 模板 B: 除可以使用全局全索引/全目录文件 index_all.txt/toc_all.txt 外，也可以使用分卷文件 index_all_01.txt, index_all_02.txt ... 或 toc_all_01.txt, toc_all_02.txt ... （分卷文件中的页码无需加`[n]`前缀）
* 模板 D: 同模板 B, 不过因为没有页码, 所以分卷文件和全局文件无区别

> 还可以在目录文件、全索引或全目录文件名上标识分卷名称（这样就不用在 `build.toml` 中设置 vol_names 项）, 比如 toc_01_军事卷、 toc_all_01_军事卷.txt 或 index_all_01_军事卷.txt, 这样, 程序将会从文件名中读取卷名

## 四、其他功能简介

## 参考

+ https://github.com/liuyug/mdict-utils
+ https://github.com/VimWei/MdxSourceBuilder
