# Descriptive Statistical Analysis Module
# ========================================
# Analyzes distribution of total_price, unit_price, floor_area, building_age
# By district, layout, decoration, etc.

import pandas as pd
import numpy as np
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DescriptiveAnalyzer:
    """Descriptive statistical analysis of housing data"""

    def __init__(self, df):
        self.df = df
        self.results = {}

    def analyze_all(self):
        """Run all descriptive analyses"""
        print("Running descriptive statistical analysis...")

        self.results["overview"] = self.overview_stats()
        self.results["by_district"] = self.by_district()
        self.results["by_layout"] = self.by_layout()
        self.results["by_decoration"] = self.by_decoration()
        self.results["by_orientation"] = self.by_orientation()
        self.results["by_floor_type"] = self.by_floor_type()
        self.results["by_age_category"] = self.by_age_category()
        self.results["by_area_category"] = self.by_area_category()
        self.results["distribution"] = self.distribution_stats()

        return self.results

    def overview_stats(self):
        """Overall descriptive statistics"""
        cols = ["total_price", "unit_price", "floor_area", "building_age", "rooms", "halls"]
        available = [c for c in cols if c in self.df.columns]

        stats = {}
        for col in available:
            series = self.df[col].dropna()
            stats[col] = {
                "count": int(len(series)),
                "mean": round(float(series.mean()), 2),
                "median": round(float(series.median()), 2),
                "std": round(float(series.std()), 2),
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
                "q25": round(float(series.quantile(0.25)), 2),
                "q75": round(float(series.quantile(0.75)), 2),
                "skewness": round(float(series.skew()), 4),
                "kurtosis": round(float(series.kurtosis()), 4),
            }

        # Overall counts
        stats["total_listings"] = len(self.df)
        if "district" in self.df.columns:
            stats["total_districts"] = int(self.df["district"].nunique())
        if "community_name" in self.df.columns:
            stats["total_communities"] = int(self.df["community_name"].nunique())
        if "near_subway" in self.df.columns:
            stats["subway_coverage"] = round(float(self.df["near_subway"].mean() * 100), 1)

        return stats

    def by_district(self):
        """Statistics by district"""
        if "district" not in self.df.columns:
            return {}

        grouped = self.df.groupby("district").agg(
            count=("total_price", "count"),
            avg_total_price=("total_price", "mean"),
            avg_unit_price=("unit_price", "mean"),
            avg_area=("floor_area", "mean"),
            median_total_price=("total_price", "median"),
            median_unit_price=("unit_price", "median"),
            avg_building_age=("building_age", "mean"),
        ).round(2)

        # Add percentage
        grouped["pct_of_total"] = (grouped["count"] / len(self.df) * 100).round(1)
        grouped = grouped.sort_values("avg_unit_price", ascending=False)

        return grouped.reset_index().to_dict(orient="records")

    def by_layout(self):
        """Statistics by layout type"""
        if "layout" not in self.df.columns:
            return {}

        grouped = self.df.groupby("layout").agg(
            count=("total_price", "count"),
            avg_total_price=("total_price", "mean"),
            avg_unit_price=("unit_price", "mean"),
            avg_area=("floor_area", "mean"),
        ).round(2)

        grouped = grouped[grouped["count"] >= 5]  # Filter rare layouts
        grouped = grouped.sort_values("count", ascending=False)

        return grouped.reset_index().to_dict(orient="records")

    def by_decoration(self):
        """Statistics by decoration status"""
        if "decoration" not in self.df.columns:
            return {}

        grouped = self.df.groupby("decoration").agg(
            count=("total_price", "count"),
            avg_total_price=("total_price", "mean"),
            avg_unit_price=("unit_price", "mean"),
            avg_area=("floor_area", "mean"),
        ).round(2)
        grouped = grouped.sort_values("avg_unit_price", ascending=False)

        return grouped.reset_index().to_dict(orient="records")

    def by_orientation(self):
        """Statistics by orientation"""
        if "orientation" not in self.df.columns:
            return {}

        grouped = self.df.groupby("orientation").agg(
            count=("total_price", "count"),
            avg_total_price=("total_price", "mean"),
            avg_unit_price=("unit_price", "mean"),
        ).round(2)
        grouped = grouped[grouped["count"] >= 5]
        grouped = grouped.sort_values("count", ascending=False)

        return grouped.reset_index().to_dict(orient="records")

    def by_floor_type(self):
        """Statistics by floor level"""
        if "floor_type" not in self.df.columns:
            return {}

        grouped = self.df.groupby("floor_type").agg(
            count=("total_price", "count"),
            avg_total_price=("total_price", "mean"),
            avg_unit_price=("unit_price", "mean"),
        ).round(2)

        return grouped.reset_index().to_dict(orient="records")

    def by_age_category(self):
        """Statistics by building age category"""
        if "age_category" not in self.df.columns:
            return {}

        grouped = self.df.groupby("age_category", observed=False).agg(
            count=("total_price", "count"),
            avg_total_price=("total_price", "mean"),
            avg_unit_price=("unit_price", "mean"),
            avg_area=("floor_area", "mean"),
        ).round(2)

        return grouped.reset_index().to_dict(orient="records")

    def by_area_category(self):
        """Statistics by area category"""
        if "area_category" not in self.df.columns:
            return {}

        grouped = self.df.groupby("area_category", observed=False).agg(
            count=("total_price", "count"),
            avg_total_price=("total_price", "mean"),
            avg_unit_price=("unit_price", "mean"),
        ).round(2)

        return grouped.reset_index().to_dict(orient="records")

    def distribution_stats(self):
        """Distribution statistics for histograms"""
        dist = {}

        for col in ["total_price", "unit_price", "floor_area", "building_age"]:
            if col in self.df.columns:
                series = self.df[col].dropna()
                hist, bins = np.histogram(series, bins=20)
                dist[col] = {
                    "histogram": hist.tolist(),
                    "bins": [round(b, 2) for b in bins.tolist()],
                    "mean": round(float(series.mean()), 2),
                    "median": round(float(series.median()), 2),
                }

        return dist

    def to_json(self, path=None):
        """Export results to JSON"""
        if path:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
        return json.dumps(self.results, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to cleaned data CSV")
    parser.add_argument("--output", "-o", default=None, help="Output JSON path")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    analyzer = DescriptiveAnalyzer(df)
    results = analyzer.analyze_all()
    print(json.dumps(results["overview"], ensure_ascii=False, indent=2))

    if args.output:
        analyzer.to_json(args.output)
        print(f"\nResults saved to {args.output}")
