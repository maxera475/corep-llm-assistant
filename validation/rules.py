"""
Validation engine for COREP regulatory reporting.
Checks data quality, consistency, and regulatory compliance.
"""

from typing import Dict, List, Tuple
import pandas as pd


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self):
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        self.info: List[Dict] = []
        
    def add_error(self, rule: str, message: str, details: Dict = None):
        """Add an error."""
        self.errors.append({
            "severity": "ERROR",
            "rule": rule,
            "message": message,
            "details": details or {}
        })
    
    def add_warning(self, rule: str, message: str, details: Dict = None):
        """Add a warning."""
        self.warnings.append({
            "severity": "WARNING",
            "rule": rule,
            "message": message,
            "details": details or {}
        })
    
    def add_info(self, rule: str, message: str, details: Dict = None):
        """Add an info message."""
        self.info.append({
            "severity": "INFO",
            "rule": rule,
            "message": message,
            "details": details or {}
        })
    
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0
    
    def get_all_messages(self) -> List[Dict]:
        """Get all validation messages."""
        return self.errors + self.warnings + self.info
    
    def get_summary(self) -> Dict:
        """Get validation summary."""
        return {
            "total_checks": len(self.errors) + len(self.warnings) + len(self.info),
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "info": len(self.info),
            "is_valid": self.is_valid()
        }


class COREPValidator:
    """Validates COREP regulatory reporting data."""
    
    def __init__(self):
        """Initialize validator."""
        pass
    
    def validate_analysis(self, analysis: Dict) -> ValidationResult:
        """
        Run all validation checks on analysis result.
        
        Args:
            analysis: Analysis dictionary from LLM
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult()
        
        # Run all validation checks
        self._check_required_fields(analysis, result)
        self._check_numeric_values(analysis, result)
        self._check_row_column_codes(analysis, result)
        self._check_deductions(analysis, result)
        self._check_totals(analysis, result)
        self._check_source_citations(analysis, result)
        
        return result
    
    def _check_required_fields(self, analysis: Dict, result: ValidationResult):
        """Check that all required fields are present."""
        if "template" not in analysis:
            result.add_error(
                "REQUIRED_FIELDS",
                "Missing 'template' field in analysis"
            )
        
        if "fields" not in analysis:
            result.add_error(
                "REQUIRED_FIELDS",
                "Missing 'fields' array in analysis"
            )
            return
        
        if not analysis["fields"]:
            result.add_warning(
                "REQUIRED_FIELDS",
                "No fields populated in analysis"
            )
        
        # Check each field has required properties
        required_props = ["row", "column", "value", "item_name", "justification", "source"]
        
        for idx, field in enumerate(analysis.get("fields", [])):
            for prop in required_props:
                if prop not in field:
                    result.add_error(
                        "REQUIRED_FIELDS",
                        f"Field {idx} missing required property: {prop}",
                        {"field_index": idx, "field": field}
                    )
    
    def _check_numeric_values(self, analysis: Dict, result: ValidationResult):
        """Check that all values are numeric."""
        for idx, field in enumerate(analysis.get("fields", [])):
            value = field.get("value")
            
            if value is None:
                result.add_error(
                    "NUMERIC_VALUES",
                    f"Field {idx} has null value",
                    {"field": field}
                )
            elif not isinstance(value, (int, float)):
                result.add_error(
                    "NUMERIC_VALUES",
                    f"Field {idx} has non-numeric value: {value}",
                    {"field": field, "value_type": type(value).__name__}
                )
    
    def _check_row_column_codes(self, analysis: Dict, result: ValidationResult):
        """Check that row/column codes are valid strings."""
        valid_rows = [f"{i:03d}" for i in range(10, 200, 10)]  # 010, 020, etc.
        valid_columns = ["010", "020", "030"]
        
        for idx, field in enumerate(analysis.get("fields", [])):
            row = field.get("row")
            col = field.get("column")
            
            if not isinstance(row, str):
                result.add_warning(
                    "ROW_COLUMN_CODES",
                    f"Field {idx} row code should be string: {row}",
                    {"field": field}
                )
            
            if not isinstance(col, str):
                result.add_warning(
                    "ROW_COLUMN_CODES",
                    f"Field {idx} column code should be string: {col}",
                    {"field": field}
                )
            
            # Check format (3 digits)
            if row and not (isinstance(row, str) and len(row) == 3 and row.isdigit()):
                result.add_warning(
                    "ROW_COLUMN_CODES",
                    f"Field {idx} row code has unexpected format: {row}",
                    {"field": field}
                )
    
    def _check_deductions(self, analysis: Dict, result: ValidationResult):
        """Check that deductions are negative or properly marked."""
        deduction_keywords = ["deduction", "deduct", "intangible", "goodwill"]
        
        for idx, field in enumerate(analysis.get("fields", [])):
            item_name = field.get("item_name", "").lower()
            value = field.get("value", 0)
            
            # Check if this is likely a deduction
            is_deduction = any(keyword in item_name for keyword in deduction_keywords)
            
            if is_deduction and value > 0:
                result.add_warning(
                    "DEDUCTIONS",
                    f"Field {idx} appears to be a deduction but has positive value: {value}",
                    {"field": field, "suggestion": "Deductions should be negative"}
                )
    
    def _check_totals(self, analysis: Dict, result: ValidationResult):
        """Check that totals are consistent."""
        fields = analysis.get("fields", [])
        
        if not fields:
            return
        
        # Extract values by row
        row_values = {}
        for field in fields:
            row = field.get("row")
            col = field.get("column", "010")  # Default to main column
            value = field.get("value", 0)
            
            if col == "010":  # Only check main column
                row_values[row] = value
        
        # Check CET1 calculation (simplified)
        # CET1 = Items before deductions - Deductions
        cet1_items = []
        deductions = []
        
        for row, value in row_values.items():
            if value < 0:
                deductions.append(value)
            else:
                cet1_items.append(value)
        
        if deductions:
            total_deductions = sum(deductions)
            result.add_info(
                "TOTALS",
                f"Total deductions: {total_deductions:,}",
                {"deductions": deductions}
            )
    
    def _check_source_citations(self, analysis: Dict, result: ValidationResult):
        """Check that source citations are provided."""
        for idx, field in enumerate(analysis.get("fields", [])):
            source = field.get("source", "")
            justification = field.get("justification", "")
            
            if not source or source.strip() == "":
                result.add_warning(
                    "SOURCE_CITATIONS",
                    f"Field {idx} missing source citation",
                    {"field": field}
                )
            
            if not justification or justification.strip() == "":
                result.add_warning(
                    "SOURCE_CITATIONS",
                    f"Field {idx} missing justification",
                    {"field": field}
                )
            
            # Check if source includes page number
            if source and "page" not in source.lower():
                result.add_info(
                    "SOURCE_CITATIONS",
                    f"Field {idx} source may be missing page number",
                    {"field": field}
                )


def validate_corep_analysis(analysis: Dict) -> ValidationResult:
    """
    Convenience function to validate analysis.
    
    Args:
        analysis: Analysis dictionary
        
    Returns:
        ValidationResult
    """
    validator = COREPValidator()
    return validator.validate_analysis(analysis)


if __name__ == "__main__":
    # Test the validator
    mock_analysis_valid = {
        "template": "C01.00",
        "fields": [
            {
                "row": "010",
                "column": "010",
                "value": 10000000,
                "item_name": "Share capital",
                "justification": "Ordinary shares qualify as CET1",
                "source": "Own Funds (CRR), page 15"
            }
        ]
    }
    
    mock_analysis_invalid = {
        "template": "C01.00",
        "fields": [
            {
                "row": 10,  # Should be string
                "column": "010",
                "value": "not a number",  # Should be numeric
                "item_name": "Share capital"
                # Missing justification and source
            }
        ]
    }
    
    validator = COREPValidator()
    
    print("Validating valid analysis:")
    result1 = validator.validate_analysis(mock_analysis_valid)
    print(f"Valid: {result1.is_valid()}")
    print(f"Summary: {result1.get_summary()}")
    
    print("\nValidating invalid analysis:")
    result2 = validator.validate_analysis(mock_analysis_invalid)
    print(f"Valid: {result2.is_valid()}")
    print(f"Summary: {result2.get_summary()}")
    
    print("\nErrors:")
    for error in result2.errors:
        print(f"  - {error['rule']}: {error['message']}")
    
    print("\nWarnings:")
    for warning in result2.warnings:
        print(f"  - {warning['rule']}: {warning['message']}")
