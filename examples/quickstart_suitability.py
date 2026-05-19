#!/usr/bin/env python3
"""
快速上手：适宜性评价

场景：评价某区域建设适宜性
运行：在 ArcGIS Pro Python 窗口中粘贴运行
依赖：Spatial Analyst 扩展许可
"""

import arcpy
from arcpy.sa import *

# ===== 环境设置 =====
arcpy.env.workspace = r"C:\Data\村庄规划.gdb"
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

# ===== 因子1：坡度（越平越适宜） =====
print("1. 计算坡度并重分类...")
dem = Raster("DEM")
slope = Slope(dem, "DEGREE")
slope_score = Reclassify(slope, "VALUE",
    RemapRange([[0, 5, 5], [5, 10, 4], [10, 15, 3], [15, 25, 2], [25, 90, 1]]))

# ===== 因子2：距道路距离（越近越适宜） =====
print("2. 计算距道路距离并重分类...")
dist_road = EucDistance("道路", cell_size=30)
dist_score = Reclassify(dist_road, "VALUE",
    RemapRange([[0, 200, 5], [200, 500, 4], [500, 1000, 3], [1000, 2000, 2], [2000, 10000, 1]]))

# ===== 因子3：距水体距离（适当距离最适宜） =====
print("3. 计算距水体距离并重分类...")
dist_water = EucDistance("水域", cell_size=30)
water_score = Reclassify(dist_water, "VALUE",
    RemapRange([[0, 50, 1], [50, 200, 3], [200, 500, 5], [500, 1000, 4], [1000, 10000, 2]]))

# ===== 加权叠加（AHP权重） =====
print("4. 加权叠加...")
result = (slope_score * 0.35 + dist_score * 0.35 + water_score * 0.30)

# ===== 适宜性分级 =====
print("5. 适宜性分级...")
suitability = Reclassify(result, "VALUE",
    RemapRange([[1, 2, 1], [2, 3, 2], [3, 3.5, 3], [3.5, 4, 4], [4, 5, 5]]))

# 保存
suitability.save("建设适宜性评价")

# ===== 输出统计 =====
print("\n适宜性分级完成！")
print("1=不适宜, 2=较不适宜, 3=一般适宜, 4=较适宜, 5=适宜")
print("权重: 坡度0.35 + 道路0.35 + 水体0.30")

arcpy.CheckInExtension("Spatial")
