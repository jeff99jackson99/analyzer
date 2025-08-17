import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="WaaS Dashboard Claims Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin: 10px 0;
    }
    
    .stButton > button {
        width: 100%;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

class DashboardScraper:
    def __init__(self):
        self.session = requests.Session()
        self.is_authenticated = False
        self.cookies = {}
        
    def check_login_status(self):
        """Check if we're currently logged in by trying to access the dashboard"""
        try:
            # Try to access the dashboard directly
            dashboard_url = "https://app.waas.sdsaz.us/cases/workflow/2"
            response = self.session.get(dashboard_url)
            
            if response.status_code == 200:
                # Check if we're actually logged in by looking for dashboard content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for indicators that we're logged in
                if any(indicator in response.url.lower() for indicator in ['dashboard', 'workflow', 'cases']):
                    # Check if we're not on a login page
                    login_indicators = soup.find_all(text=lambda text: text and any(
                        login in text.lower() for login in ['login', 'sign in', 'username', 'password']
                    ))
                    
                    if not login_indicators or len(login_indicators) < 3:
                        self.is_authenticated = True
                        self.cookies = self.session.cookies.get_dict()
                        return True
            
            return False
            
        except Exception as e:
            st.error(f"❌ Login check error: {e}")
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
                'url': dashboard_url,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            st.error(f"Scraping error: {e}")
            return None

class AIProcessor:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_claims(self, content):
        """Analyze dashboard content using OpenAI"""
        try:
            import openai
            
            # Configure OpenAI
            openai.api_key = self.api_key
            
            # Create a comprehensive prompt for claims analysis
            prompt = f"""
            Analyze the following dashboard content and organize it into a structured format. 
            Focus on identifying claims that are ready for action or need attention.
            
            Please provide the analysis in the following JSON format:
            {{
                "summary": {{
                    "total_claims": number,
                    "ready_for_action": number,
                    "needs_attention": number,
                    "completed": number
                }},
                "ready_claims": [
                    {{
                        "claim_id": "string",
                        "status": "string",
                        "priority": "string",
                        "next_action": "string",
                        "notes": "string"
                    }}
                ],
                "attention_needed": [
                    {{
                        "claim_id": "string",
                        "status": "string",
                        "issue": "string",
                        "recommendation": "string"
                    }}
                ],
                "general_notes": "string"
            }}
            
            Dashboard Content:
            {content[:4000]}  # Limit content length for API
            
            Focus on identifying:
            1. Claims that can move forward in the workflow
            2. Claims that are blocked or need attention
            3. Priority levels and next actions
            4. Any patterns or trends in the data
            """
            
            # Make API call
            response = openai.ChatCompletion.create(
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
    st.markdown('<h1 class="main-header">📊 WaaS Dashboard Claims Analyzer</h1>', unsafe_allow_html=True)
    
    # Show success message
    st.markdown("""
    <div class="success-box">
        <strong>🎉 Successfully Deployed on Streamlit Cloud!</strong><br>
        This app now uses a simple redirect-based authentication flow.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'scraper' not in st.session_state:
        st.session_state.scraper = DashboardScraper()
    if 'ai_processor' not in st.session_state:
        st.session_state.ai_processor = None
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    
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
            value="https://app.waas.sdsaz.us/cases/workflow/2",
            help="URL of the dashboard to scrape after login"
        )
        
        # Authentication section
        st.header("🔐 Authentication")
        
        if not st.session_state.is_authenticated:
            st.info("🔑 **New Authentication Flow:**")
            st.markdown("""
            1. **Click the button below** to go to WaaS dashboard
            2. **Log in** with your credentials on the WaaS site
            3. **Return to this app** and click "Check Login Status"
            4. **Start scraping** once authenticated!
            """)
            
            # Button to redirect to WaaS dashboard
            if st.button("🚀 Go to WaaS Dashboard", type="primary"):
                st.markdown(f"""
                <div style="background-color: #e7f3ff; padding: 15px; border-radius: 5px; border: 1px solid #b3d9ff;">
                    <h4>📋 Instructions:</h4>
                    <ol>
                        <li>Click the link below to open the WaaS dashboard</li>
                        <li>Log in with your credentials</li>
                        <li>Return to this app tab</li>
                        <li>Click "Check Login Status" button</li>
                    </ol>
                    <p><strong>🔗 <a href="{dashboard_url}" target="_blank">Open WaaS Dashboard</a></strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            # Check login status button
            if st.button("🔍 Check Login Status", type="secondary"):
                with st.spinner("Checking login status..."):
                    if st.session_state.scraper.check_login_status():
                        st.session_state.is_authenticated = True
                        st.success("✅ Successfully authenticated with WaaS dashboard!")
                        st.rerun()
                    else:
                        st.error("❌ Not authenticated. Please log in to the WaaS dashboard first.")
        else:
            st.success("🔓 **Authenticated with WaaS Dashboard**")
            if st.button("Logout"):
                st.session_state.is_authenticated = False
                st.session_state.scraper.is_authenticated = False
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
        st.info("👋 Welcome! Please use the sidebar to authenticate with the WaaS dashboard.")
        st.markdown("""
        ### What this app does:
        1. **Redirects you** to the WaaS dashboard for secure login
        2. **Scrapes** the workflow/cases dashboard content
        3. **Uses AI** to analyze and organize the content
        4. **Highlights** claims that can move forward
        5. **Creates** a structured worksheet for easy review
        
        ### Getting Started:
        1. Enter your OpenAI API key in the sidebar
        2. Click "Go to WaaS Dashboard" to authenticate
        3. Log in on the WaaS site
        4. Return and click "Check Login Status"
        5. Start scraping and analyzing!
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
            st.metric("Ready for Action", analysis.get('ready_for_action', 'N/A'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Needs Attention", analysis.get('needs_attention', 'N/A'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Completed", analysis.get('completed', 'N/A'))
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Ready claims section
    if 'ready_claims' in analysis and analysis['ready_claims']:
        st.subheader("🚀 Claims Ready for Action")
        ready_df = pd.DataFrame(analysis['ready_claims'])
        st.dataframe(ready_df, use_container_width=True)
    
    # Attention needed section
    if 'attention_needed' in analysis and analysis['attention_needed']:
        st.subheader("⚠️ Claims Needing Attention")
        attention_df = pd.DataFrame(analysis['attention_needed'])
        st.dataframe(attention_df, use_container_width=True)
    
    # General notes
    if 'general_notes' in analysis and analysis['general_notes']:
        st.subheader("📝 General Notes")
        st.info(analysis['general_notes'])

if __name__ == "__main__":
    main()
