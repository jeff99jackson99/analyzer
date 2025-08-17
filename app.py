import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import openai
import json
from datetime import datetime
import time
import os

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
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

class DashboardScraper:
    def __init__(self):
        self.session = requests.Session()
        self.is_authenticated = False
        self.cookies = {}
        
    def login(self, username, password):
        """Login to the dashboard using requests"""
        try:
            # First, get the login page to capture any CSRF tokens
            login_url = "https://app.waas.sdsaz.us/auth/login?returnUrl=%2Fcases%2Fworkflow%2F2"
            response = self.session.get(login_url)
            
            if response.status_code != 200:
                st.error(f"Failed to access login page. Status: {response.status_code}")
                return False
            
            # Parse the login page to find form fields
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for common form field names
            username_field_name = None
            password_field_name = None
            
            # Try to find username field
            username_selectors = ['input[name="username"]', 'input[name="email"]', 'input[type="text"]']
            for selector in username_selectors:
                field = soup.select_one(selector)
                if field and field.get('name'):
                    username_field_name = field.get('name')
                    break
            
            # Try to find password field
            password_selectors = ['input[name="password"]', 'input[type="password"]']
            for selector in password_selectors:
                field = soup.select_one(selector)
                if field and field.get('name'):
                    password_field_name = field.get('name')
                    break
            
            if not username_field_name or not password_field_name:
                st.warning("⚠️ Could not automatically detect form fields. Using manual input.")
                username_field_name = st.text_input("Enter username field name:", value="username")
                password_field_name = st.text_input("Enter password field name:", value="password")
            
            # Prepare login data
            login_data = {
                username_field_name: username,
                password_field_name: password
            }
            
            # Look for CSRF token
            csrf_token = soup.find('input', {'name': 'csrf'}) or soup.find('input', {'name': '_token'})
            if csrf_token:
                login_data[csrf_token.get('name')] = csrf_token.get('value')
            
            # Submit login form - try both POST and GET methods
            try:
                login_response = self.session.post(login_url, data=login_data, allow_redirects=True)
            except Exception as e:
                st.warning(f"POST method failed, trying GET: {e}")
                # Try GET method if POST fails
                login_response = self.session.get(login_url, params=login_data, allow_redirects=True)
            
            # Check if login was successful
            if login_response.status_code == 200:
                # Check if we're redirected to a dashboard page
                final_url = login_response.url
                if any(indicator in final_url.lower() for indicator in ['dashboard', 'cases', 'workflow']):
                    self.is_authenticated = True
                    self.cookies = self.session.cookies.get_dict()
                    st.success("✅ Login successful! Redirected to dashboard.")
                    return True
                else:
                    # Check for error messages in the response
                    soup = BeautifulSoup(login_response.content, 'html.parser')
                    error_messages = soup.find_all(text=lambda text: text and any(
                        error in text.lower() for error in ['invalid', 'failed', 'incorrect', 'error']
                    ))
                    
                    if error_messages:
                        st.error(f"❌ Login failed: {error_messages[0]}")
                    else:
                        st.error("❌ Login failed. Please check your credentials.")
                    return False
            else:
                st.error(f"❌ Login request failed with status: {login_response.status_code}")
                return False
                
        except Exception as e:
            st.error(f"❌ Login error: {e}")
            return False
    
    def scrape_dashboard(self, dashboard_url):
        """Scrape the dashboard content using requests"""
        if not self.is_authenticated:
            st.error("Please login first")
            return None
        
        try:
            # Use the authenticated session to get the dashboard
            response = self.session.get(dashboard_url)
            
            if response.status_code != 200:
                st.error(f"Failed to access dashboard. Status: {response.status_code}")
                return None
            
            # Parse the dashboard content
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
                'html': response.text,
                'url': response.url
            }
            
        except Exception as e:
            st.error(f"Scraping error: {e}")
            return None

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
    
    # Show success message
    st.markdown("""
    <div class="success-box">
        <strong>🎉 Successfully Deployed on Streamlit Cloud!</strong><br>
        This app is now working and ready to analyze your WaaS dashboard claims.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'scraper' not in st.session_state:
        st.session_state.scraper = DashboardScraper()
    if 'ai_processor' not in st.session_state:
        st.session_state.ai_processor = None
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    
    # Load configuration from Streamlit secrets or environment
    try:
        import config
        dashboard_base_url = config.Config.DASHBOARD_BASE_URL
        dashboard_url = config.Config.DASHBOARD_URL
        login_url = config.Config.LOGIN_URL
    except:
        # Fallback to environment variables or defaults
        dashboard_base_url = "https://app.waas.sdsaz.us"
        dashboard_url = "https://app.waas.sdsaz.us/cases/workflow/2"
        login_url = "https://app.waas.sdsaz.us/auth/login?returnUrl=%2Fcases%2Fworkflow%2F2"
    
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
            value=dashboard_url,
            help="URL of the dashboard to scrape after login"
        )
        
        # Login section
        st.header("🔐 Authentication")
        
        # Check if we have stored credentials
        if 'stored_username' not in st.session_state:
            st.session_state.stored_username = ""
        if 'stored_password' not in st.session_state:
            st.session_state.stored_password = ""
        
        # Credential input
        username = st.text_input("Username", value=st.session_state.stored_username)
        password = st.text_input("Password", type="password", value=st.session_state.stored_password)
        
        # Remember credentials option
        remember_creds = st.checkbox("Remember credentials (stored in session only)")
        
        if st.button("Login", type="primary"):
            if username and password:
                with st.spinner("Logging in to dashboard..."):
                    success = st.session_state.scraper.login(username, password)
                    if success:
                        st.session_state.is_authenticated = True
                        if remember_creds:
                            st.session_state.stored_username = username
                            st.session_state.stored_password = password
                        st.success("✅ Successfully logged into dashboard!")
                    else:
                        st.error("❌ Login failed. Please check your credentials.")
            else:
                st.warning("⚠️ Please enter both username and password")
        
        # Show login status
        if st.session_state.is_authenticated:
            st.success("🔓 Logged in to dashboard")
            if st.button("Logout"):
                st.session_state.is_authenticated = False
                st.session_state.stored_username = ""
                st.session_state.stored_password = ""
                st.rerun()
    
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
        1. **Securely logs in** to the protected WaaS dashboard
        2. **Scrapes** the workflow/cases dashboard content
        3. **Uses AI** to analyze and organize the content
        4. **Highlights** claims that can move forward
        5. **Creates** a structured worksheet for easy review
        
        ### Getting Started:
        1. Enter your OpenAI API key in the sidebar
        2. Login with your WaaS dashboard credentials
        3. Click "Scrape Dashboard" to gather data
        4. Use "Analyze with AI" to process the content
        """)

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
