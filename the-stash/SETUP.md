# The Stash - Setup Guide

## Overview

The Stash is a fully functional cannabis news aggregation blog that automatically generates posts at 4:20 AM and 4:20 PM daily. It aggregates content from multiple RSS feeds and generates AI-written blog posts.

## ✅ Project Status

The project is **complete and fully functional** with the following features:

- ✅ RSS feed aggregation from multiple cannabis news sources
- ✅ AI content generation (OpenAI, Ollama, or fallback)
- ✅ Static site generation with beautiful styling
- ✅ Automated scheduling (4:20 AM/PM)
- ✅ RSS feed and sitemap generation
- ✅ GitHub Pages deployment ready
- ✅ Content deduplication and categorization
- ✅ Comprehensive error handling

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+ (tested with Python 3.13)
- Virtual environment (recommended)

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd the-stash

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Test the Installation

```bash
# Run the test suite
python3 test_project.py
```

### 4. Generate Your First Post

```bash
# Generate a post without AI (fallback mode)
PYTHONPATH=src python3 -m stash.main publish --no-ai

# Or with Ollama (if you have it installed)
PYTHONPATH=src python3 -m stash.main publish --provider ollama --model "llama3.2:3b"

# Or with OpenAI (requires API key)
export OPENAI_API_KEY="your-api-key-here"
PYTHONPATH=src python3 -m stash.main publish --provider openai
```

### 5. View the Generated Site

```bash
# Serve the generated site locally
python3 -m http.server --directory site 8080
```

Then visit `http://localhost:8080` in your browser.

## 🔧 Configuration

### Environment Variables

Set these environment variables to customize the behavior:

```bash
# Site configuration
export BASE_URL="https://yourdomain.com"  # For RSS feeds and sitemap

# AI Generation
export GEN_PROVIDER="ollama"              # "ollama", "openai", or "none"
export GEN_MODEL="llama3.2:3b"           # Model name for provider
export OPENAI_API_KEY="your-key"         # OpenAI API key
export OLLAMA_BASE_URL="http://localhost:11434"  # Ollama server URL

# Optional: OpenAI model override
export OPENAI_MODEL="gpt-4o-mini"
```

### Customizing Feed Sources

Edit `src/stash/config.py` to modify:
- RSS feed URLs
- Number of items per source
- Maximum total items
- Site metadata

## 🤖 AI Providers

### 1. OpenAI (Recommended for best quality)

```bash
export OPENAI_API_KEY="your-api-key"
PYTHONPATH=src python3 -m stash.main publish --provider openai
```

### 2. Ollama (Local, free)

```bash
# Install Ollama: https://ollama.com
ollama pull llama3.2:3b
PYTHONPATH=src python3 -m stash.main publish --provider ollama --model "llama3.2:3b"
```

### 3. Fallback (No AI required)

```bash
PYTHONPATH=src python3 -m stash.main publish --no-ai
```

## ⏰ Automated Scheduling

### Option 1: Built-in Scheduler

```bash
# Run the built-in scheduler (4:20 AM/PM)
PYTHONPATH=src python3 run_scheduler.py
```

### Option 2: Cron (Recommended for servers)

```bash
# Edit crontab
crontab -e

# Add these lines (adjust paths):
20 4 * * *  cd /path/to/the-stash && PYTHONPATH=src .venv/bin/python -m stash.main publish >> /path/to/the-stash/cron.log 2>&1
20 16 * * * cd /path/to/the-stash && PYTHONPATH=src .venv/bin/python -m stash.main publish >> /path/to/the-stash/cron.log 2>&1
```

## 🌐 Deployment

### GitHub Pages

1. Push your code to GitHub
2. Set repository variables in Settings → Secrets and variables → Actions:
   - `BASE_URL`: `https://yourusername.github.io/your-repo-name`
   - `OPENAI_API_KEY`: Your OpenAI API key (optional)
3. The GitHub Action will automatically build and deploy on:
   - Every push to main branch
   - Scheduled at 4:20 AM and 4:20 PM UTC

### Other Static Hosting

The `site/` directory contains the complete static site. Upload it to any static hosting service:
- Netlify
- Vercel
- AWS S3
- Any web server

## 📁 Project Structure

```
the-stash/
├── src/stash/           # Main application code
│   ├── main.py         # CLI entry point
│   ├── config.py       # Configuration
│   ├── aggregator.py   # RSS feed processing
│   ├── generator.py    # AI content generation
│   ├── builder.py      # Static site generation
│   ├── scheduler.py    # Automated scheduling
│   ├── store.py        # Content storage
│   └── feeds.py        # RSS/sitemap generation
├── templates/          # HTML templates
├── public/            # Static assets (CSS)
├── site/              # Generated static site
├── content/           # Stored content and metadata
├── requirements.txt   # Python dependencies
├── run_scheduler.py   # Scheduler entry point
└── test_project.py    # Test suite
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python3 test_project.py
```

This tests:
- ✅ All module imports
- ✅ Configuration loading
- ✅ RSS feed aggregation
- ✅ Content generation
- ✅ Template rendering
- ✅ Scheduler setup
- ✅ File and directory structure

## 🔍 Troubleshooting

### Common Issues

1. **"No module named 'stash'"**
   - Make sure you're running with `PYTHONPATH=src`
   - Ensure you're in the correct directory

2. **Ollama connection refused**
   - Install Ollama: https://ollama.com
   - Start the Ollama service
   - Or use `--no-ai` for fallback mode

3. **OpenAI API errors**
   - Check your API key is set correctly
   - Ensure you have sufficient credits

4. **Feed fetching errors**
   - Some feeds may be temporarily unavailable
   - The aggregator handles failures gracefully
   - Check the logs for specific errors

### Logs

The application provides detailed logging. Look for:
- Feed fetching status
- Content generation results
- File writing operations
- Error messages

## 🎨 Customization

### Styling

Edit `public/css/styles.css` to customize the appearance. The site uses:
- CSS custom properties for easy theming
- Google Fonts (Shrikhand, Cabin)
- Gradient backgrounds and modern styling

### Templates

Modify templates in the `templates/` directory:
- `base.html` - Main layout
- `index.html` - Homepage
- `post.html` - Individual posts
- `about.html` - About page

### Content Sources

Add or modify RSS feeds in `src/stash/config.py`:
```python
feed_urls: List[str] = [
    "https://your-feed-url.com/feed/",
    # Add more feeds here
]
```

## 📊 Monitoring

The application creates several files for monitoring:
- `content/history.json` - Post history
- `content/seen_urls.json` - Deduplication cache
- `content/posts/` - Individual post metadata

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python3 test_project.py`
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use and modify as needed.

---

**The Stash** - A mellow stash of cannabis news and strains ✌️