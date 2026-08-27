# Hangzhou Second-hand Housing Analysis - Vercel API (pure Python)
# =================================================================
# Deployable reimplementation of web/backend/app.py for Vercel serverless.
# Uses ONLY the standard library + FastAPI (no pandas/numpy/sklearn) so the
# function bundle stays far below Vercel's size limit.
#
# Heavy/sampled chart payloads and descriptive statistics were precomputed
# with the exact original code (scripts/precompute_deploy_data.py) into
# api_static/*.json and are served from there. Everything else (overview,
# listings with filters/sorting/pagination, district analysis, etc.) is
# computed on the fly from data/cleaned/*.csv with plain Python.

import csv
import json
import math
import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "cleaned")
RESULTS_DIR = os.path.join(ROOT, "analysis", "results")
STATIC_DIR = os.path.join(ROOT, "api_static")
CHART_REGISTRY_PATH = os.path.join(ROOT, "charts", "chart_registry.json")

app = FastAPI(
    title="Hangzhou Second-hand Housing Analysis System",
    description="Hangzhou Second-hand Housing Price Analysis System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# DATA LOADING (pure Python)
# ============================================================

FLOAT_COLS = {
    "total_price", "unit_price", "floor_area", "total_floors",
    "construction_year", "building_age", "floor_ratio",
    "price_per_room", "area_per_room",
}
INT_COLS = {"rooms", "halls", "near_subway", "decoration_level",
            "floor_type_encoded", "orientation_south"}

_rows = None


def get_rows():
    """Load CSV rows once (latest cleaned file wins, same as app.py)."""
    global _rows
    if _rows is not None:
        return _rows

    path = None
    if os.path.isdir(DATA_DIR):
        files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")],
                       reverse=True)
        if files:
            path = os.path.join(DATA_DIR, files[0])

    rows = []
    if path:
        with open(path, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                rows.append(row)
        print(f"Loaded {len(rows)} records from {path}")
    else:
        print("[WARN] No data files found")
    _rows = rows
    return rows


def num(v):
    """Parse a cell to float, or None if missing/non-numeric."""
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def num_col(key):
    """All float values of a column (missing dropped), pandas-dropna style."""
    vals = []
    for row in get_rows():
        n = num(row.get(key))
        if n is not None:
            vals.append(n)
    return vals


def str_col(key):
    """Non-empty string values of a column."""
    vals = []
    for row in get_rows():
        v = row.get(key)
        if v not in (None, ""):
            vals.append(v)
    return vals


def mean(vals):
    return sum(vals) / len(vals) if vals else 0.0


def median(vals):
    if not vals:
        return 0.0
    s = sorted(vals)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


def groupby(key):
    """Group rows by a string column, keeping row order per group."""
    groups = {}
    for row in get_rows():
        k = row.get(key)
        if k in (None, ""):
            continue
        groups.setdefault(k, []).append(row)
    return groups


def value_counts(key):
    """Counts per value, sorted by count desc (pandas value_counts)."""
    counts = {}
    for v in str_col(key):
        counts[v] = counts.get(v, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def _json(path, default=None):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def r2(n):
    return round(float(n), 2)


def r0(n):
    return float(round(n))


# ============================================================
# API ROUTES
# ============================================================

@app.get("/api/overview")
async def get_overview():
    """Homepage data overview (same fields as the original backend)."""
    rows = get_rows()
    if not rows:
        return {"error": "No data available", "total_listings": 0}

    overview = {"total_listings": len(rows)}
    districts = str_col("district")
    communities = str_col("community_name")
    overview["total_districts"] = len(set(districts))
    overview["total_communities"] = len(set(communities))

    for key in ("total_price", "unit_price"):
        vals = num_col(key)
        if vals:
            overview[f"avg_{key}"] = r2(mean(vals))
            overview[f"median_{key}"] = r2(median(vals))
            overview[f"min_{key}"] = r2(min(vals))
            overview[f"max_{key}"] = r2(max(vals))

    areas = num_col("floor_area")
    if areas:
        overview["avg_area"] = r2(mean(areas))
        overview["median_area"] = r2(median(areas))

    ages = num_col("building_age")
    if ages:
        overview["avg_building_age"] = r2(mean(ages))

    # Highest / lowest unit price district (min 10 listings)
    groups = groupby("district")
    price_by_district = {}
    for district, rows_ in groups.items():
        vals = [n for n in (num(r.get("unit_price")) for r in rows_) if n is not None]
        if len(vals) >= 10:
            price_by_district[district] = (mean(vals), len(vals))
    if price_by_district:
        highest = max(price_by_district, key=lambda d: price_by_district[d][0])
        lowest = min(price_by_district, key=lambda d: price_by_district[d][0])
        overview["highest_price_district"] = {
            "name": highest,
            "avg_unit_price": r2(price_by_district[highest][0]),
        }
        overview["lowest_price_district"] = {
            "name": lowest,
            "avg_unit_price": r2(price_by_district[lowest][0]),
        }

    subway = num_col("near_subway")
    if subway:
        overview["subway_coverage_pct"] = round(mean(subway) * 100, 1)

    layouts = value_counts("layout")
    overview["top_layouts"] = dict(list(layouts.items())[:8])

    overview["decoration_distribution"] = value_counts("decoration")

    return overview


@app.get("/api/listings")
async def get_listings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    district: str = Query(None),
    min_price: float = Query(None),
    max_price: float = Query(None),
    min_area: float = Query(None),
    max_area: float = Query(None),
    layout: str = Query(None),
    decoration: str = Query(None),
    orientation: str = Query(None),
    keyword: str = Query(None),
    sort_by: str = Query("total_price"),
    sort_order: str = Query("desc"),
):
    """Listings with filtering, sorting and pagination (pandas semantics)."""
    rows = get_rows()
    if not rows:
        return {"data": [], "total": 0, "page": page, "page_size": page_size}

    def contains(needle, haystack):
        return haystack not in (None, "") and needle in haystack

    filtered = []
    for row in rows:
        if district and not contains(district, row.get("district")):
            continue
        price = num(row.get("total_price"))
        if min_price is not None and (price is None or price < min_price):
            continue
        if max_price is not None and (price is None or price > max_price):
            continue
        area = num(row.get("floor_area"))
        if min_area is not None and (area is None or area < min_area):
            continue
        if max_area is not None and (area is None or area > max_area):
            continue
        if layout and not contains(layout, row.get("layout")):
            continue
        if decoration and not contains(decoration, row.get("decoration")):
            continue
        if orientation and not contains(orientation, row.get("orientation")):
            continue
        if keyword and not contains(keyword, row.get("community_name")):
            continue
        filtered.append(row)

    # Sort (missing values always last, like pandas sort_values)
    if sort_by in FLOAT_COLS | INT_COLS | {"floor"}:
        def sort_key(row):
            n = num(row.get(sort_by))
            missing = 0 if n is not None else 1
            value = n if n is not None else 0.0
            return (missing, -value if sort_order == "desc" else value)

        filtered.sort(key=sort_key)
    else:
        non_missing = [r for r in filtered if r.get(sort_by) not in (None, "")]
        missing = [r for r in filtered if r.get(sort_by) in (None, "")]
        non_missing.sort(key=lambda r: str(r.get(sort_by, "")), reverse=(sort_order == "desc"))
        filtered[:] = non_missing + missing

    total = len(filtered)
    start = (page - 1) * page_size
    page_data = filtered[start:start + page_size]

    display_cols = [
        "community_name", "district", "sub_district", "total_price",
        "unit_price", "floor_area", "layout", "floor", "orientation",
        "decoration", "building_age", "construction_year",
        "near_subway", "listing_time", "listing_link",
    ]

    result = []
    for row in page_data:
        item = {}
        for col in display_cols:
            if col not in row:
                continue
            v = row.get(col)
            if v in (None, ""):
                item[col] = None
            elif col in FLOAT_COLS:
                item[col] = num(v)
            elif col in INT_COLS:
                item[col] = int(num(v)) if num(v) is not None else None
            else:
                item[col] = v
        result.append(item)

    return {
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


@app.get("/api/districts")
async def get_districts():
    """Sorted list of districts."""
    return sorted(set(str_col("district")))


@app.get("/api/layouts")
async def get_layouts():
    """Top 20 layouts by count, sorted alphabetically."""
    top = list(value_counts("layout").keys())[:20]
    return sorted(top)


@app.get("/api/district-analysis")
async def get_district_analysis():
    """Per-district price statistics (same aggregation as the original)."""
    rows = get_rows()
    if not rows:
        return []

    groups = groupby("district")
    stats = {}
    for district, rows_ in groups.items():
        tp = [n for n in (num(r.get("total_price")) for r in rows_) if n is not None]
        up = [n for n in (num(r.get("unit_price")) for r in rows_) if n is not None]
        fa = [n for n in (num(r.get("floor_area")) for r in rows_) if n is not None]
        ba = [n for n in (num(r.get("building_age")) for r in rows_) if n is not None]
        stats[district] = {
            "district": district,
            "avg_total_price": r2(mean(tp)),
            "median_total_price": r2(median(tp)),
            "avg_unit_price": r2(mean(up)),
            "median_unit_price": r2(median(up)),
            "min_total_price": r2(min(tp)) if tp else None,
            "max_total_price": r2(max(tp)) if tp else None,
            "avg_area": r2(mean(fa)),
            "avg_building_age": r2(mean(ba)),
            "count": len(tp),
        }

    result = []
    for district, s in stats.items():
        s["pct_of_total"] = round(s["count"] / len(rows) * 100, 1)
        result.append(s)

    result.sort(key=lambda s: -s["avg_unit_price"])

    ordered = []
    for s in result:
        ordered.append({
            "district": s["district"],
            "avg_total_price": s["avg_total_price"],
            "median_total_price": s["median_total_price"],
            "avg_unit_price": s["avg_unit_price"],
            "median_unit_price": s["median_unit_price"],
            "min_total_price": s["min_total_price"],
            "max_total_price": s["max_total_price"],
            "avg_area": s["avg_area"],
            "avg_building_age": s["avg_building_age"],
            "count": s["count"],
            "pct_of_total": s["pct_of_total"],
        })
    return ordered


@app.get("/api/factor-analysis")
async def get_factor_analysis():
    """Correlation + regression results from the analysis pipeline."""
    results = _json(os.path.join(RESULTS_DIR, "analysis_results.json"), {})
    return {
        "correlation": results.get("correlation", {}),
        "regression": results.get("regression", {}),
    }


@app.get("/api/pca-analysis")
async def get_pca_analysis():
    """PCA / factor analysis results."""
    results = _json(os.path.join(RESULTS_DIR, "analysis_results.json"), {})
    return results.get("pca_factor", {})


@app.get("/api/cluster-analysis")
async def get_cluster_analysis():
    """Clustering results + per-cluster summary from labeled data."""
    results = _json(os.path.join(RESULTS_DIR, "analysis_results.json"), {})

    labeled_data = None
    labeled_path = os.path.join(RESULTS_DIR, "labeled_data.csv")
    if os.path.exists(labeled_path):
        clusters = {}
        with open(labeled_path, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                c = row.get("cluster")
                if c in (None, ""):
                    continue
                clusters.setdefault(c, []).append(row)
        summaries = []
        for c, rows_ in clusters.items():
            tp = [n for n in (num(r.get("total_price")) for r in rows_) if n is not None]
            up = [n for n in (num(r.get("unit_price")) for r in rows_) if n is not None]
            fa = [n for n in (num(r.get("floor_area")) for r in rows_) if n is not None]
            ba = [n for n in (num(r.get("building_age")) for r in rows_) if n is not None]
            summaries.append({
                "cluster": int(num(c)),
                "count": len(tp),
                "avg_total_price": r2(mean(tp)),
                "avg_unit_price": r2(mean(up)),
                "avg_area": r2(mean(fa)),
                "avg_building_age": r2(mean(ba)),
            })
        labeled_data = sorted(summaries, key=lambda s: s["cluster"])

    return {
        "clustering": results.get("clustering", {}),
        "discriminant": results.get("discriminant", {}),
        "cluster_summary": labeled_data,
    }


@app.get("/api/recommendations")
async def get_recommendations():
    """Home purchase suggestions (same content as the original backend)."""
    rows = get_rows()
    results = _json(os.path.join(RESULTS_DIR, "analysis_results.json"), {})
    recommendations = []

    prices = num_col("total_price")
    if prices:
        avg_price = mean(prices)
        recommendations.append({
            "title": "Hangzhou Second-hand Housing Market Overview",
            "content": f"The current average total price of second-hand housing in Hangzhou is approximately {avg_price:.0f} (10k RMB). "
                       f"Price differences between districts are significant. Choose based on your budget.",
            "icon": "overview",
        })

    groups = groupby("district")
    unit_by_district = {}
    for district, rows_ in groups.items():
        vals = [n for n in (num(r.get("unit_price")) for r in rows_) if n is not None]
        if vals:
            unit_by_district[district] = mean(vals)
    if unit_by_district:
        cheapest = min(unit_by_district, key=unit_by_district.get)
        recommendations.append({
            "title": "Best Value District",
            "content": f"The district with the lowest unit price is {cheapest}, suitable for budget-conscious buyers. "
                       f"Consider commuting costs and amenities comprehensively.",
            "icon": "district",
        })

    areas = [n for n in (num(r.get("floor_area")) for r in rows) if n is not None]
    small_prices = [num(r.get("total_price")) for r in rows
                    if num(r.get("floor_area")) is not None
                    and num(r.get("floor_area")) < 90
                    and num(r.get("total_price")) is not None]
    if small_prices and prices:
        recommendations.append({
            "title": "Unit Size Recommendation",
            "content": f"Listings under 90sqm have an average total price of {mean(small_prices):.0f} (10k RMB), "
                       f"accounting for {len(small_prices)/len(prices)*100:.1f}% of all listings. "
                       f"Compact units are ideal entry-level choices with manageable total costs.",
            "icon": "area",
        })

    new_up, old_up = [], []
    for r in rows:
        age = num(r.get("building_age"))
        up = num(r.get("unit_price"))
        if age is None or up is None:
            continue
        if age <= 10:
            new_up.append(up)
        elif age > 20:
            old_up.append(up)
    if new_up and old_up:
        recommendations.append({
            "title": "Building Age vs Price",
            "content": f"Newer homes (within 10 years) average {mean(new_up):.0f} RMB/sqm, "
                       f"while older homes (20+ years) average {mean(old_up):.0f} RMB/sqm. "
                       f"Newer homes cost about {(mean(new_up)/mean(old_up)-1)*100:.0f}% more per sqm.",
            "icon": "age",
        })

    ridge = results.get("regression", {}).get("ridge", {})
    if ridge and "top_features" in ridge and ridge["top_features"]:
        top = ridge["top_features"][:3]
        features_text = ", ".join([f"{f['feature']}" for f in top])
        recommendations.append({
            "title": "Key Price Factors",
            "content": f"Regression analysis shows the top factors affecting price are: {features_text}. "
                       f"Model fit: R² = {ridge.get('r_squared', 'N/A')}.",
            "icon": "model",
        })

    if any(r.get("listing_time") not in (None, "") for r in rows):
        recommendations.append({
            "title": "Purchase Timing Advice",
            "content": "Pay attention to periods with high listing volumes for more choices. "
                       "Spring and autumn are typically active seasons for second-hand housing transactions. "
                       "Compare historical transaction prices in the same community and unit type.",
            "icon": "timing",
        })

    recommendations.append({
        "title": "Comprehensive Buying Guide",
        "content": "1) Prioritize: commute time, school district, unit size, building age; "
                   "2) Visit the community in person to assess environment and amenities; "
                   "3) Properties near subway lines have stronger appreciation potential; "
                   "4) Compare multiple communities in the same area for best value; "
                   "5) Older communities are cheaper but factor in renovation costs and mortgage term limits.",
        "icon": "general",
    })

    return {"recommendations": recommendations, "generated_at": "2026-06-08"}


@app.get("/api/charts")
async def get_charts():
    """Chart registry with deployment-relative paths."""
    registry = _json(CHART_REGISTRY_PATH, {})
    for chart_id, info in registry.items():
        if isinstance(info, dict) and "path" in info:
            info["path"] = f"/charts/{chart_id}.html"
    return registry


@app.get("/api/chart-data/{chart_id}")
async def get_chart_data(chart_id: str):
    """Chart payloads: heavy ones precomputed, simple ones computed here."""
    rows = get_rows()

    # ---- Precomputed payloads (exact original output) ----
    static_path = os.path.join(STATIC_DIR, f"chart_{chart_id}.json")
    if os.path.exists(static_path):
        return _json(static_path)

    # ---- Simple charts computed in pure Python ----

    if chart_id == "district_avg_unit_price":
        groups = groupby("district")
        entries = []
        for district, rows_ in groups.items():
            vals = [n for n in (num(r.get("unit_price")) for r in rows_) if n is not None]
            if len(vals) >= 10:
                entries.append((district, mean(vals)))
        entries.sort(key=lambda e: e[1])
        return {
            "type": "bar",
            "title": "Avg Unit Price by District",
            "x": [e[0] for e in entries],
            "y": [r0(e[1]) for e in entries],
            "labels": [e[0] for e in entries],
            "horizontal": True,
        }

    if chart_id == "total_price_distribution":
        prices = num_col("total_price")
        if not prices:
            return []
        lo, hi = min(prices), max(prices)
        edges = [lo + (hi - lo) * i / 20.0 for i in range(21)]
        counts = [0] * 20
        for p in prices:
            for i in range(19):
                if edges[i] <= p < edges[i + 1]:
                    counts[i] += 1
                    break
            else:
                if edges[19] <= p <= edges[20]:
                    counts[19] += 1
        return {
            "type": "bar",
            "title": "Total Price Distribution",
            "x": [f"{edges[i]:.0f}-{edges[i+1]:.0f}" for i in range(20)],
            "y": counts,
        }

    if chart_id == "avg_price_by_layout":
        groups = groupby("layout")
        entries = []
        for layout_name, rows_ in groups.items():
            vals = [n for n in (num(r.get("total_price")) for r in rows_) if n is not None]
            if len(vals) >= 10:
                entries.append((layout_name, mean(vals)))
        entries.sort(key=lambda e: e[1])
        return {
            "type": "bar",
            "title": "Avg Total Price by Layout",
            "x": [e[0] for e in entries],
            "y": [r0(e[1]) for e in entries],
            "horizontal": True,
        }

    if chart_id == "avg_price_by_decoration":
        order = ["Unfinished", "Simple", "Medium", "Fine", "Luxury", "Other"]
        groups = groupby("decoration")
        means = {}
        for decoration, rows_ in groups.items():
            vals = [n for n in (num(r.get("unit_price")) for r in rows_) if n is not None]
            if vals:
                means[decoration] = mean(vals)
        available = [d for d in order if d in means]
        return {
            "type": "bar",
            "title": "Decoration vs Avg Unit Price",
            "x": available,
            "y": [r0(means[d]) for d in available],
        }

    return {"error": "Chart not found"}


@app.get("/api/stats/descriptive")
async def get_descriptive_stats():
    """Descriptive statistics (precomputed with the original analyzer)."""
    return _json(os.path.join(STATIC_DIR, "descriptive_stats.json"), {})


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "listings_count": len(get_rows())}


# Vercel Python runtime entry point
handler = Mangum(app)
