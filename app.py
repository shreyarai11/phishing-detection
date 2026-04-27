import streamlit as st
import requests
import time
from model import predict_url

# 🔐 Get API key from Streamlit Secrets
API_KEY = st.secrets.get("API_KEY", "").strip()


# 🔍 URLScan function
def scan_url(url):
    # ❗ Check API key
    if not API_KEY:
        return "❌ API key missing. Add it in Streamlit Secrets."

    headers = {
        "Content-Type": "application/json",
        "API-Key": API_KEY,
        "User-Agent": "Phishing-Detector-App"
    }

    data = {
        "url": url,
        "visibility": "unlisted"
    }

    try:
        response = requests.post(
            "https://urlscan.io/api/v1/scan/",
            headers=headers,
            json=data
        )
    except Exception as e:
        return f"❌ Request Error: {e}"

    # ❌ Error handling
    if response.status_code != 200:
        return f"❌ Error {response.status_code}: {response.text}"

    result = response.json()
    uuid = result.get("uuid", "")

    if not uuid:
        return "❌ Failed to get scan ID"

    time.sleep(10)

    result_api = f"https://urlscan.io/api/v1/result/{uuid}/"

    # 🔁 Polling
    for _ in range(10):
        try:
            res = requests.get(result_api)
        except Exception as e:
            return f"❌ Result Fetch Error: {e}"

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

        # 🤖 ML Prediction
        try:
            ml_result = predict_url(url)
        except Exception as e:
            ml_result = f"ML Error: {e}"

        if "phishing" in str(ml_result).lower():
            st.error("🤖 ML Model: PHISHING ⚠️")
        else:
            st.success("🤖 ML Model: SAFE ✅")

        # 🔍 API Scan
        scan_result = scan_url(url)

        # 🌐 Handle API result
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

            except Exception as e:
                st.warning("⚠️ Could not extract full details")
                st.write(scan_result)

        else:
            # 🔥 Handle spam / API block
            if "spam" in str(scan_result).lower():
                st.warning("⚠️ This URL cannot be scanned (blocked by API). Try another URL.")
            else:
                st.error(scan_result)