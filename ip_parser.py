import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def parse_config(config: str) -> dict:
    """
    کانفیگ vless/trojan رو پارس می‌کنه و اجزاش رو برمی‌گردونه
    """
    if not config.startswith(("vless://", "trojan://")):
        return {}

    # جدا کردن fragment (#...)
    fragment = ""
    if "#" in config:
        config, fragment = config.rsplit("#", 1)

    # پارس اصلی
    parsed = urlparse(config)

    # دربیاوردن آیپی خالص (بدون براکت IPv6)
    host = parsed.hostname  # urlparse خودش براکت IPv6 رو حذف می‌کنه
    port = parsed.port

    return {
        "scheme": parsed.scheme,
        "uuid": parsed.username,
        "host": host,
        "port": port,
        "params": parsed.query,
        "fragment": fragment,
        "original": config + ("#" + fragment if fragment else "")
    }


def replace_ip_in_config(config: str, new_ip: str) -> str:
    """
    آیپی داخل کانفیگ رو با new_ip عوض می‌کنه
    """
    if not config.startswith(("vless://", "trojan://")):
        return config

    # جدا کردن fragment
    fragment = ""
    if "#" in config:
        config, fragment = config.rsplit("#", 1)

    parsed = urlparse(config)

    # تشخیص IPv6 برای براکت‌گذاری
    def format_host(ip: str) -> str:
        if ":" in ip:  # IPv6
            return f"[{ip}]"
        return ip  # IPv4 یا دامنه

    old_netloc = parsed.netloc  # مثلاً uuid@[2a06:...]:443

    # جایگزینی host در netloc
    # فرمت: username@host:port
    uuid = parsed.username
    port = parsed.port
    new_netloc = f"{uuid}@{format_host(new_ip)}:{port}"

    # ساخت URL جدید
    new_parsed = parsed._replace(netloc=new_netloc)
    new_config = urlunparse(new_parsed)

    if fragment:
        new_config += "#" + fragment

    return new_config


# تست
if __name__ == "__main__":
    config = "vless://88331a00-6b99-4bcb-a612-dc6597e42cbb@[2a06:98c1:3120::3]:443?encryption=none&security=tls&sni=sUmmEr-lakE-1e0c.AsaD67.WORKers.DEv&alpn=http%2F1.1&fp=chrome&type=ws&host=summer-lake-1e0c.asad67.workers.dev&path=%2FeyJqdW5rIjoiQmlpaXVGUHkyNVg1IiwicHJvdG9jb2wiOiJ2bCIsIm1vZGUiOiJwcm94eWlwIiwicGFuZWxJUHMiOltdfQ%3D%3D%3Fed%3D2560#💦 5 - VLESS - IPv6 : 443"

    print("=== پارس کانفیگ ===")
    parsed = parse_config(config)
    for k, v in parsed.items():
        print(f"{k}: {v}")

    print("\n=== جایگزینی با IPv4 ===")
    new = replace_ip_in_config(config, "104.21.10.5")
    print(new)

    print("\n=== جایگزینی با IPv6 ===")
    new = replace_ip_in_config(config, "2606:4700:4700::1111")
    print(new)