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
- Handles authentication with manual login support

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
3. **You have 30 seconds to log in** if authentication is required
4. The scraper will then:
   - Extract all record type links from the left navigation
   - Visit each record page
   - Extract the Fields table data
5. Results will be saved to `netsuite_records.json`
6. The complete JSON output will also be printed to the console

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

- `start_url`: The starting page URL
- Authentication wait time: Change `time.sleep(30)` to adjust login wait time
- Request delays: Modify `time.sleep(0.5)` between page requests
- Headless mode: Set `headless=True` in `browser.launch()` (not recommended if auth is required)

## Troubleshooting

### Authentication Issues
- Ensure you log in within the 30-second window
- Increase the wait time if needed: change `time.sleep(30)` to a larger value

### Missing Fields
- Check if the page structure has changed
- Verify the Fields table exists on the record pages

### Connection Errors
- Ensure you have access to the NetSuite documentation
- Check your network connection
- Verify the URLs are correct

## Notes

- The scraper only follows links in the left navigation menu
- It does not crawl the entire site
- Small delays are included between requests to be respectful to the server
- The browser runs in non-headless mode by default to allow authentication

## License

MIT
