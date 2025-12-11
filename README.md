# Financial QA Bot

A Python application for analyzing financial spreadsheets and answering questions in natural language.

## Overview

The Financial QA Bot reads CSV financial data and generates insights through intelligent question answering. It combines data analysis with optional AI-powered responses to provide flexible, accurate financial reporting.

**Key Capabilities:**
- Load and analyze CSV financial datasets
- Ask questions about financial metrics in plain English
- Get answers through rule-based or AI-powered modes
- Generate professional visualizations
- Export results as JSON reports

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up Google AI Studio API key (optional for AI-powered answers)
export GOOGLE_API_KEY='your-key-here'
```

### Run the Application

```bash
# Run the analysis
python app.py

# View results
cat output/financial_analysis_report.json
```

## Features

### Data Analysis
- CSV file loading with validation
- Fuzzy column matching for flexible queries
- Year/date filtering
- Data exploration tools

### Question Answering
- Rule-based pattern matching (no API key needed)
- Optional AI-powered responses using Google Gemini 1.5 Flash
- Automatic fallback to rule-based mode
- Batch question processing

### Visualizations
- Line charts for trends
- Bar charts for comparisons
- Multi-metric comparison charts
- Professional formatting with currency display

### Output
- Structured JSON reports
- PNG visualizations
- Detailed application logs
- Clean console output

## Usage

### Command Line

```bash
# Basic usage
python app.py

# With custom data file
DATA_FILE=my_data.csv python app.py

# Without AI (rule-based only)
USE_LLM=false python app.py

# With custom configuration
OUTPUT_DIR=reports LOG_LEVEL=DEBUG python app.py
```

### As a Python Module

```python
from app import FinancialQABot
from finqa_bot.config import Config

# Initialize
config = Config(DATA_FILE="data.csv", USE_LLM=True)
bot = FinancialQABot(config)
bot.load_data()

# Ask questions
result = bot.ask("What was revenue in 2023?")
print(result["answer"])

# Batch processing
questions = ["What was net income in 2021?", "What were expenses in 2020?"]
report_file = bot.generate_report(questions)

# Generate charts
bot.export_chart("Revenue", chart_type="line")
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_LLM` | true | Enable AI-powered answers |
| `LLM_MODEL` | models/gemini-2.0-flash | Model to use (Gemini 2.0 Flash recommended) |
| `GOOGLE_API_KEY` | (none) | Google AI Studio API key |
| `DATA_FILE` | sample_data.csv | Input CSV file |
| `OUTPUT_DIR` | output | Output directory |
| `LOG_LEVEL` | INFO | Logging level |

### Python Configuration

```python
from finqa_bot.config import Config

config = Config(
    DATA_FILE="your_data.csv",
    USE_LLM=True,
    MODEL="gpt-4o-mini",
    OUTPUT_DIR="reports",
    LOG_LEVEL="INFO"
)
```

## Data Format

Your CSV should contain a Year/Date column and financial metric columns:

```csv
Year,Revenue,Net_Income,Operating_Expenses,Total_Assets
2019,1000000,150000,300000,2000000
2020,1150000,172500,330000,2300000
2021,1380000,207000,360000,2650000
2022,1520000,228000,380000,2900000
2023,1650000,247500,400000,3100000
```

Supported question patterns:
- "What was [metric] in [year]?"
- "What is the [metric]?"
- "How much was [metric] in [year]?"

Recognized metrics: Revenue, Sales, Net Income, Profit, Expenses, Assets

## Project Structure

```
├── app.py                         # Main application
├── requirements.txt               # Dependencies
├── sample_data.csv               # Example data
├── .env                          # API key (optional)
│
├── finqa_bot/                    # Core package
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── logger.py                 # Logging setup
│   ├── data_indexer.py           # CSV data loading
│   ├── retriever.py              # Data retrieval
│   ├── qa_chain.py               # Question answering
│   ├── visualizer.py             # Chart generation
│   └── error_handler.py          # Error management
│
├── README.md                     # This file
└── output/                       # Generated artifacts (auto-created)
    ├── financial_analysis_report.json
    ├── charts/
    └── finqa_bot.log
```

## Output Format

### Report (JSON)

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

### Generated Files
- `output/financial_analysis_report.json` - Complete analysis results
- `output/charts/*.png` - Visualizations
- `output/finqa_bot.log` - Detailed logs

## API Keys

### Getting a Google AI Studio Key

1. Visit https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)

### Setting the Key

**macOS/Linux:**
```bash
export GOOGLE_API_KEY='your-key-here'
```

**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY='your-key-here'
```

### Cost

- **Model**: Gemini 1.5 Flash
- **FREE**: Generous free tier (60 requests per minute)
- **Input**: Free up to 1M tokens/min
- **Output**: Free up to 1M tokens/min
- **No credit card required**

## Core Modules

### DataIndexer
Loads and manages CSV data.
```python
indexer = DataIndexer('data.csv')
columns = indexer.get_columns()
data = indexer.head(5)
```

### Retriever
Finds specific values with intelligent matching.
```python
retriever = Retriever(indexer)
column = retriever.find_column('revenue')      # Fuzzy match
value = retriever.get_value('Revenue', year=2023)
```

### QAChain
Generates answers to questions.
```python
qa = QAChain(retriever, use_llm=True)
answer = qa.generate_answer("What was revenue in 2023?")
```

### Visualizer
Creates charts and graphs.
```python
viz = Visualizer(indexer.data)
viz.plot_metric_over_time('Revenue', output_file='chart.png')
viz.plot_comparison(['Revenue', 'Net_Income'])
```

## Troubleshooting

### API Key Not Found
```bash
export OPENAI_API_KEY='sk-your-key'
python app.py
```

### Data File Not Found
```bash
DATA_FILE=/full/path/to/data.csv python app.py
```

### Dependencies Missing
```bash
pip install -r requirements.txt
```

### LLM Unavailable
The bot automatically falls back to rule-based mode if:
- API key is not set
- LLM request fails
- `USE_LLM=false` is set

## Performance

- **Data loading**: ~100ms
- **Per question**: ~200-500ms
- **Chart generation**: ~500ms per chart
- **Memory usage**: ~50MB
- **Disk usage**: ~1MB for output

## Technology Stack

- **Python 3.10+**
- **pandas 2.3.3** - Data processing
- **numpy 2.3.5** - Numerical computing
- **matplotlib 3.10.8** - Visualizations
- **LangChain 0.3.15** - LLM framework
- **Google Generative AI 0.8.3** - Gemini 1.5 Flash API
- **python-dotenv 1.0.0** - Environment variables



## Examples

### Basic Analysis
```bash
python app.py
```

### Custom Questions
Edit the questions list in `app.py` (lines 170-175):
```python
business_questions = [
    "What was revenue in 2023?",
    "How did profit change from 2019 to 2023?"
]
```

### Programmatic Usage
```python
from app import FinancialQABot

bot = FinancialQABot()
bot.load_data("my_data.csv")
answer = bot.ask("What was net income in 2021?")
print(answer)
```

## License

Educational project for FE-520.

## Support

- Check `output/finqa_bot.log` for detailed logs
- Ensure CSV format matches examples above
