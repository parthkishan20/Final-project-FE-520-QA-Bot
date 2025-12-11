"""
Visualizer Module
=================

This module creates charts and visualizations for financial data.
Phase 6 implementation.
"""

import matplotlib.pyplot as plt
import os


class Visualizer:
    """
    Creates charts and visualizations for financial data.
    
    Uses matplotlib to generate professional-looking charts.
    """
    
    def __init__(self, data):
        """
        Initialize the Visualizer.
        
        Args:
            data: pandas DataFrame with financial data
        """
        self.data = data
    
    def plot_metric_over_time(self, metric, output_file=None, show=True):
        """
        Create a line chart showing how a metric changes over time.
        
        Args:
            metric (str): Column name to plot (e.g., 'Revenue')
            output_file (str): Path to save the chart (optional)
            show (bool): Whether to display the chart
            
        Returns:
            str: Path to saved file, or None if not saved
        """
        # Find the year column
        year_col = None
        for col in self.data.columns:
            if col.lower() in ['year', 'date', 'period']:
                year_col = col
                break
        
        if year_col is None:
            raise ValueError("Could not find a year/date column in the data")
        
        # Check if metric exists
        if metric not in self.data.columns:
            raise ValueError(f"Metric '{metric}' not found. Available: {list(self.data.columns)}")
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(self.data[year_col], self.data[metric], marker='o', linewidth=2, markersize=8)
        
        # Styling
        plt.title(f'{metric.replace("_", " ")} Over Time', fontsize=16, fontweight='bold')
        plt.xlabel(year_col, fontsize=12)
        plt.ylabel(metric.replace('_', ' '), fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Format y-axis as currency if the values are large
        ax = plt.gca()
        if self.data[metric].max() > 1000:
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        
        # Save if requested
        saved_path = None
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            saved_path = output_file
            print(f"✓ Chart saved to: {output_file}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close()
        
        return saved_path
    
    def plot_comparison(self, metrics, output_file=None, show=True):
        """
        Create a chart comparing multiple metrics over time.
        
        Args:
            metrics (list): List of column names to compare
            output_file (str): Path to save the chart (optional)
            show (bool): Whether to display the chart
            
        Returns:
            str: Path to saved file, or None if not saved
        """
        # Find the year column
        year_col = None
        for col in self.data.columns:
            if col.lower() in ['year', 'date', 'period']:
                year_col = col
                break
        
        if year_col is None:
            raise ValueError("Could not find a year/date column in the data")
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 7))
        
        for metric in metrics:
            if metric in self.data.columns:
                ax.plot(self.data[year_col], self.data[metric], 
                       marker='o', linewidth=2, markersize=6, label=metric.replace('_', ' '))
        
        # Styling
        plt.title('Financial Metrics Comparison', fontsize=16, fontweight='bold')
        plt.xlabel(year_col, fontsize=12)
        plt.ylabel('Amount ($)', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        
        # Save if requested
        saved_path = None
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            saved_path = output_file
            print(f"✓ Chart saved to: {output_file}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close()
        
        return saved_path
    
    def plot_bar_chart(self, metric, output_file=None, show=True):
        """
        Create a bar chart for a single metric.
        
        Args:
            metric (str): Column name to plot
            output_file (str): Path to save the chart (optional)
            show (bool): Whether to display the chart
            
        Returns:
            str: Path to saved file, or None if not saved
        """
        # Find the year column
        year_col = None
        for col in self.data.columns:
            if col.lower() in ['year', 'date', 'period']:
                year_col = col
                break
        
        if year_col is None:
            raise ValueError("Could not find a year/date column in the data")
        
        if metric not in self.data.columns:
            raise ValueError(f"Metric '{metric}' not found. Available: {list(self.data.columns)}")
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.bar(self.data[year_col], self.data[metric], color='steelblue', alpha=0.8)
        
        # Styling
        plt.title(f'{metric.replace("_", " ")} by Year', fontsize=16, fontweight='bold')
        plt.xlabel(year_col, fontsize=12)
        plt.ylabel(metric.replace('_', ' '), fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        
        # Format y-axis as currency
        ax = plt.gca()
        if self.data[metric].max() > 1000:
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        
        # Save if requested
        saved_path = None
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            saved_path = output_file
            print(f"✓ Chart saved to: {output_file}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close()
        
        return saved_path
