import os
import json
import sys
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CasinoBonus(BaseModel):
    """Schema for casino bonus extraction."""
    casino_name: str = Field(description="Name of the casino")
    welcome_bonus: str = Field(description="Welcome bonus offer (e.g., '100% up to 500 EUR')")
    wagering_requirement: int = Field(description="Wagering requirement multiplier as integer (e.g., 35)")
    minimum_deposit: str = Field(description="Minimum deposit amount (e.g., '20 EUR')")
    source_url: str = Field(description="URL of the scraped page")


def extract_with_openai(content: str, source_url: str) -> List[Dict[str, Any]]:
    """Extract casino bonus information using OpenAI's API."""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        client = OpenAI(api_key=api_key)
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        
        system_prompt = """You are an expert at extracting structured casino bonus information from web content.
        
Extract information for 3 casinos from the provided content. For each casino, extract:
- casino_name: The name of the casino (clean, recognizable name)
- welcome_bonus: The welcome bonus offer in a clear format (e.g., "100% up to 500 EUR")
- wagering_requirement: The wagering requirement as an integer (e.g., 35 for 35x). Extract just the number.
- minimum_deposit: The minimum deposit required (e.g., "20 EUR")
- source_url: Use the provided source URL

Return the data as a valid JSON array of objects matching the required schema. Be precise and only extract information that is clearly stated."""
        
        user_prompt = f"Source URL: {source_url}\n\nContent:\n{content}\n\nExtract casino bonus information for 3 casinos."
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # If result is wrapped in a key, unwrap it
        if isinstance(result, dict):
            if "casinos" in result:
                return result["casinos"]
            elif "data" in result:
                return result["data"]
            else:
                # Maybe it's a single object or wrapped differently
                # Try to find array
                for key, value in result.items():
                    if isinstance(value, list):
                        return value
                # If single object, wrap in list
                return [result] if result else []
        return result if isinstance(result, list) else []
    
    except Exception as e:
        print(f"Error with OpenAI extraction: {e}", file=sys.stderr)
        raise


def extract_with_anthropic(content: str, source_url: str) -> List[Dict[str, Any]]:
    """Extract casino bonus information using Anthropic's API."""
    try:
        from anthropic import Anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        client = Anthropic(api_key=api_key)
        model = os.getenv("LLM_MODEL", "claude-3-5-haiku-20241022")
        
        system_prompt = """You are an expert at extracting structured casino bonus information from web content.
        
Extract information for 3 casinos from the provided content. For each casino, extract:
- casino_name: The name of the casino (clean, recognizable name)
- welcome_bonus: The welcome bonus offer in a clear format (e.g., "100% up to 500 EUR")
- wagering_requirement: The wagering requirement as an integer (e.g., 35 for 35x). Extract just the number.
- minimum_deposit: The minimum deposit required (e.g., "20 EUR")
- source_url: Use the provided source URL

Return the data as a valid JSON array. Be precise and only extract information that is clearly stated."""
        
        user_prompt = f"Source URL: {source_url}\n\nContent:\n{content}\n\nExtract casino bonus information for 3 casinos. Return as JSON array."
        
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=0.1,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Extract text from response
        text = response.content[0].text if response.content else "[]"
        
        # Try to parse JSON (may be wrapped in markdown)
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        result = json.loads(text.strip())
        return result if isinstance(result, list) else []
    
    except Exception as e:
        print(f"Error with Anthropic extraction: {e}", file=sys.stderr)
        raise
