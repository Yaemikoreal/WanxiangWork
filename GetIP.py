import requests

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        data = response.json()
        ip_address = data['ip']
        return ip_address
    except requests.exceptions.RequestException as e:
        print(f"Error getting public IP: {e}")
        return None

# 调用函数
public_ip = get_public_ip()
if public_ip:
    print(f"Your public IP address is: {public_ip}")
else:
    print("Could not retrieve your public IP address.")