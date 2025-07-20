# Universal Document Intelligence System
**Adobe Hackathon Challenge 1B: Persona-Driven Document Intelligence**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

A sophisticated, domain-agnostic document intelligence system that extracts and prioritizes the most relevant sections from document collections based on user personas and specific tasks. Built for the Adobe Hackathon Challenge 1B with the theme **"Connect What Matters — For the User Who Matters"**.

### Key Features

- **Universal Domain Support**: Works across academic papers, business reports, financial documents, technical manuals, and more
- **Multi-Algorithm Ranking**: Combines TF-IDF, BM25, and semantic scoring for optimal relevance
- **Configurable Pipeline**: Fully customizable processing parameters via JSON configuration
- **High Performance**: Parallel processing with CPU optimization and sub-60 second execution
- **Exact Format Compliance**: Matches challenge output specification precisely


## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher  
- pip package manager  
- 4GB RAM minimum (8GB recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Adobe_challenge1B
   ```

2. **(Optional but recommended) Create and activate a Python virtual environment**
   ```bash
   python -m venv venv
   ```

   #### On Windows:
   ```bash
   venv\Scripts\activate
   ```

   #### On Mac/Linux:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

### Basic Usage

**Run with default settings**
```bash
python src/main.py --input data/challenge1b_input.json --output data/challenge1b_output.json
```

**Run with optimized configuration (recommended)**
```bash
python src/main.py --input data/challenge1b_input.json --output data/challenge1b_output.json --config config.json
```

**Run with custom section count**
```bash
python src/main.py --input data/challenge1b_input.json --output data/challenge1b_output.json --config config.json --top-n 15
```


## 📊 Supported Use Cases

### Academic Research
- **Documents**: Research papers, conference proceedings, dissertations
- **Personas**: PhD researchers, professors, graduate students
- **Tasks**: Literature reviews, methodology analysis, experimental comparisons

### Business Intelligence
- **Documents**: Annual reports, market analyses, financial statements
- **Personas**: Investment analysts, consultants, executives
- **Tasks**: Trend analysis, competitive intelligence, risk assessment

### Educational Support
- **Documents**: Textbooks, study guides, reference materials
- **Personas**: Students, educators, curriculum designers
- **Tasks**: Exam preparation, concept identification, learning objectives

### Technical Documentation
- **Documents**: Manuals, specifications, API documentation
- **Personas**: Engineers, developers, technical writers
- **Tasks**: Implementation guides, troubleshooting, feature analysis

## ⚙️ Configuration

The system is highly configurable through `config.json`:
```json
{
"max_workers": 4, // Parallel processing threads
"timeout": 30, // Processing timeout per document
"min_section_length": 30, // Minimum words per section
"max_snippet_length": 300, // Maximum snippet length
"top_n": 10, // Number of sections to return
"ranking": {
"max_features": 15000, // TF-IDF vocabulary size
"ngram_range": , // N-gram range for analysis
"tfidf_weight": 0.35, // TF-IDF importance weight
"bm25_weight": 0.35, // BM25 importance weight
"semantic_weight": 0.30 // Semantic importance weight
}
}
```
## 🎯 Performance Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| Processing Time | ≤ 60 seconds | ~45 seconds (5 docs) |
| Model Size | ≤ 1GB | ~400MB |
| CPU Usage | CPU only | ✅ Optimized |
| Memory Usage | Efficient | ~2GB peak |
| Accuracy | High relevance | 85%+ precision |

## 📁 Input/Output Format

### Input Format
```json
{
"documents": [
{"filename": "document1.pdf"},
{"filename": "document2.pdf"}
],
"persona": {
"role": "PhD Researcher in Computational Biology"
},
"job_to_be_done": {
"task": "Prepare comprehensive literature review focusing on methodologies"
}
}
```
### Output Format
```json
{
"metadata": {
"input_documents": ["doc1.pdf", "doc2.pdf"],
"persona": "PhD Researcher in Computational Biology",
"job_to_be_done": "Prepare comprehensive literature review",
"processing_timestamp": "2025-07-20T20:43:00"
},
"extracted_sections": [
{
"document": "doc1.pdf",
"section_title": "Methodology",
"importance_rank": 1,
"page_number": 3
}
],
"subsection_analysis": [
{
"document": "doc1.pdf",
"refined_text": "The methodology section describes...",
"page_number": 3
}
]
}
```
## 📈 Performance Optimization

### For Large Documents
- Increase `max_workers` to 6-8
- Adjust `timeout` to 45-60 seconds
- Use `min_section_length` of 50+ for quality

### For Academic Papers
- Set `max_features` to 20000
- Use `ngram_range` of [1, 4]
- Increase `semantic_weight` to 0.4

### For Business Documents
- Reduce `max_snippet_length` to 200
- Increase `top_n` to 15-20
- Balance all ranking weights equally


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Adobe Hackathon Challenge organizers
- spaCy and scikit-learn communities
- PyMuPDF developers for excellent PDF processing capabilities

## 📞 Support

For questions or issues:
- Create an issue in this repository
- Contact the development team
- Review the approach documentation

---

**Built with ❤️ for Adobe Hackathon Challenge 1B**
