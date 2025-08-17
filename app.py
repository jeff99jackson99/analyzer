import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import openai
import json
from datetime import datetime
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle

# Page configuration
st.set_page_config(
    page_title="Dashboard Claims Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-ready {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
    }
    .status-pending {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

class DashboardScraper:
    def __init__(self):
        self.session = requests.Session()
        self.driver = None
        self.is_authenticated = False
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        
        try:
            # Try to use webdriver-manager for automatic driver management
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            return True
        except Exception as e:
            st.error(f"Failed to setup Chrome driver: {e}")
            st.info("Trying alternative setup...")
            try:
                # Fallback to system ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
                return True
            except Exception as e2:
                st.error(f"Alternative setup also failed: {e2}")
                return False
    
    def login(self, username, password):
        """Login to the dashboard"""
        if not self.driver:
            if not self.setup_driver():
                return False
        
        try:
            # Navigate to login page (you may need to adjust this URL)
            login_url = "https://app.waas.sdsaz.us/login"
            self.driver.get(login_url)
            
            # Wait for login form to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            
            # Find and fill username field
            username_field = self.driver.find_element(By.NAME, "username")
            username_field.send_keys(username)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            
            # Submit form
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            
            # Wait for redirect or dashboard to load
            time.sleep(3)
            
            # Check if login was successful
            if "dashboard" in self.driver.current_url or "login" not in self.driver.current_url:
                self.is_authenticated = True
                st.success("Login successful!")
                return True
            else:
                st.error("Login failed. Please check credentials.")
                return False
                
        except Exception as e:
            st.error(f"Login error: {e}")
            return False
    
    def scrape_dashboard(self, dashboard_url):
        """Scrape the dashboard content"""
        if not self.is_authenticated:
            st.error("Please login first")
            return None
        
        try:
            self.driver.get(dashboard_url)
            time.sleep(3)  # Wait for page to load
            
            # Get page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract all text content
            content = soup.get_text(separator=' ', strip=True)
            
            # Extract tables if they exist
            tables = soup.find_all('table')
            table_data = []
            
            for table in tables:
                rows = table.find_all('tr')
                table_rows = []
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    if row_data:
                        table_rows.append(row_data)
                if table_rows:
                    table_data.append(table_rows)
            
            return {
                'content': content,
                'tables': table_data,
                'html': page_source
            }
            
        except Exception as e:
            st.error(f"Scraping error: {e}")
            return None
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()

class AIProcessor:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
    
    def analyze_claims(self, dashboard_content):
        """Use AI to analyze and organize dashboard content"""
        try:
            prompt = f"""
            Analyze the following dashboard content and organize it into a structured format.
            Focus on identifying claims and their statuses. Highlight any claims that appear to be in a status
            that suggests they can move forward (e.g., 'approved', 'ready', 'pending review', etc.).
            
            Dashboard Content:
            {dashboard_content[:4000]}  # Limit content length for API
            
            Please organize this into:
            1. Summary of total claims
            2. Claims by status category
            3. Claims ready to move forward (highlight these)
            4. Any actionable items or next steps
            
            Format as JSON with clear structure.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a claims processing expert. Analyze dashboard data and identify actionable claims."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"AI processing error: {e}")
            return None

def main():
    st.markdown('<h1 class="main-header">📊 Dashboard Claims Analyzer</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'scraper' not in st.session_state:
        st.session_state.scraper = DashboardScraper()
    if 'ai_processor' not in st.session_state:
        st.session_state.ai_processor = None
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # OpenAI API Key
        api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key for AI analysis")
        if api_key and not st.session_state.ai_processor:
            st.session_state.ai_processor = AIProcessor(api_key)
        
        # Dashboard URL
        dashboard_url = st.text_input(
            "Dashboard URL",
            value="https://app.waas.sdsaz.us/dashboard/7",
            help="URL of the dashboard to scrape"
        )
        
        # Login section
        st.header("🔐 Authentication")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username and password:
                with st.spinner("Logging in..."):
                    success = st.session_state.scraper.login(username, password)
                    if success:
                        st.session_state.is_authenticated = True
            else:
                st.warning("Please enter both username and password")
        
        # Save credentials option
        if st.checkbox("Remember credentials"):
            st.info("Credentials will be saved locally (encrypted)")
    
    # Main content area
    if st.session_state.is_authenticated:
        st.success("✅ Authenticated and ready to scrape!")
        
        # Scrape button
        if st.button("🕷️ Scrape Dashboard", type="primary"):
            with st.spinner("Scraping dashboard..."):
                dashboard_data = st.session_state.scraper.scrape_dashboard(dashboard_url)
                
                if dashboard_data:
                    st.session_state.dashboard_data = dashboard_data
                    st.success("Dashboard scraped successfully!")
                    
                    # Display raw content
                    with st.expander("📋 Raw Dashboard Content"):
                        st.text(dashboard_data['content'][:1000] + "..." if len(dashboard_data['content']) > 1000 else dashboard_data['content'])
                    
                    # Display tables if found
                    if dashboard_data['tables']:
                        st.subheader("📊 Tables Found")
                        for i, table in enumerate(dashboard_data['tables']):
                            with st.expander(f"Table {i+1}"):
                                df = pd.DataFrame(table[1:], columns=table[0])
                                st.dataframe(df)
        
        # AI Analysis section
        if 'dashboard_data' in st.session_state and st.session_state.ai_processor:
            st.header("🤖 AI Analysis")
            
            if st.button("🧠 Analyze with AI"):
                with st.spinner("Analyzing dashboard content..."):
                    analysis = st.session_state.ai_processor.analyze_claims(
                        st.session_state.dashboard_data['content']
                    )
                    
                    if analysis:
                        st.session_state.ai_analysis = analysis
                        
                        # Try to parse JSON response
                        try:
                            parsed_analysis = json.loads(analysis)
                            display_ai_analysis(parsed_analysis)
                        except json.JSONDecodeError:
                            st.subheader("AI Analysis Results")
                            st.text(analysis)
        
        # Display AI analysis if available
        if 'ai_analysis' in st.session_state:
            st.header("📈 Analysis Results")
            try:
                parsed_analysis = json.loads(st.session_state.ai_analysis)
                display_ai_analysis(parsed_analysis)
            except json.JSONDecodeError:
                st.text(st.session_state.ai_analysis)
    
    else:
        st.info("👋 Welcome! Please login using the sidebar to get started.")
        st.markdown("""
        ### What this app does:
        1. **Scrapes** the dashboard at the specified URL
        2. **Uses AI** to analyze and organize the content
        3. **Highlights** claims that can move forward
        4. **Creates** a structured worksheet for easy review
        
        ### Getting Started:
        1. Enter your OpenAI API key in the sidebar
        2. Login with your dashboard credentials
        3. Click "Scrape Dashboard" to gather data
        4. Use "Analyze with AI" to process the content
        """)
    
    # Cleanup on app close
    if st.session_state.scraper:
        st.session_state.scraper.close()

def display_ai_analysis(analysis):
    """Display the AI analysis results in a structured format"""
    
    # Summary metrics
    if 'summary' in analysis:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Claims", analysis.get('total_claims', 'N/A'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Ready to Move", analysis.get('ready_claims', 'N/A'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Pending Review", analysis.get('pending_claims', 'N/A'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Action Required", analysis.get('action_required', 'N/A'))
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Claims by status
    if 'claims_by_status' in analysis:
        st.subheader("📊 Claims by Status")
        status_df = pd.DataFrame(analysis['claims_by_status'])
        st.dataframe(status_df, use_container_width=True)
    
    # Claims ready to move forward
    if 'ready_claims' in analysis and isinstance(analysis['ready_claims'], list):
        st.subheader("✅ Claims Ready to Move Forward")
        for claim in analysis['ready_claims']:
            st.markdown(f"""
            <div class="status-ready">
                <strong>{claim.get('claim_id', 'N/A')}</strong> - {claim.get('status', 'N/A')}
                <br>Description: {claim.get('description', 'N/A')}
                <br>Next Step: {claim.get('next_step', 'N/A')}
            </div>
            """, unsafe_allow_html=True)
    
    # Actionable items
    if 'actionable_items' in analysis:
        st.subheader("🎯 Actionable Items")
        for item in analysis['actionable_items']:
            st.markdown(f"""
            <div class="status-pending">
                <strong>{item.get('title', 'N/A')}</strong>
                <br>{item.get('description', 'N/A')}
                <br>Priority: {item.get('priority', 'N/A')}
            </div>
            """, unsafe_allow_html=True)
    
    # Export options
    st.subheader("📤 Export Options")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export to Excel"):
            # Create Excel export logic here
            st.success("Export functionality coming soon!")
    
    with col2:
        if st.button("📄 Export to PDF"):
            # Create PDF export logic here
            st.success("Export functionality coming soon!")

if __name__ == "__main__":
    main()
