
## Steps to run:

1. Install packages

```
pip install -r requirements.txt
```

2. Set values in `.env` file

```
FIRECRAWL_API_KEY = ""
URL = "" #URL to crawl
SOURCE_LIBRARY = "" #Name of the library being crawled (optional)
```

3. Crawl and save the data

```
python crawl_and_save.py
```

4. Process the saved data to markdown

```
python process.py
```

5. The output is available inside `markdown_docs` folder.

## Note

There are two scripts namely `crawl_and_save.py` and `process.py` to first crawl and save raw data to avoid having to crawl again and spend unnecessary credits in case of processing failures.