# Hangzhou Second-hand Housing Analysis System
# =============================================
# Configuration File

# Database
DATABASE_URL = "sqlite:///database/hangzhou_housing.db"

# Scraper Settings
SCRAPER = {
    "base_url": "https://hz.lianjia.com/ershoufang/",
    "max_pages": 120,
    "delay_min": 2,
    "delay_max": 5,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "timeout": 15,
}

# Data Cleaning Settings
CLEANING = {
    "price_outlier_std": 3,  # Z-score threshold for price outliers
    "area_min": 20,           # Minimum reasonable area (sqm)
    "area_max": 500,          # Maximum reasonable area (sqm)
    "price_per_sqm_min": 5000,  # Minimum reasonable unit price
    "price_per_sqm_max": 150000, # Maximum reasonable unit price
    "building_age_max": 80,   # Maximum reasonable building age
}

# Analysis Settings
ANALYSIS = {
    "n_clusters": 5,          # Number of clusters for K-means
    "n_factors": 5,           # Number of factors for factor analysis
    "test_size": 0.3,         # Test set ratio
    "random_state": 42,
}

# Server Settings
SERVER = {
    "host": "127.0.0.1",
    "port": 8000,
    "reload": True,
}
