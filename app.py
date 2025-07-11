# ✅ Streamlit MVP: JD & Candidate Upload + Folder Creation + Google Sheets Logging

import streamlit as st
import pandas as pd
import os
import datetime
import pytesseract
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheet Setup ---
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SHEET_NAME = "Recruitment Tracker"
CREDENTIALS_FILE = "your-google-service-account.json"  # Upload this in Streamlit Cloud if needed

@st.cache_resource
def connect_to_sheet():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPE)
    gc = gspread.authorize(creds)
    sheet = gc.open(SHEET_NAME).sheet1
    return sheet

sheet = connect_to_sheet()

# --- UI ---
st.title("🤖 AI Recruiter Assistant – MVP")
st.markdown("Upload JD (text/image) and Candidate Excel. I’ll do the rest.")

uploaded_jd = st.file_uploader("Upload JD (PDF/Image/Text)", type=["txt", "png", "jpg", "jpeg"])
uploaded_excel = st.file_uploader("Upload Candidate Excel", type=["xlsx", "xls"])

# --- Step 1: Extract JD Text ---
def extract_text(file):
    if file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    elif file.type.startswith("image"):
        image = Image.open(file)
        return pytesseract.image_to_string(image)
    else:
        return "[Unsupported format for JD text extraction]"

# --- Step 2: Process Uploaded Excel ---
def process_excel(file):
    return pd.read_excel(file)

# --- Step 3: Create Folder Name ---
def create_folder_name(jd_text):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    first_line = jd_text.strip().split("\n")[0]
    title = first_line[:40].replace(" ", "_")
    return f"{title}_{today}"

# --- Step 4: Upload to Google Sheet ---
def write_to_sheet(df):
    for _, row in df.iterrows():
        sheet.append_row(row.fillna("").astype(str).tolist())

# --- Main Logic ---
if uploaded_jd and uploaded_excel:
    jd_text = extract_text(uploaded_jd)
    candidates_df = process_excel(uploaded_excel)
    folder_name = create_folder_name(jd_text)

    st.success(f"📁 Created folder: {folder_name}")
    st.code(jd_text[:500], language='markdown')
    st.dataframe(candidates_df)

    # Add JD and folder info to the Excel
    candidates_df["Source"] = folder_name
    write_to_sheet(candidates_df)
    st.success("✅ Candidate details logged to Google Sheet!")

    # Save files to local folder (you can change this to cloud later)
    os.makedirs(folder_name, exist_ok=True)
    with open(os.path.join(folder_name, "JD.txt"), "w") as f:
        f.write(jd_text)
    candidates_df.to_excel(os.path.join(folder_name, "candidates.xlsx"), index=False)
    st.info("All files saved to folder locally (in online cloud, link this to S3/Drive)")
else:
    st.warning("Please upload both JD and Candidate Excel file")
