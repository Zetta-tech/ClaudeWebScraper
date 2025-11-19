# NetSuite Records Browser Web Scraper

A Python web scraper that extracts field information from the NetSuite Records Browser documentation. Now supports both native Playwright scraping and cloud-based scraping via Apify.

## Features

- **Two scraping modes:**
  - Native Playwright scraper for local development and debugging
  - Cloud-based Apify scraper for scalable, production scraping
- Scrapes all record types from the NetSuite Records Browser left navigation
- Extracts detailed field information including:
  - Internal ID
  - Type
  - nlapiSubmitField value
  - Label
  - Required status
  - Help text
- Outputs data as structured JSON
- Debug mode with detailed logging and HTML export
- Environment variable configuration for API keys

## Prerequisites

- Python 3.8 or higher
- Access to NetSuite documentation (requires authentication)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd ClaudeWebScraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

### Option 1: Native Playwright Scraper (Local)

Run the local scraper:
```bash
python netsuite_scraper.py
```

### Option 2: Apify Cloud Scraper (Recommended for Production)

1. Set up your Apify API token:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Apify API token
# Get your token from: https://console.apify.com/account/integrations
```

2. Install the additional dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Apify scraper:
```bash
python apify_scraper.py
```

The script will prompt you to select an example:
- **Option 1**: Basic scraper (demonstrates basic Apify usage)
- **Option 2**: NetSuite Records Browser scraper (production use case)

### What to expect:

1. A Chrome browser window will open
2. The script will navigate to the NetSuite Records Browser
3. The scraper will:
   - Extract all record type links from the left navigation
   - Visit each record page
   - Extract the Fields table data
   - Display detailed progress and debug information
4. Results will be saved to `netsuite_records.json`
5. The complete JSON output will also be printed to the console
6. Debug files (HTML snapshots, link lists) will be saved to `debug/` folder

## Output Format

The scraper generates a JSON array with the following structure:

```json
[
  {
    "recordName": "Amortization Template",
    "recordInternalId": "amortizationtemplate",
    "fields": [
      {
        "internalId": "acctcontra",
        "type": "select",
        "nlsapiSubmitField": "false",
        "label": "Contra Account",
        "required": false,
        "help": "Select the account that accumulates amortized balances..."
      }
    ]
  }
]
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Apify API Configuration
APIFY_API_TOKEN=your_apify_api_token_here
```

Get your Apify API token from: https://console.apify.com/account/integrations

### Native Scraper Configuration

You can modify the following in `netsuite_scraper.py`:

- `DEBUG = True`: Enable/disable debug mode (saves HTML and detailed logs)
- `start_url`: The starting page URL
- Request delays: Modify `time.sleep(0.5)` between page requests
- Headless mode: Set `headless=True` in `browser.launch()` to run without visible browser

### Apify Scraper Configuration

The `ApifyWebScraper` class accepts the following parameters:

- `start_urls`: List of URLs to scrape
- `page_function`: Custom JavaScript function to extract data
- `max_pages_per_crawl`: Maximum number of pages to scrape
- `max_crawling_depth`: How deep to crawl from start URLs
- `proxy_configuration`: Proxy settings (uses Apify proxy by default)

## Debugging

When debug mode is enabled (`DEBUG = True`), the scraper saves:

- `debug/page_source.html`: HTML of the starting page
- `debug/found_links.txt`: List of all discovered record links
- `debug/record_0_*.html`: HTML of first few record pages

Use these files to troubleshoot if the scraper isn't finding links or extracting data correctly.

## Troubleshooting

### No Links Found
- Check `debug/page_source.html` to see if the page loaded correctly
- Look for navigation menu structure in the HTML
- The scraper tries multiple strategies to find links

### No Data Extracted
- Check `debug/record_0_*.html` files to see the structure of record pages
- Look for the "Fields" heading and table structure
- Console output shows what headings and tables were found

### Connection Errors
- Ensure you have access to the NetSuite documentation
- Check your network connection
- Verify the URLs are correct

## Notes

### Native Scraper
- Only follows links in the left navigation menu
- Does not crawl the entire site
- Small delays are included between requests to be respectful to the server
- Browser runs in non-headless mode by default for visibility
- Debug mode is enabled by default to help troubleshoot any issues
- Uses multiple strategies to find navigation links
- Detailed progress information is printed to the console

### Apify Scraper
- Runs in the cloud on Apify's infrastructure
- Automatically handles proxies and browser management
- Better for large-scale scraping tasks
- Provides run history and monitoring via Apify Console
- Supports advanced features like scheduling and webhooks
- Results are stored in Apify datasets with retention policies

## Comparison: Native vs Apify

| Feature | Native Scraper | Apify Scraper |
|---------|---------------|---------------|
| Setup complexity | Low | Medium (requires API token) |
| Cost | Free | Paid (based on usage) |
| Scale | Limited by local resources | Highly scalable |
| Maintenance | Manual browser management | Automatic |
| Debugging | Easy (visible browser) | Via logs and screenshots |
| Best for | Development, small tasks | Production, large-scale |

## API Integration

The `apify_scraper.py` module provides a clean Python API:

```python
from apify_scraper import ApifyWebScraper

# Initialize
scraper = ApifyWebScraper()  # Reads APIFY_API_TOKEN from .env

# Simple scraping
results = scraper.scrape_urls(
    urls=["https://example.com"],
    max_pages_per_crawl=10
)

# Advanced scraping with custom extraction
results = scraper.scrape(
    start_urls=[{"url": "https://example.com"}],
    page_function="""
        async function pageFunction(context) {
            const { page } = context;
            const title = await page.title();
            return { title };
        }
    """,
    max_pages_per_crawl=100,
    max_crawling_depth=2
)
```

## License

MIT
