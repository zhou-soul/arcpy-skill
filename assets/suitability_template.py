#!/usr/bin/env python3
"""
适宜性评价完整脚本模板

功能：多因子加权叠加适宜性评价
典型应用：建设用地适宜性评价、农业适宜性评价、生态敏感性评价

使用方式：
1. 修改下方 CONFIG 区域的参数
2. 在 ArcGIS Pro Python 窗口运行，或作为脚本工具

依赖：ArcGIS Pro + Spatial Analyst 扩展许可
"""

import arcpy
from arcpy.sa import *
import os

# ===================== 配置区域（根据项目修改） =====================

CONFIG = {
    # 工作空间
    "workspace": r"C:\Data\Project.gdb",
    "output_dir": r"C:\Output",
    
    # 评价因子定义：[因子名称, 栅格路径/数据集名, 权重, 重分类规则]
    # 重分类规则：RemapRange([[起, 止, 分值], ...])
    "factors": [
        {
            "name": "坡度",
            "source": "slope",
            "weight": 0.30,
            "reclass": [[0, 5, 5], [5, 10, 4], [10, 15, 3], [15, 25, 2], [25, 90, 1]],
            "reclass_type": "RANGE",  # RANGE 或 VALUE
        },
        {
            "name": "距道路距离",
            "source": "dist_road",
            "weight": 0.25,
            "reclass": [[0, 200, 5], [200, 500, 4], [500, 1000, 3], [1000, 2000, 2], [2000, 10000, 1]],
            "reclass_type": "RANGE",
        },
        {
            "name": "高程",
            "source": "dem",
            "weight": 0.20,
            "reclass": [[0, 300, 5], [300, 500, 4], [500, 800, 3], [800, 1200, 2], [1200, 5000, 1]],
            "reclass_type": "RANGE",
        },
        {
            "name": "土地利用",
            "source": "landuse",
            "weight": 0.25,
            "reclass": [[11, 1], [12, 2], [21, 3], [31, 4], [41, 5]],
            "reclass_type": "VALUE",
        },
    ],
    
    # 适宜性分级标准
    "classification": [[1, 2, "不适宜"], [2, 3, "较不适宜"], [3, 3.5, "一般适宜"], [3.5, 4, "较适宜"], [4, 5, "适宜"]],
    
    # 输出名称
    "output_name": "suitability_result",
}

# ===================== 执行区域 =====================

def run_suitability_analysis(config):
    """执行适宜性评价"""
    
    # 1. 环境设置
    arcpy.env.workspace = config["workspace"]
    arcpy.env.overwriteOutput = True
    
    # 2. 检出许可
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
    else:
        raise RuntimeError("需要 Spatial Analyst 许可证")
    
    print("=" * 50)
    print("适宜性评价分析")
    print("=" * 50)
    
    # 3. 因子重分类与加权
    reclassified = []
    weights = []
    
    for factor in config["factors"]:
        print(f"\n处理因子: {factor['name']} (权重={factor['weight']})")
        
        raster = Raster(factor["source"])
        
        # 重分类
        if factor["reclass_type"] == "RANGE":
            remap = RemapRange(factor["reclass"])
        else:
            remap = RemapValue(factor["reclass"])
        
        reclassed = Reclassify(raster, "VALUE", remap)
        reclassified.append(reclassed)
        weights.append(factor["weight"])
        
        print(f"  重分类完成")
    
    # 4. 加权叠加
    print("\n执行加权叠加...")
    weighted_sum = sum(r * w for r, w in zip(reclassified, weights))
    
    # 5. 分类输出
    print("进行适宜性分级...")
    class_remap = RemapRange([[c[0], c[1], i+1] for i, c in enumerate(config["classification"])])
    classified = Reclassify(weighted_sum, "VALUE", class_remap)
    
    # 6. 保存结果
    output_path = os.path.join(config["output_dir"], f"{config['output_name']}.tif")
    classified.save(output_path)
    
    # 7. 统计各等级面积
    print(f"\n{'='*50}")
    print("适宜性分级结果")
    print(f"{'='*50}")
    
    total_area = 0
    for i, cls in enumerate(config["classification"]):
        level_raster = Con(classified == i + 1, 1)
        area = (ZonalStatistics(level_raster, "VALUE", level_raster, "SUM") * 
                arcpy.env.cellSize * arcpy.env.cellSize) if level_raster is not None else 0
        
        # 简化面积统计
        count_result = arcpy.management.GetCount(
            arcpy.conversion.RasterToPolygon(level_raster, "in_memory\\temp_poly", "NO_SIMPLIFY")
        )
        
        level_name = cls[2]
        print(f"  等级{i+1} ({level_name}): 分值范围 {cls[0]}-{cls[1]}")
    
    # 8. 归还许可
    arcpy.CheckInExtension("Spatial")
    
    print(f"\n分析完成！结果已保存至: {output_path}")
    return output_path


if __name__ == "__main__":
    run_suitability_analysis(CONFIG)
