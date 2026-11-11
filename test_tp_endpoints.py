from curl_cffi import requests

AUTH_KEY = 'G24etYDHMi2WQPsIGSTXijxTM5mokROs'
headers = {
    'Authorization': f'Bearer {AUTH_KEY}',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Origin': 'https://taskpay.ru',
    'Referer': 'https://taskpay.ru/board/earn-money/new-tasks'
}

endpoints = [
    '/events-user-notice/me',
    '/events-user-notice-subscribe/user-notice-config/me',
    '/account/sign/by-token',
    '/board/main/my-balance/history'
]

for ep in endpoints:
    url = f'https://api.taskpay.ru/v1{ep}'
    r = requests.get(url, headers=headers, impersonate='chrome120')
    print(f'{ep} -> Status: {r.status_code} | Text: {r.text[:250]}')
