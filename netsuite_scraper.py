#!/usr/bin/env python3
"""
NetSuite Records Browser Scraper

This script scrapes the NetSuite Records Browser and extracts field information
for all record types.
"""

import json
import time
import os
from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup

# Debug mode: saves HTML files for inspection
DEBUG = True


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


def extract_record_data(page: Page, url: str, record_index: int = 0):
    """Extract record name, internal ID, and fields from a record page."""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(1)  # Small delay to ensure page is fully loaded

        html = page.content()
        soup = BeautifulSoup(html, 'lxml')

        # Debug: Save HTML for first few records
        if DEBUG and record_index < 3:
            os.makedirs('debug', exist_ok=True)
            filename = f"debug/record_{record_index}_{os.path.basename(url)}"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  [DEBUG] Saved HTML to {filename}")

        # Extract record name from the main heading (h1)
        record_name_elem = soup.find('h1')
        if not record_name_elem:
            print(f"  ✗ No h1 heading found")
            if DEBUG and record_index < 3:
                # Show what headings we found
                all_headings = soup.find_all(['h1', 'h2', 'h3'])
                print(f"    Found headings: {[h.get_text(strip=True)[:50] for h in all_headings[:5]]}")
            return None
        record_name = record_name_elem.get_text(strip=True)
        print(f"  Record name: {record_name}")

        # Extract record internal ID from the URL (most reliable)
        record_internal_id = url.split('/')[-1].replace('.html', '')
        print(f"  Record internal ID: {record_internal_id}")

        # Find the Fields table
        # Try multiple heading levels and text patterns
        fields_heading = None
        for heading_tag in ['h2', 'h3', 'h4', 'h5']:
            fields_heading = soup.find(heading_tag, string=lambda x: x and 'Fields' in str(x))
            if fields_heading:
                print(f"  Found 'Fields' heading as <{heading_tag}>")
                break

        if not fields_heading:
            print(f"  ✗ No 'Fields' heading found")
            if DEBUG and record_index < 3:
                # Show what headings we found
                all_h2 = soup.find_all(['h2', 'h3', 'h4'])
                print(f"    Found h2/h3/h4: {[h.get_text(strip=True) for h in all_h2[:10]]}")
            return None

        # Find the table after the Fields heading
        table = fields_heading.find_next('table')
        if not table:
            print(f"  ✗ No table found after 'Fields' heading")
            return None

        # Parse table rows
        fields = []
        rows = table.find_all('tr')
        print(f"  Found table with {len(rows)} rows (including header)")

        # Debug: print header row
        if DEBUG and record_index < 3 and len(rows) > 0:
            header_cells = rows[0].find_all(['th', 'td'])
            print(f"    Table headers: {[cell.get_text(strip=True) for cell in header_cells]}")

        for row in rows[1:]:  # Skip header row
            field_data = parse_field_row(row)
            if field_data:
                fields.append(field_data)

        print(f"  ✓ Extracted {len(fields)} fields")

        return {
            "recordName": record_name,
            "recordInternalId": record_internal_id,
            "fields": fields
        }

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        if DEBUG:
            import traceback
            traceback.print_exc()
        return None


def get_record_links(page: Page, start_url: str):
    """Extract all record type links from the left navigation menu."""
    print(f"Loading page: {start_url}")
    page.goto(start_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)  # Wait for page to fully load

    html = page.content()
    soup = BeautifulSoup(html, 'lxml')

    # Debug: Save HTML
    if DEBUG:
        os.makedirs('debug', exist_ok=True)
        with open('debug/page_source.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✓ Saved page HTML to debug/page_source.html")

    # Try multiple strategies to find navigation links
    record_links = set()

    # Strategy 1: Look for all links with '/record/' in href
    print("\n[Strategy 1] Searching for all links with '/record/' in href...")
    all_links = soup.find_all('a', href=True)
    print(f"  Found {len(all_links)} total links on page")

    for link in all_links:
        href = link.get('href', '')
        link_text = link.get_text(strip=True)

        # Check if it's a record link
        if '/record/' in href and href.endswith('.html'):
            # Make absolute URL
            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                base_url = '/'.join(start_url.split('/')[:3])
                full_url = base_url + href
            else:
                base_url = '/'.join(start_url.split('/')[:-1])
                full_url = base_url + '/' + href

            record_links.add(full_url)
            if DEBUG:
                print(f"    Found: {link_text[:50]} -> {os.path.basename(full_url)}")

    print(f"  Strategy 1 found: {len(record_links)} record links")

    # Strategy 2: Try to find navigation by common class/id patterns
    print("\n[Strategy 2] Looking for navigation container...")
    nav_selectors = [
        ('nav', None),
        ('aside', None),
        ('div', {'id': lambda x: x and 'nav' in x.lower()}),
        ('div', {'class': lambda x: x and any(term in str(x).lower() for term in ['nav', 'sidebar', 'menu', 'toc', 'tree'])}),
        ('ul', {'class': lambda x: x and any(term in str(x).lower() for term in ['nav', 'menu', 'tree'])}),
    ]

    for tag, attrs in nav_selectors:
        if attrs:
            containers = soup.find_all(tag, attrs)
        else:
            containers = soup.find_all(tag)

        if containers:
            print(f"  Found {len(containers)} <{tag}> elements matching pattern")
            for container in containers:
                nav_links = container.find_all('a', href=True)
                for link in nav_links:
                    href = link.get('href', '')
                    if href.endswith('.html') and '/record/' in href:
                        # Make absolute URL
                        if href.startswith('http'):
                            full_url = href
                        elif href.startswith('/'):
                            base_url = '/'.join(start_url.split('/')[:3])
                            full_url = base_url + href
                        else:
                            base_url = '/'.join(start_url.split('/')[:-1])
                            full_url = base_url + '/' + href
                        record_links.add(full_url)

    print(f"  Strategy 2 total found: {len(record_links)} record links")

    # Convert to sorted list
    record_links_list = sorted(list(record_links))

    # Debug: Save found links
    if DEBUG:
        with open('debug/found_links.txt', 'w', encoding='utf-8') as f:
            for link in record_links_list:
                f.write(f"{link}\n")
        print(f"\n✓ Saved {len(record_links_list)} links to debug/found_links.txt")

    return record_links_list


def main():
    """Main scraper function."""
    start_url = "https://system.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2025_2/script/record/amortizationtemplate.html"

    print("="*80)
    print("NetSuite Records Browser Scraper")
    print("="*80)
    print(f"Debug mode: {DEBUG}")
    print(f"Starting URL: {start_url}\n")

    with sync_playwright() as p:
        # Launch browser in headful mode for visibility
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Get all record links
        print("="*80)
        print("STEP 1: Extracting record links from navigation")
        print("="*80)
        record_links = get_record_links(page, start_url)

        if not record_links:
            print("\n⚠ ERROR: No record links found!")
            print("Check debug/page_source.html to see the page structure.")
            browser.close()
            return

        print(f"\n✓ Found {len(record_links)} record links")

        # Process each record
        print("\n" + "="*80)
        print(f"STEP 2: Processing {len(record_links)} record pages")
        print("="*80)
        results = []

        for i, url in enumerate(record_links):
            print(f"\n[{i+1}/{len(record_links)}] {os.path.basename(url)}")
            record_data = extract_record_data(page, url, record_index=i)
            if record_data:
                results.append(record_data)

            # Small delay between requests
            time.sleep(0.5)

        browser.close()

    # Output results as JSON
    print("\n" + "="*80)
    print("STEP 3: Saving results")
    print("="*80)

    output_file = "netsuite_records.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✓ Scraping complete!")
    print(f"✓ Successfully extracted: {len(results)} / {len(record_links)} records")
    print(f"✓ Results saved to: {output_file}")

    if DEBUG:
        print(f"✓ Debug files saved to: debug/")

    # Also print to stdout as requested
    print("\n" + "="*80)
    print("JSON OUTPUT")
    print("="*80)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
