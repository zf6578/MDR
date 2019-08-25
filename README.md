# MDR-Tree

**Python for MDR-tree construction**

Design of Efficient Storage Organization and Query Algorithm Based on Two-dimensional Geospatial Big Data

## Overview

**MDR-Tree** 由于城市交通信息的复杂性、数据量大、更新速度快等特征，当前的空间索引技术很难针对二维地理空间信息数据进行高效的检索。为了优化空间大数据下二维地理空间信息数据的存储组织结构，提高检索效率，本文提出了一种对二维地理空间信息数据进行多层切片递归的空间索引树构造算法MDR-Tree(Multiple Dimensional Recursive-Tree)



## Installation



## Features



## Documentation



## How to use MDR-Tree
**初始化** 首先我们先从OSM开源地图库中下载天津，北京以及全国地图，获取到其中的道路网数据并加载
**查询demo** 在初始化地图后，我们可以利用query_MDR_demo的代码进行数据查询，其中GPS点数据可以用我们提供的，其中pikcle文件是北京的
打点数据，TJ.csv文件是天津市的打点数据，也可以用其他任意打点数据进行区域查询，只需要输入二维经纬度坐标即可。

## More info
**对比实验** 本文采用STR-tree算法和STR-网格混合树算法作为对比算法
排序切片递归树算法 [STR, read this](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=582015&tag=1/).

STR和网格混合树算法 [STR-网格混合树，read this](https://ieeexplore.ieee.org/document/5980718/).

