import requests
import re

def main():
    try:
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0','Content-Type':'application/x-www-form-urlencoded'}
        ret = requests.get(url="http://www.89ip.cn/tqdl.html?api=1&num=9999",headers=headers)
        text1 = re.findall(";\\n</script>\\n(.*)<br><br>",ret.text,re.S)
        for i in text1:
            data = i.split('<br>')
        return data
    except:
        return []

main()
