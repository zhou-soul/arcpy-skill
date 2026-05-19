# arcgis-pro-copilot 🗺️🐍

> ArcGIS Pro / ArcPy 智能助手 Skill —— 让 AI 帮你写 GIS 脚本、做空间分析、搞规划出图

[![Skill](https://img.shields.io/badge/ima.copilot-Skill-blue)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.9+-green)](https://www.python.org/)
[![ArcGIS](https://img.shields.io/badge/ArcGIS_Pro-3.x-orange)](https://www.esri.com/en-us/arcgis/products/arcgis-pro)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 这是什么

`arcgis-pro-copilot` 是一个为 [ima.copilot](https://ima.copilot) 平台设计的 Skill，让 AI 助手成为你的 ArcGIS Pro / ArcPy 专家搭档。它能：

- 🐍 **ArcPy 代码生成** —— 说人话，得代码。根据自然语言需求直接生成可运行的 ArcPy 脚本
- 🗺️ **空间分析工作流** —— 适宜性评价、水文分析、距离分析、叠加分析，一套流程搞定
- 📊 **数据批量处理** —— 批量裁剪/投影/字段计算/GDB合并/CAD互转，告别重复劳动
- 🎨 **制图自动化** —— 批量出图、布局模板、空间地图系列，出图效率翻倍
- 🏘️ **规划专项工具** —— 用地平衡表、指标计算、选址论证、冲突检测，规划师量身定制

## 🎯 适用人群

- 城乡规划师（村庄规划、专项规划、选址论证）
- GIS 分析师（空间建模、批量处理）
- 国土空间规划从业者（用地分析、指标论证）
- 任何需要在 ArcGIS Pro 中用 Python 提效的人

## 📦 项目结构

```
arcgis-pro-copilot/
├── SKILL.md                          # Skill 定义文件（核心）
├── README.md                         # 你正在看的这个
├── LICENSE                           # MIT 许可证
├── .gitignore
│
├── references/                       # 参考文档（按需加载）
│   ├── arcpy-quick-ref.md           # ArcPy 核心 API 速查
│   ├── spatial-analysis-workflows.md # 空间分析工作流详解
│   ├── data-management-patterns.md  # 数据管理模式与最佳实践
│   ├── cartography-automation.md    # 制图自动化脚本模板
│   └── planning-toolkit.md          # 城乡规划专项工具实现
│
├── scripts/                          # 可直接执行的实用脚本
│   ├── batch_buffer.py              # 批量缓冲区分析
│   ├── export_maps.py               # 批量导出地图为 PDF/PNG
│   ├── land_use_stats.py            # 用地面积统计与平衡表
│   └── field_calculator.py          # 批量字段计算工具
│
├── assets/                           # 模板文件
│   ├── suitability_template.py      # 适宜性评价完整脚本模板
│   └── planning_stats_template.py   # 规划统计报告模板
│
└── examples/                         # 额外示例
    ├── quickstart_buffer.py         # 快速上手：缓冲区分析
    ├── quickstart_suitability.py    # 快速上手：适宜性评价
    └── quickstart_batch_export.py   # 快速上手：批量出图
```

## 🚀 快速开始

### 在 ima.copilot 中使用

1. 将本项目克隆到你的 ima.copilot skills 目录
2. 在对话中说"帮我写个缓冲区分析的脚本"或"分析这个区域的建设适宜性"
3. AI 助手会自动加载 Skill 并提供专业帮助

### 独立使用脚本

脚本不依赖 ima.copilot，可以直接在 ArcGIS Pro 的 Python 窗口运行：

```bash
# 批量缓冲区分析
python scripts/batch_buffer.py --input roads --output road_buffers --field TYPE --distances "主干道=500,次干道=300"

# 批量导出地图
python scripts/export_maps.py --aprx CURRENT --output C:/Output/ --format pdf --dpi 300

# 用地面积统计
python scripts/land_use_stats.py --input parcels --field LANDUSE_CODE --output balance.csv
```

### 在 ArcGIS Pro Python 窗口直接粘贴

```python
import arcpy
from arcpy.sa import *

# 示例：30秒做一个坡度分析
arcpy.CheckOutExtension("Spatial")
dem = Raster("dem")
slope = Slope(dem, "DEGREE")
suitable = Con(slope <= 15, 1, 0)  # 坡度≤15°为适宜
suitable.save("suitable_slope")
arcpy.CheckInExtension("Spatial")
print("坡度适宜性分析完成！")
```

## 🏘️ 规划师专属

本项目特别为城乡规划师设计，内置规划常见场景的工具链：

| 场景 | 工具/工作流 | 关键输出 |
|------|------------|----------|
| 村庄规划 | 用地平衡表生成 | 面积统计表 + CSV |
| 选址论证 | 多因子适宜性评价 | 适宜性分级图 |
| 用地冲突 | 现状vs规划对比 | 冲突检测报告 |
| 设施覆盖 | 公服可达性分析 | 覆盖率 + 盲区 |
| 指标论证 | 容积率/密度/绿地率 | 指标计算结果 |
| 批量出图 | 空间地图系列 | 按村/按区批量PDF |

## 📚 参考文档速查

| 文档 | 内容 | 何时查看 |
|------|------|----------|
| [ArcPy速查](references/arcpy-quick-ref.md) | 模块、游标、工具、环境设置 | 写脚本时快速查API |
| [空间分析](references/spatial-analysis-workflows.md) | 适宜性/水文/距离/叠加 | 做空间分析项目时 |
| [数据管理](references/data-management-patterns.md) | 批量裁剪/投影/字段/质量检查 | 数据处理和清洗时 |
| [制图自动化](references/cartography-automation.md) | 布局/符号/导出/地图系列 | 出图和制图时 |
| [规划工具](references/planning-toolkit.md) | 用地统计/指标/选址/冲突检测 | 做规划项目时 |

## 🤝 参与贡献

欢迎贡献！无论是修复bug、添加新脚本、补充工作流模板，还是改进文档。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-tool`)
3. 提交修改 (`git commit -m 'Add amazing planning tool'`)
4. 推送到分支 (`git push origin feature/amazing-tool`)
5. 提交 Pull Request

### 贡献方向

- 🔧 更多规划专项脚本（红线检测、生态评价、交通可达性...）
- 📊 更多空间分析工作流（网络分析、3D分析、时序分析...）
- 🌍 更多坐标系预设（各省市常用坐标系...）
- 📝 中文/英文双语改进
- 🧪 测试用例

## 📋 依赖

- **ArcGIS Pro** 3.x（推荐 3.1+）
- **Python** 3.9+（ArcGIS Pro 自带）
- **扩展许可**（按需）：
  - Spatial Analyst — 栅格分析
  - 3D Analyst — 三维分析
  - Network Analyst — 网络分析
  - Image Analyst — 影像分析

## 📄 许可证

[MIT License](LICENSE) — 自由使用、修改和分发。

## ⚠️ 免责声明

本工具仅供学习和参考，脚本使用前请在测试环境验证。空间分析结果需结合专业判断，规划指标计算请以当地规范为准。

---

<p align="center">
 Made with ❤️ by planners, for planners
</p>
