"""
Retriever Module
================

This module finds specific values from the data based on keywords.
"""

from difflib import get_close_matches


class Retriever:
    """
    Retrieves specific values from financial data based on queries.
    
    Works with a DataIndexer to find columns and filter data.
    """
    
    def __init__(self, data_indexer):
        """
        Initialize the Retriever.
        
        Args:
            data_indexer: DataIndexer instance with loaded data
        """
        self.indexer = data_indexer
        self.data = data_indexer.data
    
    def find_column(self, keyword):
        """
        Find the best matching column name for a keyword.
        
        Args:
            keyword (str): The column name or keyword to search for
            
        Returns:
            str: The matching column name, or None if not found
        """
        columns = self.indexer.get_columns()
        
        # First try exact match (case-insensitive)
        keyword_lower = keyword.lower()
        for col in columns:
            if col.lower() == keyword_lower:
                return col
        
        # Try fuzzy matching for similar names
        matches = get_close_matches(keyword, columns, n=1, cutoff=0.6)
        if matches:
            return matches[0]
        
        # If still no match, return None
        print(f"⚠️  Column '{keyword}' not found. Available columns: {columns}")
        return None
    
    def get_value(self, column_keyword, year=None):
        """
        Get a specific value from the data.
        
        Args:
            column_keyword (str): Column name or keyword
            year (int, optional): Filter by this year
            
        Returns:
            The value(s) from the data
        """
        # Find the matching column
        column = self.find_column(column_keyword)
        if column is None:
            return None
        
        # If no year specified, return the whole column
        if year is None:
            return self.data[column]
        
        # Filter by year
        filtered_data = self.filter_by_year(year)
        
        if filtered_data.empty:
            print(f"⚠️  No data found for year {year}")
            return None
        
        # Return the value for that year
        result = filtered_data[column]
        
        # If only one value, return it directly
        if len(result) == 1:
            return result.iloc[0]
        
        return result
    
    def filter_by_year(self, year):
        """
        Filter the data to only rows matching a specific year.
        
        Args:
            year (int): The year to filter by
            
        Returns:
            pd.DataFrame: Filtered data for that year
        """
        # Try to find a year column
        year_col = None
        for col in ['Year', 'year', 'DATE', 'Date']:
            if col in self.data.columns:
                year_col = col
                break
        
        if year_col is None:
            raise ValueError("Cannot filter by year: No 'Year' column found in data")
        
        # Filter the data
        filtered = self.data[self.data[year_col] == year]
        return filtered
