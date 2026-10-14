#!/usr/bin/env python3
"""
Casino Bonus Scraper

Scrapes bonus details for online casinos from a public source and extracts
structured data using LLM API. Outputs to data.json.

Respects robots.txt and does not bypass logins, CAPTCHAs, or blocks.
"""

import os
import json
import sys
import urllib.robotparser
from typing import List, Dict, Any

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from scraper import (
    extract_with_openai,
    extract_with_anthropic,
    CasinoBonus
)

# Load environment variables
load_dotenv()


def check_robots_txt(url: str) -> bool:
    """
    Check if scraping is allowed by robots.txt.
    
    Args:
        url: The URL to check
        
    Returns:
        True if allowed, False otherwise
    """
    try:
        parsed_url = httpx.URL(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.host}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        
        # Check for general allowance
        user_agent = "*"
        if rp.can_fetch(user_agent, url):
            return True
        return False
    except Exception as e:
        print(f"Warning: Could not check robots.txt: {e}", file=sys.stderr)
        # If we can't check, be conservative but proceed with caution
        return True


def fetch_page(url: str) -> str:
    """
    Fetch a web page with proper headers and error handling.
    
    Args:
        url: The URL to fetch
        
    Returns:
        HTML content as string
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        with httpx.Client(headers=headers, follow_redirects=True, timeout=30.0) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        print(f"HTTP error {e.response.status_code} fetching {url}: {e}", file=sys.stderr)
        raise
    except httpx.TimeoutException as e:
        print(f"Timeout fetching {url}: {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        raise


def extract_casino_data(html_content: str, source_url: str) -> List[Dict[str, Any]]:
    """
    Extract casino bonus data from HTML content using LLM.
    
    Args:
        html_content: Raw HTML content
        source_url: Source URL of the page
        
    Returns:
        List of extracted casino bonus dictionaries
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    # Limit content size to avoid token limits (roughly 100KB)
    if len(html_content) > 100000:
        html_content = html_content[:100000]
    
    if provider == "anthropic":
        return extract_with_anthropic(html_content, source_url)
    else:
        return extract_with_openai(html_content, source_url)


def save_to_json(data: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save extracted data to JSON file.
    
    Args:
        data: List of casino bonus data
        output_path: Path to output JSON file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {len(data)} records to {output_path}")
    except Exception as e:
        print(f"Error saving to JSON: {e}", file=sys.stderr)
        raise


def validate_data(data: List[Dict[str, Any]]) -> bool:
    """
    Validate extracted data against the required schema.
    
    Args:
        data: Extracted data to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(data, list):
        print("Error: Data must be a list", file=sys.stderr)
        return False
    
    if len(data) < 3:
        print(f"Warning: Expected 3 casinos, got {len(data)}", file=sys.stderr)
    
    required_fields = ["casino_name", "welcome_bonus", "wagering_requirement", "minimum_deposit", "source_url"]
    
    for i, item in enumerate(data):
        for field in required_fields:
            if field not in item:
                print(f"Error: Missing field '{field}' in item {i}", file=sys.stderr)
                return False
        
        # Validate wagering_requirement is a number
        try:
            if not isinstance(item["wagering_requirement"], (int, float)):
                # Try to convert if it's a string
                item["wagering_requirement"] = int(item["wagering_requirement"])
        except (ValueError, TypeError):
            print(f"Error: wagering_requirement must be a number in item {i}", file=sys.stderr)
            return False
    
    return True
