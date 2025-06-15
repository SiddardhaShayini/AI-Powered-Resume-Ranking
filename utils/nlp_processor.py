import spacy
import re
from collections import Counter
import streamlit as st

class NLPProcessor:
    """Handles all NLP operations using SpaCy"""
    
    def __init__(self):
        """Initialize SpaCy model with error handling"""
        try:
            # Try to load the English model
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            try:
                # Try alternative loading method for cloud deployment
                import en_core_web_sm
                self.nlp = en_core_web_sm.load()
            except ImportError:
                st.warning("SpaCy English model not available. Using basic text processing fallback.")
                # Use a basic fallback
                self.nlp = None
        
        # Define common technical skills and keywords
        self.technical_skills = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 'kotlin', 'swift'],
            'web_dev': ['html', 'css', 'react', 'angular', 'vue', 'nodejs', 'django', 'flask', 'express'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'ml_ai': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'figma', 'photoshop', 'illustrator']
        }
        
        # Soft skills keywords
        self.soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
            'creative', 'adaptable', 'organized', 'detail oriented', 'time management',
            'project management', 'collaboration', 'mentoring', 'training'
        ]
        
        # Experience indicators
        self.experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*yrs?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*years?\s*(?:in|with|of)',
            r'(\d+)\+?\s*year\s*(?:in|with|of)',
        ]
    
    def preprocess_text(self, text):
        """
        Preprocess text using SpaCy pipeline
        
        Args:
            text (str): Raw text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        if not text or not self.nlp:
            return text.lower() if text else ""
        
        try:
            # Process text with SpaCy
            doc = self.nlp(text)
            
            # Extract meaningful tokens
            tokens = []
            for token in doc:
                # Skip stop words, punctuation, and whitespace
                if (not token.is_stop and 
                    not token.is_punct and 
                    not token.is_space and 
                    len(token.text) > 2):
                    
                    # Use lemmatized form
                    tokens.append(token.lemma_.lower())
            
            return " ".join(tokens)
            
        except Exception as e:
            st.warning(f"NLP processing failed, using basic preprocessing: {str(e)}")
            return self._basic_preprocess(text)
    
    def _basic_preprocess(self, text):
        """Basic text preprocessing fallback"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_skills(self, text):
        """
        Extract technical and soft skills from text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Dictionary containing technical and soft skills
        """
        text_lower = text.lower()
        found_skills = {
            'technical': [],
            'soft': []
        }
        
        # Extract technical skills
        for category, skills in self.technical_skills.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    found_skills['technical'].append(skill)
        
        # Extract soft skills
        for skill in self.soft_skills:
            if skill.lower() in text_lower:
                found_skills['soft'].append(skill)
        
        return found_skills
    
    def extract_experience_years(self, text):
        """
        Extract years of experience from text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            int: Maximum years of experience found
        """
        max_years = 0
        text_lower = text.lower()
        
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                try:
                    years = int(match)
                    max_years = max(max_years, years)
                except ValueError:
                    continue
        
        return max_years
    
    def extract_entities(self, text):
        """
        Extract named entities from text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Dictionary of entities by type
        """
        if not self.nlp:
            return {}
        
        try:
            doc = self.nlp(text)
            entities = {}
            
            for ent in doc.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(ent.text)
            
            return entities
            
        except Exception as e:
            st.warning(f"Entity extraction failed: {str(e)}")
            return {}
    
    def get_keywords(self, text, top_n=20):
        """
        Extract important keywords from text
        
        Args:
            text (str): Text to analyze
            top_n (int): Number of top keywords to return
            
        Returns:
            list: List of important keywords
        """
        if not self.nlp:
            # Fallback to simple word frequency
            words = re.findall(r'\b\w{3,}\b', text.lower())
            word_freq = Counter(words)
            return [word for word, freq in word_freq.most_common(top_n)]
        
        try:
            doc = self.nlp(text)
            
            # Extract important words (nouns, adjectives, proper nouns)
            keywords = []
            for token in doc:
                if (token.pos_ in ['NOUN', 'ADJ', 'PROPN'] and
                    not token.is_stop and
                    not token.is_punct and
                    len(token.text) > 2):
                    keywords.append(token.lemma_.lower())
            
            # Count frequency and return top keywords
            keyword_freq = Counter(keywords)
            return [word for word, freq in keyword_freq.most_common(top_n)]
            
        except Exception as e:
            st.warning(f"Keyword extraction failed: {str(e)}")
            return []
    
    def calculate_text_similarity(self, text1, text2):
        """
        Calculate semantic similarity between two texts using SpaCy
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Similarity score between 0 and 1
        """
        if not self.nlp or not text1 or not text2:
            return 0.0
        
        try:
            doc1 = self.nlp(text1)
            doc2 = self.nlp(text2)
            
            return doc1.similarity(doc2)
            
        except Exception as e:
            st.warning(f"Similarity calculation failed: {str(e)}")
            return 0.0
