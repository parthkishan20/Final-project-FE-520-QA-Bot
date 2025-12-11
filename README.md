# Financial QA Bot - Production Edition

**A production-ready financial analysis tool that reads CSV data and answers business questions using AI-powered natural language processing.**

---

## 🎯 Overview

The Financial QA Bot is an enterprise-grade application for analyzing financial spreadsheets and generating insights through natural language questions. It combines:

- **Data Analysis**: pandas-based CSV processing
- **Smart Retrieval**: Fuzzy matching for flexible queries  
- **AI Integration**: Optional GPT-4o-mini for sophisticated answers
- **Visualizations**: Professional charts for business reports
- **Production Features**: Logging, configuration management, batch processing

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
cd Final-project-FE-520

# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key (optional)
export OPENAI_API_KEY='sk-your-key-here'
```

### Run the Application

```bash
# Production analysis
python app.py

# Output: financial_analysis_report.json + charts in output/
```

---

## 📊 Business Use Cases

**Financial Analysis**
- Revenue trend analysis
- Profit margin tracking
- Expense monitoring
- Asset valuation

**Reporting**
- Automated Q&A reports
- Batch analysis processing
- Chart generation
- JSON export for integration

**Integration**
- Business intelligence dashboards
- Financial data pipelines
- Automated reporting systems

---

## 📁 Project Structure

```
Final-project-FE-520/
├── finqa_bot/                 # Core package
│   ├── __init__.py           # Package exports
│   ├── data_indexer.py       # CSV data loading
│   ├── retriever.py          # Smart data retrieval
│   ├── qa_chain.py           # Question answering
│   ├── visualizer.py         # Chart generation
│   ├── error_handler.py      # Error management
│   ├── config.py             # Configuration
│   └── logger.py             # Production logging
│
├── app.py                     # Production application
├── sample_data.csv            # Example financial data
├── output/                    # Generated reports & charts
│   ├── financial_analysis_report.json
│   └── charts/
│
├── README.md                  # This file
└── requirements.txt           # Dependencies
```

---

## 💻 API Usage

### As a Python Module

```python
from app import FinancialQABot
from finqa_bot.config import Config

# Initialize with custom config
config = Config(
    DATA_FILE="your_data.csv",
    USE_LLM=True,
    MODEL="gpt-4o-mini"
)

bot = FinancialQABot(config)
bot.load_data()

# Ask questions
result = bot.ask("What was revenue in 2023?")
print(result["answer"])

# Batch processing
questions = [
    "What was net income in 2021?",
    "What were operating expenses in 2020?"
]
report_file = bot.generate_report(questions)

# Generate charts
bot.export_chart("Revenue", chart_type="line")
```

### Command Line

```bash
# Production run with defaults
python app.py

# With custom configuration
DATA_FILE=my_data.csv OUTPUT_DIR=reports python app.py

# With LLM disabled (faster, free)
USE_LLM=false python app.py
```

---

## ⚙️ Configuration

Edit `finqa_bot/config.py` or set environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_LLM` | true | Enable AI-powered answers |
| `LLM_MODEL` | gpt-4o-mini | Model to use |
| `DATA_FILE` | sample_data.csv | Input CSV file |
| `OUTPUT_DIR` | output | Output directory |
| `LOG_LEVEL` | INFO | Logging level |

---

## 📊 Output Format

### Analysis Report (JSON)

```json
{
  "metadata": {
    "total_questions": 4,
    "successful": 4,
    "model": "gpt-4o-mini"
  },
  "results": [
    {
      "question": "What was revenue in 2023?",
      "answer": "The Revenue in 2023 was $1,650,000.",
      "status": "success"
    }
  ]
}
```

### Generated Artifacts

- `output/financial_analysis_report.json` - Complete analysis
- `output/charts/*.png` - Visualizations
- `output/finqa_bot.log` - Detailed logs

---

## 🔑 API Key Setup

### Get an OpenAI Key

1. Visit https://platform.openai.com/api-keys
2. Create a new secret key
3. Copy the key (starts with `sk-`)

### Set Environment Variable

**macOS/Linux:**
```bash
export OPENAI_API_KEY='sk-your-key-here'
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY='sk-your-key-here'
```

### Cost

- **GPT-4o-mini**: $0.15 per 1M input tokens, $0.60 per 1M output tokens
- **Cost per question**: ~$0.0001-0.0002 (very cheap)
- **Free tier**: $5 credit available

---

## 📈 Data Format

Your CSV should have:
- One **Year/Date** column
- One or more **financial metric** columns

**Example:**

```csv
Year,Revenue,Net_Income,Operating_Expenses,Total_Assets
2019,1000000,150000,300000,2000000
2020,1150000,172500,330000,2300000
2021,1380000,207000,360000,2650000
2022,1520000,228000,380000,2900000
2023,1650000,247500,400000,3100000
```

---

## 🧪 Testing

```bash
# Run production demo
python app.py

# View report
cat output/financial_analysis_report.json

# Check logs
cat output/finqa_bot.log

# View charts
open output/charts/revenue.png  # macOS
```

---

## 🛠️ Development

### Project Phases

- **Phase 0**: Environment setup
- **Phase 1**: Package structure
- **Phase 2**: DataIndexer (CSV loading)
- **Phase 3**: Retriever (data finding)
- **Phase 4**: QAChain (rule-based QA)
- **Phase 5**: LangChain integration (AI)
- **Phase 6**: Visualizations (charts)
- **Phase 7**: Error handling (robustness)
- **Phase 8**: Production deployment

### Key Technologies

- **pandas**: Data processing
- **LangChain**: LLM orchestration
- **OpenAI**: GPT-4o-mini model
- **matplotlib**: Visualizations
- **Python 3.10+**: Language

---

## 📝 Logging

Logs are written to `output/finqa_bot.log` and console:

```
2025-12-11 15:43:51 - __main__ - INFO - Financial QA Bot initialized
2025-12-11 15:43:51 - __main__ - INFO - Loading data from: sample_data.csv
2025-12-11 15:43:51 - __main__ - INFO - ✓ Data loaded: 5 rows
```

Change log level:

```bash
LOG_LEVEL=DEBUG python app.py
```

---

## 🐛 Troubleshooting

### API Key Not Found

```bash
export OPENAI_API_KEY='sk-your-key'
python app.py
```

### Data File Not Found

```bash
# Use absolute path
DATA_FILE=/path/to/data.csv python app.py
```

### LLM Disabled

The bot falls back to rule-based QA if:
- API key is not set
- USE_LLM=false
- LLM request fails

```bash
USE_LLM=false python app.py
```

---

## 📄 License

Educational project for FE-520.

---

## 📧 Support

- Check `output/finqa_bot.log` for issues
- Verify CSV format matches examples
- Ensure API key has sufficient credits

---

**Production-Ready Financial QA Bot** ✨
