#!/usr/bin/env python3
"""
NetSuite Records Browser Scraper

This script scrapes the NetSuite Records Browser and extracts field information
for all record types.
"""

import json
import time
from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup


def parse_field_row(row):
    """Parse a single field row from the Fields table."""
    cells = row.find_all('td')
    if len(cells) < 6:
        return None

    return {
        "internalId": cells[0].get_text(strip=True),
        "type": cells[1].get_text(strip=True),
        "nlsapiSubmitField": cells[2].get_text(strip=True),
        "label": cells[3].get_text(strip=True),
        "required": cells[4].get_text(strip=True).lower() == 'true',
        "help": cells[5].get_text(strip=True)
    }


def extract_record_data(page: Page, url: str):
    """Extract record name, internal ID, and fields from a record page."""
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(1)  # Small delay to ensure page is fully loaded

        html = page.content()
        soup = BeautifulSoup(html, 'lxml')

        # Extract record name from the main heading (h1)
        record_name_elem = soup.find('h1')
        if not record_name_elem:
            print(f"Warning: No h1 found for {url}")
            return None
        record_name = record_name_elem.get_text(strip=True)

        # Extract record internal ID from the page
        # It's typically shown near the top, often in a format like "Internal ID: xyz"
        # or can be extracted from the URL
        record_internal_id = url.split('/')[-1].replace('.html', '')

        # Alternative: Try to find it in the page content
        internal_id_elem = soup.find(string=lambda text: text and 'Internal ID:' in text)
        if internal_id_elem:
            # Extract the ID value after "Internal ID:"
            parent = internal_id_elem.find_parent()
            if parent:
                text = parent.get_text(strip=True)
                if 'Internal ID:' in text:
                    record_internal_id = text.split('Internal ID:')[-1].strip()

        # Find the Fields table
        fields_heading = soup.find(['h2', 'h3', 'h4'], string=lambda x: x and 'Fields' in x)
        if not fields_heading:
            print(f"Warning: No 'Fields' heading found for {record_name}")
            return None

        # Find the table after the Fields heading
        table = fields_heading.find_next('table')
        if not table:
            print(f"Warning: No table found after 'Fields' heading for {record_name}")
            return None

        # Parse table rows
        fields = []
        rows = table.find_all('tr')[1:]  # Skip header row

        for row in rows:
            field_data = parse_field_row(row)
            if field_data:
                fields.append(field_data)

        return {
            "recordName": record_name,
            "recordInternalId": record_internal_id,
            "fields": fields
        }

    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return None


def get_record_links(page: Page, start_url: str):
    """Extract all record type links from the left navigation menu."""
    page.goto(start_url, wait_until="networkidle", timeout=30000)
    time.sleep(2)  # Wait for page to fully load

    html = page.content()
    soup = BeautifulSoup(html, 'lxml')

    # Find the left navigation menu
    # Common patterns: nav, aside, div with class containing 'nav', 'sidebar', 'menu'
    nav_container = (
        soup.find('nav') or
        soup.find('aside') or
        soup.find('div', class_=lambda x: x and any(term in x.lower() for term in ['nav', 'sidebar', 'menu', 'toc']))
    )

    if not nav_container:
        # Try finding all links and filter for record links
        print("Navigation container not found, searching all links...")
        all_links = soup.find_all('a', href=True)
        record_links = []

        for link in all_links:
            href = link.get('href')
            # Filter for record links based on the pattern
            if href and '/record/' in href and href.endswith('.html'):
                # Make absolute URL
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    base_url = '/'.join(start_url.split('/')[:3])
                    full_url = base_url + href
                else:
                    base_url = '/'.join(start_url.split('/')[:-1])
                    full_url = base_url + '/' + href

                record_links.append(full_url)

        # Remove duplicates
        return list(set(record_links))

    # Extract links from navigation
    links = nav_container.find_all('a', href=True)
    record_links = []

    for link in links:
        href = link.get('href')
        if href and '.html' in href:
            # Make absolute URL
            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                base_url = '/'.join(start_url.split('/')[:3])
                full_url = base_url + href
            else:
                base_url = '/'.join(start_url.split('/')[:-1])
                full_url = base_url + '/' + href

            record_links.append(full_url)

    # Remove duplicates
    return list(set(record_links))


def main():
    """Main scraper function."""
    start_url = "https://system.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2025_2/script/record/amortizationtemplate.html"

    print("Starting NetSuite Records Browser scraper...")
    print("A browser window will open. Please log in if required.")
    print("The scraper will wait 30 seconds for you to authenticate.\n")

    with sync_playwright() as p:
        # Launch browser in headful mode to allow manual authentication
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to start page
        print(f"Navigating to: {start_url}")
        page.goto(start_url, timeout=60000)

        # Wait for user to authenticate
        print("\nPlease log in if required.")
        print("Waiting 30 seconds for authentication...")
        time.sleep(30)

        # Get all record links
        print("\nExtracting record links from navigation...")
        record_links = get_record_links(page, start_url)
        print(f"Found {len(record_links)} record links")

        # Process each record
        results = []
        for i, url in enumerate(record_links, 1):
            print(f"\nProcessing {i}/{len(record_links)}: {url}")
            record_data = extract_record_data(page, url)
            if record_data:
                results.append(record_data)
                print(f"  ✓ Extracted {len(record_data['fields'])} fields from '{record_data['recordName']}'")
            else:
                print(f"  ✗ Failed to extract data")

            # Small delay between requests
            time.sleep(0.5)

        browser.close()

    # Output results as JSON
    output_file = "netsuite_records.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Scraping complete!")
    print(f"✓ Extracted data for {len(results)} records")
    print(f"✓ Results saved to: {output_file}")

    # Also print to stdout as requested
    print("\n" + "="*80)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
