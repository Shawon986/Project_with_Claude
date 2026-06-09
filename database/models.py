# Database Models for Hangzhou Second-hand Housing Analysis

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_URL

Base = declarative_base()

class HousingListing(Base):
    """Raw scraped housing listing data"""
    __tablename__ = "housing_listings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    community_name = Column(String(200), comment="Community name")
    district = Column(String(100), comment="District")
    sub_district = Column(String(100), comment="Sub-district / block")
    total_price = Column(Float, comment="Total price (10k RMB)")
    unit_price = Column(Float, comment="Unit price (RMB/sqm)")
    floor_area = Column(Float, comment="Floor area (sqm)")
    layout = Column(String(50), comment="Layout (e.g., 3室2厅)")
    rooms = Column(Integer, comment="Number of bedrooms")
    halls = Column(Integer, comment="Number of living rooms")
    floor = Column(String(50), comment="Floor level (low/middle/high)")
    floor_num = Column(String(50), comment="Floor number description")
    total_floors = Column(Integer, comment="Total floors of building")
    orientation = Column(String(100), comment="Orientation")
    decoration = Column(String(100), comment="Decoration status")
    construction_year = Column(Integer, comment="Construction year")
    building_age = Column(Integer, comment="Building age (years)")
    near_subway = Column(Integer, default=0, comment="Near subway (0=no, 1=yes)")
    listing_time = Column(String(50), comment="Listing time")
    listing_link = Column(String(500), comment="Source link")
    created_at = Column(String(50), comment="Record creation time")

class CleanedListing(Base):
    """Cleaned and processed listing data"""
    __tablename__ = "cleaned_listings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    community_name = Column(String(200))
    district = Column(String(100))
    sub_district = Column(String(100))
    total_price = Column(Float)
    unit_price = Column(Float)
    floor_area = Column(Float)
    layout = Column(String(50))
    rooms = Column(Integer)
    halls = Column(Integer)
    floor_type = Column(String(20))  # low/middle/high
    total_floors = Column(Integer)
    orientation_encoded = Column(String(50))  # south, north, east, west encoded
    decoration_level = Column(Integer)  # 0-3 encoded
    construction_year = Column(Integer)
    building_age = Column(Integer)
    near_subway = Column(Integer)
    listing_time = Column(String(50))
    listing_link = Column(String(500))
    # Derived fields
    floor_ratio = Column(Float)  # floor position ratio
    price_per_room = Column(Float)
    area_per_room = Column(Float)

class AnalysisResult(Base):
    """Stored analysis results"""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_type = Column(String(100))
    result_name = Column(String(200))
    result_value = Column(Text)
    chart_path = Column(String(500))
    created_at = Column(String(50))


def init_db(db_path=None):
    """Initialize database and create all tables"""
    if db_path:
        engine = create_engine(f"sqlite:///{db_path}")
    else:
        engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine=None):
    """Get a database session"""
    if engine is None:
        engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
