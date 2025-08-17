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
    
    .dashboard-preview {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .alternative-urls {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
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
        
    def check_login_status(self):
        """Check if we're currently logged in by trying to access the dashboard"""
        try:
            # Try to access the dashboard directly
            dashboard_url = "https://app.waas.sdsaz.us/dashboard/7"
            
            # Add some headers to make the request look more like a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(dashboard_url, headers=headers, timeout=10)
            
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
    
    def get_dashboard_preview(self):
        """Get a preview of the dashboard content"""
        try:
            dashboard_url = "https://app.waas.sdsaz.us/dashboard/7"
            response = self.session.get(dashboard_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract key information
                title = soup.find('title')
                title_text = title.get_text() if title else "Dashboard"
                
                # Look for main content areas
                main_content = soup.find('main') or soup.find('div', {'class': 'main'}) or soup.find('div', {'id': 'main'})
                
                if main_content:
                    content = main_content.get_text(separator=' ', strip=True)[:500] + "..."
                else:
                    content = soup.get_text(separator=' ', strip=True)[:500] + "..."
                
                # Look for tables
                tables = soup.find_all('table')
                table_count = len(tables)
                
                return {
                    'title': title_text,
                    'content_preview': content,
                    'table_count': table_count,
                    'url': dashboard_url
                }
            
            return None
            
        except Exception as e:
            st.error(f"❌ Preview error: {e}")
            return None
    
    def try_multiple_urls(self):
        """Try multiple dashboard URLs to find the one with content"""
        urls_to_try = [
            "https://app.waas.sdsaz.us/dashboard/7",
            "https://app.waas.sdsaz.us/cases/workflow/2",
            "https://app.waas.sdsaz.us/cases",
            "https://app.waas.sdsaz.us/dashboard",
            "https://app.waas.sdsaz.us/workflow"
        ]
        
        results = []
        
        for url in urls_to_try:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Get content length
                    content = soup.get_text(separator=' ', strip=True)
                    content_length = len(content)
                    
                    # Count tables
                    tables = soup.find_all('table')
                    table_count = len(tables)
                    
                    # Look for claims-related content
                    claims_indicators = soup.find_all(text=lambda text: text and any(
                        claim in text.lower() for claim in ['claim', 'case', 'workflow', 'status', 'priority']
                    ))
                    
                    results.append({
                        'url': url,
                        'status': response.status_code,
                        'content_length': content_length,
                        'table_count': table_count,
                        'claims_indicators': len(claims_indicators),
                        'preview': content[:200] + "..." if content_length > 200 else content
                    })
                    
            except Exception as e:
                results.append({
                    'url': url,
                    'error': str(e),
                    'content_length': 0,
                    'table_count': 0,
                    'claims_indicators': 0,
                    'preview': f"Error: {e}"
                })
        
        return results
    
    def try_api_endpoints(self):
        """Try to find and call API endpoints that the dashboard uses"""
        api_endpoints = [
            "/api/cases",
            "/api/claims", 
            "/api/workflow",
            "/api/dashboard",
            "/api/cases/workflow",
            "/api/cases/status",
            "/api/claims/status"
        ]
        
        results = []
        base_url = "https://app.waas.sdsaz.us"
        
        for endpoint in api_endpoints:
            try:
                url = base_url + endpoint
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    try:
                        # Try to parse as JSON
                        data = response.json()
                        results.append({
                            'endpoint': endpoint,
                            'status': response.status_code,
                            'data_type': 'JSON',
                            'content_length': len(str(data)),
                            'preview': str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                        })
                    except:
                        # Not JSON, treat as text
                        content = response.text
                        results.append({
                            'endpoint': endpoint,
                            'status': response.status_code,
                            'data_type': 'Text',
                            'content_length': len(content),
                            'preview': content[:200] + "..." if len(content) > 200 else content
                        })
                else:
                    results.append({
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'data_type': 'Error',
                        'content_length': 0,
                        'preview': f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                results.append({
                    'endpoint': endpoint,
                    'status': 'Error',
                    'data_type': 'Exception',
                    'content_length': 0,
                    'preview': f"Error: {e}"
                })
        
        return results
    
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
            
            # Debug: Show what we're actually getting
            st.info(f"🔍 Scraping URL: {response.url}")
            st.info(f"📄 Response Status: {response.status_code}")
            
            # Look for different types of content
            content_parts = []
            
            # 1. Main content areas
            main_selectors = [
                'main', 'div[class*="main"]', 'div[id*="main"]', 
                'div[class*="content"]', 'div[id*="content"]',
                'div[class*="dashboard"]', 'div[id*="dashboard"]',
                'div[class*="workflow"]', 'div[id*="workflow"]'
            ]
            
            for selector in main_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(separator=' ', strip=True)
                    if text and len(text) > 10:  # Only add if meaningful content
                        content_parts.append(f"[{selector}]: {text}")
            
            # 2. Look for iframes (embedded content)
            iframes = soup.find_all('iframe')
            if iframes:
                st.info(f"🔍 Found {len(iframes)} iframe(s) - content might be embedded")
                for i, iframe in enumerate(iframes):
                    src = iframe.get('src')
                    if src:
                        content_parts.append(f"[iframe {i+1} src]: {src}")
            
            # 3. Look for JavaScript content
            scripts = soup.find_all('script')
            if scripts:
                st.info(f"🔍 Found {len(scripts)} script(s) - content might be loaded dynamically")
                for script in scripts:
                    if script.string:
                        script_content = script.string.strip()
                        if len(script_content) > 50:  # Only show substantial scripts
                            content_parts.append(f"[script]: {script_content[:200]}...")
            
            # 4. Look for data attributes that might contain content
            data_elements = soup.find_all(attrs={"data-content": True})
            if data_elements:
                st.info(f"🔍 Found {len(data_elements)} elements with data-content")
                for elem in data_elements:
                    content_parts.append(f"[data-content]: {elem.get('data-content')}")
            
            # 5. Extract all text content as fallback
            all_text = soup.get_text(separator=' ', strip=True)
            if all_text:
                content_parts.append(f"[all-text]: {all_text}")
            
            # Combine all content
            full_content = "\n\n".join(content_parts)
            
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
            
            # Show what we found
            if len(content_parts) > 1:
                st.success(f"✅ Found {len(content_parts)} content sections")
            else:
                st.warning("⚠️ Limited content found - dashboard might use JavaScript")
            
            return {
                'content': full_content,
                'tables': table_data,
                'url': dashboard_url,
                'timestamp': datetime.now().isoformat(),
                'content_sections': len(content_parts),
                'iframes_found': len(iframes),
                'scripts_found': len(scripts)
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
    if 'show_preview' not in st.session_state:
        st.session_state.show_preview = False
    if 'alternative_url' not in st.session_state:
        st.session_state.alternative_url = None
    
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
            help="URL of the dashboard to scrape after login"
        )
        
        # Authentication section
        st.header("🔐 Authentication")
        
        if not st.session_state.is_authenticated:
            st.info("🔑 **New Authentication Flow:**")
            st.markdown("""
            1. **Click the link below** to go to WaaS dashboard
            2. **Log in** with your credentials on the WaaS site
            3. **Return to this app** and click "Check Login Status"
            4. **View dashboard details** and start scraping!
            """)
            
            # Instructions and dashboard link
            st.markdown(f"""
            <div style="background-color: #e7f3ff; padding: 15px; border-radius: 5px; border: 1px solid #b3d9ff;">
                <h4>📋 Instructions:</h4>
                <ol>
                    <li>Click the link below to open the WaaS dashboard</li>
                    <li>Log in with your credentials</li>
                    <li>Return to this app tab</li>
                    <li>Click "Check Login Status" button below</li>
                </ol>
                <p><strong>🔗 <a href="https://app.waas.sdsaz.us/dashboard/7" target="_blank">Open WaaS Dashboard</a></strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Check login status button
            if st.button("🔍 Check Login Status", type="primary"):
                with st.spinner("Checking login status..."):
                    try:
                        if st.session_state.scraper.check_login_status():
                            st.session_state.is_authenticated = True
                            st.success("✅ Successfully authenticated with WaaS dashboard!")
                            st.rerun()
                        else:
                            st.error("❌ Not authenticated. Please log in to the WaaS dashboard first.")
                    except Exception as e:
                        st.error(f"❌ Error checking login status: {e}")
        else:
            st.success("🔓 **Authenticated with WaaS Dashboard**")
            
            # Show dashboard preview and navigation options
            st.subheader("📊 Dashboard Navigation")
            st.info("You're now authenticated! Choose your next step:")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Preview Dashboard", type="secondary"):
                    st.session_state.show_preview = True
                    st.rerun()
            
            with col2:
                if st.button("🚀 Go Directly to Scraping", type="primary"):
                    st.session_state.show_preview = False
                    st.rerun()
            
            if st.button("Logout"):
                st.session_state.is_authenticated = False
                st.session_state.scraper.is_authenticated = False
                st.rerun()
    
    # Main content area
    if st.session_state.is_authenticated:
        if st.session_state.show_preview:
            st.header("🔍 Dashboard Preview")
            st.info("Showing preview of dashboard content. Click 'Start Scraping' when ready to proceed.")
            
            # Get dashboard preview
            preview_data = st.session_state.scraper.get_dashboard_preview()
            if preview_data:
                st.markdown(f"""
                <div class="dashboard-preview">
                    <h3>📊 {preview_data['title']}</h3>
                    <p><strong>URL:</strong> {preview_data['url']}</p>
                    <p><strong>Tables Found:</strong> {preview_data['table_count']}</p>
                    <p><strong>Content Preview:</strong></p>
                    <div style="background-color: white; padding: 10px; border-radius: 5px; border: 1px solid #ddd;">
                        {preview_data['content_preview']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("🕷️ Start Scraping", type="primary"):
                st.session_state.show_preview = False
                st.rerun()
        
        else:
            st.success("✅ Authenticated and ready to scrape!")
            
            # Try multiple URLs button
            if st.button("🔍 Explore All Dashboard URLs", type="secondary"):
                with st.spinner("Exploring different dashboard URLs..."):
                    results = st.session_state.scraper.try_multiple_urls()
                    
                    st.subheader("🌐 Dashboard URL Analysis")
                    st.info("Here's what we found across different dashboard URLs:")
                    
                    for result in results:
                        if result['status'] == 200:
                            st.markdown(f"""
                            <div class="alternative-urls">
                                <h4>🔗 {result['url']}</h4>
                                <p><strong>Content Length:</strong> {result['content_length']} characters</p>
                                <p><strong>Tables:</strong> {result['table_count']}</p>
                                <p><strong>Claims Indicators:</strong> {result['claims_indicators']}</p>
                                <p><strong>Preview:</strong> {result['preview']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning(f"❌ {result['url']}: {result.get('error', 'Failed')}")
            
            # Try API endpoints button
            if st.button("🔌 Try API Endpoints", type="secondary"):
                with st.spinner("Exploring API endpoints..."):
                    api_results = st.session_state.scraper.try_api_endpoints()
                    
                    st.subheader("🔌 API Endpoint Analysis")
                    st.info("Here's what we found in the API endpoints:")
                    
                    for result in api_results:
                        if result['status'] == 200:
                            st.markdown(f"""
                            <div class="alternative-urls">
                                <h4>🔌 {result['endpoint']}</h4>
                                <p><strong>Data Type:</strong> {result['data_type']}</p>
                                <p><strong>Content Length:</strong> {result['content_length']} characters</p>
                                <p><strong>Preview:</strong> {result['preview']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning(f"❌ {result['endpoint']}: {result['preview']}")
            
            # Scrape button
            if st.button("🕷️ Scrape Dashboard", type="primary"):
                with st.spinner("Scraping dashboard..."):
                    dashboard_data = st.session_state.scraper.scrape_dashboard(dashboard_url)
                    
                    if dashboard_data:
                        st.session_state.dashboard_data = dashboard_data
                        st.success("Dashboard scraped successfully!")
                        
                        # Show scraping summary
                        if 'content_sections' in dashboard_data:
                            st.info(f"📊 Scraping Summary: {dashboard_data['content_sections']} content sections, {dashboard_data['iframes_found']} iframes, {dashboard_data['scripts_found']} scripts")
                        
                        # Display raw content
                        with st.expander("📋 Raw Dashboard Content"):
                            st.text(dashboard_data['content'][:2000] + "..." if len(dashboard_data['content']) > 2000 else dashboard_data['content'])
                        
                        # Display tables if found
                        if dashboard_data['tables']:
                            st.subheader("📊 Tables Found")
                            for i, table in enumerate(dashboard_data['tables']):
                                with st.expander(f"Table {i+1}"):
                                    df = pd.DataFrame(table[1:], columns=table[0])
                                    st.dataframe(df)
                        
                        # If limited content, suggest alternatives
                        if dashboard_data.get('content_sections', 0) <= 1:
                            st.warning("⚠️ Limited content found. The dashboard might:")
                            st.markdown("""
                            - **Use JavaScript** to load content dynamically
                            - **Have embedded iframes** with the actual data
                            - **Require specific user actions** to display content
                            - **Use a different URL structure**
                            
                            **Try these alternatives:**
                            """)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("🔄 Try Dashboard/7"):
                                    st.session_state.alternative_url = "https://app.waas.sdsaz.us/dashboard/7"
                                    st.rerun()
                            
                            with col2:
                                if st.button("🔄 Try Cases/Workflow"):
                                    st.session_state.alternative_url = "https://app.waas.sdsaz.us/cases/workflow/2"
                                    st.rerun()
            
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
        2. **Shows dashboard preview** after authentication
        3. **Scrapes** the workflow/cases dashboard content
        4. **Uses AI** to analyze and organize the content
        5. **Highlights** claims that can move forward
        6. **Creates** a structured worksheet for easy review
        
        ### Getting Started:
        1. Enter your OpenAI API key in the sidebar
        2. Click "Open WaaS Dashboard" to authenticate
        3. Log in on the WaaS site
        4. Return and click "Check Login Status"
        5. Preview dashboard content
        6. Start scraping and analyzing!
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
