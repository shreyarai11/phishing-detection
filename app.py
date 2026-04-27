
import streamlit as st
import requests
import time
from model import predict_url

# 🔑 Paste your API key here
API_KEY = " 019dcda5-d2a7-716f-a41f-6f97686f468d"


# 🔍 URLScan function
def scan_url(url):
    headers = {
        "Content-Type": "application/json",
        "API-Key": API_KEY,
        "User-Agent": "Phishing-Detector-App"
    }

    data = {
        "url": url,
        "visibility": "unlisted"
    }

    response = requests.post(
        "https://urlscan.io/api/v1/scan/",
        headers=headers,
        json=data
    )

    # ❌ Error handling
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
        # ✅ Auto-fix URL
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

        # 🤖 ML Output
        if "phishing" in str(ml_result).lower():
            st.error("🤖 ML Model: PHISHING ⚠️")
        else:
            st.success("🤖 ML Model: SAFE ✅")

        # 🌐 API Result Handling
        if isinstance(scan_result, dict):
            try:
                verdict = scan_result.get("verdicts", {}).get("overall", {}).get("malicious", False)

                if verdict:
                    st.error("🚨 URLScan Result: MALICIOUS")
                else:
                    st.success("✅ URLScan Result: SAFE")

                # 📊 Safe extraction
                domain = scan_result.get("page", {}).get("domain", "Not Available")
                ip = scan_result.get("page", {}).get("ip", "Not Available")

                st.write("🌍 Domain:", domain)
                st.write("🖥️ IP Address:", ip)

                # 🔗 Report
                report_url = scan_result.get("task", {}).get("reportURL", "")
                if report_url:
                    st.write("📄 Detailed Report:")
                    st.write(report_url)

            except:
                st.warning("⚠️ Could not extract full details")
                st.write(scan_result)

        else:
            # 🔥 Handle spam / API block nicely
            if "spam" in str(scan_result).lower():
                st.warning("⚠️ This URL cannot be scanned (blocked by API). Try another URL.")
            else:
                st.error(scan_result)