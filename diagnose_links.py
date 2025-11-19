#!/usr/bin/env python3
"""
Diagnostic script to inspect the actual link structure on the NetSuite page
"""

import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

start_url = "https://system.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2025_2/script/record/amortizationtemplate.html"

print("="*80)
print("NetSuite Link Diagnostic Tool")
print("="*80)
print(f"URL: {start_url}\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    print("Loading page...")
    page.goto(start_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)

    html = page.content()
    soup = BeautifulSoup(html, 'lxml')

    # Find all links
    all_links = soup.find_all('a', href=True)
    print(f"\nFound {len(all_links)} total links on page\n")

    print("="*80)
    print("ALL LINKS:")
    print("="*80)
    for i, link in enumerate(all_links, 1):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        print(f"\n{i}. Text: {text[:60]}")
        print(f"   Href: {href}")
        print(f"   Has '/record/': {'/record/' in href}")
        print(f"   Ends with '.html': {href.endswith('.html')}")

    # Check for navigation elements
    print("\n" + "="*80)
    print("NAVIGATION ELEMENTS:")
    print("="*80)

    # Look for common navigation patterns
    nav_elements = soup.find_all('nav')
    print(f"\n<nav> elements: {len(nav_elements)}")

    aside_elements = soup.find_all('aside')
    print(f"<aside> elements: {len(aside_elements)}")

    # Look for divs/uls with navigation-related classes
    divs_with_nav = soup.find_all('div', class_=lambda x: x and any(term in str(x).lower() for term in ['nav', 'sidebar', 'menu', 'toc', 'tree']))
    print(f"<div> with nav-related classes: {len(divs_with_nav)}")
    if divs_with_nav:
        for div in divs_with_nav[:3]:
            classes = div.get('class', [])
            print(f"  - Classes: {classes}")

    uls_with_nav = soup.find_all('ul', class_=lambda x: x and any(term in str(x).lower() for term in ['nav', 'menu', 'tree']))
    print(f"<ul> with nav-related classes: {len(uls_with_nav)}")
    if uls_with_nav:
        for ul in uls_with_nav[:3]:
            classes = ul.get('class', [])
            links_in_ul = ul.find_all('a', href=True)
            print(f"  - Classes: {classes}, Links inside: {len(links_in_ul)}")
            for link in links_in_ul[:5]:
                print(f"    • {link.get_text(strip=True)[:40]} -> {link.get('href', '')[:60]}")

    # Look for iframes (NetSuite might use them)
    iframes = soup.find_all('iframe')
    print(f"\n<iframe> elements: {len(iframes)}")
    if iframes:
        print("\n⚠ WARNING: Page contains iframes!")
        print("The navigation might be inside an iframe, which requires special handling.\n")
        for i, iframe in enumerate(iframes, 1):
            src = iframe.get('src', '')
            iframe_id = iframe.get('id', '')
            iframe_name = iframe.get('name', '')
            print(f"{i}. iframe:")
            print(f"   src: {src}")
            print(f"   id: {iframe_id}")
            print(f"   name: {iframe_name}")

    browser.close()

print("\n" + "="*80)
print("Check debug/page_source.html for the full HTML structure")
print("="*80)
