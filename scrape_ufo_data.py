import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time

def geocode_location(city, state):
    """Get lat/lng for a city using Nominatim (free)"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?city={city}&state={state}&country=USA&format=json"
        headers = {'User-Agent': 'UFO-Tracker/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"Geocoding error for {city}, {state}: {e}")
    return None, None

def scrape_nuforc():
    """Scrape recent reports from NUFORC"""
    reports = []
    
    try:
        # NUFORC recent reports page
        url = "https://nuforc.org/webreports/ndxevent.html"
        headers = {'User-Agent': 'UFO-Tracker/1.0'}
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse table (NUFORC uses tables for reports)
        table = soup.find('table')
        if not table:
            print("No table found")
            return reports
        
        rows = table.find_all('tr')[1:50]  # Get first 50 reports, skip header
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                try:
                    date_str = cols[0].get_text(strip=True)
                    location = cols[1].get_text(strip=True)
                    shape = cols[2].get_text(strip=True)
                    duration = cols[3].get_text(strip=True)
                    summary = cols[4].get_text(strip=True)
                    
                    # Parse location (usually "City (State)")
                    if '(' in location:
                        city = location.split('(')[0].strip()
                        state = location.split('(')[1].replace(')', '').strip()
                    else:
                        city = location
                        state = "Unknown"
                    
                    # Get coordinates
                    lat, lng = geocode_location(city, state)
                    
                    if lat and lng:
                        report = {
                            "date": date_str,
                            "city": city,
                            "state": state,
                            "lat": lat,
                            "lng": lng,
                            "shape": shape,
                            "duration": duration,
                            "summary": summary
                        }
                        reports.append(report)
                        print(f"Added: {city}, {state}")
                    
                    # Rate limit geocoding
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error parsing row: {e}")
                    continue
        
    except Exception as e:
        print(f"Scraping error: {e}")
    
    return reports

def save_data(reports):
    """Save to JSON file"""
    data = {
        "updated": datetime.now().isoformat(),
        "reports": reports
    }
    
    with open('ufo-data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Saved {len(reports)} reports")

if __name__ == "__main__":
    print("Scraping NUFORC data...")
    reports = scrape_nuforc()
    save_data(reports)
