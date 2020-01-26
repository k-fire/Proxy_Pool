import requests
import re
import threading

class startextract(threading.Thread):
    def __init__(self,i):
        super(startextract,self).__init__()
        self.i = i
    def run(self):
        global proxylist
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0','Content-Type':'application/x-www-form-urlencoded'}
        url='http://www.xicidaili.com/nn/%s'%(self.i)
        ret=requests.get(url=url,headers=headers,timeout=10)
        proxies=re.findall('<td class=\"country\"><img.*?<td>(.*?)</td>.*?<td>(.*?)</td>',ret.text,re.S)
        for i in proxies:
            proxy = ":".join(tuple(i))
            proxylist.append(proxy)


def extract():
    threadss=[]
    z = 10        # 爬取的页数
    for i in range(1,z+1):
            thread = startextract(i)
            threadss.append(thread)
    for t in threadss:
        t.start()
    for t in threadss:
        t.join()



def main():
    global proxylist
    num=0
    proxylist = []
    try:
        extract()
        return proxylist
    except:
        return []
