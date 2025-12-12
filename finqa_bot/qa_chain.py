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
                    print("⚠️  OpenRouter rate limit hit (429). Disabling LLM for this run; using rule-based answers.")
                else:
                    print(f"⚠️  OpenRouter failed: {e}, using rule-based fallback")

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
