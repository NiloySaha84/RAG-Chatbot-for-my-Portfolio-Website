# AI Brochure Generator

An intelligent brochure generation tool that scrapes website content and uses OpenAI's GPT models to automatically create professional marketing brochures.

## Features

- 🌐 **Web Scraping**: Automatically extracts content and links from any website
- 🤖 **AI-Powered**: Leverages OpenAI's GPT models to generate compelling brochure content
- 📝 **Jupyter Notebook Interface**: Interactive development environment for easy experimentation
- 🎨 **Customizable**: Flexible pipeline for tailoring brochure generation to your needs

## Prerequisites

- Python 3.11 or higher
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/brochure-generator.git
cd brochure-generator
```

2. Install dependencies using `uv` (recommended) or `pip`:

**Using uv:**
```bash
uv sync
```

**Using pip:**
```bash
pip install -e .
```

3. Set up environment variables:

Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

1. Open the Jupyter notebook:
```bash
jupyter notebook brochure_generator.ipynb
```

2. Run the cells to:
   - Scrape content from a target website
   - Extract relevant information and links
   - Generate a professional brochure using AI

### Basic Example

```python
from scraper import fetch_website_content, fetch_website_links
from openai import OpenAI

# Initialize OpenAI client
openai = OpenAI()

# Fetch website content
url = "https://example.com"
links = fetch_website_links(url)
content = fetch_website_content(url)

# Generate brochure using AI
# (See notebook for full implementation)
```

## Project Structure

```
.
├── brochure_generator.ipynb  # Main notebook with brochure generation pipeline
├── scraper.py                # Web scraping utilities
├── pyproject.toml            # Project dependencies and configuration
├── .env                      # Environment variables (create this)
└── README.md                 # This file
```

## How It Works

1. **Web Scraping**: The `scraper.py` module uses BeautifulSoup to extract clean text content and links from target websites
2. **Content Processing**: Extracts relevant information (limited to 2,000 characters for efficiency)
3. **AI Generation**: Uses OpenAI's GPT models to transform scraped content into professional brochure copy
4. **Output**: Generates formatted brochure content ready for use

## Key Dependencies

- `openai` - OpenAI API client
- `beautifulsoup4` - HTML parsing and web scraping
- `requests` - HTTP library for fetching web pages
- `python-dotenv` - Environment variable management
- `jupyter` - Interactive notebook environment
- `langchain` - LLM application framework (optional advanced features)

## Configuration

The project uses environment variables for configuration. Add these to your `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key (required)

## Model Selection

The project currently uses `gpt-5-nano` as the default model. You can modify this in the notebook:

```python
model = "gpt-4"  # or any other OpenAI model
```

## Limitations

- Web scraping is limited to 2,000 characters per page for API efficiency
- Requires an active OpenAI API key with available credits
- Some websites may block automated scraping

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with OpenAI's GPT models
- Web scraping powered by BeautifulSoup4


**Note**: Always respect website terms of service and robots.txt when scraping content. Ensure you have permission to scrape and use content from target websites.
