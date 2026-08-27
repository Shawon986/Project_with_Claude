# Compare original backend (port 8000) vs Vercel pure-python API (port 8001).
import json
import sys
import urllib.request

OLD = "http://127.0.0.1:8000"
NEW = "http://127.0.0.1:8001"

ENDPOINTS = [
    "/api/overview",
    "/api/listings",
    "/api/listings?page=2&page_size=10&district=jianggan&min_price=100&max_price=600",
    "/api/listings?sort_by=total_price&sort_order=asc&page=1&page_size=5",
    "/api/listings?sort_by=listing_time&sort_order=asc&page=1&page_size=5",
    "/api/listings?sort_by=district&sort_order=desc&page=1&page_size=5",
    "/api/listings?layout=3BR&decoration=Fine&keyword=Garden&page=1&page_size=5",
    "/api/listings?min_area=80&max_area=120&orientation=South&page=1&page_size=5",
    "/api/districts",
    "/api/layouts",
    "/api/district-analysis",
    "/api/factor-analysis",
    "/api/pca-analysis",
    "/api/cluster-analysis",
    "/api/recommendations",
    "/api/charts",
    "/api/chart-data/district_avg_unit_price",
    "/api/chart-data/total_price_distribution",
    "/api/chart-data/area_vs_total_price",
    "/api/chart-data/building_age_vs_unit_price",
    "/api/chart-data/avg_price_by_layout",
    "/api/chart-data/avg_price_by_decoration",
    "/api/chart-data/correlation_heatmap",
    "/api/chart-data/regression_results",
    "/api/chart-data/pca_factor_scores",
    "/api/chart-data/cluster_results",
    "/api/stats/descriptive",
    "/api/health",
]


def fetch(base, path):
    with urllib.request.urlopen(base + path, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def diff(a, b, path="", tol=1e-6, out=None):
    if out is None:
        out = []
    if type(a) != type(b):
        out.append(f"{path}: TYPE {type(a).__name__} vs {type(b).__name__}")
        return out
    if isinstance(a, dict):
        if set(a.keys()) != set(b.keys()):
            only_a = set(a) - set(b)
            only_b = set(b) - set(a)
            if only_a:
                out.append(f"{path}: keys only in OLD {sorted(only_a)[:10]}")
            if only_b:
                out.append(f"{path}: keys only in NEW {sorted(only_b)[:10]}")
        for k in a.keys() & b.keys():
            diff(a[k], b[k], f"{path}.{k}", tol, out)
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            out.append(f"{path}: LEN {len(a)} vs {len(b)}")
            return out
        for i, (x, y) in enumerate(zip(a, b)):
            diff(x, y, f"{path}[{i}]", tol, out)
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if abs(a - b) > tol:
            out.append(f"{path}: {a} vs {b}")
        return out
    if a != b:
        out.append(f"{path}: {a!r} vs {b!r}")
    return out


def main():
    total = 0
    for path in ENDPOINTS:
        try:
            old = fetch(OLD, path)
        except Exception as e:
            print(f"OLD FAIL {path}: {e}")
            continue
        try:
            new = fetch(NEW, path)
        except Exception as e:
            print(f"NEW FAIL {path}: {e}")
            continue
        diffs = diff(old, new, path)
        total += len(diffs)
        print(f"{'OK  ' if not diffs else 'DIFF'} {path} ({len(diffs)} differences)")
        for d in diffs[:8]:
            print(f"     {d}")
        if len(diffs) > 8:
            print(f"     ... and {len(diffs) - 8} more")
    print(f"\nTotal differences: {total}")


if __name__ == "__main__":
    main()
