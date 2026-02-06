"""
FastAPI backend for COREP Regulatory Reporting Assistant.
Provides REST API endpoints for the complete analysis pipeline.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from pathlib import Path
from datetime import datetime

from rag.retriever import RAGRetriever
from llm.reasoner import COREPReasoner
from templates.mapper import COREPTemplateMapper
from validation.rules import COREPValidator
from audit.logger import AuditLogger


# Initialize FastAPI app
app = FastAPI(
    title="COREP Regulatory Reporting Assistant",
    description="LLM-assisted regulatory reporting with RAG-based rule retrieval",
    version="1.0.0"
)


# Request/Response models
class AnalysisRequest(BaseModel):
    question: str
    scenario: str
    top_k: int = 5


class AnalysisResponse(BaseModel):
    success: bool
    analysis: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    audit_log_path: Optional[str] = None
    error: Optional[str] = None


# Global instances (initialized at startup)
retriever: Optional[RAGRetriever] = None
reasoner: Optional[COREPReasoner] = None
mapper: Optional[COREPTemplateMapper] = None
validator: Optional[COREPValidator] = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global retriever, reasoner, mapper, validator
    
    print("Initializing COREP Assistant API...")
    
    try:
        # Initialize retriever
        print("Loading RAG retriever...")
        retriever = RAGRetriever(data_dir="data")
        
        # Initialize LLM reasoner
        print("Loading LLM reasoner...")
        reasoner = COREPReasoner()
        
        # Initialize mapper and validator
        mapper = COREPTemplateMapper()
        validator = COREPValidator()
        
        print("✓ COREP Assistant API ready")
        
    except Exception as e:
        print(f"Error during startup: {e}")
        print("Make sure to run the embedding pipeline first:")
        print("  python -m ingestion.embedder")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "COREP Regulatory Reporting Assistant",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "export": "/export/{session_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    components = {
        "retriever": retriever is not None,
        "reasoner": reasoner is not None,
        "mapper": mapper is not None,
        "validator": validator is not None
    }
    
    all_ready = all(components.values())
    
    return {
        "status": "healthy" if all_ready else "degraded",
        "components": components,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_scenario(request: AnalysisRequest):
    """
    Analyze a COREP scenario.
    
    Args:
        request: Analysis request with question and scenario
        
    Returns:
        Analysis response with results
    """
    # Initialize audit logger
    logger = AuditLogger()
    
    try:
        # Log query
        logger.log_query(request.question, request.scenario)
        
        # Step 1: Retrieve relevant rules
        print(f"Retrieving relevant rules (top_k={request.top_k})...")
        results = retriever.retrieve(request.question, top_k=request.top_k)
        logger.log_retrieval(request.question, results, request.top_k)
        
        # Format for LLM
        formatted_rules = retriever.format_for_llm(results)
        
        # Step 2: LLM reasoning
        print("Performing LLM analysis...")
        analysis = reasoner.analyze_scenario(
            question=request.question,
            scenario=request.scenario,
            retrieved_rules=formatted_rules
        )
        
        logger.log_llm_call(
            prompt=f"Question: {request.question}",
            response=analysis,
            model=analysis.get("metadata", {}).get("model", "unknown"),
            tokens_used=analysis.get("metadata", {}).get("tokens_used")
        )
        
        # Step 3: Validate
        print("Validating results...")
        validation_result = validator.validate_analysis(analysis)
        logger.log_validation(validation_result)
        
        # Step 4: Template mapping
        template_code = analysis.get("template", "C01.00")
        fields_count = len(analysis.get("fields", []))
        logger.log_template_mapping(template_code, fields_count)
        
        # Save audit log
        audit_log_path = logger.save_log()
        
        return AnalysisResponse(
            success=True,
            analysis=analysis,
            validation={
                "summary": validation_result.get_summary(),
                "messages": validation_result.get_all_messages()
            },
            audit_log_path=audit_log_path
        )
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error during analysis: {error_msg}")
        logger.log_error("ANALYSIS_ERROR", error_msg)
        logger.save_log()
        
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/export")
async def export_to_excel(analysis: Dict[str, Any]):
    """
    Export analysis to Excel file.
    
    Args:
        analysis: Analysis dictionary
        
    Returns:
        File download response
    """
    try:
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"corep_report_{timestamp}.xlsx"
        output_path = Path("exports") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        # Export to Excel
        mapper.export_to_excel(analysis, str(output_path))
        
        return FileResponse(
            path=str(output_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates")
async def list_templates():
    """List available COREP templates."""
    return {
        "templates": [
            {
                "code": "C01.00",
                "name": "Own Funds",
                "description": "Common Equity Tier 1, Additional Tier 1, and Tier 2 capital"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    print("Starting COREP Assistant API...")
    print("API documentation will be available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
