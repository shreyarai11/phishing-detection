
import streamlit as st
import requests
import time
from model import predict_url

# 🔑 Paste your API key here
API_KEY = "019dcda5-d2a7-716f-a41f-6f97686f468d"


# 🔍 URLScan function
def scan_url(url):
    headers = {
        "Content-Type": "application/json",
        "API-Key": API_KEY,
        "User-Agent": "Phishing-Detector-App"   # ✅ FIX ADDED
    }

    data = {
        "url": url,
        "visibility": "unlisted"   # ✅ FIX ADDED
    }

    response = requests.post(
        "https://urlscan.io/api/v1/scan/",
        headers=headers,
        json=data
    )

    # ✅ DEBUG (shows real error)
    if response.status_code != 200:
        return f"❌ Error {response.status_code}: {response.text}"

    result = response.json()
    uuid = result["uuid"]

    time.sleep(10)

    result_api = f"https://urlscan.io/api/v1/result/{uuid}/"

    for _ in range(10):
        res = requests.get(result_api)

        if res.status_code == 200:
            return res.json()

        time.sleep(3)

    return "❌ Scan taking too long"


# 🎨 UI
st.set_page_config(page_title="Phishing Detector", page_icon="🔐")

st.title("🔐 Phishing URL Detection System")
st.write("Enter a URL to check whether it is safe or malicious.")

url = st.text_input("🌐 Enter URL here:")


# 🚀 BUTTON
if st.button("Check URL"):
    if url.strip() == "":
        st.warning("⚠️ Please enter a URL")
    else:
        # ✅ AUTO FIX URL
        if not url.startswith("http"):
            url = "https://" + url

        st.write("🔗 Checking:", url)
        st.info("⏳ Scanning URL... please wait")

        # 🔍 API Scan
        scan_result = scan_url(url)

        # 🤖 ML Prediction
        try:
            ml_result = predict_url(url)
        except:
            ml_result = "ML model error"

        st.write("🤖 ML Prediction:", ml_result)

        # 🌐 API Result
        if isinstance(scan_result, dict):
            try:
                verdict = scan_result["verdicts"]["overall"]["malicious"]

                if verdict:
                    st.error("🚨 URLScan Result: MALICIOUS")
                else:
                    st.success("✅ URLScan Result: SAFE")

                # 📊 Extra info
                st.write("🌍 Domain:", scan_result["page"]["domain"])
                st.write("🖥️ IP Address:", scan_result["page"]["ip"])

                # 🔗 Report
                st.write("📄 Detailed Report:")
                st.write(scan_result["task"]["reportURL"])

            except:
                st.warning("⚠️ Could not extract full details")
                st.write(scan_result)
        else:
            st.error(scan_result)
