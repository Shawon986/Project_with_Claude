# Hangzhou Housing Analysis - Full Pipeline
# ==========================================
# Master script to run the complete pipeline:
#   1. Scrape data
#   2. Clean data
#   3. Run analysis
#   4. Generate charts
#   5. Launch web server

import os
import sys
import argparse
import subprocess
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def run_step(name, command):
    """Run a pipeline step"""
    print("\n" + "=" * 70)
    print(f"  STEP: {name}")
    print("=" * 70)
    result = subprocess.run(command, shell=True, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"\n[ERROR] Step '{name}' failed with code {result.returncode}")
        return False
    return True


def step1_scrape(pages=120, enrich=50):
    """Step 1: Scrape data from Lianjia"""
    cmd = f"python scraper/lianjia_scraper.py --pages {pages} --enrich {enrich}"
    return run_step("1. Scrape Hangzhou Housing Data", cmd)


def step2_clean():
    """Step 2: Clean data"""
    # Find the latest raw data file
    raw_dir = os.path.join(PROJECT_ROOT, "data", "raw")
    if not os.path.exists(raw_dir):
        print("[ERROR] No raw data directory found. Run scraping first.")
        return False

    csv_files = [f for f in os.listdir(raw_dir) if f.endswith(".csv")]
    if not csv_files:
        print("[ERROR] No raw CSV files found. Run scraping first.")
        return False

    csv_files.sort(reverse=True)
    input_path = os.path.join(raw_dir, csv_files[0])
    print(f"  Using raw data: {input_path}")

    cmd = f'python analysis/data_cleaner.py "{input_path}"'
    return run_step("2. Clean Data", cmd)


def step3_analyze():
    """Step 3: Run all analysis"""
    cleaned_dir = os.path.join(PROJECT_ROOT, "data", "cleaned")
    if not os.path.exists(cleaned_dir):
        print("[ERROR] No cleaned data directory found.")
        return False

    csv_files = [f for f in os.listdir(cleaned_dir) if f.endswith(".csv")]
    if not csv_files:
        print("[ERROR] No cleaned CSV files found.")
        return False

    csv_files.sort(reverse=True)
    input_path = os.path.join(cleaned_dir, csv_files[0])
    print(f"  Using cleaned data: {input_path}")

    cmd = f'python analysis/advanced_analysis.py "{input_path}"'
    return run_step("3. Run Data Analysis", cmd)


def step4_charts():
    """Step 4: Generate charts"""
    cleaned_dir = os.path.join(PROJECT_ROOT, "data", "cleaned")
    if not os.path.exists(cleaned_dir):
        print("[ERROR] No cleaned data directory found.")
        return False

    csv_files = [f for f in os.listdir(cleaned_dir) if f.endswith(".csv")]
    if not csv_files:
        print("[ERROR] No cleaned CSV files found.")
        return False

    csv_files.sort(reverse=True)
    input_path = os.path.join(cleaned_dir, csv_files[0])
    print(f"  Using cleaned data: {input_path}")

    cmd = f'python analysis/chart_generator.py "{input_path}"'
    return run_step("4. Generate Charts", cmd)


def step5_init_db():
    """Step 5: Initialize database"""
    cmd = "python database/models.py"
    return run_step("5. Initialize Database", cmd)


def step6_serve():
    """Step 6: Start web server"""
    print("\n" + "=" * 70)
    print("  STEP 6: Starting Web Server")
    print("  Backend:  http://127.0.0.1:8000")
    print("  API Docs: http://127.0.0.1:8000/docs")
    print("=" * 70)

    cmd = "cd web/backend && python app.py"
    subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT)


def print_summary():
    """Print project summary"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   杭州二手房数据分析系统 - Hangzhou Housing Analysis       ║
╠══════════════════════════════════════════════════════════════╣
║  Pipeline Steps:                                            ║
║    1. Scrape data from hz.lianjia.com                       ║
║    2. Clean and preprocess data                             ║
║    3. Run statistical analysis                              ║
║    4. Generate visualization charts                         ║
║    5. Initialize database                                   ║
║    6. Launch web application                                ║
╠══════════════════════════════════════════════════════════════╣
║  Analysis Modules:                                          ║
║    ✓ Descriptive Statistics                                 ║
║    ✓ Correlation Analysis                                   ║
║    ✓ Multiple Regression (OLS, Ridge)                       ║
║    ✓ PCA / Factor Analysis                                  ║
║    ✓ K-Means Clustering                                     ║
║    ✓ Discriminant Analysis (LDA/QDA)                        ║
╠══════════════════════════════════════════════════════════════╣
║  Web System Pages:                                          ║
║    ✓ Homepage Data Overview                                 ║
║    ✓ Listing Search & Filter                                ║
║    ✓ District Price Analysis                                ║
║    ✓ Price Factor Analysis                                  ║
║    ✓ Comprehensive Evaluation (PCA/FA)                      ║
║    ✓ Listing Classification                                 ║
║    ✓ Purchase Recommendations                               ║
║    ✓ Visualization Charts Gallery                           ║
╚══════════════════════════════════════════════════════════════╝
    """)


def main():
    parser = argparse.ArgumentParser(
        description="Hangzhou Second-hand Housing Analysis Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--skip-scrape", action="store_true", help="Skip scraping step")
    parser.add_argument("--skip-clean", action="store_true", help="Skip cleaning step")
    parser.add_argument("--skip-analysis", action="store_true", help="Skip analysis step")
    parser.add_argument("--skip-charts", action="store_true", help="Skip chart generation")
    parser.add_argument("--pages", type=int, default=120, help="Pages to scrape (default: 120)")
    parser.add_argument("--enrich", type=int, default=50, help="Detail pages to fetch (default: 50)")
    parser.add_argument("--serve-only", action="store_true", help="Only start web server")

    args = parser.parse_args()

    print_summary()

    start_time = datetime.now()

    if args.serve_only:
        step6_serve()
        return

    # Run pipeline
    steps = [
        (lambda: step1_scrape(args.pages, args.enrich), args.skip_scrape, "scraping"),
        (step2_clean, args.skip_clean, "cleaning"),
        (step3_analyze, args.skip_analysis, "analysis"),
        (step4_charts, args.skip_charts, "chart generation"),
        (step5_init_db, False, "database init"),
    ]

    for step_fn, skip, name in steps:
        if skip:
            print(f"\n[Skipping] {name}")
            continue
        if not step_fn():
            print(f"\n[Pipeline Halted] Step '{name}' failed.")
            print("Fix the error and re-run, or use --skip-{name} to bypass.")
            return

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n{'=' * 70}")
    print(f"  Pipeline completed in {elapsed:.1f} seconds!")
    print(f"{'=' * 70}")

    # Start server
    step6_serve()


if __name__ == "__main__":
    main()
