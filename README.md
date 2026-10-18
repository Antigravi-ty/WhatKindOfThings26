# 图书高清封面资源库 (Book Covers HD Collection)

本项目整理并重构了原本低清晰度的经典机械工程教材封面，提供超高分辨率（最高达 8850×3000）的官方原版封面、展开印刷封面、立体样机效果图及高质量修复版本。

---

## 📚 封面清单与下载索引

| 序号 | 原始哈希文件名 | 书名与版本 | 主编 / 编者 | 出版社 | ISBN | 仓库提供最高规格 | 官方/高清下载链接 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `68f40fdc20cab493d8f58fbd12cbfa05.jpg` | **《机械工程图学习题集（第四版）》** | 谷艳华、闫冠、林玉祥 主编<br>张秀芝、王瑜雪 副主编<br>侯洪生 主审 | 科学出版社 | 978-7-03-048929-6 | **8850×3000** (全展开印刷级封套)<br>**4350×3000** (超清正封面)<br>**1701×1000** (高清3D立体样机) | [科学出版社全展开原图](http://www.ecsponline.com/book/2016/zk/9787030489296-004024-cv_pm-v001.jpg)<br>[3D立体原图](http://www.ecsponline.com/book/2016/lt/9787030489296-004024-fcv_lt-v001.jpg)<br>[300DPI印刷封面](http://www.ecsponline.com/book/2016/f300/9787030489296-004024-fcv_pm300-v001.jpg) |
| **2** | `b7c0b1271bf72e462537eca0b2393a4a.jpg` | **《机械工程图学（第五版）》<br>&《机械工程图学习题集（第五版）》** | 侯洪生、闫冠、谷艳华 主编（教材）<br>谷艳华、闫冠、文立阁 主编（习题集） | 科学出版社 | 978-7-03-072672-8<br>978-7-03-072666-7 | **4477×3000** (教材展开印刷封套)<br>**4394×3000** (习题集展开印刷封套)<br>**1300×1100** (高清双书立体合影) | [教材展开原图](http://www.ecsponline.com/book_2019/2022/zk/9787030726728-005031-cv_pm.jpg)<br>[习题集展开原图](http://www.ecsponline.com/book_2019/2022/zk/9787030726667-005032-cv_pm.jpg)<br>[教材3D立面](http://www.ecsponline.com/book_2019/2022/lt/9787030726728-005031-fcv_lt.jpg)<br>[习题集3D立面](http://www.ecsponline.com/book_2019/2022/lt/9787030726667-005032-fcv_lt.jpg) |
| **3** | `a26dcf56e082ce1762e9cc11b0d5670a.jpg` | **《机械制造技术基础（第2版）》** | 于骏一、邹青 主编 | 机械工业出版社 | 978-7-111-13114-4 | **1692×2400** (去块效应边缘保真超分)<br>**564×800** (机工教育官网正版) | [机工教育服务网官方图](http://s.cmpedu.com/images/upload/2019/4/1/1558376407690(FM800).jpg)<br>[天猫旗舰店商品图](https://img.alicdn.com/imgextra/i4/3446196188/O1CN01oul6dz1va9pwVdq1H_!!0-item_pic.jpg) |
| **4** | `85df3b6e93cf3b5144eacc883578d671.jpg` | **《机械设计（修订版）》** | 谭庆昌、赵洪志 主编<br>吴鹿鸣 审阅 | 高等教育出版社 | 978-7-04-023006-2 | **2400×2400** (Lanczos-4 超分重构与去噪锐化) | [高教社检索入口](https://xuanshu.hep.com.cn/) |
| **5** | `e104b54ec521cbcf75c29557ef71e7eb.jpg` | **《机械制造技术基础（第1版）》** | 于骏一、邹青 主编 | 机械工业出版社 | 7-111-13114-X /<br>978-7-111-13114-4 | **1668×2400** (双边滤波去摩尔纹与文本边缘增强) | [机工出版社服务平台](http://www.cmpedu.com/) |

---

## 📁 目录文件结构

```text
.
├── README.md
├── campus_skyline_photo_reconstructed/  # 【最新】真实照片三维浮雕重构版天际线 (2730x1535)
│   ├── 00_reconstructed_variants_overview.jpg
│   ├── 01_user_panorama_golden_relief.jpg
│   ├── 02_bilateral_gala_stage.jpg
│   ├── 03_deep_perspective_tiered.jpg
│   ├── 04_golden_night_illuminated.jpg
│   ├── 05_high_relief_papercraft_emboss.jpg
│   └── README.md
├── campus_skyline_variants/            # 学院建筑几何三维白模天际线合集 (2730x1535)
│   ├── 00_all_variants_overview.jpg
│   ├── 01_variant_bilateral_gala.jpg / .png
│   └── ...
├── scripts/                            # 光影追踪、法线浮雕重构与舞台渲染源码
└── covers/                             # 经典机械教材超清封面与立体样机库
```

---

## 🏛️ 真实照片三维浮雕重构版天际线 (Photo-Reconstructed Skyline Collection)

基于真实校区建筑摄影素材与用户提供的连贯天际线拼接版（`1829D43A869E2327B32B2A7CBC7AC64F.jpg`），采用 **Photometric Surface Normal Relief Reconstruction** 全新管线，**100% 保留真实摄影门窗网格、立柱、大台阶与遮阳百叶等标志性特征**，彻底解决前序版本“太平面、缺乏层次”的问题（详见 [campus_skyline_photo_reconstructed/README.md](campus_skyline_photo_reconstructed/README.md)）：

| Variant | 构图与视觉主题 | 核心特色与辨识度 | 预览与下载 |
| :--- | :--- | :--- | :--- |
| **Variant 01** | **用户全景重构 - 香槟立体浮雕** | 忠实还原用户上传全景序列：材料馆 $\to$ 基础实验馆大台阶 $\to$ 链传动所百叶 $\to$ 汽车拖拉机学院旧址圆角楼 | [01_user_panorama_golden_relief.jpg](campus_skyline_photo_reconstructed/01_user_panorama_golden_relief.jpg) |
| **Variant 02** | **盛典双侧合围舞台天际线** | 致敬参考图经典对称剧场展翼，左翼历史底蕴+右翼现代科研，中央开阔舞台空间与璀璨星芒 | [02_bilateral_gala_stage.jpg](campus_skyline_photo_reconstructed/02_bilateral_gala_stage.jpg) |
| **Variant 03** | **纵深三层透视与工科烟囱全景** | 建立远景（工科基地高耸烟囱+机械系旧址）、中景（链传动所+实训中心）、近景前锋（基础实验馆大台阶），多层接触阴影 | [03_deep_perspective_tiered.jpg](campus_skyline_photo_reconstructed/03_deep_perspective_tiered.jpg) |
| **Variant 04** | **盛典夜景发光视窗与探照光束** | 真实摄影窗扇注入温暖琥珀金内透发光，地面 4 组柔和舞台探照追光束斜掠过浮雕表面 | [04_golden_night_illuminated.jpg](campus_skyline_photo_reconstructed/04_golden_night_illuminated.jpg) |
| **Variant 05** | **学院标志性高浮雕与烫金折边** | 巍峨长卷汇聚五大标志性地标，山墙与立柱折边流光溢彩金属烫金高光，折纸纸雕立体触感 | [05_high_relief_papercraft_emboss.jpg](campus_skyline_photo_reconstructed/05_high_relief_papercraft_emboss.jpg) |

---

## 🏛️ 学院建筑几何立体剪影天际线 (Campus Skyline Procedural Variants)

基于学院历史与现代建筑素材，重构为类似参考图（3D几何白模剪影、金色褶皱舞台墙、地平线光带、镜面反光地板）的 8 款 2.5K 超高清视觉（详见 [campus_skyline_variants/README.md](campus_skyline_variants/README.md)）：

| Variant | 风格与构图主题 | 核心特色 | 预览与下载 |
| :--- | :--- | :--- | :--- |
| **Variant 1** | **经典双侧对流庆典展翼构图** | 忠实于参考图双侧展翼，左侧历史底蕴，右侧现代工科，中央开阔舞台 | [01_variant_bilateral_gala.jpg](campus_skyline_variants/01_variant_bilateral_gala.jpg) |
| **Variant 2** | **全景连贯天际线横卷构图** | 历史至现代建筑全景长卷，由三教门廊形成中央人文过渡，连绵起伏 | [02_variant_panoramic_skyline.jpg](campus_skyline_variants/02_variant_panoramic_skyline.jpg) |
| **Variant 3** | **殿堂式主楼向心聚焦构图** | 基础实验馆大台阶居中放大 1.35x，天幕光束聚焦，两侧建筑对称拱卫 | [03_variant_monumental_center.jpg](campus_skyline_variants/03_variant_monumental_center.jpg) |
| **Variant 4** | **多层次景深立体沙盘展台构图** | 近/中/远三重物理景深层级，微缩模型物理柔和投影与空间层次感 | [04_variant_physical_sandtable.jpg](campus_skyline_variants/04_variant_physical_sandtable.jpg) |
| **Variant 5** | **鎏金夜景泛光与发光视窗庆典版** | 温暖金黄内透发光视窗、建筑后方 4 组冲天舞台追光光束与绚烂星芒 | [05_variant_golden_luminous_night.jpg](campus_skyline_variants/05_variant_golden_luminous_night.jpg) |
| **Variant 6** | **极致极简纯净纸雕浮雕构图** | 纯净极简象牙白折纸雕塑质感，洗练几何轮廓，大面积留白的高级感 | [06_variant_minimalist_papercraft.jpg](campus_skyline_variants/06_variant_minimalist_papercraft.jpg) |
| **Variant 7** | **华章庆典金色光晕与全景大师构图** | 中心金色同心光弧与放射辉光，融合所有校区地标的全要素庆典视觉 | [07_variant_anniversary_grandeur.jpg](campus_skyline_variants/07_variant_anniversary_grandeur.jpg) |
| **Variant 8** | **烫金立体浮雕与金属微光天际线** | 烫金立体精工微光线框，边缘金箔流光勾勒，高品质浮雕质感 | [08_variant_gold_foil_emboss.jpg](campus_skyline_variants/08_variant_gold_foil_emboss.jpg) |


