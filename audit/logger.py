"""
Audit logger for COREP regulatory reporting assistant.
Tracks all processing steps, decisions, and data sources.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import uuid


class AuditLogger:
    """Logs audit trail for regulatory reporting."""
    
    def __init__(self, log_dir: str = "audit_logs"):
        """
        Initialize audit logger.
        
        Args:
            log_dir: Directory to store audit logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize new session
        self.session_id = str(uuid.uuid4())
        self.session_start = datetime.now().isoformat()
        
        self.audit_trail = {
            "session_id": self.session_id,
            "session_start": self.session_start,
            "events": []
        }
    
    def log_query(self, question: str, scenario: str):
        """
        Log the user query and scenario.
        
        Args:
            question: User question
            scenario: Scenario description
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "USER_QUERY",
            "data": {
                "question": question,
                "scenario": scenario
            }
        }
        self.audit_trail["events"].append(event)
    
    def log_retrieval(self, query: str, results: List[Dict], top_k: int):
        """
        Log document retrieval results.
        
        Args:
            query: Search query
            results: Retrieved chunks
            top_k: Number of results requested
        """
        # Simplified results for logging
        simplified_results = []
        for r in results:
            simplified_results.append({
                "source_file": r["metadata"]["source_file"],
                "page": r["metadata"]["page"],
                "similarity_score": r.get("similarity_score"),
                "text_preview": r["text"][:200] if len(r["text"]) > 200 else r["text"]
            })
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "DOCUMENT_RETRIEVAL",
            "data": {
                "query": query,
                "top_k": top_k,
                "results_count": len(results),
                "results": simplified_results
            }
        }
        self.audit_trail["events"].append(event)
    
    def log_llm_call(self, 
                     prompt: str, 
                     response: Dict,
                     model: str,
                     tokens_used: int = None):
        """
        Log LLM API call.
        
        Args:
            prompt: Prompt sent to LLM
            response: LLM response
            model: Model name
            tokens_used: Number of tokens used
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "LLM_REASONING",
            "data": {
                "model": model,
                "tokens_used": tokens_used,
                "prompt_preview": prompt[:500] if len(prompt) > 500 else prompt,
                "response": response
            }
        }
        self.audit_trail["events"].append(event)
    
    def log_validation(self, validation_result):
        """
        Log validation results.
        
        Args:
            validation_result: ValidationResult object
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "VALIDATION",
            "data": {
                "summary": validation_result.get_summary(),
                "errors": validation_result.errors,
                "warnings": validation_result.warnings,
                "info": validation_result.info
            }
        }
        self.audit_trail["events"].append(event)
    
    def log_template_mapping(self, template_code: str, fields_count: int):
        """
        Log template mapping.
        
        Args:
            template_code: COREP template code
            fields_count: Number of fields mapped
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "TEMPLATE_MAPPING",
            "data": {
                "template_code": template_code,
                "fields_count": fields_count
            }
        }
        self.audit_trail["events"].append(event)
    
    def log_export(self, output_path: str, format: str = "xlsx"):
        """
        Log file export.
        
        Args:
            output_path: Path to exported file
            format: File format
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "FILE_EXPORT",
            "data": {
                "output_path": output_path,
                "format": format
            }
        }
        self.audit_trail["events"].append(event)
    
    def log_error(self, error_type: str, error_message: str, details: Dict = None):
        """
        Log an error.
        
        Args:
            error_type: Type of error
            error_message: Error message
            details: Additional details
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "ERROR",
            "data": {
                "error_type": error_type,
                "message": error_message,
                "details": details or {}
            }
        }
        self.audit_trail["events"].append(event)
    
    def save_log(self, filename: str = None) -> str:
        """
        Save audit log to file.
        
        Args:
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Path to saved log file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audit_log_{timestamp}_{self.session_id[:8]}.json"
        
        log_path = self.log_dir / filename
        
        # Add session end time
        self.audit_trail["session_end"] = datetime.now().isoformat()
        
        # Calculate session duration
        start = datetime.fromisoformat(self.session_start)
        end = datetime.now()
        duration = (end - start).total_seconds()
        self.audit_trail["session_duration_seconds"] = duration
        
        # Save to file
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(self.audit_trail, f, indent=2, ensure_ascii=False)
        
        return str(log_path)
    
    def get_trail_summary(self) -> Dict:
        """
        Get summary of audit trail.
        
        Returns:
            Summary dictionary
        """
        event_types = {}
        for event in self.audit_trail["events"]:
            event_type = event["event_type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            "session_id": self.session_id,
            "session_start": self.session_start,
            "total_events": len(self.audit_trail["events"]),
            "event_types": event_types
        }
    
    def get_formatted_trail(self) -> str:
        """
        Get human-readable formatted audit trail.
        
        Returns:
            Formatted string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("AUDIT TRAIL")
        lines.append("=" * 80)
        lines.append(f"Session ID: {self.session_id}")
        lines.append(f"Start Time: {self.session_start}")
        lines.append("")
        
        for i, event in enumerate(self.audit_trail["events"], 1):
            lines.append(f"{i}. {event['event_type']}")
            lines.append(f"   Time: {event['timestamp']}")
            
            # Format event data
            if event['event_type'] == "USER_QUERY":
                lines.append(f"   Question: {event['data']['question']}")
                lines.append(f"   Scenario: {event['data']['scenario'][:100]}...")
            
            elif event['event_type'] == "DOCUMENT_RETRIEVAL":
                lines.append(f"   Query: {event['data']['query']}")
                lines.append(f"   Results: {event['data']['results_count']} chunks retrieved")
            
            elif event['event_type'] == "LLM_REASONING":
                lines.append(f"   Model: {event['data']['model']}")
                lines.append(f"   Tokens: {event['data'].get('tokens_used', 'N/A')}")
            
            elif event['event_type'] == "VALIDATION":
                summary = event['data']['summary']
                lines.append(f"   Valid: {summary['is_valid']}")
                lines.append(f"   Errors: {summary['errors']}, Warnings: {summary['warnings']}")
            
            elif event['event_type'] == "TEMPLATE_MAPPING":
                lines.append(f"   Template: {event['data']['template_code']}")
                lines.append(f"   Fields: {event['data']['fields_count']}")
            
            elif event['event_type'] == "FILE_EXPORT":
                lines.append(f"   Path: {event['data']['output_path']}")
            
            elif event['event_type'] == "ERROR":
                lines.append(f"   Error: {event['data']['message']}")
            
            lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)


def create_audit_logger(log_dir: str = "audit_logs") -> AuditLogger:
    """
    Convenience function to create audit logger.
    
    Args:
        log_dir: Directory for logs
        
    Returns:
        AuditLogger instance
    """
    return AuditLogger(log_dir=log_dir)


if __name__ == "__main__":
    # Test the audit logger
    logger = AuditLogger(log_dir="test_audit_logs")
    
    # Simulate a session
    logger.log_query(
        "How should share capital be classified?",
        "Bank has €10M share capital"
    )
    
    logger.log_retrieval(
        "share capital classification",
        [{"metadata": {"source_file": "test.pdf", "page": 1}, 
          "text": "Sample text", "similarity_score": 0.85}],
        top_k=5
    )
    
    logger.log_llm_call(
        "Analyze this scenario...",
        {"template": "C01.00", "fields": []},
        "gpt-4",
        tokens_used=1500
    )
    
    # Save log
    log_path = logger.save_log()
    print(f"Audit log saved to: {log_path}")
    
    # Print summary
    print("\nSummary:")
    print(logger.get_trail_summary())
    
    # Print formatted trail
    print("\n" + logger.get_formatted_trail())
