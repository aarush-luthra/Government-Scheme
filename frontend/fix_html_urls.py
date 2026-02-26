import os
import re

html_files = [
    '/Users/aarushluthra/Documents/Government-Scheme-1/frontend/saved.html',
    '/Users/aarushluthra/Documents/Government-Scheme-1/frontend/admin.html',
    '/Users/aarushluthra/Documents/Government-Scheme-1/frontend/login.html',
    '/Users/aarushluthra/Documents/Government-Scheme-1/frontend/signup.html'
]

for filepath in html_files:
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        
        if 'API_BASE_URL' in content and 'const API_BASE_URL' not in content:
            # find first <script> block and insert it at the top
            content = re.sub(
                r'(<script[^>]*>)(\s*)',
                r"\1\2const API_BASE_URL = 'http://127.0.0.1:8000';\n    ",
                content,
                count=1  # Only replace the first occurrence
            )
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Fixed {filepath}")
