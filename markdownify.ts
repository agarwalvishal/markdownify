import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse
from markdownify import markdownify as md

# --- Configuration ---
BASE_URL = "https://docs.colyseus.io/"
OUTPUT_DIR = "colyseus_markdown_docs"
# A set to keep track of visited URLs to avoid infinite loops and duplicates
visited_urls = set()
# --- LLM Optimization Selectors ---
# Target the main content container where the documentation article resides.
# (This class is often used in Docusaurus and similar frameworks)
CONTENT_SELECTOR = 'div[class*="docItemContainer"], article[class*="docItemContainer"]' 
# --- ---

def is_local_doc_link(url):
    """Check if the link points to a documentation page within the same site."""
    return url.startswith(BASE_URL) or url.startswith('/')

def clean_filename(url_path):
    """Converts a URL path to a safe filename."""
    # Remove leading/trailing slashes and common extensions
    path = url_path.strip('/').replace('.html', '').replace('.htm', '')
    # Replace slashes with underscores for nesting indication
    filename = path.replace('/', '__')
    if not filename:
        return "index.md"
    # Ensure filename is safe
    return re.sub(r'[\\/:*?"<>|]', '', filename) + ".md"

def fetch_and_convert(url):
    """Fetches a page, extracts content, converts to Markdown, and saves."""
    if url in visited_urls:
        return
    
    print(f"Processing: {url}")
    visited_urls.add(url)
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {url} with status {response.status_code}")
            return
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Extraction: Find the main documentation content area
        content_div = soup.select_one(CONTENT_SELECTOR)
        if not content_div:
            print(f"Warning: Could not find content in {url}. Skipping.")
            return

        # 2. Conversion: Convert the extracted HTML to Markdown
        markdown_text = md(
            str(content_div),
            heading_style="ATX",
            strong_em_symbol='**', # Enforce standard Markdown formatting
            default_row_align='left'
        )

        # 3. Initial Cleaning & Optimization:
        
        # A. Prepend Crucial Metadata (YAML Frontmatter)
        parsed_url = urlparse(url)
        path = parsed_url.path
        if not path.endswith('/'): path += '/'
        
        frontmatter = f"""---
title: "{soup.title.string.split('|')[0].strip() if soup.title else 'Untitled Page'}"
source_url: "{url}"
source_library: "Colyseus API Documentation"
path_key: "{path}"
---
\n"""
        
        # B. Regex cleaning for common doc site artifacts (e.g., "On this page" titles)
        # Remove empty lines and common navigational text
        markdown_text = re.sub(r'\n\s*\n', '\n\n', markdown_text.strip())
        markdown_text = re.sub(r'#+\s*On this page\s*', '', markdown_text, flags=re.IGNORECASE)
        markdown_text = re.sub(r'#+\s*In this section\s*', '', markdown_text, flags=re.IGNORECASE)

        final_content = frontmatter + markdown_text
        
        # Save the file
        file_name = clean_filename(path)
        save_path = os.path.join(OUTPUT_DIR, file_name)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"Successfully saved: {file_name}")

        # 4. Crawling: Find next links recursively
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Resolve relative URLs
            next_url = urljoin(BASE_URL, href)
            
            # Check if it's a documentation link and hasn't been visited
            if is_local_doc_link(next_url) and next_url not in visited_urls:
                # Basic check to skip anchor links within the same page
                if urlparse(next_url).fragment and next_url.split('#')[0] == url.split('#')[0]:
                    continue
                # Simple check to ensure we only crawl paths, not file downloads (e.g., .zip)
                if not any(ext in next_url for ext in ['.pdf', '.zip', '.tar']):
                    # Recursive call
                    fetch_and_convert(next_url.split('#')[0]) # Split to ignore URL fragments
                    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred for {url}: {e}")

if __name__ == '__main__':
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"Starting crawl of {BASE_URL}...")
    fetch_and_convert(BASE_URL)
    print("\nCrawl and conversion complete.")
    print(f"Markdown files are saved in the '{OUTPUT_DIR}' directory.")
