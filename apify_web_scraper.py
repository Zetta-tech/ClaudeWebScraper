#!/usr/bin/env python3
"""Utilities for running the Apify Web Scraper actor."""

import argparse
import json
import os
from typing import List, Dict, Any, Optional

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()


def get_apify_client() -> ApifyClient:
    """Return an authenticated Apify client using the APIFY_TOKEN env var."""

    token = os.getenv("APIFY_TOKEN")
    if not token:
        raise RuntimeError(
            "APIFY_TOKEN is not set. Copy .env.example to .env and provide your token."
        )
    return ApifyClient(token)


def run_apify_web_scraper(
    start_urls: List[str],
    max_requests: int = 25,
    pseudo_urls: Optional[List[str]] = None,
    proxy_country: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the Apify Web Scraper actor and return the run metadata and dataset items."""

    actor_id = os.getenv("APIFY_WEB_SCRAPER_ACTOR_ID", "apify/web-scraper")
    client = get_apify_client()
    actor_client = client.actor(actor_id)

    run_input: Dict[str, Any] = {
        "startUrls": [{"url": url} for url in start_urls],
        "maxRequestsPerCrawl": max_requests,
        "crawlerType": "playwright:chromium",
        "runMode": "PRODUCTION",
        "proxyConfiguration": {"useApifyProxy": True},
    }

    if pseudo_urls:
        run_input["pseudoUrls"] = [{"purl": purl} for purl in pseudo_urls]

    if proxy_country:
        run_input["proxyConfiguration"]["apifyProxyCountry"] = proxy_country

    run = actor_client.call(run_input=run_input)
    dataset_id = run.get("defaultDatasetId")

    items: List[Dict[str, Any]] = []
    if dataset_id:
        dataset_client = client.dataset(dataset_id)
        items = dataset_client.list_items(clean=True)["items"]

    return {"run": run, "items": items}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Apify Web Scraper actor with sensible defaults"
    )
    parser.add_argument(
        "--start-url",
        action="append",
        required=True,
        help="Starting URL(s) for the crawl. Pass multiple times for more URLs.",
    )
    parser.add_argument(
        "--max-requests",
        type=int,
        default=25,
        help="Limit the number of pages to crawl",
    )
    parser.add_argument(
        "--pseudo-url",
        action="append",
        help="Optional pseudo URLs to constrain link following",
    )
    parser.add_argument(
        "--proxy-country",
        help="Two-letter country code for the Apify proxy",
    )
    parser.add_argument(
        "--output",
        help="Path to save the dataset items as JSON",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    results = run_apify_web_scraper(
        start_urls=args.start_url,
        max_requests=args.max_requests,
        pseudo_urls=args.pseudo_url,
        proxy_country=args.proxy_country,
    )

    items = results["items"]
    print(
        json.dumps(
            {"runId": results["run"].get("id"), "itemCount": len(items)}, indent=2
        )
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(items)} items to {args.output}")


if __name__ == "__main__":
    main()
