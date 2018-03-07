from scrapy.selector import Selector
import pymysql as py
import requests


comm = py.connect(host="127.0.0.1", user="root", passwd="123456", db="test")
cursor = comm.cursor()


def crawl_ips():
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0"}

    for i in range(20):
        true_page = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)
        print(i)
        selector = Selector(text=true_page.text)
        all_trs = selector.css("#ip_list tr")

        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])
            all_tests = tr.css("td::text").extract()
            proxy_type = tr.xpath("td[6]/text()").extract()[0]

            ip = all_tests[0]
            port = all_tests[1]

            ip_list.append((ip, port, proxy_type, speed))

        for ip_info in ip_list:
            cursor.execute(
                '''insert proxy_ip(ip, port, proxy_type, speed) values('{0}', '{1}', '{2}', '{3}')ON DUPLICATE KEY UPDATE
                ip=VALUES(ip), port=VALUES(port), proxy_type=VALUES(proxy_type), speed=VALUES(speed)'''.format(
                        ip_info[0], ip_info[1], ip_info[2], ip_info[3])
            )
            comm.commit()


class Get_ip(object):

    def delete_ip(self, ip):
        delete_sql = '''
              delete from proxy_ip where ip='{0}'
              '''.format(ip)
        cursor.execute(delete_sql)
        comm.commit()
        return True

    def juge_ip(self, ip, port, proxy_type):
        http_url = "https://wwww.baidu.com"
        if proxy_type == "HTTP":
            proxy_url_http = "http://{0}:{1}".format(ip, port)
        else:
            proxy_url_http = "https://{0}:{1}".format(ip, port)
        print(proxy_url_http)
        try:
            proxy_dict = {
                "http": proxy_url_http
                }
            response = requests.get(http_url, proxies=proxy_dict, timeout=3)
            print(response.status_code)
        except Exception as e:
            print("代理地址无效")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code <300:
                print("代理地址有效")
                return True
            else:
                print("代理地址无效")
                self.delete_ip(ip)
                return False

    def random_ip(self):
        sql = "select ip, port, proxy_type from proxy_ip ORDER BY RAND() limit 1"
        cursor.execute(sql)
        comm.commit()
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            proxy_type = ip_info[2]
            print(proxy_type, "://", ip, ":", port)
            juge_re = self.juge_ip(ip, port, proxy_type)
            if juge_re:
                return "{3}://{0}:{1}".format(ip, port, proxy_type)
            else:
                return self.random_ip()

if __name__ =="__main__":
    # crawl_ips()//
    get_ip = Get_ip()
    get_ip.random_ip()