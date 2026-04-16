import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from fake_useragent import UserAgent

def get_stealth_session():
    session = requests.Session()
    ua = UserAgent()
    session.headers.update({
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })
    return session

def scrape_tga_stealth(code, session):
    url = f"https://training.gov.au/Training/Details/{code}"
    try:
        # Randomized wait between 3-7 seconds to mimic human browsing
        time.sleep(random.uniform(3, 7))
        
        response = session.get(url, timeout=20)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Initialize with your exact CSV column names
            data = {"Qualification Code": code, "ANZSCO Identifier": "N/A", "Taxonomy - Occupation": "N/A"}
            
            rows = soup.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    label = cells[0].get_text(strip=True)
                    if "ANZSCO Identifier" in label:
                        data["ANZSCO Identifier"] = f"{cells[1].get_text(strip=True)} - {cells[2].get_text(strip=True)}"
                    elif "Taxonomy - Occupation" in label:
                        data["Taxonomy - Occupation"] = cells[2].get_text(strip=True)
            return data
        return {"Qualification Code": code, "Error": f"Status {response.status_code}"}
    except Exception as e:
        return {"Qualification Code": code, "Error": str(e)}

# Streamlit UI
st.title("TGA Accurate CSV Extractor")
input_codes = st.text_area("Enter Codes (one per line)")

if st.button("Extract Data"):
    codes = [c.strip() for c in input_codes.split("\n") if c.strip()]
    results = []
    session = get_stealth_session()
    
    for code in codes:
        st.write(f"Processing {code}...")
        res = scrape_tga_stealth(code, session)
        results.append(res)
    
    df = pd.DataFrame(results)
    st.dataframe(df)
    
    # Matching your exact CSV format
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="output.csv", mime="text/csv")
