from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
import pandas as pd

class ReportGenerator:
    """Generates comprehensive HR reports in PDF format"""
    
    def __init__(self):
        """Initialize report generator with styles"""
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=12,
            textColor=colors.darkblue
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
    
    def generate_report(self, results, job_description, results_df):
        """
        Generate comprehensive HR report
        
        Args:
            results (list): List of ranking results
            job_description (str): Original job description
            results_df (DataFrame): Results dataframe for display
            
        Returns:
            BytesIO: PDF report as bytes buffer
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build report content
        story = []
        
        # Title page
        story.extend(self._create_title_page())
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(results))
        
        # Job description analysis
        story.extend(self._create_job_analysis(job_description))
        
        # Detailed rankings
        story.extend(self._create_detailed_rankings(results))
        
        # Recommendations
        story.extend(self._create_recommendations(results))
        
        # Methodology
        story.extend(self._create_methodology())
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def _create_title_page(self):
        """Create title page content"""
        story = []
        
        # Title
        title = Paragraph("AI-Powered Resume Ranking Report", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        subtitle = Paragraph("Comprehensive Candidate Analysis and Rankings", self.heading_style)
        story.append(subtitle)
        story.append(Spacer(1, 1*inch))
        
        # Report info
        current_date = datetime.now().strftime("%B %d, %Y")
        info_data = [
            ["Report Generated:", current_date],
            ["Analysis Type:", "AI-Powered NLP Resume Ranking"],
            ["Technology Stack:", "SpaCy, Scikit-learn, TF-IDF Vectorization"],
            ["Scoring Method:", "Multi-factor Weighted Algorithm"]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 1*inch))
        
        # Disclaimer
        disclaimer = Paragraph(
            "<b>Disclaimer:</b> This report is generated using AI-powered natural language processing techniques. "
            "While the analysis provides valuable insights, it should be used as a supplementary tool alongside "
            "human judgment in the recruitment process.",
            self.body_style
        )
        story.append(disclaimer)
        
        return story
    
    def _create_executive_summary(self, results):
        """Create executive summary section"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.heading_style))
        
        # Summary statistics
        total_candidates = len(results)
        avg_score = sum(r['scores']['overall_score'] for r in results) / total_candidates if results else 0
        top_score = max(r['scores']['overall_score'] for r in results) if results else 0
        
        summary_text = f"""
        This report analyzes {total_candidates} candidate resumes against the provided job description using 
        advanced Natural Language Processing techniques. The analysis employs a multi-factor scoring algorithm 
        that evaluates keyword matching, technical skills alignment, experience levels, and semantic similarity.
        
        <b>Key Findings:</b><br/>
        • Total Candidates Analyzed: {total_candidates}<br/>
        • Average Overall Score: {avg_score:.1f}%<br/>
        • Highest Score Achieved: {top_score:.1f}%<br/>
        • Recommended Candidates: {len([r for r in results if r['scores']['overall_score'] >= 70])} (Score ≥ 70%)
        """
        
        story.append(Paragraph(summary_text, self.body_style))
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _create_job_analysis(self, job_description):
        """Create job description analysis section"""
        story = []
        
        story.append(Paragraph("Job Description Analysis", self.heading_style))
        
        # Truncate job description for display
        truncated_desc = job_description[:500] + "..." if len(job_description) > 500 else job_description
        
        analysis_text = f"""
        <b>Job Description Overview:</b><br/>
        {truncated_desc}
        
        <b>Analysis Methodology:</b><br/>
        The job description was processed using SpaCy NLP pipeline to extract key requirements, 
        technical skills, and experience indicators. These elements form the basis for candidate 
        evaluation and scoring.
        """
        
        story.append(Paragraph(analysis_text, self.body_style))
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _create_detailed_rankings(self, results):
        """Create detailed rankings section"""
        story = []
        
        story.append(Paragraph("Detailed Candidate Rankings", self.heading_style))
        
        # Create rankings table
        table_data = [["Rank", "Candidate", "Overall Score", "Keyword Match", "Skills Match", "Experience", "TF-IDF Similarity"]]
        
        for i, result in enumerate(results):
            scores = result['scores']
            table_data.append([
                str(i + 1),
                result['filename'].replace('.pdf', ''),
                f"{scores['overall_score']:.1f}%",
                f"{scores['keyword_score']:.1f}%",
                f"{scores['skills_score']:.1f}%",
                f"{scores['experience_score']:.1f}%",
                f"{scores['tfidf_similarity']:.1f}%"
            ])
        
        # Create table
        rankings_table = Table(table_data, colWidths=[0.6*inch, 1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        rankings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(rankings_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Top candidates details
        if results:
            story.append(Paragraph("Top Candidate Analysis", self.heading_style))
            
            top_candidate = results[0]
            top_analysis = f"""
            <b>Highest Ranked Candidate: {top_candidate['filename'].replace('.pdf', '')}</b><br/>
            Overall Score: {top_candidate['scores']['overall_score']:.1f}%<br/><br/>
            
            <b>Strengths:</b><br/>
            • Keyword Alignment: {top_candidate['scores']['keyword_score']:.1f}% match with job requirements<br/>
            • Technical Skills: {top_candidate['scores']['skills_score']:.1f}% alignment with required skills<br/>
            • Experience Level: {top_candidate['scores']['experience_score']:.1f}% match with experience requirements<br/>
            • Semantic Similarity: {top_candidate['scores']['tfidf_similarity']:.1f}% contextual relevance<br/>
            """
            
            story.append(Paragraph(top_analysis, self.body_style))
        
        return story
    
    def _create_recommendations(self, results):
        """Create recommendations section"""
        story = []
        
        story.append(Paragraph("Hiring Recommendations", self.heading_style))
        
        # Categorize candidates
        excellent = [r for r in results if r['scores']['overall_score'] >= 80]
        good = [r for r in results if 65 <= r['scores']['overall_score'] < 80]
        moderate = [r for r in results if 50 <= r['scores']['overall_score'] < 65]
        low = [r for r in results if r['scores']['overall_score'] < 50]
        
        recommendations = f"""
        <b>Candidate Categories:</b><br/><br/>
        
        <b>🎯 Excellent Candidates ({len(excellent)} candidates):</b><br/>
        Scores ≥ 80%. Strong alignment with job requirements. Recommended for immediate interview.<br/>
        {', '.join([r['filename'].replace('.pdf', '') for r in excellent[:3]])}{'...' if len(excellent) > 3 else ''}<br/><br/>
        
        <b>✅ Good Candidates ({len(good)} candidates):</b><br/>
        Scores 65-79%. Good potential with minor gaps. Recommended for phone screening.<br/>
        {', '.join([r['filename'].replace('.pdf', '') for r in good[:3]])}{'...' if len(good) > 3 else ''}<br/><br/>
        
        <b>⚠️ Moderate Candidates ({len(moderate)} candidates):</b><br/>
        Scores 50-64%. May require additional evaluation or skills development.<br/>
        {', '.join([r['filename'].replace('.pdf', '') for r in moderate[:3]])}{'...' if len(moderate) > 3 else ''}<br/><br/>
        
        <b>❌ Low Match Candidates ({len(low)} candidates):</b><br/>
        Scores < 50%. Limited alignment with current requirements.<br/>
        {', '.join([r['filename'].replace('.pdf', '') for r in low[:3]])}{'...' if len(low) > 3 else ''}
        """
        
        story.append(Paragraph(recommendations, self.body_style))
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _create_methodology(self):
        """Create methodology section"""
        story = []
        
        story.append(Paragraph("Scoring Methodology", self.heading_style))
        
        methodology_text = """
        <b>Algorithm Overview:</b><br/>
        The AI-powered ranking system uses a weighted multi-factor approach combining natural language 
        processing and machine learning techniques.<br/><br/>
        
        <b>Scoring Components:</b><br/>
        • <b>Keyword Matching (30%):</b> Direct keyword alignment between resume and job description<br/>
        • <b>Skills Assessment (25%):</b> Technical and soft skills matching using pattern recognition<br/>
        • <b>Experience Evaluation (20%):</b> Years of experience extraction and comparison<br/>
        • <b>Semantic Similarity (25%):</b> TF-IDF vectorization with cosine similarity for contextual matching<br/><br/>
        
        <b>Technology Stack:</b><br/>
        • SpaCy: Advanced NLP processing, tokenization, and lemmatization<br/>
        • Scikit-learn: TF-IDF vectorization and cosine similarity calculations<br/>
        • Regular Expressions: Pattern matching for skills and experience extraction<br/>
        • Machine Learning: Automated feature extraction and similarity scoring<br/><br/>
        
        <b>Quality Assurance:</b><br/>
        • Multi-method PDF text extraction with fallback mechanisms<br/>
        • Robust error handling and data validation<br/>
        • Normalized scoring across all evaluation criteria<br/>
        • Transparent scoring breakdown for audit purposes
        """
        
        story.append(Paragraph(methodology_text, self.body_style))
        
        return story
