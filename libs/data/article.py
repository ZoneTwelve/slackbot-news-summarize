
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re

def custom_md(xhtml):
    soup = BeautifulSoup(xhtml, 'html.parser')

    for pre_tag in soup.find_all('pre'):
        code_content = pre_tag.get_text()
        fenced_code = f"```\n{code_content}\n```"
        pre_tag.replace_with(BeautifulSoup(fenced_code, 'html.parser'))
    md_text = md(str(soup), strip=["script", "style", 'img', 'a'])
    # replace with multiple newlines with a single newline
    md_result = re.sub(r'\n+', '\n', md_text)
    return md_result
