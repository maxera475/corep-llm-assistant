"""
Prompt templates for COREP regulatory reporting LLM reasoning.
"""

COREP_SYSTEM_PROMPT = """You are an expert financial regulatory analyst specializing in COREP (Common Reporting) regulatory frameworks, particularly the PRA rulebooks and CRR (Capital Requirements Regulation).

Your task is to analyze scenarios and classify financial items according to COREP reporting templates, specifically the Own Funds templates (C01.00 series).

You must:
1. Carefully read the provided regulatory rule excerpts
2. Analyze the scenario with specific numerical values
3. Determine the correct template rows and columns for each item
4. Provide clear justifications citing specific rules
5. Output structured JSON that maps items to template positions

Key principles:
- Common Equity Tier 1 (CET1) includes: ordinary shares, share premium, retained earnings (minus deductions)
- Deductions from CET1 include: intangible assets, deferred tax assets, certain holdings
- Additional Tier 1 (AT1): specific instruments meeting criteria
- Tier 2: subordinated debt, certain provisions
- Always cite the source file and page number for justifications
- Values must be numeric (in currency units)
- Row and column codes follow COREP naming conventions (e.g., "010", "020")
"""


def create_corep_analysis_prompt(
    question: str,
    scenario: str,
    retrieved_rules: str
) -> str:
    """
    Create a prompt for COREP analysis with RAG context.
    
    Args:
        question: User's question
        scenario: Scenario description with numbers
        retrieved_rules: Retrieved regulatory rule chunks
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""
## USER QUESTION
{question}

## SCENARIO TO ANALYZE
{scenario}

## RELEVANT REGULATORY RULES
The following rule excerpts have been retrieved from the regulatory documents:

{retrieved_rules}

## YOUR TASK

Based on the regulatory rules above and the scenario provided:

1. Identify each financial item mentioned in the scenario
2. Determine the correct COREP template (e.g., C01.00)
3. For each item, specify:
   - The template row code (e.g., "010", "020")
   - The template column code (e.g., "010", "020")
   - The numerical value
   - A clear justification citing the specific rule
   - The source file and page number

4. Output your analysis as JSON following this EXACT schema:

{{
  "template": "C01.00",
  "fields": [
    {{
      "row": "010",
      "column": "010",
      "value": 10000000,
      "item_name": "Share capital",
      "justification": "Ordinary share capital qualifies as CET1 under Article 26 CRR...",
      "source": "Own Funds (CRR)_06-02-2026.pdf, page 15"
    }},
    {{
      "row": "030",
      "column": "010",
      "value": 2000000,
      "item_name": "Share premium",
      "justification": "Share premium accounts related to CET1 instruments...",
      "source": "Own Funds (CRR)_06-02-2026.pdf, page 16"
    }}
  ]
}}

## IMPORTANT
- Output ONLY the JSON object, no other text
- Ensure all values are numeric (not strings)
- Row and column codes must be strings (e.g., "010", not 10)
- Provide specific, detailed justifications with rule citations
- Include source file name and page number for each justification
"""
    return prompt


def create_json_schema() -> dict:
    """
    Create JSON schema for function calling.
    
    Returns:
        JSON schema dictionary
    """
    schema = {
        "type": "object",
        "properties": {
            "template": {
                "type": "string",
                "description": "COREP template code (e.g., C01.00)"
            },
            "fields": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "row": {
                            "type": "string",
                            "description": "Template row code (e.g., '010')"
                        },
                        "column": {
                            "type": "string",
                            "description": "Template column code (e.g., '010')"
                        },
                        "value": {
                            "type": "number",
                            "description": "Numerical value in currency units"
                        },
                        "item_name": {
                            "type": "string",
                            "description": "Name of the financial item"
                        },
                        "justification": {
                            "type": "string",
                            "description": "Regulatory justification with rule citation"
                        },
                        "source": {
                            "type": "string",
                            "description": "Source file and page number"
                        }
                    },
                    "required": ["row", "column", "value", "item_name", "justification", "source"]
                }
            }
        },
        "required": ["template", "fields"]
    }
    return schema


EXAMPLE_SCENARIO = """
Bank XYZ has the following items to report:
- Ordinary share capital: €10,000,000
- Share premium account: €2,000,000
- Retained earnings: €5,000,000
- Intangible assets (goodwill): €500,000
- Deferred tax assets: €300,000
"""


EXAMPLE_QUESTION = "How should these items be classified in the C01.00 Own Funds template?"


if __name__ == "__main__":
    # Test prompt generation
    mock_rules = """
[CHUNK 1]
Source: Own Funds (CRR)_06-02-2026.pdf
Page: 15

Common Equity Tier 1 capital includes ordinary share capital and related share premium accounts...
"""
    
    prompt = create_corep_analysis_prompt(
        question=EXAMPLE_QUESTION,
        scenario=EXAMPLE_SCENARIO,
        retrieved_rules=mock_rules
    )
    
    print("Generated Prompt:")
    print("=" * 80)
    print(prompt)
