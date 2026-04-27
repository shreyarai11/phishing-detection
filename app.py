import streamlit as st
import requests
import time
from model import predict_url

# 🔐 DIRECT API KEY (OLD METHOD)
API_KEY = "019dce1f-4190-715a-af73-18088e8d0885"


def scan_url(url):
    headers = {
        "Content-Type": "application/json",
        "API-Key": API_KEY,
        "User-Agent": "Mozilla/5.0"
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

    return {"error": "timeout"}


# 🎨 UI
st.title("🔐 Phishing URL Detection System")

url = st.text_input("Enter URL")

if st.button("Check URL"):

    if not url.startswith("http"):
        url = "https://" + url

    st.write("Checking:", url)
    st.info("Scanning...")

    # ML prediction
    try:
        ml = predict_url(url)
        st.write("🤖 ML:", ml)
    except:
        st.write("ML error")

    # API scan
    result = scan_url(url)

    if "error" in result:
        st.error(result["error"])
    else:
        try:
            malicious = result.get("verdicts", {}).get("overall", {}).get("malicious", False)

            if malicious:
                st.error("🚨 MALICIOUS")
            else:
                st.success("✅ SAFE")

            st.write("Domain:", result.get("page", {}).get("domain"))
            st.write("IP:", result.get("page", {}).get("ip"))

            st.write("Report:", result.get("task", {}).get("reportURL"))

        except:
            st.write(result)