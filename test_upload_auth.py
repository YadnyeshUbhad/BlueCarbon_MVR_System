import requests

session = requests.Session()
response = session.post('http://127.0.0.1:5000/ngo/upload/tree_data', data={}, allow_redirects=False)
print(f'Upload endpoint status: {response.status_code}')
print(f'Location header: {response.headers.get("Location", "None")}')
print(f'Should redirect to login: {"✅" if response.status_code == 302 and "login" in response.headers.get("Location", "").lower() else "❌"}')