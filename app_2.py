from flask import Flask, request, jsonify, render_template
import requests
import concurrent.futures
import os

port = int(os.environ.get("PORT", 5000))
app = Flask(__name__)

def check_proxy(proxy_str):
    try:
        parts = proxy_str.strip().split(':')
        ip, port = parts[0], parts[1]
        auth = ""
        if len(parts) == 4:
            user, password = parts[2], parts[3]
            auth = f"{user}:{password}@"
        proxy_url = f"http://{auth}{ip}:{port}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

        r = requests.get("http://ip-api.com/json", proxies=proxies, timeout=7)
        data = r.json()

        if data["status"] == "success":
            country_code = data["countryCode"]
            country_flag = chr(127397 + ord(country_code[0])) + chr(127397 + ord(country_code[1]))
            return {
                "proxy": proxy_str,
                "working": True,
                "protocol": "HTTP",
                "country": country_code,
                "flag": country_flag
            }
    except:
        pass

    return {
        "proxy": proxy_str,
        "working": False,
        "protocol": "HTTP",
        "country": None,
        "flag": ""
    }
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/check", methods=["POST"])
def check():
    data = request.json
    proxy_list = data.get("proxies", [])
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(check_proxy, p) for p in proxy_list]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
