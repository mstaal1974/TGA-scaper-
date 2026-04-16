import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

st.set_page_config(page_title="TGA Scraper Pro", page_icon="🇦🇺")

# --- UI SETUP ---
st.title("TGA Classification Scraper")
st.markdown("Extracts **ANZSCO** and **Occupations** to match your Excel format.")

# Input for multiple codes
input_codes = st.text_area("Paste Qualification Codes (one per line or comma-separated)", 
                          placeholder="MSL20122\nMSL30122", height=150)

# --- SCRAPER LOGIC ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/119.0"
]

def scrape_tga_details(code):
    url = f"https://training.gov.au/Training/Details/{code}"
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return {"Qualification Code": code, "Error": f"Status {response.status_code}"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Format the result to match your CSV headers exactly
        data = {
            "Qualification Code": code,
            "ANZSCO Identifier": "Not Found",
            "Taxonomy - Occupation": "Not Found"
        }
        
        # Locate the Classifications table rows
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                scheme = cells[0].get_text(strip=True)
                val_code = cells[1].get_text(strip=True)
                val_text = cells[2].get_text(strip=True)
                
                if "ANZSCO Identifier" in scheme:
                    # Formats like "311400 - Science Technicians"
                    data["ANZSCO Identifier"] = f"{val_code} - {val_text}"
                
                elif "Taxonomy - Occupation" in scheme:
                    # This captures the full comma-separated list from your image
                    data["Taxonomy - Occupation"] = val_text
                    
        return data
    except Exception as e:
        return {"Qualification Code": code, "Error": str(e)}

# --- EXECUTION ---
if st.button("Run Extraction"):
    # Clean the input codes
    codes = [c.strip() for c in input_codes.replace(",", "\n").split("\n") if c.strip()]
    
    if not codes:
        st.warning("Please enter at least one code.")
    else:
        results = []
        progress_text = st.empty()
        bar = st.progress(0)
        
        for i, code in enumerate(codes):
            progress_text.text(f"Processing {code} ({i+1}/{len(codes)})...")
            res = scrape_tga_details(code)
            results.append(res)
            
            # Update progress
            bar.progress((i + 1) / len(codes))
            
            # RANDOM DELAY to prevent blocking
            # 2 to 4 seconds is usually enough for TGA
            if i < len(codes) - 1:
                time.sleep(random.uniform(2, 4))
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Show results
        st.subheader("Data Preview")
        st.dataframe(df)
        
        # Download Button (Strictly matching your CSV format)
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Scraped Data (CSV)",
            data=csv_data,
            file_name="tga_occupations_output.csv",
            mime="text/csv"
        )
        st.success("Extraction Complete!")
