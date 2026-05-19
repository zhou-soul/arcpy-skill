# ArcPy 核心 API 速查

## 模块总览

| 模块 | 导入方式 | 用途 | 许可证 |
|------|----------|------|--------|
| 核心模块 | `import arcpy` | 地理处理工具入口 | Desktop/Pro |
| Spatial Analyst | `from arcpy.sa import *` | 栅格分析 | Spatial Analyst |
| Data Access | `arcpy.da` | 游标、编辑、版本 | Desktop/Pro |
| Network Analyst | `arcpy.nax` | 网络分析 | Network Analyst |
| Mapping | `arcpy.mp` | 制图自动化 | Desktop/Pro |
| Chart | `arcpy.charts` | 图表 | Desktop/Pro |
| Image Analyst | `arcpy.ia` | 影像分析 | Image Analyst |
| 3D Analyst | `arcpy.3d` | 三维分析 | 3D Analyst |

## 环境设置

```python
import arcpy

# 工作空间
arcpy.env.workspace = r"C:\Data\Project.gdb"
arcpy.env.scratchWorkspace = r"C:\Data\Scratch.gdb"

# 覆盖设置
arcpy.env.overwriteOutput = True

# 坐标系
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4490)  # CGCS2000

# 处理范围
arcpy.env.extent = "MAXOF"  # 或指定范围

# 像元大小（栅格分析）
arcpy.env.cellSize = 30

# 并行处理
arcpy.env.parallelProcessingFactor = "75%"
```

## 游标操作

### SearchCursor — 读取数据

```python
import arcpy

# 基本用法
with arcpy.da.SearchCursor(roads, ["SHAPE@", "NAME", "LENGTH"]) as cursor:
    for row in cursor:
        geometry, name, length = row
        print(f"{name}: {length:.1f}m")

# 带条件查询
with arcpy.da.SearchCursor(
    parcels, ["OWNER", "AREA"], 
    where_clause="LANDUSE = 'Residential'"
) as cursor:
    for row in cursor:
        print(f"{row[0]}: {row[1]:.2f} 亩")

# 使用 SHAPE@JSON / SHAPE@WKT / SHAPE@XY 等令牌
with arcpy.da.SearchCursor(points, ["SHAPE@XY", "ID"]) as cursor:
    for row in cursor:
        x, y = row[0]
        print(f"ID={row[1]}, X={x}, Y={y}")
```

### InsertCursor — 写入数据

```python
# 插入新要素
fields = ["SHAPE@XY", "NAME", "CATEGORY"]
with arcpy.da.InsertCursor(target_fc, fields) as cursor:
    cursor.insertRow([(104.06, 30.67), "天府广场", "Landmark"])
    cursor.insertRow([(104.07, 30.68), "春熙路", "Commercial"])
```

### UpdateCursor — 更新/删除数据

```python
# 更新字段
with arcpy.da.UpdateCursor(
    parcels, ["AREA_MU", "AREA_SQM", "LANDUSE"],
    where_clause="LANDUSE = 'A01'"
) as cursor:
    for row in cursor:
        row[0] = row[1] / 666.67  # 平方米转亩
        cursor.updateRow(row)

# 删除要素
with arcpy.da.UpdateCursor(
    buildings, ["STATUS"], 
    where_clause="STATUS = 'Demolished'"
) as cursor:
    for row in cursor:
        cursor.deleteRow()
```

## 列表与描述

```python
# 列出要素类
fcs = arcpy.ListFeatureClasses()
fcs = arcpy.ListFeatureClasses("*村庄*", "Polygon")  # 通配符+类型过滤

# 列出字段
fields = arcpy.ListFields(fc)
for f in fields:
    print(f"{f.name} ({f.type}), 长度={f.length}")

# 描述数据
desc = arcpy.Describe(fc)
print(f"类型: {desc.shapeType}")  # Point/Polyline/Polygon
print(f"坐标系: {desc.spatialReference.name}")
print(f"路径: {desc.path}")

# 存在性检查
exists = arcpy.Exists(r"C:\Data\test.shp")
```

## 常用地理处理工具

```python
# 分析工具
arcpy.analysis.Buffer(in_features, out_feature_class, distance)
arcpy.analysis.Clip(in_features, clip_features, out_feature_class)
arcpy.analysis.Intersect(in_features, out_feature_class)
arcpy.analysis.Union(in_features, out_feature_class)
arcpy.analysis.SpatialJoin(target, join, out)
arcpy.analysis.Near(in_features, near_features)

# 管理工具
arcpy.management.Project(in_dataset, out_dataset, out_coor_system)
arcpy.management.Dissolve(in_features, out_feature_class, dissolve_field)
arcpy.management.AddField(in_table, field_name, field_type)
arcpy.management.CalculateField(in_table, field, expression)
arcpy.management.Select(in_features, out_feature_class, where_clause)
arcpy.management.CopyFeatures(in_features, out_feature_class)
arcpy.management.Merge(inputs, output)
arcpy.management.Append(inputs, target)
arcpy.management.FeatureToPolygon(in_features, out_feature_class)
arcpy.management.MultipartToSinglepart(in_features, out_feature_class)

# 转换工具
arcpy.conversion.FeatureClassToShapefile(Input_Features, Output_Folder)
arcpy.conversion.TableToExcel(Input_Table, Output_Excel_File)
arcpy.conversion.ExcelToTable(Input_Excel_File, Output_Table)
arcpy.conversion.FeatureClassToGeodatabase(Input_Features, Output_Geodatabase)
```

## Spatial Analyst 栅格分析

```python
from arcpy.sa import *

# 检出许可
arcpy.CheckOutExtension("Spatial")

# 重分类
remap = RemapValue([[1, 5], [2, 4], [3, 3], [4, 2], [5, 1]])
out_reclass = Reclassify(in_raster, "VALUE", remap)

# 栅格计算器
out_calc = Raster("slope") * 0.3 + Raster("elevation") * 0.7

# 距离分析
out_dist = EucDistance(in_features, max_distance, cell_size)
out_alloc = EucAllocation(in_features)

# 表面分析
out_slope = Slope(in_raster, "DEGREE")
out_aspect = Aspect(in_raster)
out_hillshade = Hillshade(in_raster, 315, 45)

# 叠加分析（加权总和）
out_wsum = WeightedOverlay(
    WOTable(
        [[slope_rast, 1, "VALUE", remap1],
         [dist_rast, 1, "VALUE", remap2],
         [landuse_rast, 1, "VALUE", remap3]],
        [0.4, 0.3, 0.3]
    )
)

# 保存结果
out_wsum.save(r"C:\Output\suitability.tif")

# 归还许可
arcpy.CheckInExtension("Spatial")
```

## 错误处理模式

```python
import arcpy
import os

try:
    arcpy.env.workspace = r"C:\Data\Project.gdb"
    arcpy.env.overwriteOutput = True
    
    # 主逻辑
    result = arcpy.analysis.Buffer("roads", "roads_buffer", "500 Meters")
    
    # 检查结果
    if result.maxSeverity == 0:
        count = int(arcpy.management.GetCount("roads_buffer").getOutput(0))
        print(f"成功生成 {count} 个缓冲区面")
    else:
        print(f"执行有警告: {result.getMessages(1)}")
        
except arcpy.ExecuteError:
    print(f"ArcPy 执行错误: {arcpy.GetMessages(2)}")
except Exception as e:
    print(f"其他错误: {e}")
```

## arcpy.mp 制图自动化

```python
# 获取当前项目
aprx = arcpy.mp.ArcGISProject("CURRENT")  # 或 r"path\to\project.aprx"

# 操作地图
maps = aprx.listMaps()
m = aprx.listMaps("村庄规划")[0]
lyr = m.listLayers("用地*")[0]

# 操作布局
layouts = aprx.listLayouts()
lyt = aprx.listLayouts("标准出图")[0]
mf = lyt.listElements("MAPFRAME_ELEMENT")[0]

# 导出
lyt.exportToPDF(r"C:\Output\map.pdf", resolution=300)
lyt.exportToPNG(r"C:\Output\map.png", resolution=200)
```

## 性能优化技巧

1. **in_memory 工作空间**：中间结果写入内存，大幅提速
   ```python
   temp = arcpy.analysis.Buffer(input, "in_memory\\temp_buf", "100 Meters")
   ```

2. **指定字段列表**：游标只读取需要的字段，避免 `["*"]`
3. **批量操作**：用 `arcpy.management.Merge` 合并后一次处理，替代循环内逐个操作
4. **禁用非必要更新**：编辑时关闭空间索引
5. **并行处理**：`arcpy.env.parallelProcessingFactor = "100%"`
