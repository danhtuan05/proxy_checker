import requests
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from concurrent.futures import ThreadPoolExecutor
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import json
import hashlib
import base64
import socket
import re


with open('setup.txt', 'r', encoding='utf-8') as file:
    # Đọc tất cả các dòng từ file
    lines = file.readlines()
    # In lần lượt các dòng số 1, 2 và 5 ra màn hình
    api_id = lines[0].strip().split('|')[1]
    api_hash = lines[1].strip().split('|')[1]
    phone = "+"+str(lines[2].strip().split('|')[1])
    time1 = lines[3].strip().split('|')[1]
    time_spam_from = int(time1.split('-')[0])
    time_spam_to = int(time1.split('-')[1])
    time2 = lines[4].strip().split('|')[1]
    time2_1 = time2.split('-')[0]
    time2_2 = time2.split('-')[1]
    time3 = lines[5].strip().split('|')[1]
    source = str(lines[6].strip().split('|')[1])
    mes_id1 = int(lines[7].strip().split('|')[1])
    mes_id2 = int(lines[8].strip().split('|')[1])
    already_id = int(lines[9].strip().split('|')[1])
    number_limit = int(lines[10].strip().split('|')[1])
    token = lines[14].strip().split('|')[1]


# Cấu hình logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

# logger = logging.getLogger(__name__)


WAITING_FOR_PROXY_LIST = range(1)
IPINFO_API_KEY = '4156073757b699'

GITHUB_TOKEN = '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'  # Thay bằng token của bạn
REPO = 'danhtuan05/license'
FILE_PATH = 'key.json'
API_URL = f'https://api.github.com/repos/{REPO}/contents/{FILE_PATH}'

####################################################################################################
print("BOT CHECK PROXY ĐÃ SẴN SÀNG !!")
####################################################################################################
# Hàm khởi đầu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        fr'Chào {user.mention_markdown_v2()} đến với TimeCloud\.vn\. Hãy gửi danh sách proxy theo dạng IP:PORT:USER:PASS, mỗi proxy trên một dòng để kiểm tra\.',
        reply_markup=ForceReply(selective=True),
    )

# Hàm kiểm tra từng proxy
def check_single_proxy(proxy: str) -> str:
    parts = proxy.split(':')
    if len(parts) == 2:
        ip, port = parts[0], parts[1]
        return check_rdp(ip+":"+port)
    else:
        auth = ""
        if len(parts) == 4:
            ip, port = parts[0], parts[1]
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

        try:
            response = requests.get('http://ifconfig.me/ip', proxies=http_proxies, timeout=5)
            if response.ok:
                return f'✅ - {proxy}'
        except Exception as e:
            pass

        try:
            response = requests.get('http://ifconfig.me/ip', proxies=socks_proxies, timeout=5)
            if response.ok:
                return f'✅ - SOCKS5 - {proxy}'
        except Exception as e:
            pass

        return f'🔴 - {proxy}'
# Hàm kiểm tra nhiều proxy
async def check_proxies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    processing_message = await update.message.reply_text(" 🔄 Processing...")
    proxies = update.message.text.strip().split('\n')
    extracted = []
    # Regex tìm IP:PORT:USER:PASS ở đầu chuỗi
    pattern_full = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+:[^:\s/]+:[^:\s/]+)")

    # Regex tìm IP:PORT ở đầu chuỗi (nếu không có user:pass)
    pattern_basic = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+)")
    for proxy in proxies:
        match = pattern_full.search(proxy)
        if match:
            extracted.append(match.group(1))
        else:
            match = pattern_basic.search(proxy)
            if match:
                extracted.append(match.group(1))
    result_proxy = "\n".join(extracted)
    final_proxy = result_proxy.strip().split('\n')
    proxy_count = len(final_proxy)
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_single_proxy, final_proxy))

    active_proxies = [result for result in results if '✅' in result]
    inactive_proxies = [result for result in results if '🔴' in result]
    sorted_results = active_proxies + inactive_proxies
    result_message = "\n".join(sorted_results)
    summary_message = f"\n📔 - Tổng số : {proxy_count}"

    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_message.message_id)
    
    await update.message.reply_text(result_message + summary_message)

    context.user_data['inactive_proxies'] = [proxy.split(' - ')[1] for proxy in inactive_proxies]

    # Tạo nút kiểm tra lại các proxy không hoạt động
    if inactive_proxies:
        keyboard = [
            [InlineKeyboardButton("🔁RE-CHECK !", callback_data='recheck_proxies')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Kiểm tra lại VPS/Proxy không hoạt động !", reply_markup=reply_markup)
####################################################################################################
#CHECK VPS
async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Trải nghiệm Proxy chính hãng tại TimeCloud.vn. Hãy gửi danh sách proxy theo dạng IP:PORT:USER:PASS, mỗi proxy trên một dòng để kiểm tra.")
    return WAITING_FOR_PROXY_LIST
def check_rdp(vps, timeout=5):
    try:
        ip_port = vps.split('/')[0]
        ip = ip_port.split(":")[0]
        port = ip_port.split(":")[1]
        location = get_proxy_location(ip=ip)
        try:
            s = socket.create_connection((ip, port), timeout)
            s.close()
            return f"✅ - {location} - {ip}:{port}"
        except socket.timeout:
            if port ==22:
                return f"🔴 - {ip}:{port}"
            else:
                try:
                    print("Thử 3389")
                    s = socket.create_connection((ip, 3389), timeout)
                    s.close()
                    return f"✅ - {location} - {ip}:{3389} - PORT"
                except socket.timeout:
                    return f"🔴 - {ip}:{port}"
                except socket.error as e:
                    return f"🔴 - {ip}:{port}"
    except Exception as e:
        return f"🔴 - {ip}:{port}"
async def check_vps2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    processing_message = await update.message.reply_text(" 🔄 Processing...")
    vps_1 = update.message.text.strip().split('\n')
    extracted = []
    for vps in vps_1:
        if "📔 - Tổng số" in vps:
            pass
        elif "-" in vps:
            vps_tach = vps.split('-')
            vps_final = vps_tach[1].strip()
            extracted.append(vps_final)
        else:
            # Regex IP:PORT
            pattern_ip_port = r"\b\d{1,3}(?:\.\d{1,3}){3}:\d+\b"
            # Regex chỉ IP
            pattern_ip_only = r"\b\d{1,3}(?:\.\d{1,3}){3}\b"
            match = re.search(pattern_ip_port, vps)
            if match:
                extracted.append(match.group())
            else:
                match_ip = re.search(pattern_ip_only, vps)
                if match_ip:
                    extracted.append(f"{match_ip.group()}:3389")
    result_vps = "\n".join(extracted)
    final_vps = result_vps.strip().split('\n')
    proxy_count = len(final_vps)
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_rdp, final_vps))
    active_vps = [result for result in results if '✅' in result]
    inactive_vps = [result for result in results if '🔴' in result]
    sorted_results_vps = active_vps + inactive_vps
    result_message_vps = "\n".join(sorted_results_vps)
    summary_message_vps = f"\n📔 - Tổng số VPS : {proxy_count}"

    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_message.message_id)
    
    await update.message.reply_text(result_message_vps + summary_message_vps)

    context.user_data['inactive_vps'] = [vps.split(' - ')[1] for vps in inactive_vps]
    # Tạo nút kiểm tra lại các proxy không hoạt động
    if inactive_vps:
        keyboard = [
            [InlineKeyboardButton("🔁RE-CHECK !", callback_data='recheck_vps')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Kiểm tra lại VPS không hoạt động !", reply_markup=reply_markup)

    return ConversationHandler.END


################################################################################
# CHECK PROXY + LOCATION
async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Trải nghiệm Proxy chính hãng tại TimeCloud.vn. Hãy gửi danh sách proxy theo dạng IP:PORT:USER:PASS, mỗi proxy trên một dòng để kiểm tra.")
    return WAITING_FOR_PROXY_LIST


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
        location = loca+" - "+flag
        return location
    except Exception as e:
        # logger.error(f"Error fetching location for IP {ip}: {e}")
        return 'Unknown location'


def check_single_proxy_lo(proxy: str) -> str:
    try:
        parts = proxy.split(':')
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
        location = get_proxy_location(ip)
        try:
            response = requests.get('http://ifconfig.me/ip', proxies=http_proxies, timeout=5)
            if response.ok:
                return f'✅ - {location} - {proxy}'
        except Exception as e:
            pass
        try:
            response = requests.get('http://ifconfig.me/ip', proxies=socks_proxies, timeout=5)
            if response.ok:
                return f'✅ - SOCKS5 - {location} - {proxy}'
        except Exception as e:
            pass

        return f'🔴 - {proxy}'
    except:
        return f'🔴 - {proxy}'






# Extract IP:PORT from proxy strings
async def check_proxies_lo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    processing_message = await update.message.reply_text(" 🔄 Processing...")
    proxies = update.message.text.strip().split('\n')
    extracted = []
    # Regex tìm IP:PORT:USER:PASS ở đầu chuỗi
    pattern_full = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+:[^:\s/]+:[^:\s/]+)")

    # Regex tìm IP:PORT ở đầu chuỗi (nếu không có user:pass)
    pattern_basic = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+)")
    for proxy in proxies:
        match = pattern_full.search(proxy)
        if match:
            extracted.append(match.group(1))
        else:
            match = pattern_basic.search(proxy)
            if match:
                extracted.append(match.group(1))
    result_proxy = "\n".join(extracted)
    final_proxy = result_proxy.strip().split('\n')
    proxy_count = len(final_proxy)
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_single_proxy_lo, final_proxy))
    active_proxies = [result for result in results if '✅' in result]
    inactive_proxies = [result for result in results if '🔴' in result]
    sorted_results = active_proxies + inactive_proxies
    result_message = "\n".join(sorted_results)
    summary_message = f"\n📔 - Tổng số proxy : {proxy_count}"

    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_message.message_id)
    
    await update.message.reply_text(result_message + summary_message)
    
    # End the conversation
    return ConversationHandler.END
################################################################################
# CHECK VỊ TRÍ 


def get_proxy_location_de(ip: str) -> str:
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
        country_loca = f"{data.get('location', {}).get('country', {}).get('name', 'Unknown country')}"
        loca_1 = f"{data.get('location', {}).get('region', {}).get('name', 'Unknown country')}"
        flag = flags.get(loca.upper(), "N/A")
        location = flag+" - "+loca_1+" - "+country_loca
        return location
    except Exception as e:
        # logger.error(f"Error fetching location for IP {ip}: {e}")
        return 'Unknown location'


def check_single_proxy_lo_de(proxy: str) -> str:
    try:
        parts = proxy.split(':')
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
        location = get_proxy_location_de(ip)
        try:
            response = requests.get('http://ifconfig.me/ip', proxies=http_proxies, timeout=5)

            if response.ok:
                return f'✅- {ip} - {location}'
        except:
            try:
                response = requests.get('http://ifconfig.me/ip', proxies=socks_proxies, timeout=5)
                if response.ok:
                    return f'✅ - SOCKS5 - {ip} - {location}'
            except:
                return f'🔴 - {ip}'
    except Exception as e:
        return f'🔴 - {ip}'
# Extract IP:PORT from proxy strings
async def check_proxies_lo_de(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    processing_message = await update.message.reply_text(" 🔄 Processing...")
    proxies = update.message.text.strip().split('\n')
    extracted = []
    # Regex tìm IP:PORT:USER:PASS ở đầu chuỗi
    pattern_full = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+:[^:\s/]+:[^:\s/]+)")

    # Regex tìm IP:PORT ở đầu chuỗi (nếu không có user:pass)
    pattern_basic = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+)")
    for proxy in proxies:
        match = pattern_full.search(proxy)
        if match:
            extracted.append(match.group(1))
        else:
            match = pattern_basic.search(proxy)
            if match:
                extracted.append(match.group(1))
    result_proxy = "\n".join(extracted)
    final_proxy = result_proxy.strip().split('\n')
    proxy_count = len(final_proxy)
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_single_proxy_lo_de, final_proxy))
    active_proxies = [result for result in results if '✅' in result]
    inactive_proxies = [result for result in results if '🔴' in result]
    sorted_results = active_proxies + inactive_proxies
    result_message = "\n".join(sorted_results)
    summary_message = f"\n📔 - Tổng số proxy : {proxy_count}"

    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_message.message_id)
    
    await update.message.reply_text(result_message + summary_message)
    
    # End the conversation
    return ConversationHandler.END

################################################################################
# TÁCH CHUỖI
async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Trải nghiệm Proxy chính hãng tại TimeCloud.vn. Hãy gửi danh sách proxy theo dạng IP:PORT:USER:PASS, mỗi proxy trên một dòng để kiểm tra.")
    return WAITING_FOR_PROXY_LIST


# Extract IP:PORT from proxy strings
async def handle_proxy_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    proxies = update.message.text.strip().split('\n')
    extracted = []
    
    # Regex tìm IP:PORT:USER:PASS ở đầu chuỗi
    pattern_full = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+:[^:\s/]+:[^:\s/]+)")

    # Regex tìm IP:PORT ở đầu chuỗi (nếu không có user:pass)
    pattern_basic = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+)")
    for proxy in proxies:
        match = pattern_full.search(proxy)
        if match:
            extracted.append(match.group(1))
        else:
            match = pattern_basic.search(proxy)
            if match:
                extracted.append(match.group(1))
    
    result_message = "\n".join(extracted)
    await update.message.reply_text(f"{result_message}")
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = await update.message.reply_text("✅ Done!")
    await asyncio.sleep(1)
    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message.message_id)
    except Exception as e:
        pass
    return ConversationHandler.END
####################################################################################

# Extract IP:PORT from proxy strings
async def tach_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    proxies = update.message.text.strip().split('\n')
    extracted = []
    # Regex tìm IP:PORT:USER:PASS ở đầu chuỗi
    pattern_full = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+:[^:\s/]+:[^:\s/]+)")

    # Regex tìm IP:PORT ở đầu chuỗi (nếu không có user:pass)
    pattern_basic = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+)")
    for proxy in proxies:
        match = pattern_full.search(proxy)
        if match:
            extracted.append(match.group(1))
        else:
            match = pattern_basic.search(proxy)
            if match:
                extracted.append(match.group(1))
    result_proxy = "\n".join(extracted)
    final_proxy = result_proxy.strip().split('\n')
    extracted_1=[]
    for proxy in final_proxy:
        part_proxy = proxy.split(":")
        if len(part_proxy)==4:
            ip_proxy = part_proxy[0]
            port_proxy = part_proxy[1]
            user_proxy = part_proxy[2]
            pass_proxy = part_proxy[3]
            final_proxy_tach = "✅ - "+proxy+"\n"+"➡IP: "+ip_proxy+"\n"+"➡PORT: "+port_proxy+"\n"+"➡USER: "+user_proxy+"\n"+"➡PASS: "+pass_proxy
            extracted_1.append(f'{final_proxy_tach}')

    result_message = "\n".join(extracted_1)
    await update.message.reply_text(f"{result_message}")
    
    return ConversationHandler.END

####################################################################################

# Extract IP:PORT from proxy strings
async def create_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    hwid = update.message.text.strip()
    def generate_key(hwid):
        hashed_hwid = hashlib.sha256(hwid.encode()).hexdigest().upper()
        return f"{hashed_hwid[:6]}-{hashed_hwid[6:12]}"

    # Lấy dữ liệu hiện tại từ file JSON trên GitHub
    def get_current_data():
        response = requests.get(API_URL, headers={'Authorization': f'token {GITHUB_TOKEN}'})
        if response.status_code == 200:
            content = response.json()
            data = json.loads(base64.b64decode(content['content']).decode())
            sha = content['sha']
            return data, sha
        else:
            # Nếu file chưa tồn tại, trả về dữ liệu rỗng
            return {"valid_keys": []}, None

    # Cập nhật file key.json bằng cách bổ sung dữ liệu mới
    def update_github_file(hwid):
        key = generate_key(hwid)
        data, sha = get_current_data()

        # Kiểm tra xem HWID đã tồn tại chưa để tránh trùng lặp
        if any(entry["hwid"] == hwid for entry in data["valid_keys"]):
            result = "HWID đã tồn tại trong danh sách! - Key:"+key
        else:

            # Thêm key mới vào danh sách
            data["valid_keys"].append({"key": key, "hwid": hwid})

            # Chuẩn bị dữ liệu để commit lên GitHub
            updated_content = json.dumps(data, indent=4)
            encoded_content = base64.b64encode(updated_content.encode()).decode()

            payload = {
                "message": f"Add new key for HWID {hwid}",
                "content": encoded_content,
                "sha": sha  # Bắt buộc để cập nhật file
            }

            response = requests.put(API_URL, headers={'Authorization': f'token {GITHUB_TOKEN}'}, json=payload)

            if response.status_code in [200, 201]:
                result = "Key kích hoạt: "+key
            else:
                print("Lỗi khi cập nhật file:", response.json())
        return result
    await update.message.reply_text(update_github_file(hwid=hwid))
    
    return ConversationHandler.END



################################################################################
#CHECK LẠI PROXY

async def recheck_proxies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    proxies = context.user_data.get('inactive_proxies', [])
    if not proxies:
        await update.callback_query.message.reply_text("Không có proxy nào cần kiểm tra lại.")
        return
    processing_message = await update.callback_query.message.reply_text(" 🔄 Processing...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_single_proxy, proxies))

    active_proxies = [result for result in results if '✅' in result]
    still_inactive_proxies = [result for result in results if '🔴' in result]
    sorted_results = active_proxies + still_inactive_proxies
    result_message = "\n".join(sorted_results)
    summary_message = f"\n📔 - Tổng số: {len(proxies)}"
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_message.message_id)
    await update.callback_query.message.reply_text(result_message + summary_message)
    context.user_data['inactive_proxies'] = [proxy.split(' - ')[1] for proxy in still_inactive_proxies]
    if still_inactive_proxies:
        keyboard = [
            [InlineKeyboardButton("🔁RE-CHECK !", callback_data='recheck_proxies')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text("Kiểm tra lại VPS/Proxy không hoạt động !", reply_markup=reply_markup)
##########################################################
#CHECK LẠI VPS

async def recheck_vps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    vps_1 = context.user_data.get('inactive_vps', [])
    if not vps_1:
        await update.callback_query.message.reply_text("Không có vps nào cần kiểm tra lại.")
        return
    processing_message = await update.callback_query.message.reply_text(" 🔄 Processing...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_rdp, vps_1))

    active_vps = [result for result in results if '✅' in result]
    still_inactive_vps = [result for result in results if '🔴' in result]
    sorted_results = active_vps + still_inactive_vps
    result_message = "\n".join(sorted_results)
    summary_message = f"\n📔 - Tổng số VPS: {len(vps_1)}"
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_message.message_id)
    await update.callback_query.message.reply_text(result_message + summary_message)
    context.user_data['inactive_vps'] = [proxy.split(' - ')[1] for proxy in still_inactive_vps]
    if still_inactive_vps:
        keyboard = [
            [InlineKeyboardButton("🔁RE-CHECK !", callback_data='recheck_vps')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text("Kiểm tra lại VPS không hoạt động !", reply_markup=reply_markup)





################################################################################

def main() -> None:
    # Thay 'YOUR_TOKEN' bằng token bạn nhận được từ BotFather
    application = Application.builder().token("7293405808:AAHQOs-nmp607D_4FXv_OlOnIdnQjs8JZLw").build()
    application.add_handler(CallbackQueryHandler(recheck_proxies, pattern='recheck_proxies'))
    application.add_handler(CallbackQueryHandler(recheck_vps, pattern='recheck_vps'))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('check_location', check_command)],
        states={
            WAITING_FOR_PROXY_LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_proxies_lo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    conv_handler_1 = ConversationHandler(
        entry_points=[CommandHandler('split', check_command)],
        states={
            WAITING_FOR_PROXY_LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_list)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    conv_handler_2 = ConversationHandler(
        entry_points=[CommandHandler('check_location_detail', check_command)],
        states={
            WAITING_FOR_PROXY_LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_proxies_lo_de)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    conv_handler_3 = ConversationHandler(
        entry_points=[CommandHandler('ip', check_command)],
        states={
            WAITING_FOR_PROXY_LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, tach_proxy)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    conv_handler_4 = ConversationHandler(
        entry_points=[CommandHandler('tao', check_command)],
        states={
            WAITING_FOR_PROXY_LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_key)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    conv_handler_5 = ConversationHandler(
        entry_points=[CommandHandler('vps', check_command)],
        states={
            WAITING_FOR_PROXY_LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_vps2)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    # Xử lý các lệnh
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(conv_handler_1)
    application.add_handler(conv_handler_2)
    application.add_handler(conv_handler_3)
    application.add_handler(conv_handler_4)
    application.add_handler(conv_handler_5)

    # Xử lý tin nhắn văn bản
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_proxies))

    # Bắt đầu bot
    application.run_polling()

if __name__ == '__main__':
    main()
