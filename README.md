# MDR-Tree

**Python for MDR-tree construction**

基于二维地理空间大数据的高效存储组织与查询算法设计

## Functionality

**MDR-Tree** 由于城市交通信息的复杂性、数据量大、更新速度快等特征，当前的空间索引技术很难针对二维地理空间信息数据进行高效的检索。为了优化空间大数据下二维地理空间信息数据的存储组织结构，提高检索效率，本文提出了一种对二维地理空间信息数据进行多层切片递归的空间索引树构造算法MDR-Tree(Multiple Dimensional Recursive-Tree)

## How to use MDR-Tree
#### 数据介绍和获取
MDR树应用于二维地理空间数据的快速查询，在MDR树空间索引结构构建过程中需要用到道路数据，在这里我们分别用城市级数据和全国级道路网格构建索引树，数据来源于开源地图数据OSM，同时，为了测试我们的算法，我们还需要不同城市的GPS打点数据。
 * 全国道路数据可以在OSM中直接下载 http://download.geofabrik.de/asia.html 选取其中的道路数据即可
 * 城市级的道路网数据获取方式有多种，我们推荐一种利用第三方开源软件库OSMNX的方法，详情请参考osmnx手册 https://osmnx.readthedocs.io/en/stable/
 * 用于测试的GPS打点数据没有特殊的要求，只需二维坐标即可，文件中tj.csv是天津市的打点数据，5767.pikcle是北京市的打点数据
#### 安装和部署
要运行我们的MDR算法，你可能需要安装如下软件库：

Name | Description
-----|------
`latest` | `master` compiled with release flag
`latest-assertions` | `master` compiled with with release flag, assertions enabled and debug symbols
`latest-debug` | `master` compiled with debug flag
`<tag>` | specific tag compiled with release flag
`<tag>-debug` | specific tag compiled with debug flag

#### 查询测试
在初始化地图后，我们可以利用query_MDR_demo的代码进行数据查询，其中GPS点数据可以用我们提供的，其中pikcle文件是北京的
打点数据，TJ.csv文件是天津市的打点数据，也可以用其他任意打点数据进行区域查询，只需要输入二维经纬度坐标即可。
#### 许可
这个项目使用的是MIT许可类型，然而数据下载使用了 [Open Database License](http://wiki.openstreetmap.org/wiki/Open_Database_License) 
#### 作者
本项目由赵凡、赵慧慧、陈仁海、冯志勇共同完成。
## More info
#### 对比实验
本文采用STR-tree算法和STR-网格混合树算法作为对比算法，算法详情如下所示：
排序切片递归树算法 [STR, read this](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=582015&tag=1/).
STR和网格混合树算法 [STR-网格混合树，read this](https://ieeexplore.ieee.org/document/5980718/).
