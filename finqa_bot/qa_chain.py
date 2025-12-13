"""
QA Chain Module
===============

This module generates answers to questions about the financial data.
"""
from dotenv import load_dotenv
import re
import os
import requests
import time
load_dotenv()  # This loads variables from .env file


class QAChain:
    """
    Generates natural language answers to financial questions.
    """
    
    def __init__(self, retriever, openrouter_api_key=None, openrouter_model=None, use_llm=True):
        """Initialize the QA Chain.

        Args:
            retriever: Retriever instance to get data from
            openrouter_api_key (str): OpenRouter API key; falls back to env var
            openrouter_model (str): OpenRouter model id
            use_llm (bool): Whether to call OpenRouter (falls back to rules when False)
        """
        self.retriever = retriever
        self.use_llm = use_llm
        self.openrouter_api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model = openrouter_model or os.getenv("OPENROUTER_MODEL", "mistralai/devstral-2512:free")
        self._cache = {}  # simple in-memory cache to avoid repeated LLM calls
        self._llm_disabled = False  # disable further calls after rate-limit errors
    
    def generate_answer(self, query):
        """
        Generate an answer to a question.
        
        Args:
            query (str): User's question in plain English
            
        Returns:
            str: Natural language answer
        """
        cache_key = query.strip().lower()
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Prefer OpenRouter (Mistral) if enabled and key present
        if self.use_llm and not self._llm_disabled and self.openrouter_api_key:
            try:
                answer = self._generate_openrouter_answer(query)
                self._cache[cache_key] = answer
                return answer
            except Exception as e:
                resp = getattr(e, "response", None)
                if resp is not None and getattr(resp, "status_code", None) == 429:
                    self._llm_disabled = True
                    print("[!]  OpenRouter rate limit hit (429). Disabling LLM for this run; using rule-based answers.")
                else:
                    print(f"[!]  OpenRouter failed: {e}, using rule-based fallback")

        # Fallback to rule-based answer (Phase 4)
        answer = self._generate_rule_based_answer(query)
        self._cache[cache_key] = answer
        return answer
    
    def _generate_openrouter_answer(self, query):
        """
        Generate answer using OpenRouter HTTP API.
        """
        metric, year = self._parse_query(query)

        data_context = ""
        if metric and year:
            value = self.retriever.get_value(metric, year=year)
            if value is not None:
                data_context = f"{metric} in {year}: ${value:,}"
        elif metric:
            for y in [2023, 2022, 2021, 2020, 2019]:
                val = self.retriever.get_value(metric, year=y)
                if val is not None:
                    data_context += f"{metric} in {y}: ${val:,}\n"

        if not data_context:
            data_context = "No specific data found for this query."

        system_prompt = "You are a helpful financial analyst. Given financial data, answer clearly and concisely."
        user_prompt = f"Given this data:\n\n{data_context}\n\nQuestion: {query}\n\nProvide a clear, professional answer."

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",  # optional but recommended
            "X-Title": "Financial QA Bot"
        }

        payload = {
            "model": self.openrouter_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3
        }

        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    
    def _generate_rule_based_answer(self, query):
        """
        Generate answer using simple rules.
        
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
        
        # Format the answer - pass query for context
        answer = self._format_answer(metric, value, year, query)
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
    
    def _format_answer(self, metric, value, year, query=""):
        """
        Format a nice answer sentence.
        
        Args:
            metric (str): The metric name
            value: The value (number or series)
            year (int, optional): The year
            query (str): Original question for context
            
        Returns:
            str: Formatted answer
        """
        import pandas as pd
        
        metric_display = metric.replace('_', ' ')
        query_lower = query.lower()
        
        # Handle pandas Series (trend data)
        if isinstance(value, pd.Series):
            if len(value) == 0:
                return f"No data available for {metric_display}."
            
            # Get the year column from the retriever's data
            year_col_data = self.retriever.data[self.retriever.indexer.get_columns()[0]]  # First column is typically Year
            
            # Create a series with year as index for better display
            value_with_years = pd.Series(value.values, index=year_col_data.values)
            
            # Check if question asks for specific year(s) with max/min
            asking_for_best = any(word in query_lower for word in ['best', 'highest', 'maximum', 'peak', 'most', 'top'])
            asking_for_worst = any(word in query_lower for word in ['worst', 'lowest', 'minimum', 'least', 'bottom'])
            asking_for_which = 'which year' in query_lower or 'what year' in query_lower or 'when was' in query_lower
            
            if asking_for_best or (asking_for_which and asking_for_best):
                max_val = value_with_years.max()
                max_years = value_with_years[value_with_years == max_val].index.tolist()
                year_str = ", ".join(map(str, max_years))
                return f"The best year(s) for {metric_display} was {year_str} with ${max_val:,.0f}."
            
            if asking_for_worst or (asking_for_which and asking_for_worst):
                min_val = value_with_years.min()
                min_years = value_with_years[value_with_years == min_val].index.tolist()
                year_str = ", ".join(map(str, min_years))
                return f"The worst year(s) for {metric_display} was {year_str} with ${min_val:,.0f}."
            
            # Default: show trend with recent values
            first_val = value_with_years.iloc[0]
            last_val = value_with_years.iloc[-1]
            pct_change = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
            
            direction = "increased" if pct_change > 0 else "decreased"
            trend_desc = f"{direction} by {abs(pct_change):.1f}%"
            
            # Show recent 5 years if available
            recent = value_with_years.tail(5)
            year_data = "\n      ".join([f"{idx}: ${val:,.0f}" for idx, val in recent.items()])
            
            return (f"{metric_display} {trend_desc} from ${first_val:,.0f} to ${last_val:,.0f}.\n"
                   f"      Recent values:\n      {year_data}")
        
        # Handle single value
        if isinstance(value, (int, float)):
            formatted_value = f"${value:,.0f}"
            if year:
                return f"The {metric_display} in {year} was {formatted_value}."
            else:
                return f"The {metric_display} is {formatted_value}."
        
        # Fallback
        return f"The {metric_display} is {value}."
    
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

