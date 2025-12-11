"""
Financial Document QA Bot Package

A simple tool to read financial data from CSV files and answer questions about it.
"""

# Import completed modules
from .data_indexer import DataIndexer
from .retriever import Retriever
from .qa_chain import QAChain
from .visualizer import Visualizer

__version__ = "0.1.0"
__all__ = ['DataIndexer', 'Retriever', 'QAChain', 'Visualizer']
