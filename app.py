#!/usr/bin/env python3
"""
Financial QA Bot - Application
==========================================

A business-ready financial analysis tool that reads CSV data and answers questions.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from finqa_bot import DataIndexer, Retriever, QAChain, Visualizer
from finqa_bot.config import Config
from finqa_bot.logger import setup_logger


class FinancialQABot:
    """Financial QA Bot."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the bot with configuration."""
        self.config = config or Config.from_env()
        self.logger = setup_logger(
            __name__, 
            log_file=self.config.LOG_FILE,
            level=getattr(logging, self.config.LOG_LEVEL)
        )
        
        self.indexer = None
        self.retriever = None
        self.qa_chain = None
        self.visualizer = None
        
        self._prepare_directories()
        self.logger.info("Financial QA Bot initialized")
    
    def _prepare_directories(self):
        """Create necessary output directories."""
        for directory in [self.config.OUTPUT_DIR, self.config.CHART_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def load_data(self, file_path: Optional[str] = None) -> bool:
        """Load financial data from CSV file."""
        file_path = file_path or self.config.DATA_FILE
        
        try:
            self.logger.info(f"Loading data from: {file_path}")
            self.indexer = DataIndexer(file_path)
            self.retriever = Retriever(self.indexer)
            self.qa_chain = QAChain(
                self.retriever,
                openrouter_api_key=self.config.OPENROUTER_API_KEY,
                openrouter_model=self.config.MODEL,
                use_llm=self.config.USE_LLM,
            )
            self.visualizer = Visualizer(self.indexer.data)
            
            if self.indexer.data is not None:
                self.logger.info(f"[SUCCESS] Data loaded: {len(self.indexer.data)} rows")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load data: {e}")
            return False
    
    def ask(self, question: str) -> Dict:
        """Ask a question and get an answer."""
        if not self.qa_chain:
            return {"error": "Data not loaded. Call load_data() first."}
        
        try:
            self.logger.debug(f"Processing question: {question}")
            answer = self.qa_chain.generate_answer(question)
            
            result = {
                "question": question,
                "answer": answer,
                "status": "success"
            }
            
            self.logger.info(f"Question answered successfully")
            return result
        
        except Exception as e:
            self.logger.error(f"Error answering question: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    def ask_batch(self, questions: List[str]) -> List[Dict]:
        """Process multiple questions."""
        self.logger.info(f"Processing batch of {len(questions)} questions")
        
        results = []
        for i, question in enumerate(questions, 1):
            result = self.ask(question)
            results.append(result)
            self.logger.debug(f"Completed question {i}/{len(questions)}")
        
        return results
    
    def generate_report(self, questions: List[str], output_file: Optional[str] = None) -> Tuple[Dict, str]:
        """Generate a business report with answers and return (report, file_path)."""
        output_file = output_file or f"{self.config.OUTPUT_DIR}/report.json"
        
        self.logger.info(f"Generating report: {output_file}")
        
        results = self.ask_batch(questions)
        
        report = {
            "metadata": {
                "total_questions": len(questions),
                "successful": sum(1 for r in results if r.get("status") == "success"),
                "model": self.config.MODEL if self.config.USE_LLM else "rule-based"
            },
            "results": results
        }
        
        # Save report
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"[SUCCESS] Report saved: {output_file}")
        return report, output_file
    
    def export_chart(self, metric: str, chart_type: str = "line") -> Optional[str]:
        """Export a metric visualization."""
        if not self.visualizer:
            self.logger.error("Visualizer not initialized")
            return None
        
        try:
            output_file = f"{self.config.CHART_DIR}/{metric.lower()}.png"
            
            self.logger.info(f"Creating {chart_type} chart for {metric}")
            
            if chart_type == "line":
                self.visualizer.plot_metric_over_time(
                    metric,
                    output_file=output_file,
                    show=False
                )
            elif chart_type == "bar":
                self.visualizer.plot_bar_chart(
                    metric,
                    output_file=output_file,
                    show=False
                )
            
            self.logger.info(f"[SUCCESS] Chart saved: {output_file}")
            return output_file
        
        except Exception as e:
            self.logger.error(f"Failed to create chart: {e}")
            return None
    
    def get_data_info(self) -> Dict:
        """Get information about loaded data."""
        if not self.indexer or self.indexer.data is None:
            return {"error": "No data loaded"}
        
        return {
            "rows": len(self.indexer.data),
            "columns": self.indexer.get_columns(),
            "file": self.indexer.file_path
        }


def generate_chart(bot, chart_type, name, output_file, **kwargs):
    """Helper to generate charts with error handling."""
    import io
    import sys
    try:
        # Suppress print output from visualizer
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        method = getattr(bot.visualizer, f'plot_{chart_type}')
        method(output_file=output_file, show=False, **kwargs)
        
        sys.stdout = old_stdout
        return (True, output_file)
    except Exception as e:
        sys.stdout = old_stdout
        return (False, str(e))


def load_questions_from_file(file_path="questions.txt"):
    """Load questions from text file. File must exist."""
    if not os.path.exists(file_path):
        print(f"\n[ERROR] Questions file '{file_path}' not found. Create it and try again.")
        exit(1)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            questions = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not questions:
            print(f"\n[ERROR] No valid questions in {file_path}. Add questions and try again.")
            exit(1)
        
        print(f"[OK] Loaded {len(questions)} questions from {file_path}")
        return questions
    except Exception as e:
        print(f"\n[ERROR] Failed to read {file_path}: {e}")
        exit(1)


def main():
    """Main entry point for use."""
    
    # Initialize bot with configuration
    config = Config.from_env()
    bot = FinancialQABot(config)
    
    # Load data
    if not bot.load_data():
        print("ERROR: Failed to load data")
        return 1
    
    # Load business questions from file
    questions_file = os.getenv("QUESTIONS_FILE", "questions.txt")
    business_questions = load_questions_from_file(questions_file)
    
    # Generate comprehensive report
    report, report_file = bot.generate_report(
        business_questions,
        output_file=f"{config.OUTPUT_DIR}/financial_analysis_report.json"
    )
    
    # Print results
    info = bot.get_data_info()
    print(f"\n{'='*80}\n{'FINANCIAL QA BOT - ANALYSIS RESULTS':^80}\n{'='*80}")
    print(f"\n[DATA INFORMATION]\n  Dataset: {info['file']}\n  Records: {info['rows']} rows\n  Columns: {', '.join(info['columns'])}")
    print(f"\n{'-'*80}\n[QUESTION & ANSWER RESULTS]\n{'-'*80}")
    
    for i, result in enumerate(report.get("results", []), 1):
        status = "Answer" if result.get("status") == "success" else "ERROR"
        answer = result.get('answer') if status == "Answer" else result.get('error', 'Unknown error')
        print(f"\n  [{i}] Question: {result['question']}\n      {status}: {answer}")
    
    # Generate charts
    print("\n" + "-"*80)
    print("[GENERATING VISUALIZATIONS]")
    print("-"*80)
    
    chart_count = 0
    charts = [
        # Basic charts
        *[("metric_over_time", f"Line chart: {m}", f"{config.CHART_DIR}/{m.lower()}.png", {"metric": m}) 
          for m in ["Revenue", "Net_Income", "Operating_Expenses"]],
        ("bar_chart", "Bar chart: Total Assets", f"{config.CHART_DIR}/total_assets_bar.png", {"metric": "Total_Assets"}),
        ("comparison", "Comparison chart", f"{config.CHART_DIR}/comparison.png", 
         {"metrics": ["Revenue", "Net_Income", "Operating_Expenses"]}),
        ("waterfall", "Waterfall chart", f"{config.CHART_DIR}/waterfall_2023.png", {"target_year": 2023}),
        ("margin_boxplot", "Box plot: Margin", f"{config.CHART_DIR}/margin_boxplot.png", {}),
        ("momentum", "Momentum analysis", f"{config.CHART_DIR}/momentum_revenue.png", 
         {"metric": "Revenue", "window_short": 2, "window_long": 3}),
        ("rolling_correlation", "Rolling correlation", f"{config.CHART_DIR}/correlation_revenue_assets.png", 
         {"metric1": "Revenue", "metric2": "Total_Assets", "window": 3}),
        
        # Advanced visualizations
        ("dual_axis_chart", "Dual Axis: Revenue vs Margin", f"{config.CHART_DIR}/dual_axis.png", 
         {"metric1": "Revenue", "metric2": "Net_Margin"}),
        ("area_stacked", "Stacked Area Chart", f"{config.CHART_DIR}/stacked_area.png", 
         {"metrics": ["Revenue", "Operating_Expenses", "Net_Income"]}),
        ("yoy_heatmap", "YoY Heatmap: Revenue", f"{config.CHART_DIR}/yoy_heatmap.png", {"metric": "Revenue"}),
        ("scatter_regression", "Scatter: Revenue vs Assets", f"{config.CHART_DIR}/scatter_regression.png", 
         {"x_metric": "Total_Assets", "y_metric": "Revenue"}),
        ("financial_ratios_dashboard", "Financial Ratios Dashboard", f"{config.CHART_DIR}/ratios_dashboard.png", {}),
        ("profitability_funnel", "Profitability Funnel", f"{config.CHART_DIR}/funnel.png", {"target_year": 2023}),
    ]
    
    for chart_type, name, file, kwargs in charts:
        success, result = generate_chart(bot, chart_type, name, file, **kwargs)
        chart_count += 1
        if success:
            print(f"  [{chart_count}][OK] {name:<30} -> {result}")
        else:
            print(f"  [{chart_count}][!] {name:<30} -> Failed: {result}")
    
    print("\n" + "="*80)
    print("[SUMMARY]")
    print(f"  Total Questions Processed: {len(business_questions)}")
    print(f"  Total Charts Generated: {chart_count}")
    print(f"  Report Location: {report_file}")
    print(f"  Charts Directory: {config.CHART_DIR}")
    print("="*80)
    print("\n[SUCCESS] Financial analysis completed successfully!")
    print("="*80 + "\n")
    
    return 0


if __name__ == "__main__":
    exit(main())
