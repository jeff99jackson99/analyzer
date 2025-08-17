# 🚀 Deployment Guide

## GitHub Setup

1. **Create a new repository on GitHub:**
   - Go to [github.com](https://github.com)
   - Click "New repository"
   - Name it: `dashboard-claims-analyzer`
   - Make it public or private (your choice)
   - Don't initialize with README (we already have one)

2. **Add the remote origin:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/dashboard-claims-analyzer.git
   git branch -M main
   git push -u origin main
   ```

## Streamlit Cloud Deployment

### Option 1: Deploy from GitHub (Recommended)

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Fill in the details:**
   - **Repository**: `YOUR_USERNAME/dashboard-claims-analyzer`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Leave blank (auto-generated)
5. **Click "Deploy!"**

### Option 2: Deploy from Local Files

1. **Install Streamlit:**
   ```bash
   pip install streamlit
   ```

2. **Run locally first:**
   ```bash
   streamlit run app.py
   ```

3. **Deploy to Streamlit Cloud:**
   ```bash
   streamlit deploy
   ```

## Environment Variables Setup

### For Streamlit Cloud:

1. **Go to your app settings**
2. **Click "Secrets"**
3. **Add your environment variables:**
   ```toml
   OPENAI_API_KEY = "sk-your-actual-api-key-here"
   DASHBOARD_BASE_URL = "https://app.waas.sdsaz.us"
   DASHBOARD_URL = "https://app.waas.sdsaz.us/dashboard/7"
   ```

### For Local Development:

1. **Copy the example file:**
   ```bash
   cp env.example .env
   ```

2. **Edit .env with your actual values:**
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   DASHBOARD_BASE_URL=https://app.waas.sdsaz.us
   DASHBOARD_URL=https://app.waas.sdsaz.us/dashboard/7
   ```

## Post-Deployment

1. **Test your app** at the provided Streamlit Cloud URL
2. **Configure your OpenAI API key** in the app
3. **Test the dashboard scraping** with your credentials
4. **Monitor the app logs** in Streamlit Cloud dashboard

## Troubleshooting

### Common Issues:

**"ChromeDriver not found"**
- The app now uses webdriver-manager for automatic driver management
- This should work automatically on Streamlit Cloud

**"Login failed"**
- Check your dashboard credentials
- Verify the dashboard URL is accessible

**"OpenAI API error"**
- Ensure your API key is correct
- Check you have credits in your OpenAI account

### Streamlit Cloud Specific:

**"Build failed"**
- Check the build logs in Streamlit Cloud
- Ensure all dependencies are in requirements.txt
- Verify the main file path is correct

**"Runtime error"**
- Check the app logs in Streamlit Cloud
- Ensure environment variables are set correctly

## Security Notes

- **Never commit** your .env file or actual API keys
- **Use Streamlit Cloud secrets** for production deployment
- **Keep your repository private** if dealing with sensitive data
- **Monitor app usage** and API costs

## Cost Considerations

- **Streamlit Cloud**: Free tier available
- **OpenAI API**: Pay-per-use, monitor your usage
- **ChromeDriver**: Free, managed automatically

---

**Happy deploying! 🎉**
