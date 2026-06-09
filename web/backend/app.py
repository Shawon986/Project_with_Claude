# Hangzhou Second-hand Housing Analysis - FastAPI Backend
# =========================================================

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
import pandas as pd
import numpy as np

from config import SERVER

app = FastAPI(
    title="Hangzhou Second-hand Housing Analysis System",
    description="Hangzhou Second-hand Housing Price Analysis System",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# DATA LOADING
# ============================================================

# Determine project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Find latest cleaned data
CLEANED_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")
CHART_DIR = os.path.join(PROJECT_ROOT, "charts")
ANALYSIS_DIR = os.path.join(PROJECT_ROOT, "analysis", "results")

# Global dataframe cache
df_cache = None
analysis_cache = None


def get_dataframe():
    """Load or return cached dataframe"""
    global df_cache
    if df_cache is not None:
        return df_cache

    if os.path.exists(CLEANED_DIR):
        csv_files = [f for f in os.listdir(CLEANED_DIR) if f.endswith(".csv")]
        if csv_files:
            # Get the most recent file
            csv_files.sort(reverse=True)
            path = os.path.join(CLEANED_DIR, csv_files[0])
            df_cache = pd.read_csv(path)
            print(f"Loaded {len(df_cache)} records from {path}")
            return df_cache

    # Try to load from raw data
    raw_dir = os.path.join(PROJECT_ROOT, "data", "raw")
    if os.path.exists(raw_dir):
        csv_files = [f for f in os.listdir(raw_dir) if f.endswith(".csv")]
        if csv_files:
            csv_files.sort(reverse=True)
            path = os.path.join(raw_dir, csv_files[0])
            df_cache = pd.read_csv(path)
            print(f"Loaded {len(df_cache)} raw records from {path}")
            return df_cache

    # Return empty dataframe if no data
    print("[WARN] No data files found")
    df_cache = pd.DataFrame()
    return df_cache


def get_analysis_results():
    """Load cached analysis results"""
    global analysis_cache
    if analysis_cache is not None:
        return analysis_cache

    results_path = os.path.join(ANALYSIS_DIR, "analysis_results.json")
    if os.path.exists(results_path):
        with open(results_path, "r", encoding="utf-8") as f:
            analysis_cache = json.load(f)
        return analysis_cache

    return {}


# ============================================================
# API ROUTES
# ============================================================

@app.get("/api/overview")
async def get_overview():
    """
    Homepage data overview:
    Total listings, avg price, avg unit price, highest unit price district, etc.
    """
    df = get_dataframe()
    if len(df) == 0:
        return {"error": "No data available", "total_listings": 0}

    overview = {
        "total_listings": int(len(df)),
    }

    if "district" in df.columns:
        overview["total_districts"] = int(df["district"].nunique())
    if "community_name" in df.columns:
        overview["total_communities"] = int(df["community_name"].nunique())

    if "total_price" in df.columns:
        prices = df["total_price"].dropna()
        overview["avg_total_price"] = round(float(prices.mean()), 2)
        overview["median_total_price"] = round(float(prices.median()), 2)
        overview["min_total_price"] = round(float(prices.min()), 2)
        overview["max_total_price"] = round(float(prices.max()), 2)

    if "unit_price" in df.columns:
        unit_prices = df["unit_price"].dropna()
        overview["avg_unit_price"] = round(float(unit_prices.mean()), 2)
        overview["median_unit_price"] = round(float(unit_prices.median()), 2)
        overview["min_unit_price"] = round(float(unit_prices.min()), 2)
        overview["max_unit_price"] = round(float(unit_prices.max()), 2)

    if "floor_area" in df.columns:
        areas = df["floor_area"].dropna()
        overview["avg_area"] = round(float(areas.mean()), 2)
        overview["median_area"] = round(float(areas.median()), 2)

    if "building_age" in df.columns:
        ages = df["building_age"].dropna()
        overview["avg_building_age"] = round(float(ages.mean()), 2)

    # Highest/Lowest unit price district
    if "district" in df.columns and "unit_price" in df.columns:
        district_prices = df.groupby("district")["unit_price"].agg(["mean", "count"]).round(2)
        district_prices = district_prices[district_prices["count"] >= 10]
        if len(district_prices) > 0:
            highest = district_prices["mean"].idxmax()
            lowest = district_prices["mean"].idxmin()
            overview["highest_price_district"] = {
                "name": highest,
                "avg_unit_price": round(float(district_prices.loc[highest, "mean"]), 2),
            }
            overview["lowest_price_district"] = {
                "name": lowest,
                "avg_unit_price": round(float(district_prices.loc[lowest, "mean"]), 2),
            }

    # Subway coverage
    if "near_subway" in df.columns:
        overview["subway_coverage_pct"] = round(float(df["near_subway"].mean() * 100), 1)

    # Layout distribution
    if "layout" in df.columns:
        top_layouts = df["layout"].value_counts().head(8).to_dict()
        overview["top_layouts"] = {str(k): int(v) for k, v in top_layouts.items()}

    # Decoration distribution
    if "decoration" in df.columns:
        dec_dist = df["decoration"].value_counts().to_dict()
        overview["decoration_distribution"] = {str(k): int(v) for k, v in dec_dist.items()}

    return overview


@app.get("/api/listings")
async def get_listings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    district: str = Query(None, description="Filter by district"),
    min_price: float = Query(None, description="Minimum total price"),
    max_price: float = Query(None, description="Maximum total price"),
    min_area: float = Query(None, description="Minimum floor area"),
    max_area: float = Query(None, description="Maximum floor area"),
    layout: str = Query(None, description="Filter by layout (e.g., 3室2厅)"),
    decoration: str = Query(None, description="Filter by decoration"),
    orientation: str = Query(None, description="Filter by orientation"),
    keyword: str = Query(None, description="Search keyword (community name)"),
    sort_by: str = Query("total_price", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
):
    """
    Listing data list with filtering, sorting, and pagination.
    """
    df = get_dataframe()
    if len(df) == 0:
        return {"data": [], "total": 0, "page": page, "page_size": page_size}

    filtered = df.copy()

    # Apply filters
    if district:
        filtered = filtered[filtered["district"].str.contains(district, na=False)]
    if min_price is not None:
        filtered = filtered[filtered["total_price"] >= min_price]
    if max_price is not None:
        filtered = filtered[filtered["total_price"] <= max_price]
    if min_area is not None:
        filtered = filtered[filtered["floor_area"] >= min_area]
    if max_area is not None:
        filtered = filtered[filtered["floor_area"] <= max_area]
    if layout:
        filtered = filtered[filtered.get("layout", pd.Series(dtype=str)).str.contains(layout, na=False)]
    if decoration:
        filtered = filtered[filtered.get("decoration", pd.Series(dtype=str)).str.contains(decoration, na=False)]
    if orientation:
        filtered = filtered[filtered.get("orientation", pd.Series(dtype=str)).str.contains(orientation, na=False)]
    if keyword:
        if "community_name" in filtered.columns:
            filtered = filtered[filtered["community_name"].str.contains(keyword, na=False)]

    # Sort
    if sort_by in filtered.columns:
        ascending = sort_order == "asc"
        filtered = filtered.sort_values(sort_by, ascending=ascending)

    # Paginate
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    page_data = filtered.iloc[start:end]

    # Select display columns
    display_cols = [
        "community_name", "district", "sub_district", "total_price",
        "unit_price", "floor_area", "layout", "floor", "orientation",
        "decoration", "building_age", "construction_year",
        "near_subway", "listing_time", "listing_link",
    ]
    available_cols = [c for c in display_cols if c in page_data.columns]
    result = page_data[available_cols].to_dict(orient="records")

    # Clean NaN values
    for item in result:
        for k, v in item.items():
            if isinstance(v, float) and np.isnan(v):
                item[k] = None

    return {
        "data": result,
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


@app.get("/api/districts")
async def get_districts():
    """Get list of districts"""
    df = get_dataframe()
    if "district" not in df.columns:
        return []
    return sorted(df["district"].dropna().unique().tolist())


@app.get("/api/layouts")
async def get_layouts():
    """Get list of layouts"""
    df = get_dataframe()
    if "layout" not in df.columns:
        return []
    top = df["layout"].value_counts().head(20).index.tolist()
    return sorted(top)


@app.get("/api/district-analysis")
async def get_district_analysis():
    """
    Regional housing price analysis:
    Average unit price by district, listing count and price distribution by district.
    """
    df = get_dataframe()
    if "district" not in df.columns or "unit_price" not in df.columns:
        return []

    grouped = df.groupby("district").agg(
        avg_total_price=("total_price", "mean"),
        median_total_price=("total_price", "median"),
        avg_unit_price=("unit_price", "mean"),
        median_unit_price=("unit_price", "median"),
        min_total_price=("total_price", "min"),
        max_total_price=("total_price", "max"),
        avg_area=("floor_area", "mean"),
        avg_building_age=("building_age", "mean"),
        count=("total_price", "count"),
    ).round(2)

    grouped["pct_of_total"] = (grouped["count"] / len(df) * 100).round(1)
    grouped = grouped.sort_values("avg_unit_price", ascending=False)

    return grouped.reset_index().to_dict(orient="records")


@app.get("/api/factor-analysis")
async def get_factor_analysis():
    """
    Housing price factor analysis:
    Relationship between factors and housing price.
    """
    results = get_analysis_results()
    return {
        "correlation": results.get("correlation", {}),
        "regression": results.get("regression", {}),
    }


@app.get("/api/pca-analysis")
async def get_pca_analysis():
    """PCA/Factor analysis results"""
    results = get_analysis_results()
    return results.get("pca_factor", {})


@app.get("/api/cluster-analysis")
async def get_cluster_analysis():
    """Cluster analysis results"""
    results = get_analysis_results()

    # Also load labeled data
    labeled_path = os.path.join(ANALYSIS_DIR, "labeled_data.csv")
    labeled_data = None
    if os.path.exists(labeled_path):
        labeled = pd.read_csv(labeled_path)
        # Return summary by cluster
        if "cluster" in labeled.columns:
            cluster_summary = labeled.groupby("cluster").agg(
                count=("total_price", "count"),
                avg_total_price=("total_price", "mean"),
                avg_unit_price=("unit_price", "mean"),
                avg_area=("floor_area", "mean"),
                avg_building_age=("building_age", "mean"),
            ).round(2)
            labeled_data = cluster_summary.reset_index().to_dict(orient="records")

    return {
        "clustering": results.get("clustering", {}),
        "discriminant": results.get("discriminant", {}),
        "cluster_summary": labeled_data,
    }


@app.get("/api/recommendations")
async def get_recommendations():
    """
    Home purchase reference suggestions based on analysis results.
    """
    df = get_dataframe()
    results = get_analysis_results()

    recommendations = []

    # 1. Price overview
    if "total_price" in df.columns and "district" in df.columns:
        avg_price = df["total_price"].mean()
        recommendations.append({
            "title": "Hangzhou Second-hand Housing Market Overview",
            "content": f"The current average total price of second-hand housing in Hangzhou is approximately {avg_price:.0f} (10k RMB). "
                      f"Price differences between districts are significant. Choose based on your budget.",
            "icon": "overview",
        })

    # 2. District recommendation
    if "district" in df.columns and "unit_price" in df.columns:
        district_prices = df.groupby("district")["unit_price"].mean().sort_values()
        if len(district_prices) > 0:
            cheapest = district_prices.index[0]
            recommendations.append({
                "title": "Best Value District",
                "content": f"The district with the lowest unit price is {cheapest}, suitable for budget-conscious buyers. "
                          f"Consider commuting costs and amenities comprehensively.",
                "icon": "district",
            })

    # 3. Area recommendation
    if "floor_area" in df.columns and "total_price" in df.columns:
        small = df[df["floor_area"] < 90]
        if len(small) > 0:
            recommendations.append({
                "title": "Unit Size Recommendation",
                "content": f"Listings under 90sqm have an average total price of {small['total_price'].mean():.0f} (10k RMB), "
                          f"accounting for {len(small)/len(df)*100:.1f}% of all listings. "
                          f"Compact units are ideal entry-level choices with manageable total costs.",
                "icon": "area",
            })

    # 4. Building age analysis
    if "building_age" in df.columns:
        new = df[df["building_age"] <= 10]
        old = df[df["building_age"] > 20]
        if len(new) > 0 and len(old) > 0:
            recommendations.append({
                "title": "Building Age vs Price",
                "content": f"Newer homes (within 10 years) average {new['unit_price'].mean():.0f} RMB/sqm, "
                          f"while older homes (20+ years) average {old['unit_price'].mean():.0f} RMB/sqm. "
                          f"Newer homes cost about {(new['unit_price'].mean()/old['unit_price'].mean()-1)*100:.0f}% more per sqm.",
                "icon": "age",
            })

    # 5. Regression insights
    regression = results.get("regression", {})
    ridge = regression.get("ridge", {})
    if ridge and "top_features" in ridge:
        top = ridge["top_features"][:3]
        features_text = ", ".join([f"{f['feature']}" for f in top])
        recommendations.append({
            "title": "Key Price Factors",
            "content": f"Regression analysis shows the top factors affecting price are: {features_text}. "
                      f"Model fit: R² = {ridge.get('r_squared', 'N/A')}.",
            "icon": "model",
        })

    # 6. Timing advice
    if "listing_time" in df.columns:
        recommendations.append({
            "title": "Purchase Timing Advice",
            "content": "Pay attention to periods with high listing volumes for more choices. "
                      "Spring and autumn are typically active seasons for second-hand housing transactions. "
                      "Compare historical transaction prices in the same community and unit type.",
            "icon": "timing",
        })

    # 7. General advice
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
    """Get list of available charts"""
    chart_registry = os.path.join(CHART_DIR, "chart_registry.json")
    if os.path.exists(chart_registry):
        with open(chart_registry, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@app.get("/api/chart-data/{chart_id}")
async def get_chart_data(chart_id: str):
    """
    Get specific chart data for frontend rendering.
    Returns either the HTML file content or structured data.
    """
    df = get_dataframe()

    # Return structured data for each chart type
    if chart_id == "district_avg_unit_price":
        if "district" not in df.columns:
            return []
        grouped = df.groupby("district").agg(
            avg_unit_price=("unit_price", "mean"),
            count=("total_price", "count"),
        ).round(0)
        grouped = grouped[grouped["count"] >= 10].sort_values("avg_unit_price", ascending=True)
        return {
            "type": "bar",
            "title": "Avg Unit Price by District",
            "x": grouped.index.tolist(),
            "y": grouped["avg_unit_price"].tolist(),
            "labels": grouped.index.tolist(),
            "horizontal": True,
        }

    elif chart_id == "total_price_distribution":
        if "total_price" not in df.columns:
            return []
        prices = df["total_price"].dropna()
        hist, bins = np.histogram(prices, bins=20)
        return {
            "type": "bar",
            "title": "Total Price Distribution",
            "x": [f"{bins[i]:.0f}-{bins[i+1]:.0f}" for i in range(len(bins)-1)],
            "y": hist.tolist(),
        }

    elif chart_id == "area_vs_total_price":
        if "floor_area" not in df.columns or "total_price" not in df.columns:
            return []
        data = df[["floor_area", "total_price"]].dropna()
        if len(data) > 3000:
            data = data.sample(3000, random_state=42)
        return {
            "type": "scatter",
            "title": "Floor Area vs Total Price",
            "data": [{"x": float(row["floor_area"]), "y": float(row["total_price"])}
                     for _, row in data.iterrows()],
            "xLabel": "Floor Area (sqm)",
            "yLabel": "Total Price (10k RMB)",
        }

    elif chart_id == "building_age_vs_unit_price":
        if "building_age" not in df.columns or "unit_price" not in df.columns:
            return []
        data = df[["building_age", "unit_price"]].dropna()
        if len(data) > 3000:
            data = data.sample(3000, random_state=42)
        return {
            "type": "scatter",
            "title": "Building Age vs Unit Price",
            "data": [{"x": float(row["building_age"]), "y": float(row["unit_price"])}
                     for _, row in data.iterrows()],
            "xLabel": "Building Age (years)",
            "yLabel": "Unit Price (RMB/sqm)",
        }

    elif chart_id == "avg_price_by_layout":
        if "layout" not in df.columns:
            return []
        grouped = df.groupby("layout").agg(
            avg_price=("total_price", "mean"),
            count=("total_price", "count"),
        ).round(0)
        grouped = grouped[grouped["count"] >= 10].sort_values("avg_price", ascending=True)
        return {
            "type": "bar",
            "title": "Avg Total Price by Layout",
            "x": grouped.index.tolist(),
            "y": grouped["avg_price"].tolist(),
            "horizontal": True,
        }

    elif chart_id == "avg_price_by_decoration":
        if "decoration" not in df.columns:
            return []
        order = ["Unfinished", "Simple", "Medium", "Fine", "Luxury", "Other"]
        grouped = df.groupby("decoration")["unit_price"].mean().round(0)
        available = [d for d in order if d in grouped.index]
        values = [float(grouped[d]) for d in available]
        return {
            "type": "bar",
            "title": "Decoration vs Avg Unit Price",
            "x": available,
            "y": values,
        }

    elif chart_id == "correlation_heatmap":
        numeric_cols = [
            "total_price", "unit_price", "floor_area", "rooms", "halls",
            "total_floors", "building_age", "decoration_level",
            "floor_type_encoded", "orientation_south", "near_subway",
        ]
        available = [c for c in numeric_cols if c in df.columns]
        corr = df[available].corr().round(3)
        label_map = {
            "total_price": "Total Price", "unit_price": "Unit Price", "floor_area": "Floor Area",
            "rooms": "Bedrooms", "halls": "Living Rooms", "total_floors": "Total Floors",
            "building_age": "Building Age", "decoration_level": "Decoration Level",
            "floor_type_encoded": "Floor Type", "orientation_south": "South-facing",
            "near_subway": "Near Subway",
        }
        labels = [label_map.get(c, c) for c in corr.columns]
        heatmap_data = []
        for i, row_name in enumerate(corr.index):
            for j, col_name in enumerate(corr.columns):
                heatmap_data.append([j, i, float(corr.iloc[i, j])])
        return {
            "type": "heatmap",
            "title": "Correlation Heatmap",
            "xLabels": labels,
            "yLabels": labels,
            "data": heatmap_data,
            "min": -1,
            "max": 1,
        }

    elif chart_id == "regression_results":
        from sklearn.linear_model import LinearRegression
        feature_cols = [
            "floor_area", "rooms", "halls", "total_floors",
            "building_age", "decoration_level", "floor_type_encoded",
            "orientation_south", "near_subway", "floor_ratio",
        ]
        district_cols = [c for c in df.columns if c.startswith("district_")]
        available = [c for c in feature_cols + district_cols if c in df.columns]
        if "total_price" not in df.columns:
            return {"error": "Missing total_price"}
        X = df[available].fillna(0)
        y = df["total_price"].dropna()
        X = X.loc[y.index]
        model = LinearRegression()
        model.fit(X, y)
        importance = sorted(
            [{"feature": f, "coefficient": round(float(c), 4)} for f, c in zip(X.columns, model.coef_)],
            key=lambda x: abs(x["coefficient"]), reverse=True
        )[:15]
        label_map = {
            "floor_area": "Floor Area", "rooms": "Bedrooms", "halls": "Living Rooms",
            "total_floors": "Total Floors", "building_age": "Building Age",
            "decoration_level": "Decoration Level", "floor_type_encoded": "Floor Type",
            "orientation_south": "South-facing", "near_subway": "Near Subway",
            "floor_ratio": "Floor Ratio",
        }
        return {
            "type": "bar",
            "title": "Regression Coefficients",
            "x": [label_map.get(f["feature"], f["feature"].replace("district_", "")) for f in reversed(importance)],
            "y": [f["coefficient"] for f in reversed(importance)],
            "horizontal": True,
        }

    elif chart_id == "pca_factor_scores":
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        exclude = [c for c in numeric_cols if c.startswith("district_") or c in ["id"]]
        feature_cols = [c for c in numeric_cols if c not in exclude]
        data = df[feature_cols].dropna()
        X = StandardScaler().fit_transform(data)
        pca = PCA(n_components=min(5, len(feature_cols)))
        pca.fit(X)
        explained = [round(float(v), 4) for v in pca.explained_variance_ratio_]
        cumulative = [round(float(v), 4) for v in np.cumsum(explained)]
        pcs = [f"PC{i+1}" for i in range(len(explained))]
        return {
            "type": "bar",
            "title": "PCA Explained Variance",
            "x": pcs,
            "y": explained,
            "extraLine": cumulative,
            "extraLabel": "Cumulative",
        }

    elif chart_id == "cluster_results":
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        features = ["total_price", "floor_area", "unit_price"]
        available = [c for c in features if c in df.columns]
        X = df[available].dropna()
        X_scaled = StandardScaler().fit_transform(X)
        n_clusters = 5
        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        colors = ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de"]
        series_data = []
        for i in range(n_clusters):
            cluster_pts = X[labels == i]
            if len(cluster_pts) > 800:
                cluster_pts = cluster_pts.sample(800, random_state=42)
            series_data.append({
                "name": f"Cluster {i+1}",
                "data": [{"x": float(r["floor_area"]), "y": float(r["total_price"])}
                         for _, r in cluster_pts.iterrows()],
                "color": colors[i % len(colors)],
            })
        return {
            "type": "multi-scatter",
            "title": "Clustering Results (Area vs Total Price)",
            "xLabel": "Floor Area (sqm)",
            "yLabel": "Total Price (10k RMB)",
            "series": series_data,
        }

    # Default: return HTML chart file if it exists
    chart_path = os.path.join(CHART_DIR, f"{chart_id}.html")
    if os.path.exists(chart_path):
        with open(chart_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    return {"error": "Chart not found"}


@app.get("/api/stats/descriptive")
async def get_descriptive_stats():
    """Descriptive statistics"""
    from analysis.descriptive_stats import DescriptiveAnalyzer
    df = get_dataframe()
    if len(df) == 0:
        return {}
    analyzer = DescriptiveAnalyzer(df)
    return analyzer.analyze_all()


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "listings_count": len(get_dataframe())}


# ============================================================
# STATIC FILES & FRONTEND
# ============================================================

# Serve chart files
if os.path.exists(CHART_DIR):
    app.mount("/charts", StaticFiles(directory=CHART_DIR), name="charts")

# Serve frontend (if built)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "web", "frontend", "dist")
if os.path.exists(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str = ""):
        """Serve Vue frontend SPA"""
        file_path = os.path.join(FRONTEND_DIR, full_path) if full_path else os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import uvicorn
    print(f"Starting Hangzhou Housing Analysis Server...")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Data records: {len(get_dataframe())}")
    uvicorn.run(
        "app:app",
        host=SERVER["host"],
        port=SERVER["port"],
        reload=SERVER["reload"],
    )
