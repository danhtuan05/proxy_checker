from flask import Flask, request, jsonify, render_template
import requests
import concurrent.futures
import os

port = int(os.environ.get("PORT", 5000))
app = Flask(__name__)

def check_proxy(proxy_str):
    try:
        parts = proxy_str.strip().split(":")
        ip, port, user, password = parts
        proxy_url = f"http://{user}:{password}@{ip}:{port}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=5)
        if r.status_code == 200:
            return proxy_str, True
    except:
        pass
    return proxy_str, False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    data = request.json
    proxy_list = data.get('proxies', [])

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_proxy, proxy) for proxy in proxy_list]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    working = [p for p, ok in results if ok]
    not_working = [p for p, ok in results if not ok]
    return jsonify({'working': working, 'not_working': not_working})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
