# Streamlit Cloud Deployment Guide

## Files for Streamlit Cloud Deployment

The following files have been created/updated to ensure proper deployment on Streamlit Cloud:

### 1. `.streamlit/config.toml`
Updated configuration for cloud deployment:
```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[theme]
base = "light"
```

### 2. `requirements_streamlit.txt`
Dependencies with SpaCy model for Streamlit Cloud:
```
streamlit
spacy
scikit-learn
pandas
numpy
plotly
reportlab
PyPDF2
pdfplumber
en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

### 3. `packages.txt`
System packages for Streamlit Cloud:
```
python3-dev
```

## Deployment Steps

1. **Upload Files to GitHub Repository**
   - Push all files to your GitHub repository
   - Ensure all files mentioned above are included

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Connect your GitHub account
   - Select your repository: `AI-Powered-Resume-Ranker`
   - Set main file path: `app.py`
   - Advanced settings:
     - Python version: 3.11
     - Requirements file: Use the pyproject.toml or requirements_streamlit.txt

3. **Common Issues and Solutions**

   **Issue: SpaCy model not found**
   - The app includes fallback mechanisms for SpaCy model loading
   - If deployment fails, try renaming `requirements_streamlit.txt` to `requirements.txt`

   **Issue: Import errors**
   - The application has robust error handling for missing dependencies
   - Check the logs for specific dependency issues

   **Issue: Memory limits**
   - Streamlit Cloud has memory limitations
   - The app is optimized for efficient memory usage

## Alternative Deployment Files

If the primary requirements don't work, try these alternatives:

### Alternative requirements.txt:
```
streamlit==1.45.1
spacy>=3.8.0
scikit-learn>=1.7.0
pandas>=2.3.0
numpy>=2.3.0
plotly>=6.1.0
reportlab>=4.4.0
PyPDF2>=3.0.0
pdfplumber>=0.11.0
```

### SpaCy model installation script (setup.sh):
```bash
#!/bin/bash
python -m spacy download en_core_web_sm
```

## Troubleshooting

1. **App won't start**: Check the Streamlit Cloud logs for specific error messages
2. **SpaCy errors**: The app includes fallback text processing if SpaCy fails to load
3. **PDF processing issues**: Multiple fallback methods are implemented for PDF text extraction
4. **Memory issues**: The app uses caching to minimize memory usage

## Testing the Deployment

Once deployed, test these features:
1. Upload sample PDF resumes
2. Use sample job descriptions
3. Generate rankings and reports
4. Check the analytics dashboard

The application includes comprehensive error handling to ensure it works even with limited resources or missing components.