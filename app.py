import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

st.set_page_config(page_title="TGA Scraper", page_icon="🔍")

st.title("Training.gov.au Data Extractor")
st.write("Enter Qualification Codes (comma-separated) to extract ANZSCO and Occupation data.")

# Input area
input_codes = st.text_input("Codes", value="MSL20122, MSL30122")

def scrape_tga(qual_code):
    url = f"https://training.gov.au/Training/Details/{qual_code}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        result = {"Code": qual_code, "ANZSCO": "N/A", "Occupations": "N/A"}
        
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                scheme = cells[0].get_text(strip=True)
                if "ANZSCO Identifier" in scheme:
                    result["ANZSCO"] = f"{cells[1].get_text(strip=True)} - {cells[2].get_text(strip=True)}"
                elif "Taxonomy - Occupation" in scheme:
                    result["Occupations"] = cells[2].get_text(strip=True)
        return result
    except:
        return None

if st.button("Start Scraping"):
    codes = [c.strip() for c in input_codes.split(",")]
    results = []
    
    progress_bar = st.progress(0)
    for i, code in enumerate(codes):
        data = scrape_tga(code)
        if data:
            results.append(data)
        time.sleep(1) # Safety delay
        progress_bar.progress((i + 1) / len(codes))
    
    df = pd.DataFrame(results)
    
    # Show data in the app
    st.subheader("Results")
    st.dataframe(df)
    
    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name="tga_data.csv",
        mime="text/csv",
    )
