import streamlit as st
import requests
import json
import schedule
import time
from datetime import datetime, timedelta
from dateutil import parser
import pandas as pd
from twilio.rest import Client
import os
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Teams Calendar Manager",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for priority styling
st.markdown("""
<style>
    .priority-high {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    
    .priority-medium {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    
    .priority-low {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    
    .meeting-card {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .countdown {
        font-size: 1.2em;
        font-weight: bold;
        color: #f44336;
    }
</style>
""", unsafe_allow_html=True)

class TeamsCalendarManager:
    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.tenant_id = os.getenv('TENANT_ID')
        self.access_token = None
        
        # Twilio setup
        self.twilio_client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        self.user_phone = os.getenv('USER_PHONE_NUMBER')
        
        # Meeting notifications tracking
        self.sent_notifications = set()
        
    def get_access_token(self):
        """Get Microsoft Graph API access token"""
        try:
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'https://graph.microsoft.com/.default',
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                return True
            else:
                st.error(f"Failed to get access token: {response.status_code}")
                return False
                
        except Exception as e:
            st.error(f"Error getting access token: {e}")
            return False
    
    def get_calendar_events(self):
        """Fetch calendar events from Microsoft Graph API"""
        if not self.access_token:
            if not self.get_access_token():
                return []
        
        try:
            # Get events for next 24 hours
            now = datetime.now()
            end_time = now + timedelta(days=1)
            
            url = "https://graph.microsoft.com/v1.0/me/calendarView"
            params = {
                'startDateTime': now.isoformat() + 'Z',
                'endDateTime': end_time.isoformat() + 'Z',
                '$orderby': 'start/dateTime'
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                events = response.json().get('value', [])
                return self.process_events(events)
            else:
                st.error(f"Failed to fetch calendar events: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Error fetching calendar events: {e}")
            return []
    
    def process_events(self, events):
        """Process and prioritize calendar events"""
        processed_events = []
        
        for event in events:
            start_time = parser.parse(event['start']['dateTime'])
            end_time = parser.parse(event['end']['dateTime'])
            
            # Calculate time until meeting
            time_until = start_time - datetime.now()
            minutes_until = int(time_until.total_seconds() / 60)
            
            # Determine priority
            if minutes_until <= 30:
                priority = 'high'
            elif minutes_until <= 120:
                priority = 'medium'
            else:
                priority = 'low'
            
            # Check if we should send SMS notification
            if 0 <= minutes_until <= 5 and event['id'] not in self.sent_notifications:
                self.send_sms_notification(event, minutes_until)
                self.sent_notifications.add(event['id'])
            
            processed_events.append({
                'id': event['id'],
                'subject': event.get('subject', 'No Subject'),
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time,
                'minutes_until': minutes_until,
                'priority': priority,
                'location': event.get('location', {}).get('displayName', 'No Location'),
                'attendees': len(event.get('attendees', [])),
                'is_online': event.get('isOnlineMeeting', False)
            })
        
        # Sort by priority and time
        processed_events.sort(key=lambda x: (x['priority'] == 'high', x['minutes_until']))
        return processed_events
    
    def send_sms_notification(self, event, minutes_until):
        """Send SMS notification about upcoming meeting"""
        try:
            subject = event.get('subject', 'Meeting')
            start_time = parser.parse(event['start']['dateTime'])
            
            message_body = f"�� Meeting Reminder: {subject} starts in {minutes_until} minutes at {start_time.strftime('%I:%M %p')}"
            
            self.twilio_client.messages.create(
                body=message_body,
                from_=self.twilio_phone,
                to=self.user_phone
            )
            
            st.success(f"📱 SMS notification sent for: {subject}")
            
        except Exception as e:
            st.error(f"Failed to send SMS: {e}")
    
    def display_events(self, events):
        """Display calendar events with priority styling"""
        if not events:
            st.info("📅 No upcoming meetings found")
            return
        
        # High priority meetings (next 30 minutes)
        high_priority = [e for e in events if e['priority'] == 'high']
        if high_priority:
            st.subheader("🔴 High Priority - Next 30 Minutes")
            for event in high_priority:
                self.display_event_card(event, 'high')
        
        # Medium priority meetings (next 2 hours)
        medium_priority = [e for e in events if e['priority'] == 'medium']
        if medium_priority:
            st.subheader("🟠 Medium Priority - Next 2 Hours")
            for event in medium_priority:
                self.display_event_card(event, 'medium')
        
        # Low priority meetings (rest of day)
        low_priority = [e for e in events if e['priority'] == 'low']
        if low_priority:
            st.subheader("🟢 Low Priority - Rest of Day")
            for event in low_priority:
                self.display_event_card(event, 'low')
    
    def display_event_card(self, event, priority):
        """Display individual event card"""
        priority_class = f"priority-{priority}"
        
        # Calculate countdown
        if event['minutes_until'] > 0:
            countdown_text = f"⏰ Starts in {event['minutes_until']} minutes"
        else:
            countdown_text = f"🔄 In progress (ends in {abs(event['minutes_until'])} minutes)"
        
        st.markdown(f"""
        <div class="meeting-card {priority_class}">
            <h4>📅 {event['subject']}</h4>
            <p><strong>Time:</strong> {event['start_time'].strftime('%I:%M %p')} - {event['end_time'].strftime('%I:%M %p')}</p>
            <p><strong>Duration:</strong> {event['duration']}</p>
            <p><strong>Location:</strong> {event['location']}</p>
            <p><strong>Attendees:</strong> {event['attendees']}</p>
            <p><strong>Online Meeting:</strong> {'✅ Yes' if event['is_online'] else '❌ No'}</p>
            <p class="countdown">{countdown_text}</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    st.title("📅 Teams Calendar Manager")
    st.markdown("**Smart calendar management with SMS notifications**")
    
    # Initialize calendar manager
    if 'calendar_manager' not in st.session_state:
        st.session_state.calendar_manager = TeamsCalendarManager()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check if environment variables are set
        if not os.getenv('CLIENT_ID'):
            st.error("❌ CLIENT_ID not set")
        if not os.getenv('CLIENT_SECRET'):
            st.error("❌ CLIENT_SECRET not set")
        if not os.getenv('TENANT_ID'):
            st.error("❌ TENANT_ID not set")
        if not os.getenv('TWILIO_ACCOUNT_SID'):
            st.error("❌ TWILIO_ACCOUNT_SID not set")
        if not os.getenv('TWILIO_AUTH_TOKEN'):
            st.error("❌ TWILIO_AUTH_TOKEN not set")
        if not os.getenv('TWILIO_PHONE_NUMBER'):
            st.error("❌ TWILIO_PHONE_NUMBER not set")
        
        # Refresh button
        if st.button("🔄 Refresh Calendar", type="primary"):
            st.rerun()
        
        # Manual SMS test
        if st.button("📱 Test SMS"):
            try:
                st.session_state.calendar_manager.twilio_client.messages.create(
                    body="🧪 Test SMS from Teams Calendar Manager",
                    from_=st.session_state.calendar_manager.twilio_phone,
                    to=st.session_state.calendar_manager.user_phone
                )
                st.success("✅ Test SMS sent!")
            except Exception as e:
                st.error(f"❌ Test SMS failed: {e}")
    
    # Main content
    if all([os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'), os.getenv('TENANT_ID')]):
        # Get and display calendar events
        with st.spinner("📅 Fetching your Teams calendar..."):
            events = st.session_state.calendar_manager.get_calendar_events()
            st.session_state.calendar_manager.display_events(events)
        
        # Auto-refresh every 30 seconds
        st.info("🔄 Calendar auto-refreshes every 30 seconds")
        
    else:
        st.error("""
        ❌ **Configuration Required**
        
        Please set the following environment variables in your `.env` file:
        
        - `CLIENT_ID` - Azure App Registration Client ID
        - `CLIENT_SECRET` - Azure App Registration Client Secret  
        - `TENANT_ID` - Azure Tenant ID
        - `TWILIO_ACCOUNT_SID` - Twilio Account SID
        - `TWILIO_AUTH_TOKEN` - Twilio Auth Token
        - `TWILIO_PHONE_NUMBER` - Twilio Phone Number
        
        See the README.md for setup instructions.
        """)
        
        st.info("""
        📚 **Setup Guide:**
        
        1. **Azure App Registration**: Create an app in Azure AD with Graph API permissions
        2. **Twilio Account**: Sign up for Twilio and get your credentials
        3. **Environment Variables**: Copy `.env.example` to `.env` and fill in your values
        4. **Run App**: Execute `streamlit run app.py`
        """)

if __name__ == "__main__":
    main()
