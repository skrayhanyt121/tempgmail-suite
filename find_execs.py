import re
from curl_cffi import requests

s = requests.Session(curl_options={113: 1}, impersonate='chrome120')
r = s.get('https://taskpay.ru/board/static/js/main.13c1307c.js')

routes = set(re.findall(r'["\'](/tasks-execs[^"\']*)["\']', r.text))
print('tasks-execs routes found:')
for rt in sorted(routes):
    print(rt)

exec_routes = set(re.findall(r'["\'](/v1/[^"\']+)["\']', r.text))
print('\nDirect /v1/ routes found:')
for rt in sorted(exec_routes):
    print(rt)
