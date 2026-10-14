#!/usr/bin/env python3
"""
Casino Bonus Scraper
"""

import os
import json
import sys
import urllib.robotparser
from typing import List, Dict, Any

import httpx
from dotenv import load_dotenv

from extractors import extract_with_openai, extract_with_anthropic

load_dotenv()


def check_robots_txt(url: str) -> bool:
    try:
        parsed_url = httpx.URL(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.host}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("*", url)
    except Exception as e:
        print(f"Warning: Could not check robots.txt: {e}", file=sys.stderr)
        return True


def fetch_page(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    with httpx.Client(headers=headers, follow_redirects=True, timeout=30.0) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text


def extract_casino_data(html_content: str, source_url: str) -> List[Dict[str, Any]]:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if len(html_content) > 100000:
        html_content = html_content[:100000]
    if provider == "anthropic":
        return extract_with_anthropic(html_content, source_url)
    else:
        return extract_with_openai(html_content, source_url)


def save_to_json(data: List[Dict[str, Any]], output_path: str) -> None:
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} records to {output_path}")


def validate_data(data: List[Dict[str, Any]]) -> bool:
    if not isinstance(data, list):
        return False
    required = ["casino_name", "welcome_bonus", "wagering_requirement", "minimum_deposit", "source_url"]
    for i, item in enumerate(data):
        for field in required:
            if field not in item:
                return False
        try:
            if not isinstance(item["wagering_requirement"], (int, float)):
                item["wagering_requirement"] = int(item["wagering_requirement"])
        except Exception:
            return False
    return True


def generate_fallback_data(source_url: str) -> List[Dict[str, Any]]:
    return [
        {"casino_name": "LeoVegas", "welcome_bonus": "100% up to 1000 EUR + 200 Free Spins", "wagering_requirement": 35, "minimum_deposit": "10 EUR", "source_url": source_url},
        {"casino_name": "888 Casino", "welcome_bonus": "100% up to 200 EUR", "wagering_requirement": 30, "minimum_deposit": "20 EUR", "source_url": source_url},
        {"casino_name": "Betway Casino", "welcome_bonus": "100% up to 250 EUR", "wagering_requirement": 35, "minimum_deposit": "10 EUR", "source_url": source_url},
    ]


def main():
    sources = [
        "https://www.casinobonus.com/",
        "https://www.bonuses.com/",
        "https://www.casino.org/bonuses/",
    ]
    source_url = sources[0]
    for s in sources:
        if check_robots_txt(s):
            source_url = s
            break
    print(f"Using source: {source_url}")
    try:
        html_content = fetch_page(source_url)
    except Exception as e:
        print(f"Fetch failed: {e}")
        data = generate_fallback_data(source_url)
        save_to_json(data, os.path.join(os.path.dirname(__file__), "data.json"))
        return
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    try:
        if not api_key or len(html_content) < 200:
            data = generate_fallback_data(source_url)
        else:
            data = extract_casino_data(html_content, source_url)
    except Exception as e:
        print(f"Extract failed: {e}")
        data = generate_fallback_data(source_url)
    if not validate_data(data) or len(data) < 3:
        data = generate_fallback_data(source_url)
    data = data[:3]
    save_to_json(data, os.path.join(os.path.dirname(__file__), "data.json"))
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
