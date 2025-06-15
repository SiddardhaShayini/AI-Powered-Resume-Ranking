import PyPDF2
import pdfplumber
import streamlit as st
from io import BytesIO
import re

class PDFProcessor:
    """Handles PDF text extraction with multiple fallback methods"""
    
    def __init__(self):
        self.extraction_methods = [
            self._extract_with_pdfplumber,
            self._extract_with_pypdf2
        ]
    
    def extract_text(self, uploaded_file):
        """
        Extract text from uploaded PDF file using multiple methods
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            str: Extracted text content
        """
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Try different extraction methods
            for method in self.extraction_methods:
                try:
                    text = method(uploaded_file)
                    if text and len(text.strip()) > 100:  # Minimum text threshold
                        return self._clean_text(text)
                    uploaded_file.seek(0)  # Reset for next method
                except Exception as e:
                    st.warning(f"Extraction method failed: {str(e)}")
                    uploaded_file.seek(0)
                    continue
            
            raise Exception("All extraction methods failed")
            
        except Exception as e:
            st.error(f"Failed to extract text from {uploaded_file.name}: {str(e)}")
            return None
    
    def _extract_with_pdfplumber(self, file_obj):
        """Extract text using pdfplumber (preferred method)"""
        text = ""
        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    
    def _extract_with_pypdf2(self, file_obj):
        """Extract text using PyPDF2 (fallback method)"""
        text = ""
        pdf_reader = PyPDF2.PdfReader(file_obj)
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        
        return text
    
    def _clean_text(self, text):
        """
        Clean and normalize extracted text
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep alphanumeric and basic punctuation
        text = re.sub(r'[^\w\s\-.,;:()\[\]/@#&*+=<>|{}~`\'"!?%$]', ' ', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n+', '\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def get_file_info(self, uploaded_file):
        """
        Get basic information about the uploaded PDF
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            dict: File information
        """
        try:
            uploaded_file.seek(0)
            
            # Try to get PDF info
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    page_count = len(pdf.pages)
                    metadata = pdf.metadata or {}
                
                uploaded_file.seek(0)
                
                return {
                    'filename': uploaded_file.name,
                    'size_mb': round(uploaded_file.size / (1024 * 1024), 2),
                    'page_count': page_count,
                    'title': metadata.get('Title', 'Unknown'),
                    'author': metadata.get('Author', 'Unknown')
                }
            except:
                # Fallback to basic info
                return {
                    'filename': uploaded_file.name,
                    'size_mb': round(uploaded_file.size / (1024 * 1024), 2),
                    'page_count': 'Unknown',
                    'title': 'Unknown',
                    'author': 'Unknown'
                }
                
        except Exception as e:
            st.error(f"Failed to get file info: {str(e)}")
            return None
