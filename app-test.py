import streamlit as st

st.title("🚀 Test App - Streamlit Cloud Compatible")

st.write("This is a minimal test app to verify Streamlit Cloud deployment.")

st.success("✅ If you can see this, the basic deployment is working!")

# Test basic imports
try:
    import requests
    st.write("✅ requests imported successfully")
except ImportError as e:
    st.error(f"❌ requests import failed: {e}")

try:
    import pandas as pd
    st.write("✅ pandas imported successfully")
except ImportError as e:
    st.error(f"❌ pandas import failed: {e}")

try:
    from bs4 import BeautifulSoup
    st.write("✅ beautifulsoup4 imported successfully")
except ImportError as e:
    st.error(f"❌ beautifulsoup4 import failed: {e}")

st.write("---")
st.write("**Next step:** Once this works, we'll add the full dashboard functionality.")
