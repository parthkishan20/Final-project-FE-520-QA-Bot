"""
QA Chain Module
===============

This module generates answers to questions about the financial data.
Phase 4: Simple rule-based QA
Phase 5: Enhanced with LangChain integration (optional)
"""
from dotenv import load_dotenv
import re
import os
load_dotenv()  # This loads variables from .env file
# Try to import LangChain - it's optional
try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class QAChain:
    """
    Generates natural language answers to financial questions.
    
    Phase 4: Uses simple pattern matching
    Phase 5: Can optionally use LangChain/LLM for better answers
    """
    
    def __init__(self, retriever, use_llm=False, api_key=None):
        """
        Initialize the QA Chain.
        
        Args:
            retriever: Retriever instance to get data from
            use_llm (bool): Whether to use LangChain/LLM (Phase 5)
            api_key (str): OpenAI API key (optional, can use env var)
        """
        self.retriever = retriever
        self.use_llm = use_llm and LANGCHAIN_AVAILABLE
        self.llm = None
        
        # Initialize LLM if requested
        if self.use_llm:
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    self.llm = ChatOpenAI(
                        model="gpt-4o-mini",
                        temperature=0.3,
                        api_key=api_key
                    )
                    print("✓ LLM enabled (using GPT-4o-mini)")
                except Exception as e:
                    print(f"⚠️  Could not initialize LLM: {e}")
                    print("   Falling back to rule-based QA")
                    self.use_llm = False
            else:
                print("⚠️  No API key found. Set OPENAI_API_KEY to use LLM.")
                print("   Using rule-based QA")
                self.use_llm = False
    
    def generate_answer(self, query):
        """
        Generate an answer to a question.
        
        Args:
            query (str): User's question in plain English
            
        Returns:
            str: Natural language answer
        """
        # Try LLM first if enabled
        if self.use_llm and self.llm:
            try:
                return self._generate_llm_answer(query)
            except Exception as e:
                print(f"⚠️  LLM failed: {e}, using fallback")
                # Fall through to rule-based
        
        # Fallback to rule-based answer (Phase 4)
        return self._generate_rule_based_answer(query)
    
    def _generate_llm_answer(self, query):
        """
        Generate answer using LangChain and LLM (Phase 5).
        
        Args:
            query (str): User's question
            
        Returns:
            str: LLM-generated answer
        """
        # Parse query to get context
        metric, year = self._parse_query(query)
        
        # Get relevant data
        data_context = ""
        if metric and year:
            value = self.retriever.get_value(metric, year=year)
            if value is not None:
                data_context = f"{metric} in {year}: ${value:,}"
        elif metric:
            # Get some recent years
            for y in [2023, 2022, 2021, 2020, 2019]:
                val = self.retriever.get_value(metric, year=y)
                if val is not None:
                    data_context += f"{metric} in {y}: ${val:,}\n"
        
        if not data_context:
            data_context = "No specific data found for this query."
        
        # Create the prompt
        system_prompt = """You are a helpful financial analyst. 
Given financial data, answer questions clearly and concisely.
Format dollar amounts nicely and provide context when helpful."""
        
        user_prompt = f"""Given this data:

{data_context}

Question: {query}

Please provide a clear, professional answer."""
        
        # Call the LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content.strip()
    
    def _generate_rule_based_answer(self, query):
        """
        Generate answer using simple rules (Phase 4).
        
        Args:
            query (str): User's question
            
        Returns:
            str: Rule-based answer
        """
        # Parse the query to extract metric and year
        metric, year = self._parse_query(query)
        
        if not metric:
            return "I couldn't understand what metric you're asking about. Try asking about revenue, net income, expenses, or assets."
        
        # Get the value from the retriever
        value = self.retriever.get_value(metric, year=year)
        
        if value is None:
            return f"I couldn't find data for {metric}" + (f" in {year}" if year else "") + "."
        
        # Format the answer
        answer = self._format_answer(metric, value, year)
        return answer
    
    def _parse_query(self, query):
        """
        Parse a query to extract the metric and year.
        
        Args:
            query (str): User's question
            
        Returns:
            tuple: (metric, year) - year is None if not found
        """
        query_lower = query.lower()
        
        # Extract year (look for 4-digit numbers starting with 20)
        year_match = re.search(r'\b(20\d{2})\b', query)
        year = int(year_match.group(1)) if year_match else None
        
        # Extract metric - look for common financial terms
        metric = None
        
        # Check for revenue
        if 'revenue' in query_lower or 'sales' in query_lower:
            metric = 'Revenue'
        
        # Check for net income
        elif 'net income' in query_lower or 'net profit' in query_lower or 'profit' in query_lower:
            metric = 'Net_Income'
        
        # Check for expenses
        elif 'expense' in query_lower or 'operating expense' in query_lower:
            metric = 'Operating_Expenses'
        
        # Check for assets
        elif 'asset' in query_lower or 'total asset' in query_lower:
            metric = 'Total_Assets'
        
        return metric, year
    
    def _format_answer(self, metric, value, year):
        """
        Format a nice answer sentence.
        
        Args:
            metric (str): The metric name
            value: The value (number or series)
            year (int, optional): The year
            
        Returns:
            str: Formatted answer
        """
        # Format the metric name nicely (replace underscores with spaces)
        metric_display = metric.replace('_', ' ')
        
        # Format the value nicely
        if isinstance(value, (int, float)):
            formatted_value = self._format_number(value)
        else:
            # If it's a series/list, just use the first value
            formatted_value = self._format_number(value)
        
        # Build the sentence
        if year:
            answer = f"The {metric_display} in {year} was {formatted_value}."
        else:
            answer = f"The {metric_display} is {formatted_value}."
        
        return answer
    
    def _format_number(self, value):
        """
        Format a number nicely with commas and dollar sign.
        
        Args:
            value: Number to format
            
        Returns:
            str: Formatted number
        """
        try:
            num = float(value)
            return f"${num:,.0f}"
        except:
            return str(value)
