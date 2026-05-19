# 数据管理模式与最佳实践

## 1. 批量裁剪

```python
import arcpy
import os

arcpy.env.workspace = r"C:\Data\Project.gdb"
arcpy.env.overwriteOutput = True

clip_fc = r"C:\Data\StudyArea.shp"  # 裁剪范围
out_gdb = r"C:\Data\Clipped.gdb"

# 批量裁剪所有面要素类
fcs = arcpy.ListFeatureClasses("", "Polygon")
for fc in fcs:
    out_name = f"{fc}_clip"
    arcpy.analysis.Clip(fc, clip_fc, os.path.join(out_gdb, out_name))
    print(f"已裁剪: {fc} → {out_name}")
```

## 2. 批量投影转换

```python
import arcpy
import os

arcpy.env.workspace = r"C:\Data\Raw"
out_gdb = r"C:\Data\Projected.gdb"

# 目标坐标系：CGCS2000 3度带
target_sr = arcpy.SpatialReference(4527)  # 根据实际区域选择带号

fcs = arcpy.ListFeatureClasses()
for fc in fcs:
    desc = arcpy.Describe(fc)
    if desc.spatialReference.factoryCode != target_sr.factoryCode:
        out_name = f"{fc}_proj"
        arcpy.management.Project(fc, os.path.join(out_gdb, out_name), target_sr)
        print(f"已投影: {fc} → {out_name}")
    else:
        print(f"跳过(已是目标坐标系): {fc}")
```

## 3. 字段批量处理

### 批量添加字段

```python
import arcpy

fc = r"C:\Data\Project.gdb\parcels"
fields_to_add = [
    ("AREA_MU", "DOUBLE", "面积(亩)"),
    ("LANDUSE_CODE", "TEXT", "地类编码", 10),
    ("LANDUSE_NAME", "TEXT", "地类名称", 20),
    ("IS_CONSTRUCTION", "SHORT", "是否建设用地"),
]

for field_def in fields_to_add:
    name, ftype = field_def[0], field_def[1]
    alias = field_def[2] if len(field_def) > 2 else name
    length = field_def[3] if len(field_def) > 3 else None
    
    # 检查字段是否已存在
    existing = [f.name for f in arcpy.ListFields(fc)]
    if name not in existing:
        if length:
            arcpy.management.AddField(fc, name, ftype, field_alias=alias, field_length=length)
        else:
            arcpy.management.AddField(fc, name, ftype, field_alias=alias)
        print(f"已添加字段: {name}")
```

### 批量字段计算

```python
import arcpy

fc = r"C:\Data\Project.gdb\parcels"

# 面积换算
arcpy.management.CalculateField(fc, "AREA_MU", "!SHAPE.area! / 666.67", "PYTHON3")

# 条件计算：根据编码判断是否建设用地
code = """
def is_construction(landuse_code):
    construction_codes = ['A01', 'A02', 'A03', 'B01', 'B02']
    return 1 if landuse_code in construction_codes else 0
"""
arcpy.management.CalculateField(fc, "IS_CONSTRUCTION", "is_construction(!LANDUSE_CODE!)", "PYTHON3", code)

# 地类名称映射
mapping = """
def get_name(code):
    names = {
        'A01': '城镇住宅用地', 'A02': '农村宅基地', 'A03': '机关团体用地',
        'B01': '工业用地', 'B02': '仓储用地',
        'C01': '耕地', 'C02': '园地', 'C03': '林地'
    }
    return names.get(code, '未分类')
"""
arcpy.management.CalculateField(fc, "LANDUSE_NAME", "get_name(!LANDUSE_CODE!)", "PYTHON3", mapping)
```

## 4. 多GDB合并

```python
import arcpy
import os

# 将多个GDB中同名要素类合并到一个GDB
source_folder = r"C:\Data\Villages"
target_gdb = r"C:\Data\Merged.gdb"
target_fc_name = "parcels"  # 要合并的要素类名

all_fcs = []
for root, dirs, files in arcpy.da.Walk(source_folder, datatype="FeatureClass"):
    for f in files:
        if f == target_fc_name:
            all_fcs.append(os.path.join(root, f))

if all_fcs:
    arcpy.management.Merge(all_fcs, os.path.join(target_gdb, f"{target_fc_name}_merged"))
    print(f"已合并 {len(all_fcs)} 个要素类")
```

## 5. 数据质量检查

```python
import arcpy

def check_data_quality(fc):
    """检查要素类的数据质量"""
    issues = []
    
    # 1. 空几何检查
    with arcpy.da.SearchCursor(fc, ["OID@", "SHAPE@"]) as cursor:
        for row in cursor:
            if row[1] is None or row[1].pointCount == 0:
                issues.append(f"OID {row[0]}: 空几何")
    
    # 2. 几何修复
    arcpy.management.RepairGeometry(fc)
    
    # 3. 必填字段空值检查
    required_fields = ["LANDUSE_CODE", "AREA"]
    for field in required_fields:
        with arcpy.da.SearchCursor(fc, [field, "OID@"]) as cursor:
            for row in cursor:
                if row[0] is None or row[0] == "":
                    issues.append(f"OID {row[1]}: 字段 {field} 为空")
    
    # 4. 面积合理性
    with arcpy.da.SearchCursor(fc, ["SHAPE@AREA", "OID@"]) as cursor:
        for row in cursor:
            if row[0] <= 0:
                issues.append(f"OID {row[1]}: 面积异常 ({row[0]:.2f})")
    
    return issues

# 使用
issues = check_data_quality(r"C:\Data\Project.gdb\parcels")
for issue in issues:
    print(issue)
```

## 6. CAD与GIS互转

```python
# CAD → GIS
arcpy.conversion.CADToGeodatabase(
    r"C:\Data\Drawing.dwg", 
    r"C:\Data\Output.gdb",
    "CAD_Import",
    arcpy.SpatialReference(4527)
)

# GIS → CAD
arcpy.conversion.FeatureClassToCAD(
    r"C:\Data\Project.gdb\parcels",
    r"C:\Data\Output\parcels.dwg",
    "DWG_R2018"
)
```

## 7. Excel/CSV 交互

```python
# Excel → 表
arcpy.conversion.ExcelToTable(
    r"C:\Data\stats.xlsx", 
    r"C:\Data\Project.gdb\stats_table"
)

# 表 → Excel
arcpy.conversion.TableToExcel(
    r"C:\Data\Project.gdb\stats_table",
    r"C:\Output\stats_output.xlsx"
)

# CSV 导入（用游标，更灵活）
import csv

target_fc = r"C:\Data\Project.gdb\imported_points"
fields = ["SHAPE@XY", "NAME", "VALUE"]

with arcpy.da.InsertCursor(target_fc, fields) as cursor:
    with open(r"C:\Data\points.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            x, y = float(row["X"]), float(row["Y"])
            cursor.insertRow([(x, y), row["NAME"], float(row["VALUE"])])
```

## 最佳实践

1. **始终设置 overwriteOutput**：避免脚本因输出已存在而中断
2. **用 in_memory 做中间处理**：速度提升数倍
3. **游标只选需要的字段**：避免 `["*"]`
4. **大数据分块处理**：用 where_clause 分批次，避免内存溢出
5. **事务管理**：用 `arcpy.da.Editor` 管理编辑会话，出错可回滚
6. **路径用原始字符串**：`r"C:\path"` 防止转义问题
