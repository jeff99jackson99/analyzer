import streamlit as st

st.title("🚀 Minimal Test App")
st.write("This app uses NO external dependencies.")
st.write("Only built-in Python and Streamlit.")

st.success("✅ If you see this, basic deployment is working!")

# Test basic Python functionality
import datetime
st.write(f"Current time: {datetime.datetime.now()}")

# Test if we can import basic libraries
try:
    import json
    st.write("✅ json imported successfully")
except ImportError as e:
    st.error(f"❌ json import failed: {e}")

try:
    import os
    st.write("✅ os imported successfully")
except ImportError as e:
    st.error(f"❌ os import failed: {e}")

st.write("---")
st.write("**This app should deploy without any requirements issues.**")
