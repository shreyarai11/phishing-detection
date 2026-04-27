import streamlit as st
import requests
import time
from model import predict_url

# 🔐 URLSCAN API KEY (put directly OR later move to secrets)
API_KEY = "019dce1f-4190-715a-af73-18088e8d0885"

# -----------------------------
# 🌐 URLSCAN SUBMIT FUNCTION
# -----------------------------
def submit_scan(url):
    headers = {
        "API-Key": API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    data = {
        "url": url,
        "visibility": "public"
    }

    try:
        res = requests.post(
            "https://urlscan.io/api/v1/scan/",
            headers=headers,
            json=data
        )

        # 🚨 handle spam block
        if res.status_code != 200:
            return {"error": res.text}

        return res.json()

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# 🔍 GET RESULT FUNCTION
# -----------------------------
def get_result(uuid):
    result_url = f"https://urlscan.io/api/v1/result/{uuid}/"

    for _ in range(15):
        try:
            r = requests.get(result_url)

            if r.status_code == 200:
                return r.json()

        except:
            pass

        time.sleep(3)

    return {"error": "Scan timeout"}


# -----------------------------
# 🎨 UI
# -----------------------------
st.set_page_config(page_title="Phishing Detector", page_icon="🔐")

st.title("🔐 Phishing URL Detection System")
st.write("Check whether a URL is safe or malicious")

url = st.text_input("🌐 Enter URL:")


# -----------------------------
# 🚀 BUTTON
# -----------------------------
if st.button("Check URL"):

    if not url:
        st.warning("Enter a URL")
        st.stop()

    if not url.startswith("http"):
        url = "https://" + url

    st.write("🔗 Checking:", url)
    st.info("Scanning... please wait")

    # -------------------------
    # 🤖 ML PREDICTION
    # -------------------------
    try:
        ml_result = predict_url(url)

        if "phishing" in str(ml_result).lower():
            st.error("🤖 ML: PHISHING ⚠️")
        else:
            st.success("🤖 ML: SAFE ✅")

    except Exception as e:
        st.warning(f"ML Error: {e}")

    # -------------------------
    # 🌐 URLSCAN API
    # -------------------------
    scan = submit_scan(url)

    if "error" in scan:
        st.error("❌ URLScan Error")
        st.write(scan["error"])
        st.stop()

    uuid = scan.get("uuid")

    if not uuid:
        st.error("No scan ID returned")
        st.stop()

    st.write("⏳ Scan started... waiting results")

    result = get_result(uuid)

    if "error" in result:
        st.error(result["error"])
    else:
        try:
            verdict = result.get("verdicts", {}).get("overall", {}).get("malicious", False)

            if verdict:
                st.error("🚨 MALICIOUS WEBSITE")
            else:
                st.success("✅ SAFE WEBSITE")

            page = result.get("page", {})

            st.write("🌍 Domain:", page.get("domain"))
            st.write("🖥️ IP:", page.get("ip"))

            report = result.get("task", {}).get("reportURL")
            if report:
                st.write("📄 Report:", report)

        except Exception as e:
            st.warning(f"Parsing error: {e}")