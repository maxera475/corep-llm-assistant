"""
Streamlit frontend for COREP Regulatory Reporting Assistant.
Interactive UI for regulatory analysis and reporting.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

from rag.retriever import RAGRetriever
from llm.reasoner import COREPReasoner
from templates.mapper import COREPTemplateMapper
from validation.rules import COREPValidator
from audit.logger import AuditLogger


# Page configuration
st.set_page_config(
    page_title="COREP Regulatory Reporting Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #f0fff0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff8e1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #fff0f0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'validation_result' not in st.session_state:
    st.session_state.validation_result = None
if 'audit_logger' not in st.session_state:
    st.session_state.audit_logger = None


@st.cache_resource
def load_components():
    """Load and cache components."""
    try:
        retriever = RAGRetriever(data_dir="data")
        reasoner = COREPReasoner()
        mapper = COREPTemplateMapper()
        validator = COREPValidator()
        
        return retriever, reasoner, mapper, validator, None
    except Exception as e:
        return None, None, None, None, str(e)


def main():
    """Main application."""
    
    # Header
    st.markdown('<div class="main-header">📊 COREP Regulatory Reporting Assistant</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    AI-powered assistant for COREP regulatory reporting with RAG-based rule retrieval.
    """)
    
    # Load components
    retriever, reasoner, mapper, validator, error = load_components()
    
    if error:
        st.error(f"""
        **⚠️ Initialization Error**
        
        {error}
        
        Please ensure:
        1. The embedding pipeline has been run: `python -m ingestion.embedder`
        2. Google Gemini API key is set in `.env` file
        3. All dependencies are installed: `pip install -r requirements.txt`
        """)
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        top_k = st.slider(
            "Number of retrieved rules",
            min_value=3,
            max_value=10,
            value=5,
            help="Number of relevant rule chunks to retrieve"
        )
        
        st.markdown("---")
        st.markdown("### 📚 About")
        st.info("""
        This prototype demonstrates:
        - RAG-based rule retrieval
        - LLM reasoning over regulations
        - Structured COREP template filling
        - Validation and audit trails
        """)
        
        st.markdown("---")
        st.markdown("### 📖 Example")
        if st.button("Load Example"):
            st.session_state.example_question = "How should these items be classified in the C01.00 Own Funds template?"
            st.session_state.example_scenario = """Bank XYZ financial position:

- Ordinary share capital: €10,000,000
- Share premium accounts: €2,000,000
- Retained earnings: €5,000,000
- Other reserves: €1,500,000
- Intangible assets (goodwill): €500,000
- Deferred tax assets: €300,000

Please classify these items according to CRR requirements."""
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-header">📝 Input</div>', unsafe_allow_html=True)
        
        # Question input
        question = st.text_input(
            "Your Question",
            value=st.session_state.get('example_question', ''),
            placeholder="e.g., How should share premium be classified?",
            help="Ask a question about COREP classification"
        )
        
        # Scenario input
        scenario = st.text_area(
            "Scenario Description",
            value=st.session_state.get('example_scenario', ''),
            height=300,
            placeholder="Describe the scenario with specific values...\n\nExample:\nBank has:\n- Share capital: €10,000,000\n- Retained earnings: €5,000,000\n- ...",
            help="Provide details of the items to be classified"
        )
    
    with col2:
        st.markdown('<div class="section-header">💡 Tips</div>', unsafe_allow_html=True)
        
        st.markdown("""
        **For best results:**
        
        1. **Be Specific**: Include actual values in euros
        2. **Use Proper Names**: Use regulatory terminology (e.g., "ordinary share capital", "CET1")
        3. **Provide Context**: Mention relevant characteristics (e.g., "subordinated debt with 5-year maturity")
        4. **One Template**: Focus on one template type (e.g., Own Funds C01.00)
        
        **Example Items:**
        - Share capital and premium
        - Retained earnings
        - Reserves
        - Intangible assets
        - Deferred tax assets
        - Subordinated debt
        """)
    
    # Run button
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    
    with col_btn1:
        run_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)
    
    with col_btn2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.session_state.analysis_result = None
        st.session_state.validation_result = None
        st.session_state.audit_logger = None
        st.rerun()
    
    # Process analysis
    if run_button:
        if not question or not scenario:
            st.error("⚠️ Please provide both a question and scenario description.")
            return
        
        # Initialize audit logger
        logger = AuditLogger()
        st.session_state.audit_logger = logger
        
        with st.spinner("🔍 Analyzing scenario..."):
            try:
                # Log query
                logger.log_query(question, scenario)
                
                # Step 1: Retrieve rules
                st.write("**Step 1:** Retrieving relevant regulatory rules...")
                results = retriever.retrieve(question, top_k=top_k)
                logger.log_retrieval(question, results, top_k)
                
                formatted_rules = retriever.format_for_llm(results)
                
                # Step 2: LLM reasoning
                st.write("**Step 2:** Performing LLM analysis...")
                analysis = reasoner.analyze_scenario(
                    question=question,
                    scenario=scenario,
                    retrieved_rules=formatted_rules
                )
                
                logger.log_llm_call(
                    prompt=question,
                    response=analysis,
                    model=analysis.get("metadata", {}).get("model", "unknown"),
                    tokens_used=analysis.get("metadata", {}).get("tokens_used")
                )
                
                # Step 3: Validate
                st.write("**Step 3:** Validating results...")
                validation_result = validator.validate_analysis(analysis)
                logger.log_validation(validation_result)
                
                # Step 4: Template mapping
                template_code = analysis.get("template", "C01.00")
                fields_count = len(analysis.get("fields", []))
                logger.log_template_mapping(template_code, fields_count)
                
                # Save results
                st.session_state.analysis_result = analysis
                st.session_state.validation_result = validation_result
                st.session_state.retrieved_results = results
                
                st.success("✅ Analysis completed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                logger.log_error("ANALYSIS_ERROR", str(e))
                return
    
    # Display results
    if st.session_state.analysis_result:
        st.markdown("---")
        st.markdown('<div class="section-header">📊 Results</div>', unsafe_allow_html=True)
        
        analysis = st.session_state.analysis_result
        validation_result = st.session_state.validation_result
        
        # Validation summary
        summary = validation_result.get_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Template", analysis.get("template", "N/A"))
        col2.metric("Fields", len(analysis.get("fields", [])))
        col3.metric("Errors", summary["errors"])
        col4.metric("Warnings", summary["warnings"])
        
        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Summary Table", 
            "📄 Template View", 
            "✅ Validation", 
            "📚 Retrieved Rules",
            "📝 Audit Trail"
        ])
        
        with tab1:
            st.markdown("#### Detailed Field Breakdown")
            df_details = mapper.create_detailed_table(analysis)
            
            # Format for display
            if not df_details.empty:
                st.dataframe(
                    df_details,
                    width='stretch',
                    height=400
                )
            else:
                st.warning("No fields to display")
        
        with tab2:
            st.markdown("#### COREP Template Format")
            df_template = mapper.create_dataframe_from_analysis(analysis)
            
            # Format values as currency
            st.dataframe(
                df_template.style.format("{:,.0f}"),
                width='stretch'
            )
        
        with tab3:
            st.markdown("#### Validation Results")
            
            if validation_result.is_valid():
                st.markdown('<div class="success-box">✅ All validations passed!</div>', 
                           unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box">❌ Validation failed - review errors below</div>', 
                           unsafe_allow_html=True)
            
            # Show errors
            if validation_result.errors:
                st.markdown("**🔴 Errors:**")
                for err in validation_result.errors:
                    st.error(f"**{err['rule']}**: {err['message']}")
            
            # Show warnings
            if validation_result.warnings:
                st.markdown("**🟡 Warnings:**")
                for warn in validation_result.warnings:
                    st.warning(f"**{warn['rule']}**: {warn['message']}")
            
            # Show info
            if validation_result.info:
                st.markdown("**ℹ️ Information:**")
                for info in validation_result.info:
                    st.info(f"**{info['rule']}**: {info['message']}")
        
        with tab4:
            st.markdown("#### Retrieved Regulatory Rules")
            
            if 'retrieved_results' in st.session_state:
                for i, result in enumerate(st.session_state.retrieved_results, 1):
                    with st.expander(
                        f"📄 Chunk {i} - {result['metadata']['source_file']} (Page {result['metadata']['page']})"
                    ):
                        st.markdown(f"**Similarity Score:** {result.get('similarity_score', 'N/A'):.4f}")
                        st.markdown("**Content:**")
                        st.text(result['text'])
        
        with tab5:
            st.markdown("#### Audit Trail")
            
            if st.session_state.audit_logger:
                logger = st.session_state.audit_logger
                
                st.markdown(f"**Session ID:** `{logger.session_id}`")
                st.markdown(f"**Start Time:** {logger.session_start}")
                
                # Event summary
                summary_data = logger.get_trail_summary()
                st.json(summary_data)
                
                # Formatted trail
                with st.expander("View Detailed Trail"):
                    st.text(logger.get_formatted_trail())
        
        # Export options
        st.markdown("---")
        st.markdown('<div class="section-header">💾 Export</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Export to Excel
            if st.button("📥 Download Excel Report", use_container_width=True):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"corep_report_{timestamp}.xlsx"
                    output_path = Path("exports") / filename
                    output_path.parent.mkdir(exist_ok=True)
                    
                    path = mapper.export_to_excel(analysis, str(output_path))
                    
                    if st.session_state.audit_logger:
                        st.session_state.audit_logger.log_export(str(path), "xlsx")
                    
                    with open(path, "rb") as f:
                        st.download_button(
                            label="📥 Download File",
                            data=f,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    st.success(f"✅ Excel file created: {filename}")
                    
                except Exception as e:
                    st.error(f"Error creating Excel file: {str(e)}")
        
        with col2:
            # Export audit log
            if st.button("📄 Download Audit Log", use_container_width=True):
                if st.session_state.audit_logger:
                    try:
                        log_path = st.session_state.audit_logger.save_log()
                        
                        with open(log_path, "r") as f:
                            st.download_button(
                                label="📥 Download Log",
                                data=f.read(),
                                file_name=Path(log_path).name,
                                mime="application/json",
                                use_container_width=True
                            )
                        
                        st.success(f"✅ Audit log saved")
                        
                    except Exception as e:
                        st.error(f"Error saving audit log: {str(e)}")
        
        with col3:
            # Export JSON
            if st.button("📋 Download Analysis JSON", use_container_width=True):
                json_str = json.dumps(analysis, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )


if __name__ == "__main__":
    main()
