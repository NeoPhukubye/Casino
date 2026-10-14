import os
import json
import sys
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class CasinoBonus(BaseModel):
    casino_name: str = Field(description="Name of the casino")
    welcome_bonus: str = Field(description="Welcome bonus offer")
    wagering_requirement: int = Field(description="Wagering requirement multiplier as integer")
    minimum_deposit: str = Field(description="Minimum deposit amount")
    source_url: str = Field(description="URL of the scraped page")


def extract_with_openai(content: str, source_url: str) -> List[Dict[str, Any]]:
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        client = OpenAI(api_key=api_key)
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        system_prompt = """You are an expert at extracting structured casino bonus information from web content.
Extract information for 3 casinos. Return as a valid JSON array."""
        user_prompt = f"Source URL: {source_url}\n\nContent:\n{content}\n\nExtract casino bonus info for 3 casinos."
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, list):
                    return value
            return [result] if result else []
        return result if isinstance(result, list) else []
    except Exception as e:
        print(f"Error with OpenAI extraction: {e}", file=sys.stderr)
        raise


def extract_with_anthropic(content: str, source_url: str) -> List[Dict[str, Any]]:
    try:
        from anthropic import Anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        client = Anthropic(api_key=api_key)
        model = os.getenv("LLM_MODEL", "claude-3-5-haiku-20241022")
        system_prompt = "Extract 3 casino bonuses as JSON array."
        user_prompt = f"Source URL: {source_url}\n\nContent:\n{content}\n\nReturn JSON array."
        response = client.messages.create(
            model=model, max_tokens=4096, temperature=0.1, system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        text = response.content[0].text if response.content else "[]"
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
