"""Error Handler Module
====================

This module provides nice, user-friendly error messages and exception handling.
"""


class FinQAError(Exception):
    """Base exception for FinQA Bot errors."""
    pass


class FileLoadError(FinQAError):
    """Raised when a file cannot be loaded."""
    
    def __init__(self, filepath, reason=None):
        self.filepath = filepath
        self.reason = reason
        message = f"Could not load file: {filepath}"
        if reason:
            message += f"\nReason: {reason}"
        super().__init__(message)


class ColumnNotFoundError(FinQAError):
    """Raised when a requested column doesn't exist."""
    
    def __init__(self, column, available_columns):
        self.column = column
        self.available_columns = available_columns
        message = f"Column '{column}' not found."
        if available_columns:
            message += f"\nAvailable columns: {', '.join(available_columns)}"
        super().__init__(message)


class DataNotFoundError(FinQAError):
    """Raised when requested data doesn't exist."""
    
    def __init__(self, query, suggestion=None):
        self.query = query
        self.suggestion = suggestion
        message = f"No data found for: {query}"
        if suggestion:
            message += f"\nSuggestion: {suggestion}"
        super().__init__(message)


class QueryParseError(FinQAError):
    """Raised when a query cannot be understood."""
    
    def __init__(self, query, reason=None):
        self.query = query
        self.reason = reason
        message = f"Could not understand query: '{query}'"
        if reason:
            message += f"\nReason: {reason}"
        message += "\nTry asking about specific metrics like 'revenue', 'net income', 'expenses', or 'assets'."
        super().__init__(message)


class VisualizationError(FinQAError):
    """Raised when chart creation fails."""
    
    def __init__(self, chart_type, reason=None):
        self.chart_type = chart_type
        self.reason = reason
        message = f"Failed to create {chart_type} chart"
        if reason:
            message += f": {reason}"
        super().__init__(message)


def handle_error(error, user_friendly=True):
    """
    Convert errors to user-friendly messages.
    
    Args:
        error: The exception object
        user_friendly (bool): Whether to return simplified message
        
    Returns:
        str: Error message for the user
    """
    if isinstance(error, FinQAError):
        return str(error)
    
    if user_friendly:
        # Convert common errors to friendly messages
        error_type = type(error).__name__
        
        if error_type == "FileNotFoundError":
            return f"❌ File not found. Please check the file path and try again."
        
        elif error_type == "PermissionError":
            return f"❌ Permission denied. Check file permissions."
        
        elif error_type == "KeyError":
            return f"❌ Column or key not found in the data."
        
        elif error_type == "ValueError":
            return f"❌ Invalid value provided: {str(error)}"
        
        elif error_type == "TypeError":
            return f"❌ Type error: {str(error)}"
        
        else:
            return f"❌ An error occurred: {str(error)}"
    else:
        # Return full technical error
        return f"{type(error).__name__}: {str(error)}"


def validate_file_path(filepath):
    """
    Validate that a file path exists and is readable.
    
    Args:
        filepath: Path to validate
        
    Raises:
        FileLoadError: If file doesn't exist or can't be read
    """
    import os
    
    if not filepath:
        raise FileLoadError(filepath, "No file path provided")
    
    if not os.path.exists(filepath):
        raise FileLoadError(filepath, "File does not exist")
    
    if not os.path.isfile(filepath):
        raise FileLoadError(filepath, "Path is not a file")
    
    if not os.access(filepath, os.R_OK):
        raise FileLoadError(filepath, "File is not readable (permission denied)")


def validate_column(column, available_columns):
    """
    Validate that a column exists.
    
    Args:
        column: Column name to check
        available_columns: List of available columns
        
    Raises:
        ColumnNotFoundError: If column doesn't exist
    """
    if column not in available_columns:
        raise ColumnNotFoundError(column, available_columns)
