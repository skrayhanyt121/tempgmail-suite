import re
from curl_cffi import requests

r = requests.get('https://taskpay.ru/board/static/js/main.13c1307c.js', impersonate='chrome120')
matches = set(re.findall(r'h\([\'"`][A-Z]+[\'"`]\s*,\s*[\'"`](/[^\'"`]+)[\'"`]', r.text))
print('Direct h() endpoints:', matches)

matches2 = set(re.findall(r'[\'"`](/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_\-]+)*)[\'"`]', r.text))
api_like = [m for m in matches2 if any(k in m for k in ['task', 'user', 'account', 'balance', 'order', 'earn'])]
print('Total api-like routes:', len(api_like))
for m in sorted(api_like)[:25]:
    print(' ', m)
