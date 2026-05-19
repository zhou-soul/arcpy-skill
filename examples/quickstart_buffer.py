#!/usr/bin/env python3
"""
快速上手：缓冲区分析

场景：分析村庄道路的影响范围
运行：在 ArcGIS Pro Python 窗口中粘贴运行
"""

import arcpy

# ===== 环境设置 =====
arcpy.env.workspace = r"C:\Data\村庄规划.gdb"
arcpy.env.overwriteOutput = True

# ===== 单一距离缓冲区 =====
print("1. 简单缓冲区（道路500米范围）...")
arcpy.analysis.Buffer("道路", "道路_500m缓冲", "500 Meters")

# ===== 多环缓冲区 =====
print("2. 多环缓冲区（道路100/300/500米）...")
arcpy.analysis.MultipleRingBuffer(
    "道路", 
    "道路_多环缓冲", 
    [100, 300, 500],
    "Meters", "distance", "ALL"
)

# ===== 按类型不同距离缓冲 =====
print("3. 按道路类型差异化缓冲...")
# 主干道500米、次干道300米、支路100米
road_types = {"主干道": "500 Meters", "次干道": "300 Meters", "支路": "100 Meters"}

buffers = []
for rtype, dist in road_types.items():
    temp = f"in_memory\\buf_{rtype}"
    arcpy.management.Select("道路", temp, f"TYPE = '{rtype}'")
    arcpy.analysis.Buffer(temp, f"道路_{rtype}_缓冲", dist)
    buffers.append(f"道路_{rtype}_缓冲")
    print(f"  {rtype}: {dist}")

# 合并
arcpy.management.Merge(buffers, "道路_分类缓冲_合并")

# ===== 统计缓冲区内用地 =====
print("4. 统计缓冲区内各类用地面积...")
arcpy.analysis.SpatialJoin(
    "用地斑块", "道路_500m缓冲", "缓冲区内用地",
    join_operation="JOIN_ONE_TO_ONE",
    match_option="WITHIN"
)

print("\n缓冲区分析完成！查看结果图层。")
