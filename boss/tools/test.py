import requests

def ip():

    if proxy_type == "HTTP":
        proxy_url_http = "http://{0}:{1}".format(ip, port)
    else:
        proxy_url_http = "https://{0}:{1}".format(ip, port)
    print(proxy_url_http)
    try:
        proxy_dict = {
            "http": proxy_url_http
        }
        response = requests.get(http_url, proxies=proxy_dict)
        print(response)
    except Exception as e:
        print("代理地址无效")
        self.delete_ip(ip)
        return False
    else:
        code = response.status_code
        if code >= 200 and code < 300:
            print("代理地址有效")
            return True
        else:
            print("代理地址无效")
            self.delete_ip(ip)
            return False


http_url = "http://www.xicidaili.com/nn"
proxy_dict = {
    "http": "118.114.77.47:8080"
}
response = requests.get(http_url, proxies=proxy_dict)
print(response)