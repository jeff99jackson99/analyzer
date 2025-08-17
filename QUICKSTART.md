# 🚀 Quick Start Guide

Get your Dashboard Claims Analyzer running in 5 minutes!

## ⚡ Super Quick Start

1. **Install dependencies:**
   ```bash
   python setup.py
   ```

2. **Configure your API key:**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the app:**
   ```bash
   python run.py
   ```

4. **Open your browser** to `http://localhost:8501`

## 🔧 Manual Setup (if needed)

### Prerequisites
- Python 3.8+
- Chrome browser
- OpenAI API key

### Step-by-step

1. **Install Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install ChromeDriver:**
   ```bash
   # macOS
   brew install chromedriver
   
   # Windows/Linux
   # Download from: https://chromedriver.chromium.org/
   ```

3. **Create environment file:**
   ```bash
   cp env.example .env
   ```

4. **Edit .env file:**
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

5. **Test setup:**
   ```bash
   python test_setup.py
   ```

6. **Launch app:**
   ```bash
   streamlit run app.py
   ```

## 🎯 First Time Usage

1. **Enter your OpenAI API key** in the sidebar
2. **Login** with your dashboard credentials
3. **Click "Scrape Dashboard"** to gather data
4. **Use "Analyze with AI"** to process the content
5. **Review highlighted claims** that can move forward

## 🆘 Troubleshooting

### Common Issues

**"ChromeDriver not found"**
```bash
brew install chromedriver  # macOS
```

**"OpenAI API key error"**
- Check your .env file has the correct API key
- Ensure you have credits in your OpenAI account

**"Login failed"**
- Verify your dashboard credentials
- Check if the dashboard URL is correct

**"Dependencies missing"**
```bash
python setup.py
```

## 📞 Need Help?

- Check the full [README.md](README.md)
- Run `python test_setup.py` to diagnose issues
- Ensure all files are in the same directory

---

**Happy analyzing! 🎉**
