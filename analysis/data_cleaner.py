# Data Cleaning Module for Hangzhou Second-hand Housing Data
# ============================================================
# Handles: missing values, duplicates, outliers, format conversion, text standardization

import pandas as pd
import numpy as np
import re
import json
import os
import sys
import io
from datetime import datetime

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CLEANING

class HousingDataCleaner:
    """Clean and preprocess second-hand housing data"""

    def __init__(self, data):
        """
        Initialize cleaner with raw data.

        Args:
            data: list of dicts or pandas DataFrame
        """
        if isinstance(data, list):
            self.df = pd.DataFrame(data)
        else:
            self.df = data.copy()
        self.original_count = len(self.df)
        self.cleaning_log = []

    def log_step(self, step_name, before_count, after_count, description=""):
        """Log a cleaning step"""
        removed = before_count - after_count
        self.cleaning_log.append({
            "step": step_name,
            "before": before_count,
            "after": after_count,
            "removed": removed,
            "removed_pct": f"{removed/before_count*100:.2f}%" if before_count > 0 else "0%",
            "description": description
        })
        return after_count

    def clean(self):
        """Run complete cleaning pipeline"""
        print("=" * 60)
        print("Starting Data Cleaning Pipeline")
        print(f"Original records: {self.original_count}")
        print("=" * 60)

        count = len(self.df)

        # Step 1: Remove duplicate records
        print("\n[Step 1] Removing duplicate records...")
        count = self.remove_duplicates()

        # Step 2: Handle missing values
        print("\n[Step 2] Handling missing values...")
        count = self.handle_missing_values()

        # Step 3: Remove outliers
        print("\n[Step 3] Removing outliers...")
        count = self.remove_outliers()

        # Step 4: Convert field formats
        print("\n[Step 4] Converting field formats...")
        count = self.convert_formats()

        # Step 5: Standardize text fields
        print("\n[Step 5] Standardizing text fields...")
        count = self.standardize_text()

        # Step 6: Encode categorical variables
        print("\n[Step 6] Encoding categorical variables...")
        count = self.encode_categorical()

        # Step 7: Create derived fields
        print("\n[Step 7] Creating derived fields...")
        count = self.create_derived_fields()

        # Step 8: Final validation
        print("\n[Step 8] Final validation...")
        count = self.final_validation()

        print(f"\n{'=' * 60}")
        print(f"Cleaning complete!")
        print(f"Original records: {self.original_count}")
        print(f"Final records:   {len(self.df)}")
        print(f"Records removed: {self.original_count - len(self.df)} ({(self.original_count - len(self.df))/self.original_count*100:.1f}%)")
        print(f"{'=' * 60}")

        return self.df

    def remove_duplicates(self):
        """Remove duplicate records based on listing link and community+area+price"""
        before = len(self.df)

        # Remove exact duplicates by listing link
        if "listing_link" in self.df.columns:
            self.df = self.df.drop_duplicates(subset=["listing_link"], keep="first")

        # Remove near-duplicates (same community, area, price)
        dup_cols = ["community_name", "floor_area", "total_price"]
        available_cols = [c for c in dup_cols if c in self.df.columns]
        if len(available_cols) >= 2:
            self.df = self.df.drop_duplicates(subset=available_cols, keep="first")

        self.df = self.df.reset_index(drop=True)
        return self.log_step("Remove duplicates", before, len(self.df),
                            "Removed records with same listing link or same community+area+price")

    def handle_missing_values(self):
        """Handle missing values in each column"""
        before = len(self.df)
        missing_report = {}

        for col in self.df.columns:
            missing_count = self.df[col].isna().sum()
            if missing_count > 0:
                missing_report[col] = missing_count

        print(f"  Columns with missing values: {missing_report}")

        # Numeric columns: fill with median
        numeric_cols = ["total_price", "unit_price", "floor_area", "rooms", "halls",
                       "total_floors", "construction_year", "building_age"]
        for col in numeric_cols:
            if col in self.df.columns and self.df[col].isna().sum() > 0:
                self.df[col] = self.df[col].fillna(self.df[col].median())

        # Categorical columns: fill with mode
        categorical_cols = ["district", "sub_district", "layout", "floor", "orientation",
                           "decoration", "community_name"]
        for col in categorical_cols:
            if col in self.df.columns and self.df[col].isna().sum() > 0:
                mode_val = self.df[col].mode()
                if len(mode_val) > 0:
                    self.df[col] = self.df[col].fillna(mode_val[0])
                else:
                    self.df[col] = self.df[col].fillna("未知")

        # Binary columns: fill with 0
        if "near_subway" in self.df.columns:
            self.df["near_subway"] = self.df["near_subway"].fillna(0)

        # Derive unit_price from total_price / floor_area if missing
        if "unit_price" in self.df.columns and "total_price" in self.df.columns and "floor_area" in self.df.columns:
            mask = self.df["unit_price"].isna() & self.df["total_price"].notna() & self.df["floor_area"].notna()
            if mask.sum() > 0:
                self.df.loc[mask, "unit_price"] = (
                    self.df.loc[mask, "total_price"] * 10000 / self.df.loc[mask, "floor_area"]
                )

        # Derive building_age from construction_year if missing
        if "building_age" in self.df.columns and "construction_year" in self.df.columns:
            current_year = datetime.now().year
            mask = self.df["building_age"].isna() & self.df["construction_year"].notna()
            if mask.sum() > 0:
                self.df.loc[mask, "building_age"] = current_year - self.df.loc[mask, "construction_year"]

        # Remove rows where critical fields are still missing
        critical_cols = ["total_price", "floor_area"]
        available_critical = [c for c in critical_cols if c in self.df.columns]
        if available_critical:
            self.df = self.df.dropna(subset=available_critical)

        self.df = self.df.reset_index(drop=True)
        return self.log_step("Handle missing values", before, len(self.df),
                            f"Filled missing values with median/mode; dropped rows with missing critical fields")

    def remove_outliers(self):
        """Remove statistical outliers"""
        before = len(self.df)

        # Unit price outliers (Z-score method)
        if "unit_price" in self.df.columns and len(self.df) > 0:
            mean = self.df["unit_price"].mean()
            std = self.df["unit_price"].std()
            if std > 0:
                z_threshold = CLEANING["price_outlier_std"]
                z_scores = np.abs((self.df["unit_price"] - mean) / std)
                self.df = self.df[z_scores <= z_threshold]

        # Total price outliers
        if "total_price" in self.df.columns and len(self.df) > 0:
            mean = self.df["total_price"].mean()
            std = self.df["total_price"].std()
            if std > 0:
                z_scores = np.abs((self.df["total_price"] - mean) / std)
                self.df = self.df[z_scores <= CLEANING["price_outlier_std"]]

        # Area range check
        if "floor_area" in self.df.columns:
            self.df = self.df[
                (self.df["floor_area"] >= CLEANING["area_min"]) &
                (self.df["floor_area"] <= CLEANING["area_max"])
            ]

        # Unit price range check
        if "unit_price" in self.df.columns:
            self.df = self.df[
                (self.df["unit_price"] >= CLEANING["price_per_sqm_min"]) &
                (self.df["unit_price"] <= CLEANING["price_per_sqm_max"])
            ]

        # Building age range check
        if "building_age" in self.df.columns:
            self.df = self.df[self.df["building_age"] <= CLEANING["building_age_max"]]

        self.df = self.df.reset_index(drop=True)
        return self.log_step("Remove outliers", before, len(self.df),
                            f"Removed records with Z-score > {CLEANING['price_outlier_std']} or outside reasonable ranges")

    def convert_formats(self):
        """Convert field formats to proper types"""
        before = len(self.df)

        # Ensure numeric columns are numeric
        numeric_cols = ["total_price", "unit_price", "floor_area", "rooms", "halls",
                       "total_floors", "construction_year", "building_age"]
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

        # Convert near_subway to int
        if "near_subway" in self.df.columns:
            self.df["near_subway"] = pd.to_numeric(self.df["near_subway"], errors="coerce").fillna(0).astype(int)

        # Ensure listing_time is string
        if "listing_time" in self.df.columns:
            self.df["listing_time"] = self.df["listing_time"].astype(str)

        # Round float columns
        for col in ["total_price", "unit_price", "floor_area"]:
            if col in self.df.columns:
                self.df[col] = self.df[col].round(2)

        self.df = self.df.reset_index(drop=True)
        return self.log_step("Convert formats", before, len(self.df),
                            "Converted columns to proper numeric types and rounded floats")

    def standardize_text(self):
        """Standardize text field values"""
        before = len(self.df)

        # Standardize orientation
        if "orientation" in self.df.columns:
            orientation_map = {
                "South": "South", "North": "North", "East": "East", "West": "West",
                "North-South": "North-South", "Southeast": "Southeast", "Southwest": "Southwest",
                "Northeast": "Northeast", "Northwest": "Northwest", "East-West": "East-West",
            }
            self.df["orientation"] = self.df["orientation"].apply(
                lambda x: orientation_map.get(x.strip() if isinstance(x, str) else x, x)
            )

        # Standardize decoration
        if "decoration" in self.df.columns:
            decoration_map = {
                "Unfinished": "Unfinished", "Rough": "Unfinished",
                "Simple": "Simple", "Basic": "Simple",
                "Medium": "Medium", "Moderate": "Medium",
                "Fine": "Fine", "Refined": "Fine",
                "Luxury": "Luxury", "Luxurious": "Luxury",
                "Other": "Other", "Unknown": "Other",
            }
            self.df["decoration"] = self.df["decoration"].apply(
                lambda x: decoration_map.get(x.strip() if isinstance(x, str) else x, x)
            )

        # Standardize floor type
        if "floor" in self.df.columns:
            floor_map = {
                "Low Floor": "Low Floor", "low": "Low Floor",
                "Middle Floor": "Middle Floor", "middle": "Middle Floor",
                "High Floor": "High Floor", "high": "High Floor",
                "Ground": "Low Floor", "Top": "High Floor", "Basement": "Low Floor",
            }
            self.df["floor_type"] = self.df["floor"].apply(
                lambda x: floor_map.get(x.strip() if isinstance(x, str) else x, "middle")
            )

        # Standardize district names
        if "district" in self.df.columns:
            # Remove extra spaces and normalize
            self.df["district"] = self.df["district"].apply(
                lambda x: x.strip() if isinstance(x, str) else x
            )

        self.df = self.df.reset_index(drop=True)
        return self.log_step("Standardize text", before, len(self.df),
                            "Standardized orientation, decoration, floor type, and district names")

    def encode_categorical(self):
        """Encode categorical variables for analysis"""
        before = len(self.df)

        # Encode decoration level (ordinal)
        if "decoration" in self.df.columns:
            decoration_order = {"Unfinished": 0, "Simple": 1, "Medium": 2, "Fine": 3, "Luxury": 4, "Other": 1}
            self.df["decoration_level"] = self.df["decoration"].map(decoration_order).fillna(1).astype(int)

        # Encode floor type
        if "floor_type" in self.df.columns:
            floor_order = {"Low Floor": 0, "Middle Floor": 1, "High Floor": 2}
            self.df["floor_type_encoded"] = self.df["floor_type"].map(floor_order).fillna(1).astype(int)

        # Encode orientation (grouped)
        if "orientation" in self.df.columns:
            south_groups = ["South", "North-South", "Southeast", "Southwest"]
            self.df["orientation_south"] = self.df["orientation"].apply(
                lambda x: 1 if str(x) in south_groups else 0
            )

        # District one-hot encoding
        if "district" in self.df.columns:
            district_dummies = pd.get_dummies(self.df["district"], prefix="district")
            self.df = pd.concat([self.df, district_dummies], axis=1)

        self.df = self.df.reset_index(drop=True)
        return self.log_step("Encode categorical", before, len(self.df),
                            "Encoded decoration, floor type, orientation as numeric; one-hot encoded districts")

    def create_derived_fields(self):
        """Create derived/calculated fields"""
        before = len(self.df)

        # Floor ratio: relative position in building
        if "total_floors" in self.df.columns and "floor_type" in self.df.columns:
            floor_pos = {"Low Floor": 0.25, "Middle Floor": 0.5, "High Floor": 0.75}
            self.df["floor_ratio"] = self.df["floor_type"].map(floor_pos).fillna(0.5)

        # Price per room
        if "total_price" in self.df.columns and "rooms" in self.df.columns:
            self.df["rooms_safe"] = self.df["rooms"].clip(lower=1)
            self.df["price_per_room"] = self.df["total_price"] / self.df["rooms_safe"]
            self.df = self.df.drop(columns=["rooms_safe"])

        # Area per room
        if "floor_area" in self.df.columns and "rooms" in self.df.columns:
            self.df["rooms_safe"] = self.df["rooms"].clip(lower=1)
            self.df["area_per_room"] = self.df["floor_area"] / self.df["rooms_safe"]
            self.df = self.df.drop(columns=["rooms_safe"])

        # Building age categories
        if "building_age" in self.df.columns:
            bins = [0, 5, 10, 15, 20, 30, 100]
            labels = ["0-5yr", "5-10yr", "10-15yr", "15-20yr", "20-30yr", "30yr+"]
            self.df["age_category"] = pd.cut(self.df["building_age"], bins=bins, labels=labels)

        # Area categories
        if "floor_area" in self.df.columns:
            bins = [0, 50, 70, 90, 120, 150, 500]
            labels = ["<50sqm", "50-70sqm", "70-90sqm", "90-120sqm", "120-150sqm", ">150sqm"]
            self.df["area_category"] = pd.cut(self.df["floor_area"], bins=bins, labels=labels)

        # Price categories
        if "total_price" in self.df.columns:
            bins = [0, 100, 150, 200, 300, 400, 500, 100000]
            labels = ["<1M", "1-1.5M", "1.5-2M", "2-3M", "3-4M", "4-5M", ">5M"]
            self.df["price_category"] = pd.cut(self.df["total_price"], bins=bins, labels=labels)

        self.df = self.df.reset_index(drop=True)
        return self.log_step("Create derived fields", before, len(self.df),
                            "Created floor_ratio, price_per_room, area_per_room, and categorical bucketed fields")

    def final_validation(self):
        """Final validation check"""
        before = len(self.df)

        # Remove any remaining NaN in critical fields
        critical = ["total_price", "floor_area", "unit_price"]
        available = [c for c in critical if c in self.df.columns]
        self.df = self.df.dropna(subset=available)

        # Ensure all records have district
        if "district" in self.df.columns:
            self.df = self.df[self.df["district"].notna()]

        # Remove negative values
        for col in ["total_price", "unit_price", "floor_area", "building_age"]:
            if col in self.df.columns:
                self.df = self.df[self.df[col] >= 0]

        self.df = self.df.reset_index(drop=True)
        return self.log_step("Final validation", before, len(self.df),
                            "Removed remaining NaN in critical fields and negative values")

    def get_cleaning_report(self):
        """Generate cleaning report as DataFrame"""
        return pd.DataFrame(self.cleaning_log)

    def print_report(self):
        """Print detailed cleaning report"""
        print("\n" + "=" * 70)
        print("DATA CLEANING REPORT")
        print("=" * 70)
        print(f"{'Step':<25} {'Before':>8} {'After':>8} {'Removed':>8} {'%':>8}")
        print("-" * 70)
        for entry in self.cleaning_log:
            print(f"{entry['step']:<25} {entry['before']:>8} {entry['after']:>8} {entry['removed']:>8} {entry['removed_pct']:>8}")
        print("-" * 70)
        print(f"{'TOTAL':<25} {self.original_count:>8} {len(self.df):>8} {self.original_count - len(self.df):>8} "
              f"{(self.original_count - len(self.df))/self.original_count*100:.1f}%")
        print("=" * 70)


def load_and_clean(input_path, output_dir=None):
    """Load raw data, clean it, and save cleaned data"""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cleaned")
    os.makedirs(output_dir, exist_ok=True)

    # Load data
    print(f"Loading data from: {input_path}")
    if input_path.endswith(".json"):
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif input_path.endswith(".csv"):
        data = pd.read_csv(input_path)
    else:
        raise ValueError(f"Unsupported file format: {input_path}")

    # Clean data
    cleaner = HousingDataCleaner(data)
    cleaned = cleaner.clean()
    cleaner.print_report()

    # Save cleaned data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(output_dir, f"hangzhou_cleaned_{len(cleaned)}_{timestamp}.csv")
    json_path = os.path.join(output_dir, f"hangzhou_cleaned_{len(cleaned)}_{timestamp}.json")

    cleaned.to_csv(csv_path, index=False, encoding="utf-8-sig")
    cleaned.to_json(json_path, orient="records", force_ascii=False, indent=2)

    print(f"\nCleaned data saved to:")
    print(f"  CSV:  {csv_path}")
    print(f"  JSON: {json_path}")

    return cleaned, cleaner


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clean Hangzhou housing data")
    parser.add_argument("input", help="Path to raw data file (JSON or CSV)")
    parser.add_argument("--output-dir", "-o", default=None, help="Output directory for cleaned data")

    args = parser.parse_args()

    cleaned_df, cleaner = load_and_clean(args.input, args.output_dir)
