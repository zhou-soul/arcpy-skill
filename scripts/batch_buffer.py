#!/usr/bin/env python3
"""
批量缓冲区分析脚本

功能：对指定要素类中的要素按不同字段值生成不同距离的缓冲区
用法：在 ArcGIS Pro Python 窗口或作为脚本工具运行

示例：
    python batch_buffer.py --input roads --output C:/Data/Output.gdb/road_buffers --field TYPE --distances "主干道=500,次干道=300,支路=100"
"""

import arcpy
import os
import sys
import argparse


def batch_buffer(input_fc, output_fc, field=None, distance_map=None, default_distance="100 Meters", dissolve="NONE"):
    """
    批量缓冲区分析
    
    参数:
        input_fc: 输入要素类
        output_fc: 输出要素类
        field: 用于确定缓冲距离的字段（可选）
        distance_map: 字段值到缓冲距离的映射，如 {"主干道": "500 Meters"}
        default_distance: 默认缓冲距离
        dissolve: 融合选项 NONE/ALL/LIST
    """
    arcpy.env.overwriteOutput = True
    
    if not field or not distance_map:
        # 统一距离缓冲
        arcpy.analysis.Buffer(input_fc, output_fc, default_distance, dissolve_option=dissolve)
        count = int(arcpy.management.GetCount(output_fc).getOutput(0))
        print(f"缓冲完成: {count} 个要素, 距离={default_distance}")
        return output_fc
    
    # 按字段值分批缓冲
    temp_buffers = []
    
    # 获取所有唯一值
    unique_values = set()
    with arcpy.da.SearchCursor(input_fc, [field]) as cursor:
        for row in cursor:
            unique_values.add(row[0])
    
    # 对每种值生成缓冲
    for value in unique_values:
        # 确定缓冲距离
        distance = distance_map.get(str(value), default_distance)
        
        # 选择要素
        temp_sel = "in_memory\\sel_" + str(value).replace(" ", "_")
        where = f"{field} = '{value}'"
        arcpy.management.Select(input_fc, temp_sel, where)
        
        # 缓冲
        temp_buf = "in_memory\\buf_" + str(value).replace(" ", "_")
        arcpy.analysis.Buffer(temp_sel, temp_buf, distance, dissolve_option=dissolve)
        
        # 添加距离字段
        arcpy.management.AddField(temp_buf, "BUF_DIST", "TEXT", field_length=50)
        arcpy.management.CalculateField(temp_buf, "BUF_DIST", f'"{distance}"', "PYTHON3")
        
        temp_buffers.append(temp_buf)
        print(f"  {value}: 缓冲距离={distance}")
    
    # 合并所有缓冲结果
    if len(temp_buffers) > 1:
        arcpy.management.Merge(temp_buffers, output_fc)
    elif len(temp_buffers) == 1:
        arcpy.management.CopyFeatures(temp_buffers[0], output_fc)
    
    # 清理内存
    for temp in temp_buffers:
        arcpy.management.Delete(temp)
        arcpy.management.Delete(temp.replace("buf_", "sel_"))
    
    count = int(arcpy.management.GetCount(output_fc).getOutput(0))
    print(f"\n批量缓冲完成: 共 {count} 个缓冲区要素")
    
    return output_fc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量缓冲区分析")
    parser.add_argument("--input", required=True, help="输入要素类路径")
    parser.add_argument("--output", required=True, help="输出要素类路径")
    parser.add_argument("--field", help="用于确定缓冲距离的字段名")
    parser.add_argument("--distances", help="字段值到距离的映射，格式: 值1=距离1,值2=距离2")
    parser.add_argument("--default", default="100 Meters", help="默认缓冲距离")
    parser.add_argument("--dissolve", default="NONE", choices=["NONE", "ALL"], help="是否融合")
    
    args = parser.parse_args()
    
    distance_map = None
    if args.distances:
        distance_map = {}
        for pair in args.distances.split(","):
            key, val = pair.split("=")
            distance_map[key.strip()] = val.strip()
    
    batch_buffer(args.input, args.output, args.field, distance_map, args.default, args.dissolve)
