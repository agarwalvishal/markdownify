import os
import re
import pickle
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
INPUT_FILE = "crawl_data.pkl"  # File to load from
OUTPUT_DIR = "markdown_docs"
# ---------------------

def url_to_filename(url):
    """Converts a URL to a safe, hierarchical filename."""
    if not url:
        return "index.md" # Fallback
        
    parsed_url = urlparse(url)
    path = parsed_url.path
    path = path.strip('/')
    
    if not path:
        filename = "index.md"
    else:
        # Replace slashes with a double underscore to flatten
        filename = path.replace('/', '__') + ".md"
        
    # Final sanitation
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    
    # Handle case where filename might be empty *after* sanitation
    if not filename.replace('.md', ''):
        return "index.md"
        
    return filename

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Loading raw data from {INPUT_FILE}...")
    try:
        with open(INPUT_FILE, 'rb') as f:
            crawl_result = pickle.load(f)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        print("Please run crawl_and_save.py first.")
        return
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    print(f"Processing {len(crawl_result.data)} documents...")

    # --- [THIS IS THE CORRECTED LOOP BASED ON YOUR DEBUG LOG] ---
    for item in crawl_result.data: 
        
        # 1. Get Markdown (item.markdown)
        if not hasattr(item, 'markdown') or not item.markdown: 
            url_for_skip = item.metadata.source_url if hasattr(item, 'metadata') and hasattr(item.metadata, 'source_url') else 'Unknown URL'
            print(f"Skipping {url_for_skip} - No markdown content.")
            continue
        
        # 2. Get Source URL (item.metadata.source_url)
        source_url = None
        if hasattr(item, 'metadata') and hasattr(item.metadata, 'source_url'):
            source_url = item.metadata.source_url
            
        if not source_url:
            print(f"Warning: Could not find source_url for an item. Skipping.")
            continue

        # 3. Get Title (item.metadata.title)
        title = "Untitled"
        if hasattr(item, 'metadata') and hasattr(item.metadata, 'title'):
            title = item.metadata.title

        # 4. Create Filename
        filename = url_to_filename(source_url)
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        frontmatter = f"""---
title: "{title}"
source_url: "{source_url}"
source_library: "{os.getenv('SOURCE_LIBRARY')}"
---
\n"""
        
        final_content = frontmatter + item.markdown 
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
            
        print(f"Saved: {filepath}")

    print("\nAll documentation saved successfully.")
    print(f"Your '{OUTPUT_DIR}' folder should now be populated.")


if __name__ == "__main__":
    main()
