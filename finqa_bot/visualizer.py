"""
Visualizer Module
=================

This module creates charts and visualizations for financial data.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
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
        self.data = data.copy() # Work on a copy to avoid mutating original data
        
        # Ensure year column is identified standardly for internal use
        self.year_col = None
        for col in self.data.columns:
            if col.lower() in ['year', 'date', 'period']:
                self.year_col = col
                break
        
        # Pre-calculate common derived metrics if they don't exist
        if 'Net_Margin' not in self.data.columns and 'Net_Income' in self.data.columns and 'Revenue' in self.data.columns:
            self.data['Net_Margin'] = self.data['Net_Income'] / self.data['Revenue'] * 100

        # Handle date conversion for time-series plotting
        if self.year_col:
            try:
                self.data['Date_Obj'] = pd.to_datetime(self.data[self.year_col], format='%Y')
            except:
                self.data['Date_Obj'] = self.data[self.year_col]

    def _get_year_col(self):
        """Helper to safely get the year column."""
        if self.year_col is None:
            raise ValueError("Could not find a year/date column in the data")
        return self.year_col

    def plot_metric_over_time(self, metric, output_file=None, show=True):
        """
        Create a line chart showing how a metric changes over time.
        """
        year_col = self._get_year_col()
        
        if metric not in self.data.columns:
            raise ValueError(f"Metric '{metric}' not found. Available: {list(self.data.columns)}")
        
        plt.figure(figsize=(10, 6))
        plt.plot(self.data[year_col], self.data[metric], marker='o', linewidth=2, markersize=8)
        
        plt.title(f'{metric.replace("_", " ")} Over Time', fontsize=16, fontweight='bold')
        plt.xlabel(year_col, fontsize=12)
        plt.ylabel(metric.replace('_', ' '), fontsize=12)
        plt.grid(True, alpha=0.3)
        
        ax = plt.gca()
        if self.data[metric].max() > 1000:
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        
        saved_path = None
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            saved_path = output_file
            print(f"✓ Chart saved to: {output_file}")
        
        if show: plt.show()
        else: plt.close()
        
        return saved_path
    
    def plot_comparison(self, metrics, output_file=None, show=True):
        """
        Create a chart comparing multiple metrics over time.
        """
        year_col = self._get_year_col()
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        for metric in metrics:
            if metric in self.data.columns:
                ax.plot(self.data[year_col], self.data[metric], 
                        marker='o', linewidth=2, markersize=6, label=metric.replace('_', ' '))
        
        plt.title('Financial Metrics Comparison', fontsize=16, fontweight='bold')
        plt.xlabel(year_col, fontsize=12)
        plt.ylabel('Amount ($)', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        plt.tight_layout()
        
        saved_path = None
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            saved_path = output_file
            print(f"✓ Chart saved to: {output_file}")
        
        if show: plt.show()
        else: plt.close()
        
        return saved_path
    
    def plot_bar_chart(self, metric, output_file=None, show=True):
        """
        Create a bar chart for a single metric.
        """
        year_col = self._get_year_col()
        
        if metric not in self.data.columns:
            raise ValueError(f"Metric '{metric}' not found.")
        
        plt.figure(figsize=(10, 6))
        plt.bar(self.data[year_col], self.data[metric], color='steelblue', alpha=0.8)
        
        plt.title(f'{metric.replace("_", " ")} by Year', fontsize=16, fontweight='bold')
        plt.xlabel(year_col, fontsize=12)
        plt.ylabel(metric.replace('_', ' '), fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        
        ax = plt.gca()
        if self.data[metric].max() > 1000:
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        
        saved_path = None
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            saved_path = output_file
            print(f"✓ Chart saved to: {output_file}")
        
        if show: plt.show()
        else: plt.close()
        
        return saved_path

    # ==========================================
    # NEW ADVANCED PLOTS ADDED BELOW
    # ==========================================

    def plot_waterfall(self, target_year=None, output_file=None, show=True):
        """
        Create a P&L Waterfall chart for a specific year.
        If target_year is None, uses the most recent year.
        """
        year_col = self._get_year_col()
        
        # Determine year
        if target_year is None:
            target_year = self.data[year_col].max()
            
        row = self.data[self.data[year_col] == target_year]
        if row.empty:
            raise ValueError(f"Year {target_year} not found in data.")
        
        row = row.iloc[0] # Get Series
        
        # Calculate components
        revenue = row['Revenue']
        op_ex = -row['Operating_Expenses'] # Negative for waterfall drop
        net_income = row['Net_Income']
        # Implied other costs
        other_costs = -(revenue - row['Operating_Expenses'] - net_income)
        
        categories = ['Revenue', 'Op. Expenses', 'Other Costs', 'Net Income']
        values = [revenue, op_ex, other_costs, net_income]
        measures = ['absolute', 'relative', 'relative', 'total']
        
        # Calculate bar start positions
        starts = []
        running_sum = 0
        for val, measure in zip(values, measures):
            if measure == 'absolute':
                starts.append(0)
                running_sum += val
            elif measure == 'relative':
                starts.append(running_sum)
                running_sum += val
            else: # total
                starts.append(0)
        
        # Plotting
        plt.figure(figsize=(10, 6))
        colors = ['green', 'red', 'red', 'blue']
        bars = plt.bar(categories, values, bottom=starts, color=colors, edgecolor='black', alpha=0.7)
        
        # Add value labels
        for bar, val, measure in zip(bars, values, measures):
            y_pos = bar.get_y() + bar.get_height()/2
            if measure == 'total': y_pos = val + (val*0.05)
            
            plt.text(bar.get_x() + bar.get_width()/2, y_pos, 
                     f"${int(val):,}", 
                     ha='center', va='center', fontweight='bold')
            
        plt.title(f'Profit & Loss Waterfall ({target_year})', fontsize=16, fontweight='bold')
        plt.ylabel('Amount ($)', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        
        saved_path = None
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            saved_path = output_file
            print(f"✓ Chart saved to: {output_file}")
        
        if show: plt.show()
        else: plt.close()
        return saved_path

    def plot_margin_boxplot(self, output_file=None, show=True):
        """
        Create a box plot showing Net Margin distribution by Decade.
        """
        year_col = self._get_year_col()
        
        # Ensure derived metrics exist locally
        plot_df = self.data.copy()
        if 'Net_Margin' not in plot_df.columns:
            plot_df['Net_Margin'] = plot_df['Net_Income'] / plot_df['Revenue'] * 100
            
        plot_df['Decade'] = (plot_df[year_col] // 10) * 10
        plot_df['Decade_Label'] = plot_df['Decade'].astype(str) + 's'
        
        decades = sorted(plot_df['Decade_Label'].unique())
        plot_data = [plot_df[plot_df['Decade_Label'] == d]['Net_Margin'].values for d in decades]
        
        plt.figure(figsize=(10, 6))
        box = plt.boxplot(plot_data, labels=decades, patch_artist=True, medianprops=dict(color="black", linewidth=1.5))
        
        # Colors
        colors_list = ['lightblue', 'lightgreen', 'lightpink', 'lightyellow', 'lightgrey']
        # Cycle through colors if more decades than colors
        for i, patch in enumerate(box['boxes']):
            patch.set_facecolor(colors_list[i % len(colors_list)])
            
        plt.title('Net Margin Distribution by Decade', fontsize=16, fontweight='bold')
        plt.ylabel('Net Margin (%)', fontsize=12)
        plt.xlabel('Decade', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.5)
        
        saved_path = None
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            saved_path = output_file
            print(f"✓ Chart saved to: {output_file}")
        
        if show: plt.show()
        else: plt.close()
        return saved_path

    def plot_momentum(self, metric='Net_Income', window_short=5, window_long=15, output_file=None, show=True):
        """
        Create a Momentum Chart comparing short-term vs long-term moving averages.
        """
        if metric not in self.data.columns:
             raise ValueError(f"Metric '{metric}' not found.")
        
        # Calculate Rolling Averages
        ma_short = self.data[metric].rolling(window=window_short).mean()
        ma_long = self.data[metric].rolling(window=window_long).mean()
        
        plt.figure(figsize=(12, 6))
        
        # Use Date_Obj for x-axis if available, else standard year column
        x_axis = self.data['Date_Obj'] if 'Date_Obj' in self.data.columns else self.data[self._get_year_col()]
        
        plt.plot(x_axis, self.data[metric], label=f'Actual {metric}', color='gray', alpha=0.3)
        plt.plot(x_axis, ma_short, label=f'{window_short}-Year MA (Momentum)', color='orange', linewidth=2)
        plt.plot(x_axis, ma_long, label=f'{window_long}-Year MA (Trend)', color='blue', linewidth=2)
        
        # Fill between
        plt.fill_between(x_axis, ma_short, ma_long, 
                         where=(ma_short >= ma_long), 
                         interpolate=True, color='green', alpha=0.1, label='Positive Momentum')
        
        plt.fill_between(x_axis, ma_short, ma_long, 
                         where=(ma_short < ma_long), 
                         interpolate=True, color='red', alpha=0.1, label='Negative Momentum')
        
        plt.title(f'{metric.replace("_", " ")} Momentum Analysis', fontsize=16, fontweight='bold')
        plt.ylabel(metric.replace('_', ' '), fontsize=12)
        plt.legend(loc='upper left')
        plt.grid(True, alpha=0.5)
        
        saved_path = None
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            saved_path = output_file
            print(f"✓ Chart saved to: {output_file}")
        
        if show: plt.show()
        else: plt.close()
        return saved_path

    def plot_rolling_correlation(self, metric1='Revenue', metric2='Total_Assets', window=10, output_file=None, show=True):
        """
        Create a Rolling Correlation chart between two metrics.
        """
        if metric1 not in self.data.columns or metric2 not in self.data.columns:
             raise ValueError("One or both metrics not found in data.")
             
        # Calculate Rolling Correlation
        rolling_corr = self.data[metric1].rolling(window=window).corr(self.data[metric2])
        
        plt.figure(figsize=(10, 5))
        
        x_axis = self.data['Date_Obj'] if 'Date_Obj' in self.data.columns else self.data[self._get_year_col()]
        
        plt.plot(x_axis, rolling_corr, color='purple', linewidth=2, marker='.')
        
        plt.title(f'{window}-Year Rolling Correlation: {metric1} vs {metric2}', fontsize=16, fontweight='bold')
        plt.ylabel('Correlation Coefficient', fontsize=12)
        plt.axhline(1.0, color='black', alpha=0.3, linewidth=1)
        plt.grid(True)
        
        saved_path = None
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            saved_path = output_file
            print(f"✓ Chart saved to: {output_file}")
        
        if show: plt.show()
        else: plt.close()
        return saved_path