import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import os
from utils.pdf_processor import PDFProcessor
from utils.nlp_processor import NLPProcessor
from utils.scoring_engine import ScoringEngine
from utils.report_generator import ReportGenerator
from sample_data.job_descriptions import SAMPLE_JOB_DESCRIPTIONS

# Page configuration
st.set_page_config(
    page_title="AI-Powered Resume Ranker",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize processors with error handling
@st.cache_resource
def initialize_processors():
    """Initialize and cache the NLP processor to avoid reloading models"""
    try:
        return {
            'pdf_processor': PDFProcessor(),
            'nlp_processor': NLPProcessor(),
            'scoring_engine': ScoringEngine(),
            'report_generator': ReportGenerator()
        }
    except Exception as e:
        st.error(f"Failed to initialize processors: {str(e)}")
        return None

# Try to initialize processors
try:
    processors = initialize_processors()
    if processors is None:
        st.stop()
except Exception as e:
    st.error(f"Critical error during startup: {str(e)}")
    st.stop()

def main():
    st.title("🎯 AI-Powered Resume Ranking System")
    st.markdown("**Rank resumes against job descriptions using advanced NLP techniques**")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Resume Ranking", "Analytics Dashboard", "About"]
        )
    
    if page == "Resume Ranking":
        resume_ranking_page()
    elif page == "Analytics Dashboard":
        analytics_dashboard()
    else:
        about_page()

def resume_ranking_page():
    st.header("📄 Resume Ranking")
    
    # Job Description Input
    st.subheader("1. Job Description")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Option to use sample job descriptions
        use_sample = st.checkbox("Use sample job description")
        
        if use_sample:
            selected_job = st.selectbox(
                "Select a sample job description:",
                list(SAMPLE_JOB_DESCRIPTIONS.keys())
            )
            job_description = SAMPLE_JOB_DESCRIPTIONS[selected_job]
            st.text_area("Job Description:", value=job_description, height=200, disabled=True)
        else:
            job_description = st.text_area(
                "Enter job description:",
                height=200,
                placeholder="Paste the job description here..."
            )
    
    with col2:
        st.info("💡 **Tips:**\n\n• Include key skills and requirements\n• Mention specific technologies\n• Add experience requirements\n• Include soft skills")
    
    # Resume Upload
    st.subheader("2. Upload Resumes")
    
    uploaded_files = st.file_uploader(
        "Choose PDF resume files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload multiple PDF resumes to rank against the job description"
    )
    
    # Processing and Results
    if st.button("🚀 Analyze Resumes", type="primary", disabled=not (job_description and uploaded_files)):
        if job_description and uploaded_files:
            with st.spinner("Processing resumes... This may take a moment."):
                results = process_resumes(job_description, uploaded_files)
                
            if results:
                display_results(results, job_description)
        else:
            st.warning("Please provide both job description and resume files.")

def process_resumes(job_description, uploaded_files):
    """Process uploaded resumes and return ranking results"""
    try:
        if not processors:
            st.error("System not properly initialized. Please refresh the page.")
            return None
            
        results = []
        
        # Process each resume
        for uploaded_file in uploaded_files:
            try:
                # Extract text from PDF
                resume_text = processors['pdf_processor'].extract_text(uploaded_file)
                
                if resume_text:
                    # Preprocess text
                    processed_resume = processors['nlp_processor'].preprocess_text(resume_text)
                    processed_job_desc = processors['nlp_processor'].preprocess_text(job_description)
                    
                    # Calculate scores
                    scores = processors['scoring_engine'].calculate_scores(
                        processed_resume, 
                        processed_job_desc,
                        resume_text,
                        job_description
                    )
                    
                    results.append({
                        'filename': uploaded_file.name,
                        'resume_text': resume_text,
                        'processed_text': processed_resume,
                        'scores': scores
                    })
                else:
                    st.warning(f"Could not extract text from {uploaded_file.name}")
                    
            except Exception as e:
                st.warning(f"Error processing {uploaded_file.name}: {str(e)}")
                continue
        
        # Sort by overall score
        results.sort(key=lambda x: x['scores']['overall_score'], reverse=True)
        return results
        
    except Exception as e:
        st.error(f"Error processing resumes: {str(e)}")
        return None

def display_results(results, job_description):
    """Display ranking results with visualizations and insights"""
    st.subheader("📊 Ranking Results")
    
    # Create results dataframe
    df_results = pd.DataFrame([
        {
            'Rank': i + 1,
            'Candidate': result['filename'].replace('.pdf', ''),
            'Overall Score': f"{result['scores']['overall_score']:.1f}%",
            'Keyword Match': f"{result['scores']['keyword_score']:.1f}%",
            'Skills Match': f"{result['scores']['skills_score']:.1f}%",
            'Experience Score': f"{result['scores']['experience_score']:.1f}%",
            'TF-IDF Similarity': f"{result['scores']['tfidf_similarity']:.1f}%"
        }
        for i, result in enumerate(results)
    ])
    
    # Display ranking table
    st.dataframe(
        df_results,
        use_container_width=True,
        hide_index=True
    )
    
    # Visualization
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall scores bar chart
        fig_bar = px.bar(
            x=[result['filename'].replace('.pdf', '') for result in results],
            y=[result['scores']['overall_score'] for result in results],
            title="Overall Scores Comparison",
            labels={'x': 'Candidates', 'y': 'Score (%)'},
            color=[result['scores']['overall_score'] for result in results],
            color_continuous_scale='Viridis'
        )
        fig_bar.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Radar chart for top candidate
        if results:
            top_candidate = results[0]
            scores = top_candidate['scores']
            
            categories = ['Keyword Match', 'Skills Match', 'Experience', 'TF-IDF Similarity']
            values = [
                scores['keyword_score'],
                scores['skills_score'], 
                scores['experience_score'],
                scores['tfidf_similarity']
            ]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=top_candidate['filename'].replace('.pdf', '')
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100])
                ),
                title=f"Top Candidate: {top_candidate['filename'].replace('.pdf', '')}"
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    
    # Detailed analysis for each candidate
    st.subheader("🔍 Detailed Analysis")
    
    for i, result in enumerate(results):
        with st.expander(f"#{i+1} - {result['filename'].replace('.pdf', '')} (Score: {result['scores']['overall_score']:.1f}%)"):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Key Insights:**")
                
                # Extract key insights
                insights = processors['scoring_engine'].get_insights(
                    result['processed_text'], 
                    job_description,
                    result['scores']
                )
                
                for insight in insights:
                    st.write(f"• {insight}")
                
                # Show matched keywords
                matched_keywords = processors['scoring_engine'].get_matched_keywords(
                    result['resume_text'], 
                    job_description
                )
                
                if matched_keywords:
                    st.write("**Matched Keywords:**")
                    keyword_badges = " ".join([f"`{kw}`" for kw in matched_keywords[:10]])
                    st.markdown(keyword_badges)
            
            with col2:
                st.write("**Score Breakdown:**")
                score_data = {
                    'Metric': ['Keyword Match', 'Skills Match', 'Experience', 'TF-IDF Similarity'],
                    'Score': [
                        result['scores']['keyword_score'],
                        result['scores']['skills_score'],
                        result['scores']['experience_score'],
                        result['scores']['tfidf_similarity']
                    ]
                }
                st.bar_chart(pd.DataFrame(score_data).set_index('Metric'))
    
    # Generate and download HR report
    st.subheader("📋 HR Report")
    
    if st.button("Generate HR Report", type="secondary"):
        with st.spinner("Generating comprehensive HR report..."):
            report_buffer = processors['report_generator'].generate_report(
                results, 
                job_description, 
                df_results
            )
            
            st.download_button(
                label="📥 Download HR Report (PDF)",
                data=report_buffer.getvalue(),
                file_name="resume_ranking_report.pdf",
                mime="application/pdf"
            )
            
            st.success("HR Report generated successfully!")

def analytics_dashboard():
    """Analytics dashboard showing system statistics and insights"""
    st.header("📈 Analytics Dashboard")
    
    # This would typically show historical data, but for demo purposes,
    # we'll show some sample analytics
    st.info("💡 This dashboard would show historical ranking data, trends, and system performance metrics in a production environment.")
    
    # Sample metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Resumes Processed", "1,247", "23")
    
    with col2:
        st.metric("Average Processing Time", "2.3s", "-0.2s")
    
    with col3:
        st.metric("Top Match Score", "94.5%", "2.1%")
    
    with col4:
        st.metric("System Accuracy", "87.2%", "1.5%")
    
    # Sample charts
    st.subheader("Processing Trends")
    
    # Generate sample data for visualization
    import numpy as np
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='W')
    sample_data = pd.DataFrame({
        'Date': dates,
        'Resumes Processed': np.random.randint(10, 50, len(dates)),
        'Average Score': np.random.uniform(60, 90, len(dates))
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_line = px.line(sample_data, x='Date', y='Resumes Processed', 
                          title='Weekly Resume Processing Volume')
        st.plotly_chart(fig_line, use_container_width=True)
    
    with col2:
        fig_scatter = px.scatter(sample_data, x='Date', y='Average Score',
                               title='Average Matching Scores Over Time')
        st.plotly_chart(fig_scatter, use_container_width=True)

def about_page():
    """About page with system information and methodology"""
    st.header("ℹ️ About the AI Resume Ranking System")
    
    st.markdown("""
    ### Overview
    This AI-powered resume ranking system uses advanced Natural Language Processing (NLP) techniques 
    to automatically score and rank candidate resumes against job descriptions.
    
    ### Key Features
    - **PDF Text Extraction**: Automatically extracts text from PDF resume files
    - **NLP Processing**: Uses SpaCy for advanced text preprocessing and analysis
    - **TF-IDF Vectorization**: Implements scikit-learn's TF-IDF for text similarity
    - **Multi-factor Scoring**: Considers keywords, skills, experience, and semantic similarity
    - **Interactive Interface**: User-friendly Streamlit web interface
    - **HR Reports**: Generates comprehensive downloadable reports
    
    ### Scoring Methodology
    The system uses a weighted scoring algorithm that considers:
    
    1. **Keyword Matching (30%)**: Direct matches with job description keywords
    2. **Skills Assessment (25%)**: Technical and soft skills alignment
    3. **Experience Evaluation (20%)**: Years of experience and relevant background
    4. **Semantic Similarity (25%)**: TF-IDF cosine similarity for contextual matching
    
    ### Technology Stack
    - **Frontend**: Streamlit for web interface
    - **NLP**: SpaCy for text processing and analysis
    - **ML**: Scikit-learn for TF-IDF vectorization and similarity calculations
    - **PDF Processing**: PyPDF2/pdfplumber for text extraction
    - **Visualization**: Plotly for interactive charts and graphs
    - **Reports**: ReportLab for PDF report generation
    
    ### Data Privacy
    - No resume data is stored permanently
    - All processing happens in memory during the session
    - No personal information is transmitted to external services
    """)
    
    with st.expander("📚 Technical Details"):
        st.markdown("""
        #### Text Preprocessing Pipeline
        1. PDF text extraction with error handling
        2. Text cleaning and normalization
        3. Tokenization using SpaCy
        4. Stop word removal and lemmatization
        5. Named entity recognition for skills extraction
        
        #### Scoring Algorithm
        ```python
        overall_score = (
            keyword_score * 0.30 +
            skills_score * 0.25 +
            experience_score * 0.20 +
            tfidf_similarity * 0.25
        )
        ```
        
        #### Performance Optimization
        - Cached model loading for faster processing
        - Batch processing for multiple resumes
        - Efficient vectorization using sparse matrices
        """)

if __name__ == "__main__":
    main()
