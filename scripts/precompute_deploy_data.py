# Precompute static API payloads for the Vercel deployment.
# ============================================================
# The Vercel backend (api/index.py) is pure Python (no pandas/numpy/sklearn)
# so the serverless function bundle stays small. This script runs LOCALLY
# (needs the full requirements) and uses the exact same code paths as
# web/backend/app.py to generate the heavy chart payloads and descriptive
# statistics as static JSON files in api_static/, which are then shipped
# with the deployment.
#
# Usage: .venv/Scripts/python.exe scripts/precompute_deploy_data.py

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.backend.app import get_chart_data, get_dataframe  # noqa: E402
from analysis.descriptive_stats import DescriptiveAnalyzer  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJECT_ROOT, "api_static")

# Charts whose payloads need pandas/numpy/sklearn (or sampling) and are
# precomputed here. The remaining chart ids are computed in pure Python
# inside api/index.py (simple groupbys / histogram).
HEAVY_CHARTS = [
    "correlation_heatmap",
    "regression_results",
    "pca_factor_scores",
    "cluster_results",
    "area_vs_total_price",
    "building_age_vs_unit_price",
]


async def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    for chart_id in HEAVY_CHARTS:
        payload = await get_chart_data(chart_id)
        path = os.path.join(OUT_DIR, f"chart_{chart_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        print(f"wrote {os.path.relpath(path, PROJECT_ROOT)}")

    df = get_dataframe()
    stats = DescriptiveAnalyzer(df).analyze_all()
    path = os.path.join(OUT_DIR, "descriptive_stats.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False)
    print(f"wrote {os.path.relpath(path, PROJECT_ROOT)}")


if __name__ == "__main__":
    asyncio.run(main())
