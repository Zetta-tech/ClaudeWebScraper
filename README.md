# NetSuite Records Browser Web Scraper

A Python web scraper that extracts field information from the NetSuite Records Browser documentation.

## Features

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

Run the scraper:
```bash
python netsuite_scraper.py
```

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

You can modify the following in `netsuite_scraper.py`:

- `DEBUG = True`: Enable/disable debug mode (saves HTML and detailed logs)
- `start_url`: The starting page URL
- Request delays: Modify `time.sleep(0.5)` between page requests
- Headless mode: Set `headless=True` in `browser.launch()` to run without visible browser

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

- The scraper only follows links in the left navigation menu
- It does not crawl the entire site
- Small delays are included between requests to be respectful to the server
- The browser runs in non-headless mode by default for visibility
- Debug mode is enabled by default to help troubleshoot any issues
- The scraper uses multiple strategies to find navigation links
- Detailed progress information is printed to the console

## License

MIT
