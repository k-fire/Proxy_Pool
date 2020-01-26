import requests
from lxml import etree
import time

def main():
    try:
        list = []
        for id in range(1,11):
            url = "https://www.kuaidaili.com/free/inha/%s/"%id
            headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0','Content-Type':'application/x-www-form-urlencoded'}
            ret = requests.get(url=url,headers=headers)
            html = etree.HTML(ret.text)
            ip = html.xpath("/html/body/div/div[4]/div[2]/div/div[2]/table/tbody/tr/td[1]/text()")
            port = html.xpath("/html/body/div/div[4]/div[2]/div/div[2]/table/tbody/tr/td[2]/text()")
            proxy_list = zip(ip,port)
            for i in proxy_list:
                proxy = ":".join(i)
                list.append(proxy)
            time.sleep(1)
        return list
    except:
        return []

main()
