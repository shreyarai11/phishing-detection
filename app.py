import streamlit as st
import requests
import time
from model import predict_url

# -----------------------------
# 🔐 LOAD API KEY SAFELY
# -----------------------------
API_KEY = st.secrets.get("019dce1f-4190-715a-af73-18088e8d0885", None)

if not API_KEY:
    st.error("❌ API key missing. Add it in Streamlit Secrets as API_KEY.")
    st.stop()


# -----------------------------
# 🔍 URLSCAN FUNCTION
# -----------------------------
def scan_url(url):
    headers = {
        "Content-Type": "application/json",
        "API-Key": API_KEY,
        "User-Agent": "Phishing-Detection-App"
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
        return {"error": str(e)}

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    uuid = result.get("uuid")

    if not uuid:
        return {"error": "No UUID returned"}

    # Wait for scan
    time.sleep(10)

    result_url = f"https://urlscan.io/api/v1/result/{uuid}/"

    for _ in range(10):
        try:
            res = requests.get(result_url)
            if res.status_code == 200:
                return res.json()
        except:
            pass
        time.sleep(3)

    return {"error": "Scan timeout"}


# -----------------------------
# 🎨 UI
# -----------------------------
st.set_page_config(page_title="Phishing Detector", page_icon="🔐")

st.title("🔐 Phishing URL Detection System")
st.write("Enter a URL to check whether it is safe or malicious.")

url = st.text_input("🌐 Enter URL here:")


# -----------------------------
# 🚀 BUTTON ACTION
# -----------------------------
if st.button("Check URL"):

    if not url:
        st.warning("⚠️ Please enter a URL")
        st.stop()

    if not url.startswith("http"):
        url = "https://" + url

    st.write("🔗 Checking:", url)
    st.info("⏳ Scanning URL... please wait")

    # -------------------------
    # 🤖 ML PREDICTION
    # -------------------------
    try:
        ml_result = predict_url(url)
        if "phishing" in str(ml_result).lower():
            st.error("🤖 ML Model: PHISHING ⚠️")
        else:
            st.success("🤖 ML Model: SAFE ✅")
    except Exception as e:
        st.warning(f"ML Error: {e}")

    # -------------------------
    # 🌐 URLSCAN API
    # -------------------------
    scan_result = scan_url(url)

    if isinstance(scan_result, dict) and "error" in scan_result:
        st.error(f"❌ URLScan Error: {scan_result['error']}")
    else:
        try:
            malicious = scan_result.get("verdicts", {}).get("overall", {}).get("malicious", False)

            if malicious:
                st.error("🚨 URLScan Result: MALICIOUS")
            else:
                st.success("✅ URLScan Result: SAFE")

            page = scan_result.get("page", {})
            st.write("🌍 Domain:", page.get("domain", "N/A"))
            st.write("🖥️ IP:", page.get("ip", "N/A"))

            report = scan_result.get("task", {}).get("reportURL", "")
            if report:
                st.write("📄 Report Link:")
                st.write(report)

        except Exception as e:
            st.warning(f"Parsing error: {e}")