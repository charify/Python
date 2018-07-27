#coding=utf-8
import requests
import re
import xlwt

#解析http://ris.szpl.gov.cn/bol/数据
class ParseRISURL:
    url = 'http://ris.szpl.gov.cn/bol/index.aspx'

    header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'ris.szpl.gov.cn',
    'Origin': 'http://ris.szpl.gov.cn',
    'Referer': 'http://ris.szpl.gov.cn/bol/index.aspx',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }

    data = {
    '__EVENTTARGET':'',
    '__EVENTARGUMENT':'',
    '__VIEWSTATE':'',
    '__VIEWSTATEGENERATOR':'',
    '__VIEWSTATEENCRYPTED':'',
    '__EVENTVALIDATION': '',
    'tep_name':'',
    'organ_name':'',
    'site_address':'',
    'AspNetPager1_input': '1',
    'AspNetPager1': 'go'
    }

    pageDatas = []

    def init_url(self):
        result = requests.get(self.url, headers=self.header)
        self.update_VIEWSTATE(result.text)
        self.update_EVENTVALIDATION(result.text)
        self.update_VIEWSTATEGENERATOR(result.text)
        self.get_totalNum(result.text)
        self.get_totalPage(result.text)

    def update_VIEWSTATE(self,urlText):
        self.data["__VIEWSTATE"] = re.findall('id="__VIEWSTATE".*?>', urlText)[0][24:-4]

    def update_VIEWSTATEGENERATOR(self,urlText):
        self.data["__VIEWSTATEGENERATOR"] = re.findall('id="__VIEWSTATEGENERATOR".*?>', urlText)[0][33:-4]

    def update_EVENTVALIDATION(self,urlText):
        self.data['__EVENTVALIDATION'] = re.findall('id="__EVENTVALIDATION".*?>', urlText)[0][30:-4]

    def update_pageNum(self,num):
        self.data['AspNetPager1_input'] = num


    def get_totalPage(self,urlText):
        self.totalPage = int(re.findall('总共<b>.*?</b>', urlText)[0][5:-4])

    def get_currentPage(self,urlText):
        self.currentPage = int(re.findall('当前为第<b>.*?</b>', urlText)[0][7:-4])

    def get_totalNum(self,urlText):
        self.totalNum = int(re.findall('共<b>.*?</b>条', urlText)[0][4:-5])



    #http://ris.szpl.gov.cn/bol/certdetail.aspx?    预售项目
    #http://ris.szpl.gov.cn/bol/hezuo.aspx?         项目合作方资料
    #http://ris.szpl.gov.cn/bol/projectdetail.aspx? 项目详细资料


    result = requests.post('http://ris.szpl.gov.cn/bol/index.aspx',headers = header,data=data)

    trs = re.findall('<td.*?</td>',result.text)

    def parseData(self,urlText):
        tds = re.findall('<td.*?</td>',result.text)
        try:
            for idx in range(0,len(tds)-1,6):
                temp = {
                    'id':'',
                    'preLicense':'',
                    'houseName':'',
                    'developer':'',
                    'area':'',
                    'date':''
                }
                temp['id'] = re.findall("id=[0-9]*?'",tds[idx+1])[0][3:-1]
                temp['preLicense'] = re.findall("'>.*?</a>",tds[idx+1])[0][2:-4]
                temp['houseName'] = re.findall("'>.*?</a>",tds[idx+2])[0][2:-4]
                temp['developer'] = re.findall(">.*?<",tds[idx+3])[0][1:-1]
                temp['area'] = re.findall(">.*?<",tds[idx+4])[0][1:-1]
                temp['date'] = re.findall(">.*?<",tds[idx+5])[0][1:-1]
                self.pageDatas.append(temp)
        except:
            print (str(id)+'--------ERROR--------')
        return self.pageDatas






ris = ParseRISURL()
ris.init_url()
#workbook = xlwt.Workbook(encoding='ascii')
#worksheet = workbook.add_sheet('House')


for i in range(0,ris.totalPage):
    try:
        with open("D:\\house.txt", "w+", encoding='utf-8') as f:
            print(i)
            ris.update_pageNum(i)
            result = requests.post(ris.url,headers = ris.header, data= ris.data)
            ris.update_EVENTVALIDATION(result.text)
            ris.update_VIEWSTATEGENERATOR(result.text)
            ris.update_VIEWSTATE(result.text)
            out = ris.parseData(result.text)
            for idx in range(0,len(out)):
                f.write(out[idx]['id']+'\t'+out[idx]['preLicense']+'\t'+out[idx]['houseName']+'\t'+out[idx]['developer']+'\t'+out[idx]['area']+'\t'+out[idx]['date']+'\n')
                '''
                worksheet.write(idx, 0, out[idx]['id'])
                worksheet.write(idx, 1, out[idx]['preLicense'])
                worksheet.write(idx, 2, out[idx]['houseName'])
                worksheet.write(idx, 3, out[idx]['developer'])
                worksheet.write(idx, 4, out[idx]['area'])
                worksheet.write(idx, 5, out[idx]['date'])
                '''
    finally:
        #workbook.save("D:\\house.xls")
        f.close()
