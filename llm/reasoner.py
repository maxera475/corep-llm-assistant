"""
LLM reasoning engine for COREP regulatory analysis.
Uses Google Gemini API with structured JSON output.
"""

import os
import json
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

from llm.prompts import (
    COREP_SYSTEM_PROMPT,
    create_corep_analysis_prompt,
    create_json_schema
)


# Load environment variables
load_dotenv()


class COREPReasoner:
    """LLM reasoning engine for COREP analysis."""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model: str = "gemini-2.5-flash",
                 temperature: float = 0.1):
        """
        Initialize the reasoner.
        
        Args:
            api_key: Google API key (or set GOOGLE_API_KEY env var)
            model: Gemini model to use
            temperature: Sampling temperature
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Google API key not found. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        genai.configure(api_key=self.api_key)
        
        # Create generation config (response_mime_type requires google-generativeai>=0.8.0)
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json"
        )
        
        self.model = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config
        )
        self.model_name = model
        self.temperature = temperature
        
        print(f"Initialized COREP Reasoner with model: {model}")
    
    def analyze_scenario(self,
                        question: str,
                        scenario: str,
                        retrieved_rules: str) -> Dict:
        """
        Analyze a scenario using LLM with retrieved rules.
        
        Args:
            question: User's question
            scenario: Scenario description
            retrieved_rules: Retrieved regulatory rules (formatted)
            
        Returns:
            Structured analysis as dictionary
        """
        # Create prompt
        user_prompt = create_corep_analysis_prompt(
            question=question,
            scenario=scenario,
            retrieved_rules=retrieved_rules
        )
        
        # Combine system prompt and user prompt for Gemini
        full_prompt = f"{COREP_SYSTEM_PROMPT}\n\n{user_prompt}"
        
        # Call Gemini API with JSON mode
        try:
            response = self.model.generate_content(full_prompt)
            
            # Parse JSON response
            result_text = response.text
            result = json.loads(result_text)
            
            # Add metadata
            result["metadata"] = {
                "model": self.model_name,
                "tokens_used": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else None,
                "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else None,
                "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else None
            }
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {result_text}")
            raise
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise
    
    def analyze_with_function_calling(self,
                                     question: str,
                                     scenario: str,
                                     retrieved_rules: str) -> Dict:
        """
        Alternative method using function declarations for structured output.
        
        Args:
            question: User's question
            scenario: Scenario description
            retrieved_rules: Retrieved rules
            
        Returns:
            Structured analysis
        """
        # For Gemini, use the standard JSON mode approach
        # Function calling syntax is different in Gemini
        return self.analyze_scenario(question, scenario, retrieved_rules)


def analyze_corep_scenario(question: str,
                          scenario: str,
                          retrieved_rules: str,
                          api_key: Optional[str] = None) -> Dict:
    """
    Convenience function to analyze a COREP scenario.
    
    Args:
        question: User question
        scenario: Scenario description
        retrieved_rules: Retrieved rules
        api_key: Google API key
        
    Returns:
        Analysis result
    """
    reasoner = COREPReasoner(api_key=api_key)
    return reasoner.analyze_scenario(question, scenario, retrieved_rules)


if __name__ == "__main__":
    # Test the reasoner
    mock_question = "How should these be classified?"
    mock_scenario = """
    Bank has:
    - Share capital: €10,000,000
    - Share premium: €2,000,000
    - Intangible assets: €500,000
    """
    mock_rules = """
[CHUNK 1]
Source: Own Funds (CRR)_06-02-2026.pdf
Page: 15

Common Equity Tier 1 items include ordinary shares and share premium. 
Intangible assets must be fully deducted from CET1.
"""
    
    try:
        reasoner = COREPReasoner()
        result = reasoner.analyze_scenario(
            question=mock_question,
            scenario=mock_scenario,
            retrieved_rules=mock_rules
        )
        
        print("Analysis Result:")
        print(json.dumps(result, indent=2))
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
