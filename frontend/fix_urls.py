import re
import os

API_BASE = "'http://127.0.0.1:8000'"

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Prepend API_BASE_URL def if script.js
    if filepath.endswith('script.js') and 'const API_BASE_URL' not in content:
        content = "const API_BASE_URL = 'http://127.0.0.1:8000';\n\n" + content

    # Replace absolute URLs with API_BASE_URL + '...'
    # fetch('http://127.0.0.1:8000/path' -> fetch(`${API_BASE_URL}/path`
    content = re.sub(
        r"fetch\(['\"]http://127\.0\.0\.1:8000/([^'\"]+)['\"]",
        r"fetch(API_BASE_URL + '/\1'",
        content
    )

    # Replace relative fetch with interpolation
    # fetch('/path' -> fetch(API_BASE_URL + '/path'
    # For backticks, fetch(`/path${x}`) -> fetch(`${API_BASE_URL}/path${x}`)
    content = re.sub(
        r"fetch\(['\"]/([^'\"]+)['\"]",
        r"fetch(API_BASE_URL + '/\1'",
        content
    )
    content = re.sub(
        r"fetch\(`/(.*?)`",
        r"fetch(`${API_BASE_URL}/\1`",
        content
    )

    # In HTML files we might not have API_BASE_URL defined globally, 
    # so we'll just hardcode http://127.0.0.1:8000 if not script.js
    if not filepath.endswith('script.js'):
        content = re.sub(
            r"fetch\(['\"]/([^'\"]+)['\"]",
            r"fetch('http://127.0.0.1:8000/\1'",
            content
        )
        content = re.sub(
            r"fetch\(`/(.*?)`",
            r"fetch(`http://127.0.0.1:8000/\1`",
            content
        )


    with open(filepath, 'w') as f:
        f.write(content)

files_to_process = [
    '/Users/aarushluthra/Documents/Government-Scheme-1/frontend/script.js',
    '/Users/aarushluthra/Documents/Government-Scheme-1/frontend/saved.html',
    '/Users/aarushluthra/Documents/Government-Scheme-1/frontend/admin.html',
    '/Users/aarushluthra/Documents/Government-Scheme-1/frontend/login.html',
    '/Users/aarushluthra/Documents/Government-Scheme-1/frontend/signup.html'
]

for filepath in files_to_process:
    if os.path.exists(filepath):
        process_file(filepath)
        print(f"Processed {filepath}")
