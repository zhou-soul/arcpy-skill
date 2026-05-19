# 城乡规划专项工具

## 1. 用地面积统计与平衡表

**场景**：村庄规划中统计各类用地面积，生成用地平衡表。

```python
import arcpy
import os

def generate_landuse_balance(fc, group_field="LANDUSE_CODE", area_field="SHAPE@AREA", output_excel=None):
    """
    生成用地平衡表
    
    参数:
        fc: 用地要素类
        group_field: 分组字段（地类编码）
        area_field: 面积字段
        output_excel: 输出Excel路径（可选）
    """
    stats = {}
    
    # 地类编码→名称映射（可自定义）
    code_names = {
        'A01': '城镇住宅用地', 'A02': '农村宅基地', 'A03': '机关团体用地',
        'A04': '科研用地', 'A05': '文化用地', 'A06': '教育用地',
        'A07': '体育用地', 'A08': '医疗卫生用地', 'A09': '社会福利用地',
        'B01': '工业用地', 'B02': '仓储用地', 'B03': '商业服务业用地',
        'C01': '耕地', 'C02': '园地', 'C03': '林地', 'C04': '草地',
        'C05': '湿地', 'C06': '水域', 'C07': '其他农用地',
        'D01': '城镇道路用地', 'D02': '交通场站用地', 'D03': '公用设施用地',
    }
    
    # 大类映射
    category_map = {
        'A': '建设用地', 'B': '建设用地', 'D': '建设用地',
        'C': '非建设用地'
    }
    
    with arcpy.da.SearchCursor(fc, [group_field, area_field]) as cursor:
        for row in cursor:
            code = row[0]
            area_sqm = row[1]  # 平方米
            area_mu = area_sqm / 666.67  # 转亩
            area_ha = area_sqm / 10000   # 转公顷
            
            if code not in stats:
                stats[code] = {'sqm': 0, 'mu': 0, 'ha': 0, 'count': 0}
            stats[code]['sqm'] += area_sqm
            stats[code]['mu'] += area_mu
            stats[code]['ha'] += area_ha
            stats[code]['count'] += 1
    
    # 输出结果
    print(f"\n{'编码':<8} {'用地名称':<16} {'大类':<10} {'图斑数':>6} {'面积(亩)':>12} {'面积(公顷)':>12}")
    print("-" * 70)
    
    total_mu = 0
    construction_mu = 0
    non_construction_mu = 0
    
    for code in sorted(stats.keys()):
        name = code_names.get(code, '未知')
        category = category_map.get(code[0], '其他')
        s = stats[code]
        total_mu += s['mu']
        if category == '建设用地':
            construction_mu += s['mu']
        else:
            non_construction_mu += s['mu']
        
        print(f"{code:<8} {name:<16} {category:<10} {s['count']:>6} {s['mu']:>12.2f} {s['ha']:>12.4f}")
    
    print("-" * 70)
    print(f"{'合计':<34} {sum(s['count'] for s in stats.values()):>6} {total_mu:>12.2f} {total_mu/15:>12.4f}")
    print(f"其中: 建设用地 {construction_mu:.2f} 亩, 非建设用地 {non_construction_mu:.2f} 亩")
    print(f"建设用地占比: {construction_mu/total_mu*100:.1f}%")
    
    # 导出Excel
    if output_excel:
        import csv
        csv_path = output_excel.replace('.xlsx', '.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['编码', '用地名称', '大类', '图斑数', '面积(平方米)', '面积(亩)', '面积(公顷)'])
            for code in sorted(stats.keys()):
                name = code_names.get(code, '未知')
                category = category_map.get(code[0], '其他')
                s = stats[code]
                writer.writerow([code, name, category, s['count'], f"{s['sqm']:.2f}", f"{s['mu']:.2f}", f"{s['ha']:.4f}"])
        print(f"\n已导出: {csv_path}")
    
    return stats
```

## 2. 建设用地指标计算

**场景**：计算地块容积率、建筑密度、绿地率等规划指标。

```python
import arcpy

def calculate_plot_ratio(fc, land_area_field="LAND_AREA", building_area_field="BUILDING_AREA"):
    """计算容积率 = 总建筑面积 / 总用地面积"""
    with arcpy.da.SearchCursor(fc, [land_area_field, building_area_field]) as cursor:
        total_land = 0
        total_building = 0
        for row in cursor:
            total_land += row[0]
            total_building += row[1]
    
    if total_land > 0:
        far = total_building / total_land
        print(f"容积率: {far:.2f}")
        return far
    return 0

def add_planning_indicators(fc):
    """批量添加规划指标字段并计算"""
    # 添加字段
    indicators = [
        ("FAR", "DOUBLE", "容积率"),
        ("BUILDING_DENSITY", "DOUBLE", "建筑密度(%)"),
        ("GREEN_RATE", "DOUBLE", "绿地率(%)"),
        ("BUILDING_HEIGHT", "DOUBLE", "建筑限高(m)"),
    ]
    
    for name, ftype, alias in indicators:
        existing = [f.name for f in arcpy.ListFields(fc)]
        if name not in existing:
            arcpy.management.AddField(fc, name, ftype, field_alias=alias)
    
    # 计算容积率
    arcpy.management.CalculateField(
        fc, "FAR", 
        "!BUILDING_AREA! / !LAND_AREA!" if "BUILDING_AREA" in existing else "0",
        "PYTHON3"
    )
    
    # 计算建筑密度
    arcpy.management.CalculateField(
        fc, "BUILDING_DENSITY",
        "!BUILDING_FOOTPRINT! / !LAND_AREA! * 100" if "BUILDING_FOOTPRINT" in existing else "0",
        "PYTHON3"
    )
```

## 3. 选址论证分析

**场景**：多条件选址，综合地形、交通、生态红线等因子。

```python
import arcpy
from arcpy.sa import *

def site_selection(
    study_area, 
    roads, 
    ecological_redline,
    slope_raster,
    dem_raster,
    road_distances=[200, 500, 1000],
    max_slope=15,
    output_gdb=r"C:\Data\Output.gdb"
):
    """
    选址论证分析
    
    条件：
    1. 不在生态红线内
    2. 坡度 ≤ max_slope 度
    3. 距道路在合理范围内
    4. 在研究区内
    """
    arcpy.CheckOutExtension("Spatial")
    arcpy.env.overwriteOutput = True
    
    # 1. 排除生态红线
    arcpy.analysis.Erase(
        study_area, ecological_redline,
        f"{output_gdb}\\step1_excl_redline"
    )
    
    # 2. 坡度筛选
    slope = Slope(dem_raster, "DEGREE")
    suitable_slope = Con(slope <= max_slope, 1, 0)
    
    # 3. 距道路距离
    dist_road = EucDistance(roads)
    suitable_dist = Con((dist_road >= road_distances[0]) & (dist_road <= road_distances[-1]), 1, 0)
    
    # 4. 综合适宜性
    suitability = suitable_slope * suitable_dist
    suitable_areas = Con(suitability == 1, 1)
    
    # 5. 转为矢量
    suitable_polygons = arcpy.conversion.RasterToPolygon(
        suitable_areas, f"{output_gdb}\\suitable_sites",
        "SIMPLIFY", "Value"
    )
    
    # 6. 按研究区裁剪
    arcpy.analysis.Clip(
        suitable_polygons, f"{output_gdb}\\step1_excl_redline",
        f"{output_gdb}\\final_suitable_sites"
    )
    
    arcpy.CheckInExtension("Spatial")
    
    # 统计结果
    count = int(arcpy.management.GetCount(f"{output_gdb}\\final_suitable_sites").getOutput(0))
    print(f"筛选完成，共 {count} 个适宜地块")
    
    return f"{output_gdb}\\final_suitable_sites"
```

## 4. 规划用地冲突检测

**场景**：检测现状用地与规划用地的冲突区域。

```python
import arcpy

def detect_landuse_conflicts(current_fc, planned_fc, current_field="LANDUSE_CODE", planned_field="PLAN_CODE", output_fc=None):
    """检测现状用地与规划用地的冲突"""
    
    # 相交分析
    intersect = arcpy.analysis.Intersect(
        [current_fc, planned_fc], "in_memory\\intersect_result"
    )
    
    # 找出地类编码不一致的区域（即冲突）
    conflicts = []
    with arcpy.da.SearchCursor(
        intersect, [current_field, planned_field, "SHAPE@AREA", "OID@"]
    ) as cursor:
        for row in cursor:
            if row[0] != row[1]:
                conflicts.append({
                    'oid': row[3],
                    'current_code': row[0],
                    'planned_code': row[1],
                    'area_sqm': row[2]
                })
    
    # 输出冲突统计
    print(f"共发现 {len(conflicts)} 处冲突区域")
    
    # 按冲突类型统计
    conflict_types = {}
    for c in conflicts:
        key = f"{c['current_code']}→{c['planned_code']}"
        if key not in conflict_types:
            conflict_types[key] = {'count': 0, 'area': 0}
        conflict_types[key]['count'] += 1
        conflict_types[key]['area'] += c['area_sqm']
    
    print(f"\n{'冲突类型':<20} {'图斑数':>6} {'面积(亩)':>12}")
    print("-" * 40)
    for key, val in sorted(conflict_types.items()):
        print(f"{key:<20} {val['count']:>6} {val['area']/666.67:>12.2f}")
    
    return conflicts
```

## 5. 公服设施覆盖分析

**场景**：分析村庄公共服务设施的服务覆盖范围，识别服务盲区。

```python
import arcpy

def service_coverage_analysis(
    facilities_fc, 
    study_area_fc,
    service_radius,
    output_gdb
):
    """
    公服设施覆盖分析
    
    参数:
        facilities_fc: 设施点图层
        study_area_fc: 研究区范围
        service_radius: 服务半径(米)，可以是统一值或按类型分
        output_gdb: 输出数据库
    """
    
    # 1. 生成服务范围（缓冲区）
    buffer_fc = arcpy.analysis.Buffer(
        facilities_fc, 
        f"{output_gdb}\\service_buffers",
        service_radius,
        dissolve_option="ALL"
    )
    
    # 2. 识别服务盲区（研究区 - 服务范围）
    blind_spots = arcpy.analysis.Erase(
        study_area_fc, buffer_fc,
        f"{output_gdb}\\service_blind_spots"
    )
    
    # 3. 统计覆盖率
    with arcpy.da.SearchCursor(study_area_fc, ["SHAPE@AREA"]) as cursor:
        total_area = sum(row[0] for row in cursor)
    
    with arcpy.da.SearchCursor(buffer_fc, ["SHAPE@AREA"]) as cursor:
        covered_area = sum(row[0] for row in cursor)
    
    coverage_rate = min(covered_area / total_area * 100, 100) if total_area > 0 else 0
    
    print(f"研究区总面积: {total_area/666.67:.2f} 亩")
    print(f"服务覆盖面积: {covered_area/666.67:.2f} 亩")
    print(f"覆盖率: {coverage_rate:.1f}%")
    
    # 4. 盲区面积
    with arcpy.da.SearchCursor(blind_spots, ["SHAPE@AREA"]) as cursor:
        blind_area = sum(row[0] for row in cursor)
    print(f"服务盲区面积: {blind_area/666.67:.2f} 亩")
    
    return {
        'coverage_rate': coverage_rate,
        'buffer': buffer_fc,
        'blind_spots': blind_spots
    }
```

## 6. 村庄规划用地分类统计

**场景**：按《村庄规划用地分类》标准统计用地。

```python
import arcpy

# 村庄规划用地分类编码（三级分类）
VILLAGE_LANDUSE_CODES = {
    # 非建设用地
    '01': '生态用地', '02': '农用地',
    '011': '林地', '012': '草地', '013': '水域', '014': '其他生态用地',
    '021': '耕地', '022': '园地', '023': '坑塘水面', '024': '设施农用地',
    # 建设用地
    '03': '农村宅基地', '04': '农村社区服务设施用地',
    '05': '公共管理与公共服务用地', '06': '商业服务业用地',
    '07': '工业用地', '08': '物流仓储用地',
    '09': '交通用地', '10': '公用设施用地',
    # 特殊用地
    '11': '文物古迹用地', '12': '殡葬用地',
}

def village_landuse_stats(fc, code_field="LANDUSE_CODE"):
    """按村庄规划用地分类统计"""
    stats = {}
    
    with arcpy.da.SearchCursor(fc, [code_field, "SHAPE@AREA"]) as cursor:
        for row in cursor:
            code = str(row[0]).strip()
            area = row[1]
            
            # 确定一级分类
            level1 = code[0] + code[1] if len(code) >= 2 else code[0]
            
            if code not in stats:
                stats[code] = {'area_sqm': 0, 'count': 0}
            stats[code]['area_sqm'] += area
            stats[code]['count'] += 1
    
    # 输出统计表
    print(f"\n{'编码':<6} {'名称':<20} {'图斑数':>6} {'面积(亩)':>12} {'面积(公顷)':>12} {'占比':>8}")
    print("-" * 70)
    
    total_mu = sum(s['area_sqm'] for s in stats.values()) / 666.67
    
    for code in sorted(stats.keys()):
        name = VILLAGE_LANDUSE_CODES.get(code, '未分类')
        s = stats[code]
        mu = s['area_sqm'] / 666.67
        ha = s['area_sqm'] / 10000
        pct = mu / total_mu * 100 if total_mu > 0 else 0
        print(f"{code:<6} {name:<20} {s['count']:>6} {mu:>12.2f} {ha:>12.4f} {pct:>7.1f}%")
    
    print("-" * 70)
    print(f"{'合计':<26} {sum(s['count'] for s in stats.values()):>6} {total_mu:>12.2f} {'':>12} {'100.0%':>8}")
    
    return stats
```
