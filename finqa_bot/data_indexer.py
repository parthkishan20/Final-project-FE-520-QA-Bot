"""
Data Indexer Module
===================
This module handles loading CSV files and providing access to the data.
"""

import pandas as pd
import os


class DataIndexer:
    """
    Loads and manages financial data from CSV files.
    
    Simple class to read CSV files and provide basic access methods.
    """
    
    def __init__(self, file_path=None):
        """
        Initialize the DataIndexer.
        
        Args:
            file_path (str, optional): Path to CSV file to load
        """
        self.data = None
        self.file_path = None
        
        if file_path:
            self.load_data(file_path)
    
    def load_data(self, file_path):
        """
        Load financial data from a CSV file.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            pd.DataFrame: The loaded data
        """
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Try to read the CSV
        try:
            self.data = pd.read_csv(file_path)
            self.file_path = file_path
            
            # Check if empty
            if self.data.empty:
                raise ValueError(f"The file {file_path} is empty")
            
            print(f"✓ Loaded {len(self.data)} rows from {file_path}")
            return self.data
            
        except pd.errors.EmptyDataError:
            raise ValueError(f"The file {file_path} is empty")
        except Exception as e:
            raise Exception(f"Error reading file: {e}")
    
    def get_columns(self):
        """
        Get list of column names.
        
        Returns:
            list: Column names
        """
        if self.data is None:
            raise ValueError("No data loaded. Please load a file first.")
        
        return list(self.data.columns)
    
    def head(self, n=5):
        """
        Get first n rows of data.
        
        Args:
            n (int): Number of rows to return
            
        Returns:
            pd.DataFrame: First n rows
        """
        if self.data is None:
            raise ValueError("No data loaded. Please load a file first.")
        
        return self.data.head(n)
    
    def info(self):
        """
        Display information about the dataset.
        """
        if self.data is None:
            raise ValueError("No data loaded. Please load a file first.")
        
        print("\n" + "="*50)
        print("DATASET INFORMATION")
        print("="*50)
        print(f"File: {self.file_path}")
        print(f"Rows: {len(self.data)}")
        print(f"Columns: {len(self.data.columns)}")
        print("\nColumn Details:")
        self.data.info()
        print("="*50 + "\n")
