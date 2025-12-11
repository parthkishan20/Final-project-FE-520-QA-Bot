#!/usr/bin/env python3
"""
Test Google AI Integration
Run this after setting GOOGLE_API_KEY to verify LLM is working.
"""

import os
from dotenv import load_dotenv
from finqa_bot import DataIndexer, Retriever, QAChain

# Load environment variables
load_dotenv()

def test_llm_integration():
    """Test if Google Gemini integration is working."""
    
    print("="*70)
    print("TESTING GOOGLE AI INTEGRATION")
    print("="*70)
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("\n❌ GOOGLE_API_KEY not found!")
        print("\nPlease set it:")
        print("  export GOOGLE_API_KEY='your-key-here'")
        print("\nOr add to .env file:")
        print("  GOOGLE_API_KEY=your-key-here")
        print("\nGet your key from: https://aistudio.google.com/app/apikey")
        return False
    
    print(f"\n✓ API Key found: {api_key[:10]}...")
    
    # Load data
    print("\n1. Loading data...")
    indexer = DataIndexer('sample_data.csv')
    retriever = Retriever(indexer)
    
    # Initialize QA Chain with LLM
    print("\n2. Initializing LLM (Gemini 2.0 Flash)...")
    qa = QAChain(retriever, use_llm=True)
    
    if not qa.use_llm:
        print("\n❌ LLM initialization failed! Check the error messages above.")
        return False
    
    print(f"   LLM Status: {'Enabled ✓' if qa.use_llm else 'Disabled ✗'}")
    
    # Test simple question
    print("\n3. Testing simple question...")
    question = "What was revenue in 2023?"
    answer = qa.generate_answer(question)
    print(f"   Q: {question}")
    print(f"   A: {answer}")
    
    # Test complex question (needs LLM)
    print("\n4. Testing complex question (requires AI)...")
    complex_question = "Analyze the revenue trend from 2019 to 2023 and explain if it's growing"
    complex_answer = qa.generate_answer(complex_question)
    print(f"   Q: {complex_question}")
    print(f"   A: {complex_answer}")
    
    print("\n" + "="*70)
    print("✅ LLM INTEGRATION WORKING!")
    print("="*70)
    print("\nYour Financial QA Bot is now using Google Gemini 1.5 Flash!")
    print("Run 'python app.py' to use the full application.")
    print("="*70)
    
    return True


if __name__ == "__main__":
    success = test_llm_integration()
    exit(0 if success else 1)
