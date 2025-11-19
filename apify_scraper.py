#!/usr/bin/env python3
"""
Apify Web Scraper Integration

This module provides integration with the Apify Web Scraper actor for flexible
web scraping tasks. It uses the Apify API to run the web-scraper actor.
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from apify_client import ApifyClient

# Load environment variables from .env file
load_dotenv()


class ApifyWebScraper:
    """
    A wrapper class for the Apify Web Scraper actor.

    This class simplifies interaction with the Apify Web Scraper actor,
    handling authentication and configuration automatically.
    """

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the Apify Web Scraper client.

        Args:
            api_token: Apify API token. If not provided, reads from APIFY_API_TOKEN env var.

        Raises:
            ValueError: If no API token is provided or found in environment.
        """
        self.api_token = api_token or os.getenv('APIFY_API_TOKEN')

        if not self.api_token:
            raise ValueError(
                "Apify API token is required. "
                "Set APIFY_API_TOKEN environment variable or pass api_token parameter."
            )

        # Initialize Apify client
        self.client = ApifyClient(self.api_token)

    def scrape(
        self,
        start_urls: List[Dict[str, str]],
        page_function: Optional[str] = None,
        max_pages_per_crawl: int = 10,
        max_crawling_depth: int = 0,
        proxy_configuration: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Run the Apify Web Scraper with the specified configuration.

        Args:
            start_urls: List of URLs to scrape. Format: [{"url": "https://example.com"}]
            page_function: JavaScript function to execute on each page for data extraction.
                          If None, returns default page data.
            max_pages_per_crawl: Maximum number of pages to scrape (default: 10)
            max_crawling_depth: Depth of crawling (0 = only start URLs, default: 0)
            proxy_configuration: Proxy settings for the scraper
            **kwargs: Additional parameters to pass to the Web Scraper actor

        Returns:
            List of scraped data dictionaries
        """
        # Build run input configuration
        run_input = {
            "startUrls": start_urls,
            "maxPagesPerCrawl": max_pages_per_crawl,
            "maxCrawlingDepth": max_crawling_depth,
        }

        # Add page function if provided
        if page_function:
            run_input["pageFunction"] = page_function

        # Add proxy configuration if provided
        if proxy_configuration:
            run_input["proxyConfiguration"] = proxy_configuration
        else:
            # Use automatic proxy by default for better reliability
            run_input["proxyConfiguration"] = {"useApifyProxy": True}

        # Add any additional parameters
        run_input.update(kwargs)

        print("Starting Apify Web Scraper...")
        print(f"Start URLs: {[url['url'] for url in start_urls]}")
        print(f"Max pages: {max_pages_per_crawl}")

        # Run the Web Scraper actor
        run = self.client.actor("apify/web-scraper").call(run_input=run_input)

        print(f"✓ Scraper run completed: {run['id']}")
        print(f"  Status: {run['status']}")

        # Fetch results from the dataset
        results = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)

        print(f"✓ Retrieved {len(results)} items")

        return results

    def scrape_urls(
        self,
        urls: List[str],
        page_function: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Convenience method to scrape a list of URLs.

        Args:
            urls: List of URL strings to scrape
            page_function: JavaScript function for data extraction
            **kwargs: Additional parameters

        Returns:
            List of scraped data dictionaries
        """
        start_urls = [{"url": url} for url in urls]
        return self.scrape(start_urls, page_function=page_function, **kwargs)


def example_netsuite_scraper():
    """
    Example: Scrape NetSuite documentation using Apify.

    This demonstrates how to use the Apify Web Scraper to extract
    field information from NetSuite Records Browser pages.
    """
    # Initialize scraper
    scraper = ApifyWebScraper()

    # Define the URLs to scrape
    urls = [
        "https://system.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2025_2/script/record/amortizationtemplate.html"
    ]

    # Define page function to extract field data
    # This JavaScript function runs in the browser context
    page_function = """
    async function pageFunction(context) {
        const { page, request } = context;

        // Get page title
        const title = await page.title();

        // Extract record name from h1
        const recordName = await page.$eval('h1', el => el.textContent.trim()).catch(() => null);

        // Extract record internal ID from URL
        const url = request.url;
        const recordInternalId = url.split('/').pop().replace('.html', '');

        // Find the Fields table
        const fields = await page.$$eval('table tr', rows => {
            const data = [];
            // Skip header row
            for (let i = 1; i < rows.length; i++) {
                const cells = rows[i].querySelectorAll('td');
                if (cells.length >= 6) {
                    data.push({
                        internalId: cells[0].textContent.trim(),
                        type: cells[1].textContent.trim(),
                        nlsapiSubmitField: cells[2].textContent.trim(),
                        label: cells[3].textContent.trim(),
                        required: cells[4].textContent.trim().toLowerCase() === 'true',
                        help: cells[5].textContent.trim()
                    });
                }
            }
            return data;
        }).catch(() => []);

        return {
            url: request.url,
            title: title,
            recordName: recordName,
            recordInternalId: recordInternalId,
            fields: fields,
            timestamp: new Date().toISOString()
        };
    }
    """

    # Run the scraper
    results = scraper.scrape_urls(
        urls,
        page_function=page_function,
        max_pages_per_crawl=5,
        max_crawling_depth=0
    )

    # Save results
    output_file = "apify_netsuite_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Results saved to: {output_file}")
    return results


def example_basic_scraper():
    """
    Example: Basic web scraping with Apify.

    This demonstrates a simple scraping task without custom page functions.
    """
    scraper = ApifyWebScraper()

    # Scrape some example URLs
    urls = [
        "https://example.com"
    ]

    results = scraper.scrape_urls(
        urls,
        max_pages_per_crawl=1,
        max_crawling_depth=0
    )

    print(f"\n✓ Scraped {len(results)} pages")
    print(json.dumps(results, indent=2))

    return results


if __name__ == "__main__":
    """
    Main function demonstrating different scraping examples.
    """
    print("="*80)
    print("Apify Web Scraper Examples")
    print("="*80)
    print()

    # Check if API token is configured
    if not os.getenv('APIFY_API_TOKEN'):
        print("ERROR: APIFY_API_TOKEN environment variable is not set!")
        print()
        print("Please:")
        print("1. Copy .env.example to .env")
        print("2. Add your Apify API token to the .env file")
        print("3. Get your token from: https://console.apify.com/account/integrations")
        exit(1)

    print("Select an example to run:")
    print("1. Basic scraper (example.com)")
    print("2. NetSuite Records Browser scraper")
    print()

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        print("\nRunning basic scraper example...")
        example_basic_scraper()
    elif choice == "2":
        print("\nRunning NetSuite scraper example...")
        example_netsuite_scraper()
    else:
        print("Invalid choice. Please run again and select 1 or 2.")
