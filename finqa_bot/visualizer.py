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
    
    def _save_and_show(self, output_file=None, show=True):
        """Helper to save and/or display chart."""
        saved_path = None
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            saved_path = output_file
            print(f"[OK] Chart saved to: {output_file}")
        if show:
            plt.show()
        else:
            plt.close()
        return saved_path

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
            print(f"[OK] Chart saved to: {output_file}")
        
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
        return self._save_and_show(output_file, show)
    
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
            print(f"[OK] Chart saved to: {output_file}")
        
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
        return self._save_and_show(output_file, show)

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
        return self._save_and_show(output_file, show)

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
        return self._save_and_show(output_file, show)

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
        return self._save_and_show(output_file, show)

    def plot_dual_axis_chart(self, metric1='Revenue', metric2='Net_Margin', output_file=None, show=True):
        """
        Create a dual-axis chart showing metric on left axis and percentage on right.
        """
        year_col = self._get_year_col()
        
        # Calculate Net_Margin if not present
        if 'Net_Margin' not in self.data.columns and metric2 == 'Net_Margin':
            self.data['Net_Margin'] = self.data['Net_Income'] / self.data['Revenue'] * 100
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        x_vals = self.data[year_col]
        color1 = 'tab:blue'
        ax1.set_xlabel('Year', fontsize=12)
        ax1.set_ylabel(metric1, color=color1, fontsize=12, fontweight='bold')
        ax1.plot(x_vals, self.data[metric1], color=color1, linewidth=2.5, marker='o', markersize=6, label=metric1)
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.grid(True, alpha=0.3)
        
        # Create second y-axis
        ax2 = ax1.twinx()
        color2 = 'tab:red'
        ax2.set_ylabel(f'{metric2} (%)', color=color2, fontsize=12, fontweight='bold')
        ax2.plot(x_vals, self.data[metric2], color=color2, linewidth=2.5, marker='s', markersize=6, label=f'{metric2} %')
        ax2.tick_params(axis='y', labelcolor=color2)
        
        plt.title(f'{metric1} vs {metric2} (Dual Axis)', fontsize=16, fontweight='bold')
        fig.tight_layout()
        return self._save_and_show(output_file, show)

    def plot_area_stacked(self, metrics=['Revenue', 'Operating_Expenses', 'Net_Income'], output_file=None, show=True):
        """
        Create a stacked area chart showing composition of metrics over time.
        """
        year_col = self._get_year_col()
        
        # Filter metrics that exist
        available_metrics = [m for m in metrics if m in self.data.columns]
        if not available_metrics:
            raise ValueError("None of the specified metrics found in data")
        
        plt.figure(figsize=(12, 7))
        x_vals = self.data[year_col]
        
        plt.stackplot(x_vals, *[self.data[m] for m in available_metrics], 
                     labels=available_metrics, alpha=0.7)
        
        plt.title('Financial Metrics - Stacked Area Chart', fontsize=16, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Amount ($)', fontsize=12)
        plt.legend(loc='upper left', fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # Format y-axis
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M' if x >= 1e6 else f'${x/1e3:.0f}K'))
        return self._save_and_show(output_file, show)

    def plot_yoy_heatmap(self, metric='Revenue', output_file=None, show=True):
        """
        Create a heatmap showing year-over-year percentage changes.
        """
        year_col = self._get_year_col()
        
        # Calculate YoY changes
        years = self.data[year_col].values
        values = self.data[metric].values
        
        # Create matrix for heatmap (year vs year)
        n = len(years)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j and values[j] != 0:
                    matrix[i, j] = ((values[i] - values[j]) / values[j]) * 100
        
        # Only show last 10 years if dataset is large
        if n > 10:
            years = years[-10:]
            matrix = matrix[-10:, -10:]
        
        plt.figure(figsize=(12, 10))
        im = plt.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=-50, vmax=50)
        
        plt.colorbar(im, label='% Change')
        plt.xticks(range(len(years)), years, rotation=45)
        plt.yticks(range(len(years)), years)
        plt.xlabel('Comparison Year', fontsize=12)
        plt.ylabel('Base Year', fontsize=12)
        plt.title(f'{metric} - Year-over-Year % Change Heatmap', fontsize=16, fontweight='bold')
        
        # Add text annotations
        for i in range(len(years)):
            for j in range(len(years)):
                if i != j:
                    plt.text(j, i, f'{matrix[i, j]:.0f}%', ha="center", va="center", color="black", fontsize=8)
        plt.tight_layout()
        return self._save_and_show(output_file, show)

    def plot_scatter_regression(self, x_metric='Total_Assets', y_metric='Revenue', output_file=None, show=True):
        """
        Create scatter plot with regression line showing relationship between two metrics.
        """
        if x_metric not in self.data.columns or y_metric not in self.data.columns:
            raise ValueError(f"Metrics {x_metric} or {y_metric} not found")
        
        x = self.data[x_metric].values
        y = self.data[y_metric].values
        
        # Calculate regression line
        coeffs = np.polyfit(x, y, 1)
        poly = np.poly1d(coeffs)
        y_fit = poly(x)
        
        # Calculate R-squared
        residuals = y - y_fit
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot)
        
        plt.figure(figsize=(10, 7))
        plt.scatter(x, y, alpha=0.6, s=100, c=range(len(x)), cmap='viridis', edgecolors='black', linewidth=1)
        plt.plot(x, y_fit, 'r--', linewidth=2, label=f'Regression Line (R²={r_squared:.3f})')
        
        plt.xlabel(x_metric, fontsize=12, fontweight='bold')
        plt.ylabel(y_metric, fontsize=12, fontweight='bold')
        plt.title(f'{y_metric} vs {x_metric}', fontsize=16, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # Add regression equation
        equation = f'y = {coeffs[0]:.2f}x + {coeffs[1]:.0f}'
        plt.text(0.05, 0.95, equation, transform=plt.gca().transAxes, 
                fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        return self._save_and_show(output_file, show)

    def plot_financial_ratios_dashboard(self, target_year=None, output_file=None, show=True):
        """
        Create a 4-panel dashboard showing key financial ratios.
        """
        year_col = self._get_year_col()
        
        if target_year:
            data_subset = self.data[self.data[year_col] == target_year]
            if data_subset.empty:
                data_subset = self.data.tail(1)
        else:
            data_subset = self.data
        
        # Calculate key ratios
        data_subset = data_subset.copy()
        data_subset['Net_Margin'] = (data_subset['Net_Income'] / data_subset['Revenue']) * 100
        data_subset['Op_Margin'] = ((data_subset['Revenue'] - data_subset['Operating_Expenses']) / data_subset['Revenue']) * 100
        data_subset['ROA'] = (data_subset['Net_Income'] / data_subset['Total_Assets']) * 100
        data_subset['Asset_Turnover'] = data_subset['Revenue'] / data_subset['Total_Assets']
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        years = data_subset[year_col].values
        
        # Panel 1: Net Margin
        ax1.plot(years, data_subset['Net_Margin'], marker='o', linewidth=2, color='green')
        ax1.set_title('Net Profit Margin (%)', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylabel('%')
        
        # Panel 2: Operating Margin
        ax2.plot(years, data_subset['Op_Margin'], marker='s', linewidth=2, color='blue')
        ax2.set_title('Operating Margin (%)', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylabel('%')
        
        # Panel 3: ROA
        ax3.plot(years, data_subset['ROA'], marker='^', linewidth=2, color='purple')
        ax3.set_title('Return on Assets (ROA %)', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.set_ylabel('%')
        ax3.set_xlabel('Year')
        
        # Panel 4: Asset Turnover
        ax4.plot(years, data_subset['Asset_Turnover'], marker='D', linewidth=2, color='orange')
        ax4.set_title('Asset Turnover Ratio', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.set_ylabel('Ratio')
        ax4.set_xlabel('Year')
        
        plt.suptitle('Financial Ratios Dashboard', fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()
        return self._save_and_show(output_file, show)

    def plot_profitability_funnel(self, target_year=2023, output_file=None, show=True):
        """
        Create a funnel chart showing profitability breakdown from Revenue to Net Income.
        """
        year_col = self._get_year_col()
        year_data = self.data[self.data[year_col] == target_year]
        
        if year_data.empty:
            year_data = self.data.tail(1)
            target_year = year_data[year_col].values[0]
        
        revenue = year_data['Revenue'].values[0]
        op_expenses = year_data['Operating_Expenses'].values[0]
        net_income = year_data['Net_Income'].values[0]
        
        # Calculate intermediate values
        operating_income = revenue - op_expenses
        
        stages = ['Revenue', 'Operating\nIncome', 'Net\nIncome']
        values = [revenue, operating_income, net_income]
        colors = ['#2E86AB', '#A23B72', '#F18F01']
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create funnel effect with trapezoids
        for i, (stage, val, color) in enumerate(zip(stages, values, colors)):
            width_top = val / revenue * 8
            width_bottom = values[i+1] / revenue * 8 if i < len(values)-1 else width_top * 0.8
            
            y_pos = -i * 2
            left = (10 - width_top) / 2
            
            # Draw trapezoid
            vertices = [
                (left, y_pos),
                (left + width_top, y_pos),
                (left + (width_top - width_bottom)/2 + width_bottom, y_pos - 1.5),
                (left + (width_top - width_bottom)/2, y_pos - 1.5)
            ]
            
            from matplotlib.patches import Polygon
            poly = Polygon(vertices, facecolor=color, edgecolor='black', linewidth=2, alpha=0.8)
            ax.add_patch(poly)
            
            # Add labels
            ax.text(5, y_pos - 0.75, stage, ha='center', va='center', fontsize=14, fontweight='bold', color='white')
            ax.text(5, y_pos - 1.2, f'${val:,.0f}', ha='center', va='center', fontsize=12, color='white')
            
            # Add percentage retention
            if i > 0:
                retention = (val / revenue) * 100
                ax.text(9.5, y_pos - 0.75, f'{retention:.1f}%', ha='left', va='center', fontsize=10, style='italic')
        
        ax.set_xlim(0, 10)
        ax.set_ylim(-7, 1)
        ax.axis('off')
        ax.set_title(f'Profitability Funnel Analysis ({target_year})', fontsize=16, fontweight='bold', pad=20)
        return self._save_and_show(output_file, show)

