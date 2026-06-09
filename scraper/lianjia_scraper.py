# Lianjia (链家) Scraper for Hangzhou Second-hand Housing
# =========================================================
# Scrapes: hz.lianjia.com/ershoufang/

import requests
from bs4 import BeautifulSoup
import time
import random
import re
import json
import csv
import os
import sys
from datetime import datetime
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SCRAPER

BASE_URL = SCRAPER["base_url"]
HEADERS = {
    "User-Agent": SCRAPER["user_agent"],
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://hz.lianjia.com/",
    "Cache-Control": "max-age=0",
}

def parse_house_info(info_str):
    """Parse houseInfo string like '3室2厅 | 89.5平米 | 南 | 精装 | 高楼层(共18层)'"""
    result = {
        "layout": None,
        "rooms": None,
        "halls": None,
        "floor_area": None,
        "orientation": None,
        "decoration": None,
        "floor": None,
        "total_floors": None,
    }

    if not info_str:
        return result

    parts = [p.strip() for p in info_str.split("|")]

    # Layout: 3室2厅
    if len(parts) >= 1:
        result["layout"] = parts[0]
        layout_match = re.match(r"(\d+)室(\d+)厅", parts[0])
        if layout_match:
            result["rooms"] = int(layout_match.group(1))
            result["halls"] = int(layout_match.group(2))

    # Area: 89.5平米
    if len(parts) >= 2:
        area_match = re.search(r"([\d.]+)", parts[1])
        if area_match:
            result["floor_area"] = float(area_match.group(1))

    # Orientation: 南, 南北, etc.
    if len(parts) >= 3:
        result["orientation"] = parts[2]

    # Decoration: 精装, 简装, 毛坯, etc.
    if len(parts) >= 4:
        result["decoration"] = parts[3]

    # Floor: 高楼层(共18层), 低楼层(共6层), etc.
    if len(parts) >= 5:
        floor_str = parts[4]
        result["floor"] = floor_str
        # Determine floor level
        if "低楼层" in floor_str:
            result["floor"] = "low"
        elif "中楼层" in floor_str:
            result["floor"] = "middle"
        elif "高楼层" in floor_str:
            result["floor"] = "high"
        # Extract total floors
        total_match = re.search(r"共(\d+)层", floor_str)
        if total_match:
            result["total_floors"] = int(total_match.group(1))

    return result


def parse_listing_item(item):
    """Parse a single listing item from the search results page"""
    try:
        # Title and link
        title_elem = item.select_one(".title a")
        if not title_elem:
            return None
        title = title_elem.get_text(strip=True)
        link = title_elem.get("href", "")
        if link and not link.startswith("http"):
            link = urljoin("https://hz.lianjia.com", link)

        # Community name from title (first space-separated part)
        community_name = title.split()[0] if title else None

        # House info
        house_info_elem = item.select_one(".houseInfo")
        house_info = house_info_elem.get_text(strip=True) if house_info_elem else ""
        parsed = parse_house_info(house_info)

        # Position info (district, sub-district)
        position_elem = item.select_one(".positionInfo")
        position_text = position_elem.get_text(strip=True) if position_elem else ""
        # Format: "西湖-文三路" or similar
        district = None
        sub_district = None
        if "-" in position_text:
            parts = position_text.split("-", 1)
            district = parts[0].strip()
            sub_district = parts[1].strip() if len(parts) > 1 else None

        # Total price
        total_price_elem = item.select_one(".totalPrice span")
        total_price = None
        if total_price_elem:
            price_text = total_price_elem.get_text(strip=True)
            try:
                total_price = float(price_text)
            except ValueError:
                total_price = None

        # Unit price
        unit_price_elem = item.select_one(".unitPrice span")
        unit_price = None
        if unit_price_elem:
            up_text = unit_price_elem.get_text(strip=True)
            up_match = re.search(r"([\d,]+)", up_text)
            if up_match:
                unit_price = float(up_match.group(1).replace(",", ""))

        # Follow info (has listing time, sometimes)
        follow_elem = item.select_one(".followInfo")
        follow_text = follow_elem.get_text(strip=True) if follow_elem else ""
        # Extract listing time if present
        listing_time = None
        # Common formats: "xx人关注 / 刚刚发布" or "xx人关注 / 1天以前发布"
        time_match = re.search(r"(\S+?发布)", follow_text)
        if time_match:
            listing_time = time_match.group(1)

        # Subway tag
        tag_elems = item.select(".tag span")
        near_subway = 0
        for tag in tag_elems:
            if "地铁" in tag.get_text(strip=True):
                near_subway = 1
                break

        return {
            "community_name": community_name,
            "district": district,
            "sub_district": sub_district,
            "total_price": total_price,
            "unit_price": unit_price,
            "floor_area": parsed.get("floor_area"),
            "layout": parsed.get("layout"),
            "rooms": parsed.get("rooms"),
            "halls": parsed.get("halls"),
            "floor": parsed.get("floor"),
            "total_floors": parsed.get("total_floors"),
            "orientation": parsed.get("orientation"),
            "decoration": parsed.get("decoration"),
            "construction_year": None,  # Need detail page
            "building_age": None,
            "near_subway": near_subway,
            "listing_time": listing_time,
            "listing_link": link,
        }

    except Exception as e:
        print(f"  [WARN] Error parsing listing item: {e}")
        return None


def scrape_detail_page(url, session):
    """Scrape additional details from a listing's detail page"""
    try:
        resp = session.get(url, headers=HEADERS, timeout=SCRAPER["timeout"])
        if resp.status_code != 200:
            return {}

        soup = BeautifulSoup(resp.text, "lxml")

        # Construction year
        year_elem = soup.select_one(".area .subInfo")
        year = None
        if year_elem:
            year_text = year_elem.get_text(strip=True)
            year_match = re.search(r"(\d{4})年建", year_text)
            if year_match:
                year = int(year_match.group(1))

        # Total floors from introContent
        intro_elems = soup.select(".introContent li")
        total_floors = None
        for elem in intro_elems:
            text = elem.get_text(strip=True)
            if "总楼层" in text or "楼层" in text:
                floor_match = re.search(r"共(\d+)层|总高(\d+)层|(\d+)层", text)
                if floor_match:
                    for g in floor_match.groups():
                        if g:
                            total_floors = int(g)
                            break

        # Subway check
        near_subway = 0
        for elem in intro_elems:
            text = elem.get_text(strip=True)
            if "地铁" in text:
                near_subway = 1
                break

        return {
            "construction_year": year,
            "total_floors_detail": total_floors,
            "near_subway_detail": near_subway,
        }

    except Exception as e:
        print(f"  [WARN] Error scraping detail page {url}: {e}")
        return {}


def scrape_all_pages(max_pages=120, start_page=1):
    """Scrape all listing pages"""
    all_listings = []
    session = requests.Session()
    session.headers.update(HEADERS)

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
    os.makedirs(output_dir, exist_ok=True)

    page = start_page
    consecutive_failures = 0

    print(f"=" * 60)
    print(f"Starting Hangzhou Lianjia Second-hand Housing Scraper")
    print(f"Target: {max_pages} pages (~{max_pages * 30} listings)")
    print(f"=" * 60)

    while page <= max_pages and consecutive_failures < 5:
        url = f"{BASE_URL}pg{page}/" if page > 1 else BASE_URL
        print(f"\n[Page {page}/{max_pages}] Fetching: {url}")

        try:
            delay = random.uniform(SCRAPER["delay_min"], SCRAPER["delay_max"])
            time.sleep(delay)

            resp = session.get(url, headers=HEADERS, timeout=SCRAPER["timeout"])
            print(f"  Status: {resp.status_code}")

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "lxml")

                # Check for anti-scraping / captcha
                if "访问验证" in resp.text or "请输入验证码" in resp.text:
                    print("  [ERROR] Anti-scraping detected! Waiting 60 seconds...")
                    time.sleep(60)
                    consecutive_failures += 1
                    continue

                listing_items = soup.select(".sellListContent li")
                print(f"  Found {len(listing_items)} listings on this page")

                if len(listing_items) == 0:
                    print("  [WARN] No listings found. Page structure may have changed.")
                    consecutive_failures += 1
                    page += 1
                    continue

                page_listings = 0
                for item in listing_items:
                    listing = parse_listing_item(item)
                    if listing and listing["total_price"] is not None:
                        all_listings.append(listing)
                        page_listings += 1

                print(f"  Parsed {page_listings} valid listings. Total: {len(all_listings)}")
                consecutive_failures = 0
                page += 1

                # Save checkpoint every 5 pages
                if page % 5 == 0:
                    checkpoint_path = os.path.join(output_dir, f"checkpoint_p{page-1}_{len(all_listings)}.json")
                    with open(checkpoint_path, "w", encoding="utf-8") as f:
                        json.dump(all_listings, f, ensure_ascii=False, indent=2)
                    print(f"  [Checkpoint] Saved {len(all_listings)} listings")

            elif resp.status_code == 302:
                print("  [ERROR] Redirected - likely anti-scraping. Stopping.")
                break
            else:
                print(f"  [ERROR] Unexpected status code: {resp.status_code}")
                consecutive_failures += 1
                page += 1

        except requests.exceptions.Timeout:
            print(f"  [ERROR] Request timeout. Retrying...")
            consecutive_failures += 1
            time.sleep(10)
        except requests.exceptions.ConnectionError:
            print(f"  [ERROR] Connection error. Waiting 30 seconds...")
            consecutive_failures += 1
            time.sleep(30)
        except Exception as e:
            print(f"  [ERROR] Unexpected error: {e}")
            consecutive_failures += 1
            page += 1

    # Final save
    final_path = os.path.join(output_dir, f"hangzhou_raw_{len(all_listings)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    csv_path = os.path.join(output_dir, f"hangzhou_raw_{len(all_listings)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(all_listings, f, ensure_ascii=False, indent=2)

    # Also save as CSV
    if all_listings:
        keys = all_listings[0].keys()
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_listings)

    print(f"\n{'=' * 60}")
    print(f"Scraping complete!")
    print(f"Total listings collected: {len(all_listings)}")
    print(f"JSON saved to: {final_path}")
    print(f"CSV saved to: {csv_path}")
    print(f"{'=' * 60}")

    return all_listings


def enrich_with_details(listings, max_detail_pages=50):
    """Enrich a sample of listings with detail page data to get construction year"""
    print(f"\n[Enrichment] Fetching detail pages for up to {max_detail_pages} listings...")
    session = requests.Session()
    session.headers.update(HEADERS)

    enriched = 0
    for i, listing in enumerate(listings):
        if enriched >= max_detail_pages:
            break
        if listing.get("construction_year") is not None:
            continue
        link = listing.get("listing_link")
        if not link:
            continue

        delay = random.uniform(1, 3)
        time.sleep(delay)

        details = scrape_detail_page(link, session)
        if details.get("construction_year"):
            listing["construction_year"] = details["construction_year"]
            # Calculate building age
            current_year = datetime.now().year
            listing["building_age"] = current_year - details["construction_year"]
            enriched += 1
            if enriched % 10 == 0:
                print(f"  Enriched {enriched} listings with construction year")

    print(f"  Done: enriched {enriched} listings")
    return listings


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape Hangzhou Lianjia second-hand housing data")
    parser.add_argument("--pages", type=int, default=120, help="Number of pages to scrape")
    parser.add_argument("--start", type=int, default=1, help="Starting page")
    parser.add_argument("--enrich", type=int, default=50, help="Number of detail pages to fetch for enrichment")
    parser.add_argument("--output", type=str, default=None, help="Output file path")

    args = parser.parse_args()

    print("Hangzhou Second-hand Housing Scraper")
    print(f"Target: {args.pages} pages, starting from page {args.start}")
    print()

    listings = scrape_all_pages(max_pages=args.pages, start_page=args.start)

    if listings and args.enrich > 0:
        listings = enrich_with_details(listings, max_detail_pages=args.enrich)

    print(f"\nFinal count: {len(listings)} listings")
