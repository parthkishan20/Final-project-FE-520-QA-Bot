# Financial QA Bot

A Python application for analyzing financial spreadsheets and answering questions in natural language with advanced visualization capabilities.

## Overview

The Financial QA Bot reads CSV financial data and generates insights through intelligent question answering. It combines data analysis with optional AI-powered responses to provide flexible, accurate financial reporting with 15 professional visualization types.

**Key Capabilities:**
- Load and analyze CSV financial datasets
- Ask questions about financial metrics in plain English
- Get intelligent answers with year-specific detection (best/worst year analysis)
- Generate 15 professional visualization types
- Export results as JSON reports
- External question management via questions.txt

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up OpenRouter API key (Mistral default) - Optional
export OPENROUTER_API_KEY='your-openrouter-key'
# Optional: choose a different OpenRouter model
export OPENROUTER_MODEL='mistralai/devstral-2512:free'
```

### Run the Application

```bash
# Create questions.txt file with your questions (one per line)
# Run the analysis
python app.py

# (Optional) Verify OpenRouter setup
python openrouter_test.py

# View results
cat output/financial_analysis_report.json
```

## Features

### Data Analysis
- CSV file loading with validation
- Fuzzy column matching for flexible queries
- Year/date filtering
- Data exploration tools
- Automatic metric calculation (Net Margin, ROA, etc.)

### Question Answering
- **Smart year detection**: Identifies "best/worst/highest/lowest" year questions
- Rule-based pattern matching (no API key needed)
- AI-powered responses using OpenRouter (default: mistralai/devstral-2512:free)
- Automatic fallback to rule-based mode
- Batch question processing from questions.txt file
- Trend analysis with percentage changes

### Visualizations (15 Types)
**Basic Charts:**
- Line charts for trends
- Bar charts for comparisons
- Multi-metric comparison charts
- Waterfall charts (P&L breakdown)
- Box plots (margin distribution)

**Advanced Visualizations:**
- Dual-axis charts (metrics vs percentages)
- Stacked area charts (composition over time)
- Year-over-year heatmaps (% change matrix)
- Scatter plots with regression (R² analysis)
- Financial ratios dashboard (4-panel display)
- Momentum analysis (moving averages)
- Rolling correlation charts
- Profitability funnel charts

### Output
- Structured JSON reports
- 15 high-resolution PNG visualizations (300 DPI)
- Detailed application logs with UTF-8 encoding
- Clean console output with [number][status] format

## Usage

### Command Line

```bash
# Basic usage (requires questions.txt file)
python app.py

# With custom data file
DATA_FILE=my_data.csv python app.py

# Without AI (rule-based only)
USE_LLM=false python app.py

# With custom configuration
OUTPUT_DIR=reports LOG_LEVEL=DEBUG python app.py
```

### Questions Management

Create a `questions.txt` file with your questions (required):
```text
# Financial Analysis Questions
What is the net profit margin for 2023?
In which years was the best time to own an asset?
What is the trend in operating expenses over the last 5 years?
Which year had the highest net income?
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
report, report_file = bot.generate_report(questions)

# Generate charts (15 types available)
bot.export_chart("Revenue", chart_type="line")
bot.visualizer.plot_dual_axis_chart("Revenue", "Net_Margin", output_file="dual_axis.png")
bot.visualizer.plot_financial_ratios_dashboard(output_file="dashboard.png")
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_LLM` | true | Enable AI-powered answers (OpenRouter) |
| `LLM_MODEL` | mistralai/devstral-2512:free | OpenRouter model to use |
| `OPENROUTER_API_KEY` | (none) | OpenRouter API key |
| `OPENROUTER_MODEL` | mistralai/devstral-2512:free | OpenRouter model name |
| `DATA_FILE` | sample_data.csv | Input CSV file |
| `OUTPUT_DIR` | output | Output directory |
| `LOG_LEVEL` | INFO | Logging level |

### Python Configuration

```python
from finqa_bot.config import Config

config = Config(
    DATA_FILE="your_data.csv",
    USE_LLM=True,
    MODEL="mistralai/devstral-2512:free",
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
- "In which years was the best/highest/maximum [metric]?" (returns specific year)
- "What is the trend in [metric]?" (returns percentage change and recent values)
- "Which year had the lowest/worst [metric]?" (returns specific year)

Recognized metrics: Revenue, Sales, Net Income, Profit, Expenses, Assets

### Smart Question Answering

The bot now intelligently detects question intent:

```text
Question: "In which years was the best time to own an asset?"
Answer: "The best year(s) for Total Assets was 2024 with $1,260,000."

Question: "What is the trend in operating expenses?"
Answer: "Operating Expenses increased by 1285.4% from $41,000 to $568,000.
         Recent values:
         2020: $435,000
         2021: $465,000
         2022: $510,000
         2023: $540,000
         2024: $568,000"
```

## Project Structure

```
├── app.py                         # Main application (optimized)
├── requirements.txt               # Dependencies
├── openrouter_test.py            # OpenRouter integration check (optional)
├── sample_data.csv               # Example data
├── questions.txt                 # Question list (required)
├── .env                          # API key (optional)
│
├── finqa_bot/                    # Core package
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── logger.py                 # Logging setup (UTF-8 encoding)
│   ├── data_indexer.py           # CSV data loading
│   ├── retriever.py              # Data retrieval with fuzzy matching
│   ├── qa_chain.py               # Question answering (enhanced with year detection)
│   ├── visualizer.py             # 15 chart types (optimized with helper methods)
│   └── error_handler.py          # Error management
│
├── README.md                     # This file
└── output/                       # Generated artifacts (auto-created)
    ├── financial_analysis_report.json
    ├── charts/                   # 15 visualizations
    └── finqa_bot.log
```

## Output Format

### Report (JSON)

```json
{
  "metadata": {
    "total_questions": 4,
    "successful": 4,
    "model": "mistralai/devstral-2512:free"
  },
  "results": [
    {
      "question": "What was revenue in 2023?",
      "answer": "The Revenue in 2023 was $19,370,714.",
      "status": "success"
    }
  ]
}
```

### Generated Files
- `output/financial_analysis_report.json` - Complete analysis results
- `output/charts/*.png` - 15 high-resolution visualizations (300 DPI)
- `output/finqa_bot.log` - Detailed logs

### Visualization Output Format
```text
[GENERATING VISUALIZATIONS]
--------------------------------------------------------------------------------
  [1][OK] Line chart: Revenue            -> output/charts/revenue.png
  [2][OK] Line chart: Net_Income         -> output/charts/net_income.png
  [3][OK] Line chart: Operating_Expenses -> output/charts/operating_expenses.png
  [4][OK] Bar chart: Total Assets        -> output/charts/total_assets_bar.png
  [5][OK] Comparison chart               -> output/charts/comparison.png
  [6][OK] Waterfall chart                -> output/charts/waterfall_2023.png
  [7][OK] Box plot: Margin               -> output/charts/margin_boxplot.png
  [8][OK] Momentum analysis              -> output/charts/momentum_revenue.png
  [9][OK] Rolling correlation            -> output/charts/correlation_revenue_assets.png
  [10][OK] Dual Axis: Revenue vs Margin   -> output/charts/dual_axis.png
  [11][OK] Stacked Area Chart             -> output/charts/stacked_area.png
  [12][OK] YoY Heatmap: Revenue           -> output/charts/yoy_heatmap.png
  [13][OK] Scatter: Revenue vs Assets     -> output/charts/scatter_regression.png
  [14][OK] Financial Ratios Dashboard     -> output/charts/ratios_dashboard.png
  [15][OK] Profitability Funnel           -> output/charts/funnel.png
```

## API Keys

### OpenRouter API Key (Mistral default)

1. Get a key from https://openrouter.ai/keys
2. Set the key and optionally choose a model

**macOS/Linux:**
```bash
export OPENROUTER_API_KEY='your-openrouter-key'
export OPENROUTER_MODEL='mistralai/devstral-2512:free'
```

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY='your-openrouter-key'
$env:OPENROUTER_MODEL='mistralai/devstral-2512:free'
```

### Cost

- **Default model**: mistralai/devstral-2512:free (no credit card required)
- Check https://openrouter.ai/models for other options and pricing

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
Creates 15 types of charts and graphs.
```python
viz = Visualizer(indexer.data)

# Basic charts
viz.plot_metric_over_time('Revenue', output_file='revenue.png')
viz.plot_comparison(['Revenue', 'Net_Income'], output_file='comparison.png')
viz.plot_bar_chart('Total_Assets', output_file='assets.png')

# Advanced visualizations
viz.plot_dual_axis_chart('Revenue', 'Net_Margin', output_file='dual_axis.png')
viz.plot_financial_ratios_dashboard(output_file='dashboard.png')
viz.plot_yoy_heatmap('Revenue', output_file='heatmap.png')
viz.plot_scatter_regression('Total_Assets', 'Revenue', output_file='regression.png')
viz.plot_profitability_funnel(target_year=2023, output_file='funnel.png')
viz.plot_area_stacked(['Revenue', 'Operating_Expenses'], output_file='stacked.png')
viz.plot_momentum('Revenue', window_short=2, window_long=3, output_file='momentum.png')
viz.plot_rolling_correlation('Revenue', 'Total_Assets', window=3, output_file='corr.png')
viz.plot_waterfall(target_year=2023, output_file='waterfall.png')
viz.plot_margin_boxplot(output_file='boxplot.png')
```

## Troubleshooting

### Questions File Missing
```bash
# Create questions.txt with your questions (one per line)
echo "What was revenue in 2023?" > questions.txt
echo "In which years was the best time to own an asset?" >> questions.txt
python app.py
```

### API Key Not Found
```bash
export OPENROUTER_API_KEY='your-openrouter-key'
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

### Unicode/Encoding Errors
All files now use UTF-8 encoding to prevent Windows cp1252 errors. Output uses ASCII-safe tags: `[OK]`, `[!]`

## Performance

- **Data loading**: ~100ms
- **Per question**: ~200-500ms (rule-based), ~1-2s (LLM)
- **Chart generation**: ~500ms per chart (15 charts total ~7.5s)
- **Memory usage**: ~80MB
- **Disk usage**: ~5MB for output (15 high-res charts)

## Technology Stack

- **Python 3.10+**
- **pandas 2.3.3** - Data processing & statistical analysis
- **numpy 2.3.5** - Numerical computing, linear regression
- **matplotlib 3.10.8** - 15 visualization types, 300 DPI exports
- **requests 2.32.3** - HTTP client for OpenRouter
- **python-dotenv 1.0.0** - Environment variables



## Examples

### Basic Analysis
```bash
# Ensure questions.txt exists
python app.py
```

### Custom Questions
Create or edit `questions.txt`:
```text
# Profitability Analysis
What is the net profit margin for 2023?
Calculate the return on assets (ROA) for 2022

# Year-Specific Queries
In which years was the best time to own an asset?
Which year had the highest net income between 2019 and 2023?

# Trend Analysis
What is the trend in operating expenses over the last 5 years?
How has the profit margin changed from 2019 to 2023?
```

### Programmatic Usage
```python
from app import FinancialQABot

bot = FinancialQABot()
bot.load_data("my_data.csv")

# Smart year detection
answer = bot.ask("In which years was the best time to own an asset?")
print(answer)  # Returns: "The best year(s) for Total Assets was 2024 with $1,260,000."

# Trend analysis
answer = bot.ask("What is the trend in revenue?")
print(answer)  # Returns percentage change and recent 5 years

# Generate all 15 visualizations
from finqa_bot import Visualizer
viz = Visualizer(bot.indexer.data)
viz.plot_financial_ratios_dashboard(output_file="dashboard.png")
```

## License

MIT License. Educational project for FE-520.

## Support

- Check `output/finqa_bot.log` for detailed logs
- Ensure CSV format matches examples above
