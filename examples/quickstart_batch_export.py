#!/usr/bin/env python3
"""
快速上手：批量出图

场景：按村庄批量导出规划图
运行：在 ArcGIS Pro Python 窗口中粘贴运行
前提：项目中已有含空间地图系列的布局
"""

import arcpy
import os

# ===== 配置 =====
output_dir = r"C:\Output\村庄规划图"
os.makedirs(output_dir, exist_ok=True)

# ===== 获取当前项目 =====
aprx = arcpy.mp.ArcGISProject("CURRENT")

# ===== 方式1：导出所有布局 =====
print("1. 导出所有布局为PDF...")
for layout in aprx.listLayouts():
    safe_name = layout.name.replace(" ", "_").replace("/", "-")
    out_pdf = os.path.join(output_dir, f"{safe_name}.pdf")
    layout.exportToPDF(out_pdf, resolution=300)
    print(f"  ✓ {layout.name}")

# ===== 方式2：利用空间地图系列批量出图 =====
print("\n2. 利用地图系列批量出图...")
for layout in aprx.listLayouts():
    if layout.mapSeries and layout.mapSeries.enabled:
        ms = layout.mapSeries
        print(f"  布局 '{layout.name}' 有 {ms.pageCount} 页")
        
        for page_num in range(1, ms.pageCount + 1):
            ms.currentPageNumber = page_num
            # 获取当前页的名称（从索引图层读取）
            page_name = ms.pageRow.NAME if hasattr(ms.pageRow, 'NAME') else f"page_{page_num}"
            # 清理文件名
            safe_page = str(page_name).replace(" ", "_").replace("/", "-").replace("\\", "-")
            out_pdf = os.path.join(output_dir, f"{safe_page}.pdf")
            layout.exportToPDF(out_pdf, resolution=200)
            print(f"    ✓ 第{page_num}页: {page_name}")

# ===== 方式3：修改文本后批量导出 =====
print("\n3. 替换动态文本后导出...")
for layout in aprx.listLayouts():
    for elm in layout.listElements("TEXT_ELEMENT"):
        # 替换标题中的占位符
        if "{村名}" in elm.text:
            elm.text = elm.text.replace("{村名}", "永兴村")
        if "{年份}" in elm.text:
            elm.text = elm.text.replace("{年份}", "2025")
    
    out_pdf = os.path.join(output_dir, f"{layout.name}_替换后.pdf")
    layout.exportToPDF(out_pdf, resolution=300)
    print(f"  ✓ {layout.name}")

aprx.save()
print(f"\n批量出图完成！输出目录: {output_dir}")
