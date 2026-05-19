# 空间分析工作流详解

## 1. 适宜性评价

**场景**：评价某区域建设适宜性，用于选址或规划决策。

### 工作流

```
确定评价因子 → 准备因子数据 → 重分类（统一量纲）→ AHP确定权重 → 加权叠加 → 分类输出
```

### 关键步骤代码

```python
import arcpy
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# 1. 准备因子（假设已有坡度、距道路距离、土地利用栅格）
slope_rast = Raster("slope")
dist_road = Raster("dist_road")
landuse = Raster("landuse")

# 2. 重分类（1-5分，5为最适宜）
# 坡度：越平越适宜
slope_reclass = Reclassify(slope_rast, "VALUE", 
    RemapRange([[0, 5, 5], [5, 10, 4], [10, 15, 3], [15, 25, 2], [25, 90, 1]]))

# 距道路距离：越近越适宜
dist_reclass = Reclassify(dist_road, "VALUE",
    RemapRange([[0, 200, 5], [200, 500, 4], [500, 1000, 3], [1000, 2000, 2], [2000, 5000, 1]]))

# 土地利用：按类型赋分
landuse_reclass = Reclassify(landuse, "VALUE",
    RemapValue([[11, 1], [12, 2], [21, 3], [31, 4], [41, 5]]))

# 3. AHP 权重（示例）
w_slope = 0.3
w_dist = 0.3
w_landuse = 0.4

# 4. 加权叠加
suitability = (slope_reclass * w_slope + 
               dist_reclass * w_dist + 
               landuse_reclass * w_landuse)

# 5. 分类输出
suit_class = Reclassify(suitability, "VALUE",
    RemapRange([[1, 2, 1], [2, 3, 2], [3, 4, 3], [4, 5, 4]]))

suit_class.save(r"C:\Output\suitability_class.tif")
arcpy.CheckInExtension("Spatial")
```

## 2. 水文分析

**场景**：提取流域、河网，用于流域规划或水土保持分析。

### 工作流

```
DEM → 填洼(Fill) → 流向(FlowDirection) → 流量累积(FlowAccumulation) → 
河网提取 → 河流链接 → 流域划分 → 集水区
```

### 关键步骤代码

```python
import arcpy
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

dem = Raster("dem_fill_ready")

# 1. 填洼
filled = Fill(dem)

# 2. 流向
flow_dir = FlowDirection(filled, "NORMAL")

# 3. 流量累积
flow_acc = FlowAccumulation(flow_dir)

# 4. 提取河网（阈值根据研究区调整）
threshold = 1000  # 累积栅格数
stream = Con(flow_acc > threshold, 1)

# 5. 河流链接
stream_link = StreamLink(stream, flow_dir)

# 6. 流域划分
watershed = Watershed(flow_dir, stream_link)

watershed.save(r"C:\Output\watershed.tif")
arcpy.CheckInExtension("Spatial")
```

## 3. 距离分析

**场景**：分析设施可达性、成本路径选址。

### 欧氏距离

```python
from arcpy.sa import *

# 到最近设施的距离
euc_dist = EucDistance("facilities", maximum_distance=5000, cell_size=30)
euc_dir = EucDirection("facilities")

# 到最近设施的分配
euc_alloc = EucAllocation("facilities", maximum_distance=5000)
```

### 成本距离

```python
from arcpy.sa import *

# 创建成本栅格（值越大越难通过）
cost_raster = Raster("cost_surface")

# 计算成本距离
out_cost_dist = CostDistance("source_points", cost_raster)
out_back_link = CostBackLink("source_points", cost_raster)

# 计算最小成本路径
out_path = CostPath("destination", out_cost_dist, out_back_link, "EACH_CELL")
```

## 4. 缓冲区与邻域分析

### 多环缓冲区

```python
# 方法1：使用工具
arcpy.analysis.MultipleRingBuffer(
    "roads", "road_buffers", 
    [100, 300, 500, 1000], 
    "Meters", "distance", "ALL"
)

# 方法2：循环创建
for dist in [100, 300, 500, 1000]:
    arcpy.analysis.Buffer(
        "roads", f"road_buf_{dist}m", 
        f"{dist} Meters"
    )
```

### 近邻分析

```python
# 计算每个要素到最近要素的距离
arcpy.analysis.Near("villages", "roads", distance_unit="METERS")

# 空间连接（统计每个缓冲区内设施数量）
arcpy.analysis.SpatialJoin(
    "village_buffers", "facilities", "village_facility_count",
    join_operation="JOIN_ONE_TO_ONE",
    match_option="INTERSECT"
)
```

## 5. 表面分析

```python
from arcpy.sa import *

dem = Raster("dem")

# 坡度（度数）
slope = Slope(dem, "DEGREE")

# 坡向
aspect = Aspect(dem)

# 山体阴影
hillshade = Hillshade(dem, 315, 45)

# 等值线
arcpy.ddd.Contour(dem, "contours_10m", contour_interval=10)

# 视域分析（需3D Analyst）
viewshed = Viewshed("observer_points", dem)
```

## 6. 叠加分析

```python
# 相交 — 提取两图层重叠部分
arcpy.analysis.Intersect(["landuse", "planning_zone"], "intersect_result")

# 标识 — 用一个图层的属性标记另一个
arcpy.analysis.Identity("landuse", "flood_zone", "landuse_flood")

# 擦除 — 从一个图层中去除另一个图层的区域
arcpy.analysis.Erase("construction_land", "ecological_redline", "available_land")

# 空间连接 — 将属性从一个图层连接到另一个
arcpy.analysis.SpatialJoin(
    "parcels", "schools", "parcels_with_schools",
    join_operation="JOIN_ONE_TO_ONE",
    match_option="WITHIN"
)
```
