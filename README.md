# Teams Calendar Manager

A Streamlit app that integrates with Microsoft Teams calendar, prioritizes meetings, and sends SMS notifications.

## Features
- 📅 Teams calendar integration via Microsoft Graph API
- 🔴 Priority sorting (upcoming meetings in red)
- 📱 SMS notifications 5 minutes before meetings
- ⚡ Real-time updates and auto-refresh
- 🎨 Beautiful priority-based UI styling

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Azure App Registration Setup
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Name: "Teams Calendar Manager"
5. Supported account types: "Accounts in this organizational directory only"
6. Redirect URI: Leave blank
7. Click "Register"

#### Configure API Permissions:
1. Go to "API permissions"
2. Click "Add a permission"
3. Select "Microsoft Graph" > "Application permissions"
4. Add these permissions:
   - `Calendars.Read` (to read calendar events)
   - `User.Read.All` (to access user calendars)
5. Click "Grant admin consent"

#### Get Credentials:
1. Copy the "Application (client) ID" → `CLIENT_ID`
2. Go to "Certificates & secrets"
3. Create new client secret → `CLIENT_SECRET`
4. Copy the "Directory (tenant) ID" → `TENANT_ID`

### 3. Twilio SMS Setup
1. Sign up at [Twilio](https://www.twilio.com)
2. Get your Account SID → `TWILIO_ACCOUNT_SID`
3. Get your Auth Token → `TWILIO_AUTH_TOKEN`
4. Get a phone number → `TWILIO_PHONE_NUMBER`

### 4. Environment Configuration
1. Copy `.env.example` to `.env`
2. Fill in your actual values:
```env
CLIENT_ID=your_actual_client_id
CLIENT_SECRET=your_actual_client_secret
TENANT_ID=your_actual_tenant_id
TWILIO_ACCOUNT_SID=your_actual_twilio_sid
TWILIO_AUTH_TOKEN=your_actual_twilio_token
TWILIO_PHONE_NUMBER=your_actual_twilio_phone
USER_PHONE_NUMBER=9285306286
```

### 5. Run the App
```bash
streamlit run app.py
```

## How It Works

1. **Calendar Integration**: Connects to Microsoft Graph API to fetch your Teams calendar
2. **Priority System**: 
   - 🔴 High: Next 30 minutes (red)
   - 🟠 Medium: Next 2 hours (orange)
   - 🟢 Low: Rest of day (green)
3. **SMS Notifications**: Automatically sends texts 5 minutes before meetings
4. **Real-time Updates**: Refreshes every 30 seconds

## Troubleshooting

- **"Failed to get access token"**: Check your Azure credentials
- **"Failed to fetch calendar events"**: Verify API permissions
- **"Test SMS failed"**: Check Twilio credentials
- **No meetings showing**: Ensure you have calendar events in the next 24 hours

## Security Notes

- Never commit your `.env` file to git
- Use environment variables for all sensitive data
- Regularly rotate your client secrets
- Monitor API usage and permissions

## Support

For issues with:
- **Azure/Graph API**: Check Azure AD app registration
- **Twilio**: Verify SMS credentials and phone numbers
- **Streamlit**: Ensure all dependencies are installed
