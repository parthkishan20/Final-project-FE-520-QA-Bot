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
                self.logger.info(f"✓ Data loaded: {len(self.indexer.data)} rows")
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
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"✓ Report saved: {output_file}")
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
            
            self.logger.info(f"✓ Chart saved: {output_file}")
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


def main():
    """Main entry point for use."""
    
    # Initialize bot with configuration
    config = Config.from_env()
    bot = FinancialQABot(config)
    
    # Load data
    if not bot.load_data():
        print("ERROR: Failed to load data")
        return 1
    
    # Business questions for analysis
    business_questions = [
        "What was the revenue in 2023?",
        "What was net income in 2021?",
        "What were operating expenses in 2020?",
        "What were total assets in 2022?",
    ]
    
    # Generate comprehensive report
    report, report_file = bot.generate_report(
        business_questions,
        output_file=f"{config.OUTPUT_DIR}/financial_analysis_report.json"
    )
    
    # Print results in clean format
    print("\n" + "="*70)
    print("FINANCIAL QA BOT - ANALYSIS RESULTS")
    print("="*70)
    
    print(f"\nData Information:")
    info = bot.get_data_info()
    print(f"  • Rows: {info['rows']}")
    print(f"  • Columns: {', '.join(info['columns'])}")
    
    print(f"\nAnalysis Results:")
    results = report.get("results", [])
    for i, result in enumerate(results, 1):
        if result.get("status") == "success":
            print(f"\n  {i}. Q: {result['question']}")
            print(f"     A: {result['answer']}")
        else:
            print(f"\n  {i}. Q: {result.get('question', 'N/A')}")
            print(f"     ERROR: {result.get('error', 'Unknown error')}")
    
    # Generate charts
    print(f"\nGenerating Visualizations:")
    metrics = ["Revenue", "Net_Income", "Operating_Expenses"]
    for metric in metrics:
        chart_file = bot.export_chart(metric, chart_type="line")
        if chart_file:
            print(f"  ✓ {metric} chart: {chart_file}")
    
    print("\n" + "="*70)
    print(f"Report saved: {report_file}")
    print("="*70 + "\n")
    
    return 0


if __name__ == "__main__":
    exit(main())
