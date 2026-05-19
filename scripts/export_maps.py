#!/usr/bin/env python3
"""
批量导出地图脚本

功能：批量导出 ArcGIS Pro 项目中的布局为 PDF/PNG
用法：
    # 导出所有布局为PDF
    python export_maps.py --aprx C:/Project/Map.aprx --output C:/Output/ --format pdf --dpi 300
    
    # 导出指定布局
    python export_maps.py --aprx CURRENT --layout "村庄规划" --format png --dpi 200
"""

import arcpy
import os
import argparse


def export_maps(aprx_path, output_dir, layout_name=None, fmt="pdf", dpi=300):
    """
    批量导出地图
    
    参数:
        aprx_path: 项目路径（"CURRENT" 或 .aprx 文件路径）
        output_dir: 输出目录
        layout_name: 指定布局名称（None=全部）
        fmt: 输出格式 pdf/png/jpeg/tiff
        dpi: 分辨率
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 打开项目
    aprx = arcpy.mp.ArcGISProject(aprx_path)
    
    # 获取布局列表
    if layout_name:
        layouts = [lyt for lyt in aprx.listLayouts() if layout_name in lyt.name]
        if not layouts:
            print(f"未找到包含 '{layout_name}' 的布局")
            return
    else:
        layouts = aprx.listLayouts()
    
    print(f"找到 {len(layouts)} 个布局待导出\n")
    
    # 导出函数映射
    export_funcs = {
        "pdf": lambda lyt, path: lyt.exportToPDF(path, resolution=dpi),
        "png": lambda lyt, path: lyt.exportToPNG(path, resolution=dpi),
        "jpeg": lambda lyt, path: lyt.exportToJPEG(path, resolution=dpi),
        "tiff": lambda lyt, path: lyt.exportToTIFF(path, resolution=dpi),
    }
    
    ext_map = {"pdf": ".pdf", "png": ".png", "jpeg": ".jpg", "tiff": ".tif"}
    
    export_func = export_funcs.get(fmt.lower())
    if not export_func:
        print(f"不支持的格式: {fmt}")
        return
    
    # 批量导出
    for i, lyt in enumerate(layouts, 1):
        # 清理文件名中的特殊字符
        safe_name = lyt.name.replace(" ", "_").replace("/", "-").replace("\\", "-")
        out_path = os.path.join(output_dir, f"{safe_name}{ext_map[fmt.lower()]}")
        
        try:
            export_func(lyt, out_path)
            size_mb = os.path.getsize(out_path) / (1024 * 1024)
            print(f"[{i}/{len(layouts)}] ✓ {lyt.name} → {out_path} ({size_mb:.1f}MB)")
        except Exception as e:
            print(f"[{i}/{len(layouts)}] ✗ {lyt.name}: 导出失败 - {e}")
    
    print(f"\n导出完成！输出目录: {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量导出 ArcGIS Pro 地图")
    parser.add_argument("--aprx", default="CURRENT", help="项目路径（默认当前项目）")
    parser.add_argument("--output", required=True, help="输出目录")
    parser.add_argument("--layout", help="布局名称（含此关键词的布局）")
    parser.add_argument("--format", default="pdf", choices=["pdf", "png", "jpeg", "tiff"], help="输出格式")
    parser.add_argument("--dpi", type=int, default=300, help="分辨率（DPI）")
    
    args = parser.parse_args()
    export_maps(args.aprx, args.output, args.layout, args.format, args.dpi)
