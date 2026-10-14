def main():
    """
    Main function to orchestrate scraping process.
    """
    # Example public casino comparison source
    # Using AskGamblers casino bonuses page as an example of a public source
    source_url = "https://www.askgamblers.com/online-casinos/bonuses"
    
    print(f"Checking robots.txt for {source_url}...")
    if not check_robots_txt(source_url):
        print("Error: Scraping not allowed by robots.txt", file=sys.stderr)
        sys.exit(1)
    
    print(f"Fetching page: {source_url}")
    try:
        html_content = fetch_page(source_url)
    except Exception as e:
        print(f"Failed to fetch page: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("Extracting casino bonus data using LLM...")
    try:
        data = extract_casino_data(html_content, source_url)
    except Exception as e:
        print(f"Failed to extract data: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("Validating extracted data...")
    if not validate_data(data):
        print("Data validation failed", file=sys.stderr)
        sys.exit(1)
    
    # Ensure we have at least 3 casinos as required
    if len(data) < 3:
        print("Warning: Only {len(data)} casinos extracted, but requirement is 3")
    
    # Take only first 3 if more are extracted
    data = data[:3]
    
    # Save to data.json in the scraper directory
    output_path = os.path.join(os.path.dirname(__file__), "data.json")
    save_to_json(data, output_path)
    
    print("\nExtraction complete!")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
