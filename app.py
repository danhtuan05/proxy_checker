from flask import Flask, request, jsonify, render_template
import requests
import concurrent.futures
import os
import re
import socket

port = int(os.environ.get("PORT", 5000))
app = Flask(__name__)
def get_proxy_location(ip: str) -> str:
    flags = {
    "AF": "🇦🇫", "AL": "🇦🇱", "DZ": "🇩🇿", "AS": "🇦🇸", "AD": "🇦🇩", "AO": "🇦🇴",
    "AG": "🇦🇬", "AR": "🇦🇷", "AM": "🇦🇲", "AU": "🇦🇺", "AT": "🇦🇹", "AZ": "🇦🇿",
    "BS": "🇧🇸", "BH": "🇧🇭", "BD": "🇧🇩", "BB": "🇧🇧", "BY": "🇧🇾", "BE": "🇧🇪",
    "BZ": "🇧🇿", "BJ": "🇧🇯", "BM": "🇧🇲", "BT": "🇧🇹", "BO": "🇧🇴", "BA": "🇧🇦",
    "BW": "🇧🇼", "BR": "🇧🇷", "BN": "🇧🇳", "BG": "🇧🇬", "BF": "🇧🇫", "BI": "🇧🇮",
    "KH": "🇰🇭", "CM": "🇨🇲", "CA": "🇨🇦", "CV": "🇨🇻", "CF": "🇨🇫", "TD": "🇹🇩",
    "CL": "🇨🇱", "CN": "🇨🇳", "CO": "🇨🇴", "KM": "🇰🇲", "CD": "🇨🇩", "CG": "🇨🇬",
    "CR": "🇨🇷", "CI": "🇨🇮", "HR": "🇭🇷", "CU": "🇨🇺", "CY": "🇨🇾", "CZ": "🇨🇿",
    "DK": "🇩🇰", "DJ": "🇩🇯", "DM": "🇩🇲", "DO": "🇩🇴", "EC": "🇪🇨", "EG": "🇪🇬",
    "SV": "🇸🇻", "GQ": "🇬🇶", "ER": "🇪🇷", "EE": "🇪🇪", "SZ": "🇸🇿", "ET": "🇪🇹",
    "FJ": "🇫🇯", "FI": "🇫🇮", "FR": "🇫🇷", "GA": "🇬🇦", "GM": "🇬🇲", "GE": "🇬🇪",
    "DE": "🇩🇪", "GH": "🇬🇭", "GR": "🇬🇷", "GD": "🇬🇩", "GT": "🇬🇹", "GN": "🇬🇳",
    "GW": "🇬🇼", "GY": "🇬🇾", "HT": "🇭🇹", "HN": "🇭🇳", "HU": "🇭🇺", "IS": "🇮🇸",
    "IN": "🇮🇳", "ID": "🇮🇩", "IR": "🇮🇷", "IQ": "🇮🇶", "IE": "🇮🇪", "IL": "🇮🇱",
    "IT": "🇮🇹", "JM": "🇯🇲", "JP": "🇯🇵", "JO": "🇯🇴", "KZ": "🇰🇿", "KE": "🇰🇪",
    "KI": "🇰🇮", "KP": "🇰🇵", "KR": "🇰🇷", "KW": "🇰🇼", "KG": "🇰🇬", "LA": "🇱🇦",
    "LV": "🇱🇻", "LB": "🇱🇧", "LS": "🇱🇸", "LR": "🇱🇷", "LY": "🇱🇾", "LI": "🇱🇮",
    "LT": "🇱🇹", "LU": "🇱🇺", "MG": "🇲🇬", "MW": "🇲🇼", "MY": "🇲🇾", "MV": "🇲🇻",
    "ML": "🇲🇱", "MT": "🇲🇹", "MH": "🇲🇭", "MR": "🇲🇷", "MU": "🇲🇺", "MX": "🇲🇽",
    "FM": "🇫🇲", "MD": "🇲🇩", "MC": "🇲🇨", "MN": "🇲🇳", "ME": "🇲🇪", "MA": "🇲🇦",
    "MZ": "🇲🇿", "MM": "🇲🇲", "NA": "🇳🇦", "NR": "🇳🇷", "NP": "🇳🇵", "NL": "🇳🇱",
    "NZ": "🇳🇿", "NI": "🇳🇮", "NE": "🇳🇪", "NG": "🇳🇬", "NO": "🇳🇴", "OM": "🇴🇲",
    "PK": "🇵🇰", "PW": "🇵🇼", "PA": "🇵🇦", "PG": "🇵🇬", "PY": "🇵🇾", "PE": "🇵🇪",
    "PH": "🇵🇭", "PL": "🇵🇱", "PT": "🇵🇹", "QA": "🇶🇦", "RO": "🇷🇴", "RU": "🇷🇺",
    "RW": "🇷🇼", "KN": "🇰🇳", "LC": "🇱🇨", "VC": "🇻🇨", "WS": "🇼🇸", "SM": "🇸🇲",
    "ST": "🇸🇹", "SA": "🇸🇦", "SN": "🇸🇳", "RS": "🇷🇸", "SC": "🇸🇨", "SL": "🇸🇱",
    "SG": "🇸🇬", "SK": "🇸🇰", "SI": "🇸🇮", "SB": "🇸🇧", "SO": "🇸🇴", "ZA": "🇿🇦",
    "SS": "🇸🇸", "ES": "🇪🇸", "LK": "🇱🇰", "SD": "🇸🇩", "SR": "🇸🇷", "SE": "🇸🇪",
    "CH": "🇨🇭", "SY": "🇸🇾", "TW": "🇹🇼", "TJ": "🇹🇯", "TZ": "🇹🇿", "TH": "🇹🇭",
    "TL": "🇹🇱", "TG": "🇹🇬", "TO": "🇹🇴", "TT": "🇹🇹", "TN": "🇹🇳", "TR": "🇹🇷",
    "TM": "🇹🇲", "TV": "🇹🇻", "UG": "🇺🇬", "UA": "🇺🇦", "AE": "🇦🇪", "GB": "🇬🇧",
    "US": "🇺🇸", "UY": "🇺🇾", "UZ": "🇺🇿", "VU": "🇻🇺", "VA": "🇻🇦", "VE": "🇻🇪",
    "VN": "🇻🇳", "YE": "🇾🇪", "ZM": "🇿🇲", "ZW": "🇿🇼"
}
    try:
        # headers = {'Authorization': f'Bearer {IPINFO_API_KEY}'} if IPINFO_API_KEY else {}
        response = requests.get(f'https://api.ipregistry.co/{ip}?key=ira_w1eGyZ3wi2XljsEa4jyt5stR6Pe8aa2knCA6')
        data = response.json()
        if 'error' in data:
            return 'Unknown location'
        loca = f"{data.get('location', {}).get('country', {}).get('code', 'Unknown country')}"
        flag = flags.get(loca.upper(), "N/A")
        return loca,flag
    except Exception as e:
        # logger.error(f"Error fetching location for IP {ip}: {e}")
        return 'Unknown location'
def check_rdp(vps, timeout=5):
    ip_port = vps.split('/')[0]
    ip = ip_port.split(":")[0]
    port = ip_port.split(":")[1]
    vps_ip = f"{ip}:{port}"
    try:
        s = socket.create_connection((ip, port), timeout)
        s.close()
        status_vps = True
        return vps_ip, status_vps
    except socket.timeout:
        if port ==22:
            status_vps = False
            return vps_ip, status_vps
        else:
            try:
                vps_ip = f"{ip}:3389"
                s = socket.create_connection((ip, 3389), timeout)
                s.close()
                status_vps = True
                return vps_ip, status_vps
            except socket.timeout:
                status_vps = False
                return vps_ip, status_vps
            except socket.error as e:
                status_vps = False
                return vps_ip, status_vps
def check_proxy(proxy_str):
    parts = proxy_str.strip().split(':')
    if len(parts) ==2:
        ip, port = parts[0], parts[1]
        loca,flag = get_proxy_location(ip=ip)
        vps_result, status_vps_1 =  check_rdp(ip+":"+port)
        return {
                    "proxy": vps_result,
                    "working": status_vps_1,
                    "protocol": "VPS",
                    "country": loca,
                    "flag": flag
                }
    else:
        ip, port = parts[0], parts[1]
        auth = ""
        if len(parts) == 4:
            user, password = parts[2], parts[3]
            auth = f"{user}:{password}@"
        http_proxies = {
            'http': f'http://{auth}{ip}:{port}',
            'https': f'https://{auth}{ip}:{port}',
        }
        socks_proxies = {
            'http': f'socks5h://{auth}{ip}:{port}',
            'https': f'socks5h://{auth}{ip}:{port}',
        }
        loca,flag = get_proxy_location(ip=ip)
        try:
            r = requests.get("http://ip-api.com/json", proxies=http_proxies, timeout=5)

            if r.ok:

                return {
                    "proxy": proxy_str,
                    "working": True,
                    "protocol": "HTTP",
                    "country": loca,
                    "flag": flag
                }
        except:
            pass
        try:
            r = requests.get("http://ip-api.com/json", proxies=socks_proxies, timeout=5)
            if r.ok:
                return {
                    "proxy": proxy_str,
                    "working": True,
                    "protocol": "SOCKS5",
                    "country": loca,
                    "flag": flag
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
    extracted = []
    pattern_full = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+:[^:\s/]+:[^:\s/]+)")

    # Regex tìm IP:PORT ở đầu chuỗi (nếu không có user:pass)
    pattern_basic = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+)")
    for proxy in proxy_list:
        match = pattern_full.search(proxy)
        if match:
            extracted.append(match.group(1))
        else:
            match = pattern_basic.search(proxy)
            if match:
                extracted.append(match.group(1))
    result_proxy = "\n".join(extracted)
    final_proxy = result_proxy.strip().split('\n')
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(check_proxy, p) for p in final_proxy]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
