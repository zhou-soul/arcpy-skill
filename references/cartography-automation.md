# 制图自动化

## 1. 批量导出地图

```python
import arcpy
import os

aprx = arcpy.mp.ArcGISProject("CURRENT")
out_dir = r"C:\Output\Maps"

# 导出所有布局为PDF
for layout in aprx.listLayouts():
    out_pdf = os.path.join(out_dir, f"{layout.name}.pdf")
    layout.exportToPDF(out_pdf, resolution=300)
    print(f"已导出: {layout.name}")

# 导出特定布局为多种格式
lyt = aprx.listLayouts("标准出图")[0]
lyt.exportToPDF(os.path.join(out_dir, "map_300dpi.pdf"), resolution=300)
lyt.exportToPNG(os.path.join(out_dir, "map_200dpi.png"), resolution=200)
lyt.exportToJPEG(os.path.join(out_dir, "map_preview.jpg"), resolution=96)
```

## 2. 自动创建布局

```python
import arcpy

aprx = arcpy.mp.ArcGISProject("CURRENT")

# 获取地图
m = aprx.listMaps("村庄规划图")[0]

# 创建新布局
lyt = aprx.createLayout(420, 297, "MILLIMETER", "A3横版")

# 添加地图框
mf = lyt.createMapFrame(m, arcpy.mp.Rectangle(10, 10, 300, 200), "主地图框")

# 添加标题
title = lyt.createText(
    arcpy.mp.Rectangle(10, 275, 300, 290),
    "TITLE",
    text="XX村村庄规划图",
    text_size=18
)

# 添加比例尺
style_item = aprx.listStyleItems("ArcGIS 2D", "SCALE_BAR", "公制比例尺 - 1")[0]
scale_bar = lyt.createScaleBar(mf, arcpy.mp.Rectangle(10, 15, 80, 25), "比例尺", style_item)

# 添加指北针
style_item_north = aprx.listStyleItems("ArcGIS 2D", "NORTH_ARROW")[0]
north_arrow = lyt.createNorthArrow(mf, arcpy.mp.Rectangle(280, 200, 295, 215), "指北针", style_item_north)

# 添加图例
legend = lyt.createLegend(mf, arcpy.mp.Rectangle(310, 50, 410, 200), "图例")

aprx.save()
print("布局创建完成")
```

## 3. 空间地图系列（批量出图）

```python
import arcpy
import os

aprx = arcpy.mp.ArcGISProject("CURRENT")
lyt = aprx.listLayouts("批量出图")[0]

# 启用空间地图系列
# 注意：需要在 ArcGIS Pro UI 中先设置好索引图层和名称字段
# 或通过 CIM 操作

# 遍历地图系列每一页导出
if lyt.mapSeries is not None:
    ms = lyt.mapSeries
    for page_num in range(1, ms.pageCount + 1):
        ms.currentPageNumber = page_num
        page_name = ms.pageRow.NAME  # 索引图层的名称字段
        out_pdf = os.path.join(r"C:\Output", f"{page_name}.pdf")
        lyt.exportToPDF(out_pdf, resolution=200)
        print(f"已导出第 {page_num} 页: {page_name}")
```

## 4. 批量修改图层符号

```python
import arcpy

aprx = arcpy.mp.ArcGISProject("CURRENT")
m = aprx.listMaps("用地规划")[0]

# 获取图层并修改渲染器
lyr = m.listLayers("用地分类")[0]

if lyr.isFeatureLayer:
    sym = lyr.symbology
    
    # 唯一值渲染
    sym.updateRenderer("UniqueValuesRenderer")
    sym.renderer.fields = ["LANDUSE_NAME"]
    
    # 修改颜色方案
    sym.renderer.colorRamp = aprx.listColorRamps("用地分类色带")[0]
    
    lyr.symbology = sym

aprx.save()
print("符号更新完成")
```

## 5. 动态文本替换

```python
import arcpy

aprx = arcpy.mp.ArcGISProject("CURRENT")

# 替换布局中的文本元素
for lyt in aprx.listLayouts():
    for elm in lyt.listElements("TEXT_ELEMENT"):
        # 替换标题中的年份
        if "年份" in elm.text:
            elm.text = elm.text.replace("2024", "2025")
        
        # 替换项目名称
        if "项目名" in elm.text:
            elm.text = "盐边县永兴镇村庄规划"

aprx.save()
```

## 6. 使用模板快速出图

```python
import arcpy
import os

# 从模板创建项目
template_aprx = r"C:\Templates\规划出图模板.aprx"
output_aprx = r"C:\Projects\XX村规划\XX村规划.aprx"

# 复制模板
import shutil
shutil.copy2(template_aprx, output_aprx)

# 修改项目中的数据源
aprx = arcpy.mp.ArcGISProject(output_aprx)
for m in aprx.listMaps():
    for lyr in m.listLayers():
        if lyr.isFeatureLayer:
            # 替换数据源
            lyr.updateConnectionProperties(
                {"database": r"C:\Templates\TemplateData.gdb"},
                {"database": r"C:\Projects\XX村规划\Data.gdb"}
            )

aprx.save()
print("项目创建完成")
```

## 导出参数速查

| 格式 | 方法 | 推荐分辨率 | 说明 |
|------|------|-----------|------|
| PDF | `exportToPDF()` | 300 | 印刷级，支持矢量 |
| PNG | `exportToPNG()` | 200 | 网页/屏幕显示 |
| JPEG | `exportToJPEG()` | 96 | 预览/邮件 |
| TIFF | `exportToTIFF()` | 300 | 印刷，支持透明 |
| SVG | `exportToSVG()` | — | 矢量编辑 |
| EMF | `exportToEMF()` | — | Office嵌入 |
