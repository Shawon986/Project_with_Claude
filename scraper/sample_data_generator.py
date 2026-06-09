# Sample Data Generator for Hangzhou Second-hand Housing
# =======================================================
# Generates realistic sample data for testing the system
# without actual web scraping. Based on real Hangzhou market patterns.

import pandas as pd
import numpy as np
import os
import sys
import io
from datetime import datetime

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Hangzhou districts with realistic characteristics (pinyin names)
HANGZHOU_DISTRICTS = {
    "Shangcheng": {"base_price": 48000, "price_std": 12000, "avg_area": 75, "age_mean": 22, "weight": 5},
    "Xiacheng":  {"base_price": 45000, "price_std": 11000, "avg_area": 78, "age_mean": 20, "weight": 4},
    "Xihu":      {"base_price": 50000, "price_std": 15000, "avg_area": 82, "age_mean": 18, "weight": 8},
    "Gongshu":   {"base_price": 42000, "price_std": 10000, "avg_area": 85, "age_mean": 16, "weight": 7},
    "Jianggan":  {"base_price": 38000, "price_std": 9000,  "avg_area": 88, "age_mean": 14, "weight": 6},
    "Binjiang":  {"base_price": 43000, "price_std": 11000, "avg_area": 92, "age_mean": 12, "weight": 6},
    "Xiaoshan":  {"base_price": 32000, "price_std": 8000,  "avg_area": 95, "age_mean": 12, "weight": 8},
    "Yuhang":    {"base_price": 30000, "price_std": 8000,  "avg_area": 98, "age_mean": 8,  "weight": 10},
    "Fuyang":    {"base_price": 22000, "price_std": 6000,  "avg_area": 100, "age_mean": 10, "weight": 3},
    "Linan":     {"base_price": 18000, "price_std": 5000,  "avg_area": 105, "age_mean": 8,  "weight": 2},
    "Qiantang":  {"base_price": 28000, "price_std": 7000,  "avg_area": 90, "age_mean": 5,  "weight": 4},
    "Linping":   {"base_price": 25000, "price_std": 6000,  "avg_area": 93, "age_mean": 10, "weight": 5},
}

LAYOUTS = ["1BR 0LR", "1BR 1LR", "2BR 1LR", "2BR 2LR", "3BR 1LR", "3BR 2LR", "4BR 2LR", "5BR 2LR", "5BR 3LR"]
LAYOUT_WEIGHTS = [0.03, 0.08, 0.15, 0.10, 0.12, 0.28, 0.15, 0.07, 0.02]

ORIENTATIONS = ["South", "North-South", "Southeast", "Southwest", "East", "West", "North", "Northeast", "Northwest", "East-West"]
ORIENTATION_WEIGHTS = [0.30, 0.25, 0.12, 0.08, 0.07, 0.05, 0.05, 0.04, 0.03, 0.01]

DECORATIONS = ["Unfinished", "Simple", "Medium", "Fine", "Luxury"]
DECORATION_WEIGHTS = [0.08, 0.20, 0.22, 0.40, 0.10]

FLOOR_TYPES = ["Low Floor", "Middle Floor", "High Floor"]
FLOOR_WEIGHTS = [0.30, 0.35, 0.35]

# Community name patterns
COMMUNITY_PREFIXES = [
    "Gemdale", "Greentown", "Vanke", "Poly", "Longfor", "CR Land", "Sunac", "Country Garden",
    "Evergrande", "COLI", "Merchants", "Yango", "CIFI", "Shimao", "Jinmao",
    "Cuiyuan", "Zhaohui", "Wensan", "Jingfang", "Desheng", "Sanliting", "Daguan",
    "Fuxing", "Jinjiang", "Wangjiang", "Ziyang", "Hubin", "Qingbo", "Xiaoying",
]
COMMUNITY_SUFFIXES = [
    "Garden", "Court", "Apartment", "City", "Mansion", "Place", "Bay", "Villa",
    "Homeland", "New Village", "Community", "Complex", "World", "Plaza", "Center",
]

SUB_DISTRICTS = {
    "Shangcheng": ["Hubin", "Qingbo", "Xiaoying", "Wangjiang", "Nanxing", "Ziyang"],
    "Xihu":      ["Wensan Road", "Gudang", "Cuiyuan", "Wenxin", "Liuxia", "Zhuantang", "Sandun"],
    "Gongshu":   ["Daguan", "Hemu", "Xiangfu", "Banshan", "Kangqiao", "Shangtang"],
    "Binjiang":  ["Xixing", "Changhe", "Puyan"],
    "Xiaoshan":  ["Beigan", "Chengxiang", "Shushan", "Xintang", "Ningwei"],
    "Yuhang":    ["Cangqian", "Wuchang", "Liangzhu", "Xianlin", "Old Yuhang", "Gouzhuang"],
    "Qiantang":  ["Xiasha", "Baiyang", "Dajiangdong"],
}


def generate_listings(n=3500, seed=42):
    """Generate realistic sample listing data"""
    np.random.seed(seed)
    current_year = datetime.now().year

    listings = []

    total_weight = sum(d["weight"] for d in HANGZHOU_DISTRICTS.values())
    district_names = list(HANGZHOU_DISTRICTS.keys())

    for i in range(n):
        district = np.random.choice(district_names, p=[HANGZHOU_DISTRICTS[d]["weight"]/total_weight for d in district_names])
        d_info = HANGZHOU_DISTRICTS[district]

        unit_price = max(8000, np.random.normal(d_info["base_price"], d_info["price_std"]))
        area = max(25, np.random.normal(d_info["avg_area"], 25))
        area = round(area, 1)
        total_price = round(unit_price * area / 10000, 1)

        layout = np.random.choice(LAYOUTS, p=LAYOUT_WEIGHTS)
        import re
        m = re.match(r"(\d+)BR\s+(\d+)LR", layout)
        rooms = int(m.group(1))
        halls = int(m.group(2))

        age = max(1, int(np.random.normal(d_info["age_mean"], 8)))
        construction_year = current_year - age

        total_floors = np.random.choice([6, 7, 11, 18, 25, 32, 33], p=[0.05, 0.08, 0.15, 0.25, 0.20, 0.15, 0.12])
        floor_type = np.random.choice(FLOOR_TYPES, p=FLOOR_WEIGHTS)
        orientation = np.random.choice(ORIENTATIONS, p=ORIENTATION_WEIGHTS)
        decoration = np.random.choice(DECORATIONS, p=DECORATION_WEIGHTS)

        community = np.random.choice(COMMUNITY_PREFIXES) + " " + np.random.choice(COMMUNITY_SUFFIXES)

        subs = SUB_DISTRICTS.get(district, ["Central"])
        sub_district = np.random.choice(subs)

        subway_prob = 0.3 + (unit_price / 100000) * 0.4
        near_subway = 1 if np.random.random() < subway_prob else 0

        days_ago = np.random.randint(1, 180)
        listing_time = f"{days_ago} days ago"

        listing_id = 100000000 + i
        listing_link = f"https://hz.lianjia.com/ershoufang/{listing_id}.html"

        listing = {
            "community_name": community,
            "district": district,
            "sub_district": sub_district,
            "total_price": total_price,
            "unit_price": round(unit_price, 0),
            "floor_area": area,
            "layout": layout,
            "rooms": rooms,
            "halls": halls,
            "floor": floor_type,
            "total_floors": total_floors,
            "orientation": orientation,
            "decoration": decoration,
            "construction_year": construction_year,
            "building_age": age,
            "near_subway": near_subway,
            "listing_time": listing_time,
            "listing_link": listing_link,
        }

        listings.append(listing)

    return listings


def generate_and_save(n=3500, output_dir=None):
    """Generate sample data and save to disk"""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Generating {n} sample listings...")
    listings = generate_listings(n)

    df = pd.DataFrame(listings)

    # Add some realistic noise (1-2% missing)
    for col in ["building_age", "construction_year", "total_floors"]:
        mask = np.random.random(len(df)) < 0.02
        df.loc[mask, col] = np.nan

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(output_dir, f"hangzhou_sample_{len(df)}_{timestamp}.csv")
    json_path = os.path.join(output_dir, f"hangzhou_sample_{len(df)}_{timestamp}.json")

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    print(f"\nSample data generated!")
    print(f"  Records: {len(df)}")
    print(f"  CSV:  {csv_path}")
    print(f"  JSON: {json_path}")

    print(f"\nData Summary:")
    print(f"  Districts: {df['district'].nunique()}")
    print(f"  Avg Total Price: {df['total_price'].mean():.1f} (10k RMB)")
    print(f"  Avg Unit Price: {df['unit_price'].mean():.0f} RMB/sqm")
    print(f"  Avg Area: {df['floor_area'].mean():.1f} sqm")
    print(f"  Avg Building Age: {df['building_age'].mean():.1f} years")
    print(f"  Subway Coverage: {df['near_subway'].mean()*100:.1f}%")

    return df


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate sample housing data for testing")
    parser.add_argument("--count", "-n", type=int, default=3500, help="Number of listings to generate")
    parser.add_argument("--output-dir", "-o", default=None, help="Output directory")
    args = parser.parse_args()

    generate_and_save(args.count, args.output_dir)
