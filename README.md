# Dashboard Claims Analyzer

A Streamlit application that scrapes dashboard content, uses AI to organize it into structured worksheets, and highlights claims that can move forward.

## Features

- 🔐 **Secure Authentication** - Login to protected dashboards
- 🕷️ **Web Scraping** - Automatically extract dashboard content
- 🤖 **AI Analysis** - Uses OpenAI to organize and analyze claims data
- 📊 **Smart Highlighting** - Identifies claims ready to move forward
- 📤 **Export Options** - Export results to Excel/PDF
- 🔑 **Persistent Login** - Remember credentials between sessions

## Setup

### Prerequisites

1. **Python 3.8+** installed
2. **Chrome browser** installed
3. **OpenAI API key** for AI analysis

### Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd dashboard-claims-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

4. Install Chrome WebDriver:
```bash
# On macOS with Homebrew:
brew install chromedriver

# Or download from: https://chromedriver.chromium.org/
```

### Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Open your browser to `http://localhost:8501`

3. Configure the app:
   - Enter your OpenAI API key
   - Login with dashboard credentials
   - Set the dashboard URL

4. Start scraping and analyzing!

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
CHROME_DRIVER_PATH=/path/to/chromedriver
```

### Dashboard URLs

Update the dashboard URL in `config.py` or use the sidebar input field.

## Security Notes

- Credentials are stored locally and encrypted
- API keys are stored in environment variables
- No sensitive data is logged or transmitted

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**: Install ChromeDriver and update the path
2. **Login failures**: Check credentials and dashboard URL
3. **Scraping errors**: Ensure the dashboard is accessible and login is successful

### Support

For issues or questions, please check the logs or contact support.

## License

This project is licensed under the MIT License.
