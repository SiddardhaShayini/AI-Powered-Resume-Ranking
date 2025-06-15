import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from collections import Counter

class ScoringEngine:
    """Handles resume scoring and ranking logic"""
    
    def __init__(self):
        """Initialize the scoring engine with weights and parameters"""
        # Scoring weights (should sum to 1.0)
        self.weights = {
            'keyword_score': 0.30,
            'skills_score': 0.25,
            'experience_score': 0.20,
            'tfidf_similarity': 0.25
        }
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        # Common technical skills for matching
        self.tech_skills_patterns = [
            r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\bc\+\+\b', r'\bc#\b',
            r'\bruby\b', r'\bphp\b', r'\bgo\b', r'\trust\b', r'\bkotlin\b',
            r'\bhtml\b', r'\bcss\b', r'\breact\b', r'\bangular\b', r'\bvue\b',
            r'\bsql\b', r'\bmysql\b', r'\bpostgresql\b', r'\bmongodb\b',
            r'\baws\b', r'\bazure\b', r'\bgcp\b', r'\bdocker\b', r'\bkubernetes\b',
            r'\bmachine learning\b', r'\bdeep learning\b', r'\btensorflow\b', r'\bpytorch\b'
        ]
    
    def calculate_scores(self, resume_text, job_desc_text, original_resume, original_job_desc):
        """
        Calculate comprehensive scores for a resume against job description
        
        Args:
            resume_text (str): Preprocessed resume text
            job_desc_text (str): Preprocessed job description text
            original_resume (str): Original resume text
            original_job_desc (str): Original job description text
            
        Returns:
            dict: Dictionary containing all calculated scores
        """
        scores = {}
        
        # 1. Keyword matching score
        scores['keyword_score'] = self._calculate_keyword_score(original_resume, original_job_desc)
        
        # 2. Skills matching score
        scores['skills_score'] = self._calculate_skills_score(original_resume, original_job_desc)
        
        # 3. Experience score
        scores['experience_score'] = self._calculate_experience_score(original_resume, original_job_desc)
        
        # 4. TF-IDF similarity score
        scores['tfidf_similarity'] = self._calculate_tfidf_similarity(resume_text, job_desc_text)
        
        # 5. Calculate overall weighted score
        scores['overall_score'] = self._calculate_overall_score(scores)
        
        return scores
    
    def _calculate_keyword_score(self, resume_text, job_desc_text):
        """Calculate keyword matching score"""
        try:
            # Extract keywords from job description
            job_keywords = self._extract_keywords(job_desc_text.lower())
            
            # Count matches in resume
            resume_lower = resume_text.lower()
            matches = 0
            total_keywords = len(job_keywords)
            
            for keyword in job_keywords:
                if keyword in resume_lower:
                    matches += 1
            
            return (matches / total_keywords * 100) if total_keywords > 0 else 0
            
        except Exception:
            return 0
    
    def _calculate_skills_score(self, resume_text, job_desc_text):
        """Calculate technical skills matching score"""
        try:
            # Extract technical skills from both texts
            job_skills = self._extract_tech_skills(job_desc_text.lower())
            resume_skills = self._extract_tech_skills(resume_text.lower())
            
            if not job_skills:
                return 50  # Neutral score if no skills specified
            
            # Calculate intersection
            matched_skills = job_skills.intersection(resume_skills)
            score = (len(matched_skills) / len(job_skills)) * 100
            
            return min(score, 100)  # Cap at 100%
            
        except Exception:
            return 0
    
    def _calculate_experience_score(self, resume_text, job_desc_text):
        """Calculate experience-based score"""
        try:
            # Extract required experience from job description
            required_years = self._extract_years_experience(job_desc_text)
            
            # Extract candidate experience from resume
            candidate_years = self._extract_years_experience(resume_text)
            
            if required_years == 0:
                return 75  # Neutral score if no experience specified
            
            if candidate_years == 0:
                return 30  # Low score if no experience found
            
            # Calculate score based on experience ratio
            ratio = candidate_years / required_years
            
            if ratio >= 1.0:
                return 100  # Meets or exceeds requirements
            elif ratio >= 0.7:
                return 80   # Close to requirements
            elif ratio >= 0.5:
                return 60   # Somewhat below requirements
            else:
                return 40   # Significantly below requirements
                
        except Exception:
            return 50
    
    def _calculate_tfidf_similarity(self, resume_text, job_desc_text):
        """Calculate TF-IDF cosine similarity"""
        try:
            if not resume_text or not job_desc_text:
                return 0
            
            # Fit TF-IDF on both texts
            corpus = [resume_text, job_desc_text]
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity * 100  # Convert to percentage
            
        except Exception:
            return 0
    
    def _calculate_overall_score(self, scores):
        """Calculate weighted overall score"""
        try:
            overall = 0
            for score_type, weight in self.weights.items():
                overall += scores.get(score_type, 0) * weight
            
            return round(overall, 1)
            
        except Exception:
            return 0
    
    def _extract_keywords(self, text):
        """Extract important keywords from text"""
        # Remove common stop words and extract meaningful words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        
        # Filter out very common words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'as', 'an', 'are', 'was', 'were', 'been', 'be', 'have',
            'has', 'had', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
            'must', 'shall', 'this', 'that', 'these', 'those', 'we', 'you', 'they'
        }
        
        keywords = [word for word in words if word.lower() not in stop_words and len(word) > 3]
        
        # Return most frequent keywords
        word_freq = Counter(keywords)
        return [word for word, freq in word_freq.most_common(20)]
    
    def _extract_tech_skills(self, text):
        """Extract technical skills using regex patterns"""
        skills = set()
        
        for pattern in self.tech_skills_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update([match.lower() for match in matches])
        
        return skills
    
    def _extract_years_experience(self, text):
        """Extract years of experience from text"""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*yrs?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*years?\s*(?:in|with)',
            r'(\d+)\+?\s*year\s*(?:in|with)'
        ]
        
        max_years = 0
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    years = int(match)
                    max_years = max(max_years, years)
                except ValueError:
                    continue
        
        return max_years
    
    def get_matched_keywords(self, resume_text, job_desc_text):
        """Get list of keywords that matched between resume and job description"""
        try:
            job_keywords = set(self._extract_keywords(job_desc_text.lower()))
            resume_words = set(self._extract_keywords(resume_text.lower()))
            
            return list(job_keywords.intersection(resume_words))
            
        except Exception:
            return []
    
    def get_insights(self, resume_text, job_desc_text, scores):
        """Generate insights based on scoring results"""
        insights = []
        
        # Overall performance insight
        overall_score = scores.get('overall_score', 0)
        if overall_score >= 80:
            insights.append("🎯 Excellent match for this position")
        elif overall_score >= 65:
            insights.append("✅ Good candidate with strong potential")
        elif overall_score >= 50:
            insights.append("⚠️ Moderate match, may need additional evaluation")
        else:
            insights.append("❌ Limited alignment with job requirements")
        
        # Keyword insights
        keyword_score = scores.get('keyword_score', 0)
        if keyword_score >= 70:
            insights.append("Strong keyword alignment with job description")
        elif keyword_score < 40:
            insights.append("Low keyword match - resume may need optimization")
        
        # Skills insights
        skills_score = scores.get('skills_score', 0)
        if skills_score >= 75:
            insights.append("Excellent technical skills match")
        elif skills_score < 50:
            insights.append("Gap in required technical skills")
        
        # Experience insights
        exp_score = scores.get('experience_score', 0)
        if exp_score >= 80:
            insights.append("Meets or exceeds experience requirements")
        elif exp_score < 60:
            insights.append("May have less experience than preferred")
        
        return insights
