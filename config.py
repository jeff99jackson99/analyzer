import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration settings
class Config:
    # OpenAI API Key
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Dashboard URLs
    DASHBOARD_BASE_URL = "https://app.waas.sdsaz.us"
    DASHBOARD_URL = "https://app.waas.sdsaz.us/cases/workflow/2"
    LOGIN_URL = "https://app.waas.sdsaz.us/auth/login?returnUrl=%2Fcases%2Fworkflow%2F2"
    
    # Selenium settings
    CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH')
    HEADLESS_MODE = True
    
    # AI Model settings
    AI_MODEL = "gpt-3.5-turbo"
    AI_TEMPERATURE = 0.3
    AI_MAX_TOKENS = 2000
    
    # Session settings
    SESSION_TIMEOUT = 3600  # 1 hour
    REMEMBER_CREDENTIALS = True
