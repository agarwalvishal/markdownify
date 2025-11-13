import os
import re
import pickle  # We will use pickle to save the raw Python object
from firecrawl import Firecrawl
from firecrawl.types import ScrapeOptions
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
OUTPUT_FILE = "crawl_data.pkl"  # We will save the raw data here
# ---------------------

def main():
    print("Starting crawl with Firecrawl (using latest v2 SDK)...")
    app = Firecrawl(api_key = os.getenv('FIRECRAWL_API_KEY'))

    try:
        DOCS_URL = os.getenv('URL')
        safe_base_url_regex = re.escape(DOCS_URL)
        exclude_pattern = f"^{safe_base_url_regex}/blog/.*"
        
        print(f"Submitting crawl job for {DOCS_URL}...")
        print(f"Exclude pattern: {exclude_pattern}")

        crawl_result = app.crawl(
            url=DOCS_URL,
            limit=175,
            exclude_paths=[exclude_pattern], 
            scrape_options=ScrapeOptions(formats=['markdown']) 
        )
        
        print(f"\nCrawl job status: {crawl_result.status}")
        
        if not crawl_result or not crawl_result.data:
            print(f"No data returned from crawl (Total pages found: {crawl_result.total}). Exiting.")
            return

        # --- THIS IS THE NEW, SAFER PART ---
        print(f"Crawl complete. Found {len(crawl_result.data)} pages.")
        print(f"Saving raw data to {OUTPUT_FILE}...")
        
        with open(OUTPUT_FILE, 'wb') as f:
            pickle.dump(crawl_result, f)
            
        print("\nRaw data saved successfully.")
        print("You can now run process.py to generate the Markdown files.")

    except Exception as e:
        print("\n--- CRAWL SCRIPT FAILED ---")
        print(f"An error occurred: {e}")
        print("Please check your API key and credits.")
        print("-----------------------\n")

if __name__ == "__main__":
    main()
