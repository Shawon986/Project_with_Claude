# Chart Generator Module
# ======================
# Generates all required charts using pyecharts for server-side rendering

import pandas as pd
import numpy as np
import json
import os
import sys
import io

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Scatter, HeatMap, Pie, Boxplot
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType


class ChartGenerator:
    """Generate all required visualization charts"""

    def __init__(self, df, output_dir=None):
        self.df = df
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "charts")
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.charts = {}

    def generate_all(self):
        """Generate all required charts"""
        print("Generating all charts...")

        charts_to_generate = [
            ("district_avg_unit_price", "Avg Unit Price by District", self.chart_district_avg_price),
            ("total_price_distribution", "Total Price Distribution", self.chart_price_distribution),
            ("area_vs_total_price", "Area vs Total Price Scatter", self.chart_area_vs_price),
            ("building_age_vs_unit_price", "Building Age vs Unit Price Scatter", self.chart_age_vs_price),
            ("avg_price_by_layout", "Avg Total Price by Layout", self.chart_layout_avg_price),
            ("avg_price_by_decoration", "Avg Unit Price by Decoration", self.chart_decoration_avg_price),
            ("correlation_heatmap", "Correlation Heatmap", self.chart_correlation_heatmap),
            ("regression_results", "Regression Model Results", self.chart_regression_results),
            ("pca_factor_scores", "PCA / Factor Score Chart", self.chart_pca_scores),
            ("cluster_results", "Clustering Results", self.chart_cluster_results),
        ]

        for chart_id, chart_name, generator in charts_to_generate:
            try:
                print(f"  Generating: {chart_name}")
                chart = generator()
                path = os.path.join(self.output_dir, f"{chart_id}.html")
                chart.render(path)
                self.charts[chart_id] = {
                    "name": chart_name,
                    "path": path,
                    "id": chart_id,
                }
            except Exception as e:
                print(f"  [WARN] Failed to generate {chart_name}: {e}")
                self.charts[chart_id] = {
                    "name": chart_name,
                    "error": str(e),
                    "id": chart_id,
                }

        # Save chart registry
        registry_path = os.path.join(self.output_dir, "chart_registry.json")
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(self.charts, f, ensure_ascii=False, indent=2)

        print(f"All charts generated in {self.output_dir}")
        return self.charts

    def chart_district_avg_price(self):
        """1. Bar chart: Average unit price by district"""
        if "district" not in self.df.columns or "unit_price" not in self.df.columns:
            raise ValueError("Missing district or unit_price columns")

        grouped = self.df.groupby("district")["unit_price"].agg(["mean", "count"]).round(0)
        grouped = grouped.sort_values("mean", ascending=True)
        grouped = grouped[grouped["count"] >= 10]

        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.ESSOS, width="900px", height="500px"))
            .add_xaxis(grouped.index.tolist())
            .add_yaxis(
                "Avg Unit Price (RMB/sqm)",
                grouped["mean"].tolist(),
                itemstyle_opts=opts.ItemStyleOpts(color="#c23531"),
                label_opts=opts.LabelOpts(position="right", formatter="{c}"),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Hangzhou Avg Unit Price by District", subtitle="Source: Lianjia"),
                xaxis_opts=opts.AxisOpts(name="District"),
                yaxis_opts=opts.AxisOpts(name="Avg Unit Price (RMB/sqm)"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
            .reversal_axis()
        )
        return bar

    def chart_price_distribution(self):
        """2. Histogram: Total price distribution"""
        if "total_price" not in self.df.columns:
            raise ValueError("Missing total_price column")

        prices = self.df["total_price"].dropna()
        hist, bins = np.histogram(prices, bins=30)

        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.ESSOS, width="900px", height="500px"))
            .add_xaxis([f"{bins[i]:.0f}-{bins[i+1]:.0f} (10k)" for i in range(len(bins)-1)])
            .add_yaxis(
                "Number of Listings",
                hist.tolist(),
                itemstyle_opts=opts.ItemStyleOpts(color="#2f4554"),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Hangzhou Second-hand Housing Total Price Distribution",
                                         subtitle=f"Total: {len(prices)} listings"),
                xaxis_opts=opts.AxisOpts(name="Total Price Range (10k RMB)", axislabel_opts=opts.LabelOpts(rotate=45)),
                yaxis_opts=opts.AxisOpts(name="Number of Listings"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
        )
        return bar

    def chart_area_vs_price(self):
        """3. Scatter: Floor area vs total price"""
        if "floor_area" not in self.df.columns or "total_price" not in self.df.columns:
            raise ValueError("Missing floor_area or total_price")

        data = self.df[["floor_area", "total_price"]].dropna()
        if len(data) > 5000:
            data = data.sample(5000, random_state=42)

        scatter = (
            Scatter(init_opts=opts.InitOpts(theme=ThemeType.ESSOS, width="900px", height="500px"))
            .add_xaxis(data["floor_area"].tolist())
            .add_yaxis(
                "Total Price (10k RMB)",
                data["total_price"].tolist(),
                symbol_size=6,
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Floor Area vs Total Price"),
                xaxis_opts=opts.AxisOpts(name="Floor Area (sqm)"),
                yaxis_opts=opts.AxisOpts(name="Total Price (10k RMB)"),
                tooltip_opts=opts.TooltipOpts(trigger="item",
                    formatter="Area: {c1} sqm<br/>Total Price: {c2} (10k RMB)"),
            )
        )
        return scatter

    def chart_age_vs_price(self):
        """4. Scatter: Building age vs unit price"""
        if "building_age" not in self.df.columns or "unit_price" not in self.df.columns:
            raise ValueError("Missing building_age or unit_price")

        data = self.df[["building_age", "unit_price"]].dropna()
        if len(data) > 5000:
            data = data.sample(5000, random_state=42)

        scatter = (
            Scatter(init_opts=opts.InitOpts(theme=ThemeType.ESSOS, width="900px", height="500px"))
            .add_xaxis(data["building_age"].tolist())
            .add_yaxis(
                "Unit Price (RMB/sqm)",
                data["unit_price"].tolist(),
                symbol_size=6,
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Building Age vs Unit Price"),
                xaxis_opts=opts.AxisOpts(name="Building Age (years)"),
                yaxis_opts=opts.AxisOpts(name="Unit Price (RMB/sqm)"),
                tooltip_opts=opts.TooltipOpts(trigger="item",
                    formatter="Age: {c1} years<br/>Unit Price: {c2} RMB/sqm"),
            )
        )
        return scatter

    def chart_layout_avg_price(self):
        """5. Bar chart: Average total price by layout"""
        if "layout" not in self.df.columns or "total_price" not in self.df.columns:
            raise ValueError("Missing layout or total_price")

        grouped = self.df.groupby("layout").agg(
            avg_price=("total_price", "mean"),
            count=("total_price", "count"),
        ).round(0)
        grouped = grouped[grouped["count"] >= 10]
        grouped = grouped.sort_values("avg_price", ascending=True)

        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.ESSOS, width="900px", height="500px"))
            .add_xaxis(grouped.index.tolist())
            .add_yaxis(
                "Avg Total Price (10k RMB)",
                grouped["avg_price"].tolist(),
                itemstyle_opts=opts.ItemStyleOpts(color="#61a0a8"),
                label_opts=opts.LabelOpts(position="right"),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Average Total Price by Layout"),
                xaxis_opts=opts.AxisOpts(name="Layout"),
                yaxis_opts=opts.AxisOpts(name="Avg Total Price (10k RMB)"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
            .reversal_axis()
        )
        return bar

    def chart_decoration_avg_price(self):
        """6. Bar chart: Average unit price by decoration"""
        if "decoration" not in self.df.columns or "unit_price" not in self.df.columns:
            raise ValueError("Missing decoration or unit_price")

        order = ["Unfinished", "Simple", "Medium", "Fine", "Luxury", "Other"]
        grouped = self.df.groupby("decoration")["unit_price"].mean().round(0)
        available = [d for d in order if d in grouped.index]
        values = [grouped[d] for d in available]

        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.ESSOS, width="900px", height="500px"))
            .add_xaxis(available)
            .add_yaxis(
                "Avg Unit Price (RMB/sqm)",
                values,
                itemstyle_opts=opts.ItemStyleOpts(color="#d48265"),
                label_opts=opts.LabelOpts(position="top", formatter="{c}"),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Average Unit Price by Decoration Status"),
                xaxis_opts=opts.AxisOpts(name="Decoration Status"),
                yaxis_opts=opts.AxisOpts(name="Avg Unit Price (RMB/sqm)"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
        )
        return bar

    def chart_correlation_heatmap(self):
        """7. Heatmap: Housing price influencing factor correlations"""
        numeric_cols = [
            "total_price", "unit_price", "floor_area", "rooms", "halls",
            "total_floors", "building_age", "decoration_level",
            "floor_type_encoded", "orientation_south", "near_subway", "floor_ratio",
        ]
        available = [c for c in numeric_cols if c in self.df.columns]
        corr = self.df[available].corr().round(3)

        x_axis = corr.columns.tolist()
        y_axis = corr.index.tolist()
        data = []
        for i, row_name in enumerate(y_axis):
            for j, col_name in enumerate(x_axis):
                data.append([j, i, float(corr.iloc[i, j])])

        # English labels
        label_map = {
            "total_price": "Total Price", "unit_price": "Unit Price", "floor_area": "Floor Area",
            "rooms": "Bedrooms", "halls": "Living Rooms", "total_floors": "Total Floors",
            "building_age": "Building Age", "decoration_level": "Decoration Level",
            "floor_type_encoded": "Floor Type", "orientation_south": "South-facing",
            "near_subway": "Near Subway", "floor_ratio": "Floor Ratio",
        }
        x_labels = [label_map.get(c, c) for c in x_axis]
        y_labels = [label_map.get(c, c) for c in y_axis]

        heatmap = (
            HeatMap(init_opts=opts.InitOpts(theme=ThemeType.ESSOS, width="900px", height="550px"))
            .add_xaxis(x_labels)
            .add_yaxis(
                "Correlation",
                y_labels,
                data,
                label_opts=opts.LabelOpts(is_show=True, position="inside", formatter="{c}"),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Housing Price Factor Correlation Heatmap"),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
                visualmap_opts=opts.VisualMapOpts(
                    min_=-1, max_=1, is_calculable=True,
                    range_color=["#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8",
                                 "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027", "#a50026"],
                ),
            )
        )
        return heatmap

    def chart_regression_results(self):
        """8. Regression model results chart"""
        from sklearn.linear_model import LinearRegression

        feature_cols = [
            "floor_area", "rooms", "halls", "total_floors",
            "building_age", "decoration_level", "floor_type_encoded",
            "orientation_south", "near_subway", "floor_ratio",
        ]
        district_cols = [c for c in self.df.columns if c.startswith("district_")]
        available = [c for c in feature_cols + district_cols if c in self.df.columns]

        if "total_price" not in self.df.columns:
            raise ValueError("Missing total_price")

        X = self.df[available].fillna(0)
        y = self.df["total_price"].dropna()
        X = X.loc[y.index]

        model = LinearRegression()
        model.fit(X, y)

        importance = pd.DataFrame({
            "feature": X.columns,
            "coefficient": model.coef_,
        })
        importance["abs_coef"] = importance["coefficient"].abs()
        importance = importance.sort_values("abs_coef", ascending=True).tail(15)

        # English labels
        label_map = {
            "floor_area": "Floor Area", "rooms": "Bedrooms", "halls": "Living Rooms",
            "total_floors": "Total Floors", "building_age": "Building Age",
            "decoration_level": "Decoration Level", "floor_type_encoded": "Floor Type",
            "orientation_south": "South-facing", "near_subway": "Near Subway",
            "floor_ratio": "Floor Ratio",
        }
        labels = [label_map.get(f, f.replace("district_", "")) for f in importance["feature"]]

        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.ESSOS, width="900px", height="500px"))
            .add_xaxis(labels)
            .add_yaxis(
                "Regression Coefficient",
                importance["coefficient"].round(4).tolist(),
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode("""
                        function(params) {
                            var val = params.value;
                            return val >= 0 ? '#c23531' : '#2f4554';
                        }
                    """)
                ),
                label_opts=opts.LabelOpts(position="right", formatter="{c}"),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Linear Regression Feature Coefficients",
                                         subtitle="Red = increases price, Blue = decreases price"),
                xaxis_opts=opts.AxisOpts(name="Feature"),
                yaxis_opts=opts.AxisOpts(name="Coefficient"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
            .reversal_axis()
        )
        return bar

    def chart_pca_scores(self):
        """9. PCA/Factor score chart"""
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        exclude = [c for c in numeric_cols if c.startswith("district_") or c in ["id"]]
        feature_cols = [c for c in numeric_cols if c not in exclude]

        data = self.df[feature_cols].dropna()
        X = StandardScaler().fit_transform(data)

        pca = PCA(n_components=min(5, len(feature_cols)))
        pca.fit(X)

        explained = pca.explained_variance_ratio_
        cumulative = np.cumsum(explained)

        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.ESSOS, width="900px", height="500px"))
            .add_xaxis([f"PC{i+1}" for i in range(len(explained))])
            .add_yaxis(
                "Explained Variance Ratio",
                [round(float(v), 4) for v in explained],
                itemstyle_opts=opts.ItemStyleOpts(color="#5470c6"),
                label_opts=opts.LabelOpts(formatter="{c}"),
            )
            .extend_axis(
                yaxis=opts.AxisOpts(name="Cumulative Explained Variance", min_=0, max_=1)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Principal Component Analysis (PCA) Explained Variance"),
                xaxis_opts=opts.AxisOpts(name="Principal Component"),
                yaxis_opts=opts.AxisOpts(name="Explained Variance Ratio"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
        )

        line = (
            Line()
            .add_xaxis([f"PC{i+1}" for i in range(len(cumulative))])
            .add_yaxis(
                "Cumulative Variance",
                [round(float(v), 4) for v in cumulative],
                yaxis_index=1,
                label_opts=opts.LabelOpts(formatter="{c}"),
                linestyle_opts=opts.LineStyleOpts(type_="dashed"),
            )
        )

        bar.overlap(line)
        return bar

    def chart_cluster_results(self):
        """10. Cluster result chart"""
        if "total_price" not in self.df.columns or "floor_area" not in self.df.columns:
            raise ValueError("Missing required columns for clustering visualization")

        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler

        features = ["total_price", "floor_area", "unit_price"]
        available = [c for c in features if c in self.df.columns]
        X = self.df[available].dropna()
        X_scaled = StandardScaler().fit_transform(X)

        n_clusters = 5
        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)

        colors = ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de"]

        scatter = (
            Scatter(init_opts=opts.InitOpts(theme=ThemeType.ESSOS, width="900px", height="550px"))
        )

        for i in range(n_clusters):
            cluster_data = X[labels == i]
            if len(cluster_data) > 1000:
                cluster_data = cluster_data.sample(1000, random_state=42)

            scatter.add_xaxis(cluster_data["floor_area"].tolist())
            scatter.add_yaxis(
                f"Cluster {i+1}",
                cluster_data["total_price"].tolist(),
                symbol_size=8,
                itemstyle_opts=opts.ItemStyleOpts(color=colors[i % len(colors)]),
                label_opts=opts.LabelOpts(is_show=False),
            )

        scatter.set_global_opts(
            title_opts=opts.TitleOpts(title="Listing Clustering Results (Area vs Total Price)"),
            xaxis_opts=opts.AxisOpts(name="Floor Area (sqm)"),
            yaxis_opts=opts.AxisOpts(name="Total Price (10k RMB)"),
            tooltip_opts=opts.TooltipOpts(trigger="item"),
        )

        return scatter


def generate_all_charts(df_path, output_dir=None):
    """Generate all charts from cleaned data"""
    print("Loading data for chart generation...")
    df = pd.read_csv(df_path)
    print(f"Loaded {len(df)} records")

    generator = ChartGenerator(df, output_dir)
    charts = generator.generate_all()

    return charts


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate all housing analysis charts")
    parser.add_argument("input", help="Path to cleaned data CSV")
    parser.add_argument("--output-dir", "-o", default=None, help="Output directory for charts")
    args = parser.parse_args()

    generate_all_charts(args.input, args.output_dir)
