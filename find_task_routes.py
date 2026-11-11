import re
from curl_cffi import requests

s = requests.Session(curl_options={113: 1}, impersonate='chrome120')
r = s.get('https://taskpay.ru/board/static/js/main.13c1307c.js')

# Find string literals in JS that look like routes
routes = set(re.findall(r'["\'](/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_\-]+)*)["\']', r.text))
print(f'Total routes found: {len(routes)}')
task_routes = [route for route in routes if 'task' in route]
print('\n--- Task Routes ---')
for tr in sorted(task_routes):
    print(tr)
