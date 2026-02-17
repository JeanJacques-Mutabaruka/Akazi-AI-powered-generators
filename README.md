# 🚀 AKAZI Generator - Multi-Format Document Generator

**Automated document generation from JSON/YAML data with professional formatting**

Generate professional documents in multiple formats:
- 📝 **AKAZI Job Descriptions** (EN/FR)
- 👤 **AKAZI CV Format**
- 👔 **MC2I Dossier de Compétences**

---

## ✨ Features

- ✅ **Multi-format support**: JSON & YAML input
- ✅ **Batch processing**: Generate multiple documents at once
- ✅ **Auto-detection**: Automatic document type recognition
- ✅ **Performance tracking**: Built-in analytics & monitoring
- ✅ **Error handling**: Graceful error management with detailed logs
- ✅ **Progress indicators**: Real-time progress bars for batch operations
- ✅ **Interactive dashboard**: Performance metrics & statistics
- ✅ **Optimized caching**: Fast repeated operations

---

## 📋 Requirements

- Python 3.8+
- pip (Python package manager)
- 4GB RAM recommended for batch operations

---

## 🔧 Installation

### 1. Clone or Download Project

```bash
cd akazi-generator
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv_akazi
venv_akazi\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv_akazi
source venv_akazi/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
```

---

## 🚀 Quick Start

### Launch Application

```bash
streamlit run streamlit_app.py
```

The application will open automatically in your browser at: **http://localhost:8501**

### Basic Workflow

1. **Upload Files**: Upload one or more JSON/YAML files
2. **Auto-Detection**: System detects document type automatically
3. **Select Formats**: Choose output formats (multiple selections allowed)
4. **Generate**: Click "Generate" to create Word documents
5. **Download**: Download individual files or ZIP archive

---

## 📁 Project Structure

```
akazi-generator/
├── config/                      # Format configurations
│   ├── akazi_jobdesc_config.py  # Job description formatting
│   ├── akazi_cv_config.py       # CV AKAZI formatting
│   └── mc2i_cv_config.py        # MC2I formatting
│
├── generators/                  # Document generators
│   ├── base_generator.py        # Base generator class
│   ├── akazi_jobdesc_generator.py
│   ├── akazi_cv_generator.py
│   ├── mc2i_cv_generator.py
│   └── generator_factory.py     # Generator factory
│
├── schemas/                     # JSON validation schemas
│   ├── akazi_jobdesc_schema.json
│   ├── akazi_cv_schema.json
│   └── mc2i_cv_schema.json
│
├── utils/                       # Utility modules
│   ├── cache_manager.py         # Caching system
│   ├── logger.py                # Structured logging
│   ├── performance.py           # Performance tracking
│   ├── validator.py             # Document validation
│   └── file_handler.py          # File operations
│
├── pages/                       # Streamlit pages
│   ├── 1_📄_Générateur_Batch.py # Main generator page
│   ├── 2_📊_Dashboard.py         # Analytics dashboard
│   ├── 3_🔍_Logs_Erreurs.py     # Error logs viewer
│   └── 4_⚙️_Configuration.py    # Settings page
│
├── logs/                        # Application logs
│   ├── processing.log           # General logs
│   ├── errors.log               # Error logs only
│   └── performance.json         # Performance metrics
│
├── tests/                       # Unit tests
│   └── ...
│
├── streamlit_app.py             # Main application entry point
├── requirements.txt             # Python dependencies
├── .streamlit/config.toml       # Streamlit configuration
└── README.md                    # This file
```

---

## 📊 Supported Document Types

### 1. AKAZI Job Description (EN/FR)

**Input Structure:**
```json
{
  "mission_title": "Senior Developer",
  "budget": "USD 5,000 - 7,000 per month",
  "description": {
    "intro": "For our client...",
    "sections": [
      {
        "title": "Responsibilities",
        "content": ["Task 1", "Task 2"]
      }
    ]
  }
}
```

**Output:** Word document with AKAZI formatting (Century Gothic, colored sections)

---

### 2. AKAZI CV

**Input Structure:**
```json
{
  "personal_info": {
    "full_name": "Jean Baptiste",
    "title": "Senior Data Analyst"
  },
  "professional_summary": "Experienced professional...",
  "experiences": [...]
}
```

**Output:** Professional CV in AKAZI format

---

### 3. MC2I Dossier de Compétences

**Input Structure:**
```json
{
  "personal_info": {
    "full_name": "Benjamin Dupuy",
    "title": "Expert Analyse et Migration Data"
  },
  "summary": {
    "experience_summary": "...",
    "technical_skills": "...",
    "functional_skills": "...",
    "conclusion": "..."
  },
  "experiences": [...]
}
```

**Output:** MC2I competency dossier (Lato font, specific color scheme)

---

## 🎯 Usage Examples

### Example 1: Single File Generation

```python
# Upload: job_senior_dev.json
# Auto-detected as: akazi_jobdesc
# Select formats: ✅ AKAZI EN, ✅ AKAZI FR
# Output: 2 Word files
```

### Example 2: Batch Processing

```python
# Upload: 5 JSON files (3 job descriptions, 2 CVs)
# Auto-detection for each file
# Select multiple formats per file
# Generate all with progress tracking
# Download as ZIP archive
```

---

## 📈 Performance & Monitoring

### Built-in Analytics

- **Real-time metrics**: Success rate, processing time, memory usage
- **Dashboard**: Visual analytics with Plotly charts
- **Performance logs**: JSON-structured logs for analysis
- **Error tracking**: Detailed error logs with stack traces

### Typical Performance

- **Single document**: < 1 second
- **Batch (10 files)**: 5-10 seconds
- **Memory usage**: ~50-100 MB per document

---

## 🔍 Troubleshooting

### Common Issues

**Issue:** Port 8501 already in use
```bash
# Solution: Use different port
streamlit run streamlit_app.py --server.port 8502
```

**Issue:** Module not found
```bash
# Solution: Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

**Issue:** File upload fails
```bash
# Check: File size < 200MB
# Check: Valid JSON/YAML format
# Check: Matches schema structure
```

---

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. --cov-report=html tests/

# Run specific test file
pytest tests/test_validator.py -v
```

---

## 📚 Documentation

### JSON Schema References

- See `/schemas/` directory for complete schema definitions
- Each schema includes validation rules and examples
- Use `validator.py` module for programmatic validation

### Configuration Guide

- See `/config/` directory for format-specific settings
- Modify fonts, colors, spacing, margins
- Create custom format configurations

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -m 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open Pull Request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Credits

- **Streamlit**: Web framework
- **python-docx**: Word document generation
- **PyYAML**: YAML parsing
- **structlog**: Structured logging
- **Plotly**: Data visualization

---

## 📞 Support

- 📧 Email: support@akazi.io
- 🐛 Issues: GitHub Issues
- 📚 Documentation: See `/docs` directory

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Author**: Jean Jacques

Made with ❤️ for automated document generation
