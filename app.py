import streamlit as st
from model import predict_url

st.title("URL Phishing Detection")

url = st.text_input("Enter URL")

if st.button("Check"):
    result = predict_url(url)
    st.write(result)