import requests
import re

def main():
    try:
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0','Content-Type':'application/x-www-form-urlencoded'}
        ret = requests.get(url="http://www.66ip.cn/mo.php?sxb=&tqsl=10000&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=",headers=headers)
        text1 = re.findall(";\\r\\n</script>(.*)<br />",ret.text,re.S)
        for i in text1:
            i1 = i.replace("\r","")
            i2 = i1.replace("\n","")
            i3 = i2.replace("\t","")
            i4 = i3.replace(" ","")
            data = i4.split('<br/>')
        return data
    except:
        return []


main()
