# 杭州二手房数据分析系统

## Hangzhou Second-hand Housing Data Analysis System

基于链家(杭州)二手房数据的完整分析系统，包含数据采集、清洗、建模分析及Web可视化展示。

---

## 项目结构

```
hangzhou-housing-analysis/
├── scraper/                       # 数据采集模块
│   └── lianjia_scraper.py         # 链家爬虫 (杭州)
├── analysis/                      # 数据分析模块
│   ├── data_cleaner.py            # 数据清洗
│   ├── descriptive_stats.py       # 描述性统计分析
│   ├── advanced_analysis.py       # 回归/聚类/PCA/判别分析
│   └── chart_generator.py         # 图表生成 (pyecharts)
├── web/                           # Web系统
│   ├── backend/
│   │   └── app.py                 # FastAPI 后端
│   └── frontend/                  # Vue 3 前端
│       └── src/
│           ├── views/             # 页面组件
│           ├── api/               # API 接口
│           └── router/            # 路由配置
├── database/
│   └── models.py                  # 数据库模型 (SQLite)
├── data/                          # 数据文件
│   ├── raw/                       # 原始数据
│   └── cleaned/                   # 清洗后数据
├── charts/                        # 生成的图表HTML
├── analysis/results/              # 分析结果JSON
├── config.py                      # 全局配置
├── run_pipeline.py                # 一键运行脚本
└── requirements.txt               # Python依赖
```

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 数据采集

```bash
# 采集120页数据 (约3600条房源)
python scraper/lianjia_scraper.py --pages 120 --enrich 50
```

### 3. 一键运行完整流程

```bash
# 运行全流程：采集 → 清洗 → 分析 → 图表 → 启动Web服务
python run_pipeline.py

# 或者跳过某些步骤
python run_pipeline.py --skip-scrape --skip-clean

# 仅启动Web服务
python run_pipeline.py --serve-only
```

### 4. 分步运行

```bash
# Step 1: 数据采集
python scraper/lianjia_scraper.py --pages 120

# Step 2: 数据清洗
python analysis/data_cleaner.py data/raw/hangzhou_raw_*.csv

# Step 3: 数据分析
python analysis/advanced_analysis.py data/cleaned/hangzhou_cleaned_*.csv

# Step 4: 图表生成
python analysis/chart_generator.py data/cleaned/hangzhou_cleaned_*.csv

# Step 5: 启动Web后端
cd web/backend && python app.py

# Step 6: 启动前端 (开发模式)
cd web/frontend && npm install && npm run dev
```

---

## 数据分析方法

| 方法 | 说明 |
|------|------|
| **描述性统计** | 总价、单价、面积、房龄的分布特征 |
| **相关性分析** | 各因素与房价的相关程度 |
| **多元回归分析** | OLS回归 + Ridge回归，建立房价预测模型 |
| **主成分分析(PCA)** | 提取影响房价的综合因子 |
| **因子分析** | 识别潜在变量结构 |
| **聚类分析(K-Means)** | 将房源分为不同类别 |
| **判别分析(LDA/QDA)** | 基于特征的房源类别判别 |

---

## Web系统功能

| 功能模块 | 说明 |
|----------|------|
| 数据概览 | 房源总数、均价、各区最高/最低单价等 |
| 房源列表 | 支持多条件筛选、排序、分页的房源查询 |
| 区域分析 | 各区房价对比、房源分布统计 |
| 因素分析 | 相关性热力图、回归模型结果展示 |
| 综合评价 | PCA/因子分析结果、综合得分展示 |
| 房源分类 | 聚类结果展示、各类特征说明 |
| 购房建议 | 基于数据的购房决策参考 |
| 可视化图表 | 10+种图表的集中展示 |

---

## 可视化图表清单

1. ✅ 各区平均单价柱状图
2. ✅ 房源总价分布直方图
3. ✅ 面积与总价散点图
4. ✅ 建筑年代与单价散点图
5. ✅ 各户型平均总价柱状图
6. ✅ 各装修状态平均单价柱状图
7. ✅ 房价影响因素相关性热力图
8. ✅ 回归模型结果图
9. ✅ 主成分/因子得分图
10. ✅ 房源聚类结果图

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 数据采集 | Python requests, BeautifulSoup4, lxml |
| 数据处理 | pandas, numpy, regex |
| 数据分析 | scikit-learn, statsmodels, scipy, factor_analyzer |
| 图表生成 | pyecharts, ECharts |
| Web后端 | FastAPI, SQLAlchemy, SQLite |
| Web前端 | Vue 3, Element Plus, ECharts, Axios |

---

## 配置说明

编辑 `config.py` 修改配置：

- `SCRAPER`: 采集参数（页数、延迟、User-Agent）
- `CLEANING`: 数据清洗阈值（异常值标准差、面积范围等）
- `ANALYSIS`: 分析参数（聚类数K、因子数、随机种子）
- `SERVER`: Web服务器配置（端口、地址）

---

## 注意事项

- 爬虫符合robots.txt规范，设置了合理延迟(2-5秒)
- 不采集个人隐私信息（房源页面均为公开数据）
- 建议在非高峰期运行采集任务
- 如遇反爬验证，脚本会自动等待60秒后重试
