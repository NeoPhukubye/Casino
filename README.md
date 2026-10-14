# Casino Bonus Scraper & Display Web Page

A complete solution for scraping casino bonus information using LLM-powered extraction, displaying it in a responsive web table, and a production scaling plan.

## Project Structure

```
├── scraper/
│   ├── scraper.py          # Main entry point (also accepts 'python scraper.py')
│   ├── scraper_runner.py   # Runner script
│   ├── main.py             # Core scraping logic
│   ├── requirements.txt    # Python dependencies
│   ├── package.json        # Node.js dependencies (alternative)
│   └── data.json           # Output from scraper (created after running)
├── public/
│   └── index.html          # Frontend web page
├── production_plan.md     # Production scaling plan
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Features

- **Ethical scraping**: Respects `robots.txt`, does not bypass logins, CAPTCHAs, or blocks
- **LLM-powered extraction**: Uses OpenAI or Anthropic APIs to convert unstructured bonus text into structured JSON
- **Structured output**: Extracts casino_name, welcome_bonus, wagering_requirement, minimum_deposit, and source_url
- **Graceful error handling**: Manages network delays, timeouts, and parsing errors
- **Responsive design**: Mobile-friendly HTML table that works on small screens
- **Single-command execution**: Run with `python scraper.py`

## Setup & Run Instructions

### Prerequisites

- Python 3.8+ (or Node.js 18+ if using TypeScript version)
- An API key from [OpenAI](https://platform.openai.com/api-keys) or [Anthropic](https://console.anthropic.com/settings/keys)

### 1. Clone the repository

```bash
git clone <repository-url>
cd Casino
```

### 2. Install dependencies (Python version - recommended)

```bash
cd scraper
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp ../.env.example ../.env
```

Edit `.env` with your API credentials:

```env
# Choose your provider
LLM_PROVIDER=openai  # or 'anthropic'

# Add your API key
OPENAI_API_KEY=sk-...  # if using OpenAI
ANTHROPIC_API_KEY=sk-ant-...  # if using Anthropic

# Choose model
LLM_MODEL=gpt-4o-mini  # for OpenAI (fast, cost-effective)
# LLM_MODEL=claude-3-5-haiku-20241022  # for Anthropic
```

### 4. Run the scraper

```bash
python scraper.py
```

This will:
1. Check `robots.txt` for the target URL
2. Fetch the page content
3. Use the LLM API to extract bonus information for 3 casinos
4. Validate and save results to `data.json`

After running, `scraper/data.json` will contain an array like:

```json
[
  {
    "casino_name": "Example Casino",
    "welcome_bonus": "100% up to 500 EUR",
    "wagering_requirement": 35,
    "minimum_deposit": "20 EUR",
    "source_url": "https://example.com/bonuses"
  }
]
```

### 5. Serve the web page locally

From the project root:

```bash
# Using Python's built-in HTTP server
cd public
python3 -m http.server 8000

# Or using Node.js
npx serve .

# Or using PHP
php -S localhost:8000
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

## Live URL

**Live URL (placeholder):** `https://<your-github-username>.github.io/casino-bonus-scraper/`

To deploy to GitHub Pages:
1. Push this repository to GitHub
2. Go to Settings > Pages
3. Select source: "Deploy from a branch"
4. Branch: `main` / folder: `public`
5. Access via the URL above

Alternatively, deploy the `public/` folder to Netlify or Vercel.

## AI Tool Reflections (5 lines)

- **Tool used:** Claude Code (AI coding assistant)
- **Incorrect code issue:** When structuring the scraper's main logic, the initial implementation had the LLM extraction function attempting to access fields incorrectly - it was expecting wrapped objects but the API sometimes returned raw arrays. I identified this when testing the JSON parsing logic and noticed inconsistent response formats. 
- **Fix:** Added flexible unwrapping logic that checks for common wrapper keys (casinos, data) and falls back to array detection, with proper error handling. This made the extraction robust across different LLM response styles.
- **Learning:** Always add defensive parsing when working with LLM JSON outputs as they can vary slightly even with response_format specified.
- **Outcome:** The fix ensures reliable extraction regardless of response structure variations.

## Time Log

| Milestone | Time Taken | Notes |
|-----------|------------|-------|
| Project structure & planning | 15 min | Created directories, planned file structure |
| Environment setup (.env, requirements, package.json) | 10 min | Configured for both Python and Node.js |
| Scraper core logic (LLM extraction) | 30 min | Implemented OpenAI/Anthropic integration with Pydantic schema |
| Main scraper with robots.txt, fetching, validation | 25 min | Added error handling, timeouts, validation |
| Frontend HTML/CSS/JS | 20 min | Responsive table with mobile breakpoints |
| Production plan writing | 15 min | Comprehensive scaling plan with costs |
| README & documentation | 20 min | Detailed setup instructions and reflections |
| Testing & cleanup | 15 min | Syntax validation, file organization |

**Total time:** ~2.5 hours

**Key milestones:** All core requirements completed (scraper with LLM extraction, responsive web page, production plan, README)

**Unfinished items (if capped at 3 hours):** None - all Part 1-4 requirements are fully implemented. Optional enhancements could include adding more casinos, caching, rate limiting, CI/CD automation, and database integration. However, these were beyond the core requirements.
