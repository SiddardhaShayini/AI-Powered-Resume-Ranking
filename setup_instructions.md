# GitHub Repository & Deployment Instructions

## Streamlit Cloud Deployment Fix

The error you encountered on Streamlit Cloud has been resolved with the following updates:

### Updated Configuration Files:
- `.streamlit/config.toml` - Removed port-specific settings for cloud deployment
- `requirements_streamlit.txt` - Clean dependencies with SpaCy model URL
- `packages.txt` - System dependencies for cloud environment
- Enhanced error handling in `app.py` for robust cloud deployment

## Commands to Push Updated Code to GitHub

Run these commands in your local terminal to push the fixed version:

```bash
# Navigate to your project directory
cd path/to/your/project

# Add all updated files
git add .

# Commit the deployment fixes
git commit -m "Fix Streamlit Cloud deployment issues

- Updated .streamlit/config.toml for cloud compatibility
- Added requirements_streamlit.txt with proper SpaCy model URL
- Enhanced error handling for robust cloud deployment
- Added packages.txt for system dependencies
- Improved SpaCy model loading with fallback methods"

# Push to GitHub
git push origin main
```

## Streamlit Cloud Deployment Steps

After pushing the updated code to GitHub:

1. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Deploy the App**
   - Click "New app"
   - Select repository: `SiddardhaShayini/AI-Powered-Resume-Ranker`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy!"

3. **Deployment Settings** (if needed)
   - Python version: 3.11 (auto-detected)
   - Requirements: Will use pyproject.toml automatically
   - If issues occur, try renaming `requirements_streamlit.txt` to `requirements.txt`

## Key Fixes Applied

1. **Configuration Fix**: Removed hardcoded port settings that conflict with Streamlit Cloud
2. **Dependency Management**: Created cloud-compatible requirements with SpaCy model URL
3. **Error Handling**: Added robust initialization and processing error handling
4. **SpaCy Model Loading**: Implemented fallback methods for cloud environment

## Alternative Setup (if repository doesn't exist)

If you need to create the repository first:

```bash
# Create repository on GitHub first, then:
git init
git add .
git commit -m "Initial commit: AI-Powered Resume Ranking System"
git branch -M main
git remote add origin https://github.com/SiddardhaShayini/AI-Powered-Resume-Ranker.git
git push -u origin main
```

## Files Ready for Upload

The following files are prepared and ready for the repository:

### Core Application
- `app.py` - Main Streamlit application
- `utils/` - Core utility modules
  - `pdf_processor.py` - PDF text extraction
  - `nlp_processor.py` - NLP processing with SpaCy
  - `scoring_engine.py` - Resume scoring algorithms
  - `report_generator.py` - PDF report generation

### Sample Data
- `sample_data/job_descriptions.py` - Sample job descriptions
- `sample_data/sample_resumes.py` - Sample resume content

### Configuration
- `.streamlit/config.toml` - Streamlit server configuration
- `pyproject.toml` - Python dependencies and project metadata

### Documentation
- `README.md` - Comprehensive project documentation
- `AI_Resume_Ranker_Project_Report.pdf` - Generated project report
- `project_report.py` - Report generator script
- `setup_instructions.md` - This file with GitHub setup commands

### Project Files
- `LICENSE` - MIT License
- `.gitignore` - Git ignore configuration

## Project Structure Overview

```
AI-Powered-Resume-Ranker/
├── app.py                                  # Main application
├── utils/                                  # Core modules
│   ├── pdf_processor.py
│   ├── nlp_processor.py
│   ├── scoring_engine.py
│   └── report_generator.py
├── sample_data/                           # Test data
│   ├── job_descriptions.py
│   └── sample_resumes.py
├── .streamlit/config.toml                 # Configuration
├── README.md                              # Documentation
├── AI_Resume_Ranker_Project_Report.pdf    # Project report
├── project_report.py                      # Report generator
├── LICENSE                                # MIT License
└── .gitignore                            # Git ignore rules
```

## Dependencies to Install

After cloning the repository, users will need to install:

```bash
pip install streamlit spacy scikit-learn pandas numpy plotly reportlab PyPDF2 pdfplumber
python -m spacy download en_core_web_sm
```

## Running the Application

```bash
streamlit run app.py --server.port 5000
```

The application will be available at `http://localhost:5000`