import json
from io import BytesIO

from bs4 import BeautifulSoup as BSoup, Tag, NavigableString
import pycurl
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# exec(open('market-stock.py').read())

class MarketStockEngine:

    def __init0__(self):
        self.driverExecutable = 'E:/proj/voc/chromedriver.exe'
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")

    def fetch_company_list(self):
        buffer = BytesIO()
        # url = 'http://localhost/static/vietnam-stock.html'
        url = 'http://stock.vietnammarkets.com/vietnam-stock-market.php'
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(pycurl.HTTPHEADER, ['Accept: application/json', 'X-Requested-By:MyClient'])
        c.setopt(pycurl.VERBOSE, 0)
        c.perform()
        c.close()
        data = buffer.getvalue()
        data = data.decode("utf-8")
        bs = BSoup(data, 'html.parser')
        cnt = 0
        datalist = []
        for tag in bs.find_all("p", "r1"):
            for tr in tag.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) != 4:
                    continue

                ticker_td = tds[0]
                ticker_a = ticker_td.select("a")
                if ticker_a:
                    ticker_symbol = ticker_a[0].contents[0]
                    url = ticker_a[0].get("href")
                else:
                    ticker_symbol = '-'
                    url = '-'

                data = {
                    'ticker symbol': ticker_symbol,
                    'url': url,
                    'company name': self.extract_content(tds[1]),
                    'business': self.extract_content(tds[2]),
                    'Listing bourse': self.extract_content(tds[3])
                }
                datalist.append(data)
                # print(data)

                # cnt += 1
                # if cnt > 3:
                #     break

        with open('company_index.json', 'w', encoding='utf-8') as f:
            json.dump(datalist, f, ensure_ascii=False)

    def fetch_company_info(self, url):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(pycurl.HTTPHEADER, ['Accept: application/json', 'X-Requested-By:MyClient'])
        c.setopt(pycurl.VERBOSE, 0)
        c.perform()
        c.close()
        data = buffer.getvalue()
        data = data.decode("utf-8")
        bs = BSoup(data, 'html.parser')
        cnt = 0

        main_tbl = bs.find_all("table")[0]
        company_profile_td = main_tbl.find_all("td")[0]
        # auditing_tr = main_tbl.find_all("tr")[1]
        # auditing_td = auditing_tr.find_all("td")[0]

        seglist = self.get_segment_list(main_tbl)
        auditing_company = self.get_info_segment(seglist, "auditing company")
        business_registration = self.get_info_segment(seglist, "business registration")
        print("auditing_company", auditing_company)
        print()
        print("business_registration", business_registration)


        clist = []
        for c in company_profile_td.contents:
            text = str(c).strip()
            if text.lower() == '<br/>':
                continue
            clist.append(text)

        # for idx, c in enumerate(clist):
        #     print(idx, c)

        data = {
            'address': clist[2],
            'phone1': clist[3],
            'phone2': clist[4],
            'email': clist[5],
            'website': clist[6]
        }
        # print(data)
        return

        for tag in bs.find_all("p", "r1"):
            for tr in tag.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) != 4:
                    continue

                ticker_td = tds[0]
                ticker_a = ticker_td.select("a")
                if ticker_a:
                    ticker_symbol = ticker_a[0].contents[0]
                    url = ticker_a[0].get("href")
                else:
                    ticker_symbol = '-'
                    url = '-'


                data = {
                    'ticker symbol': ticker_symbol,
                    'url': url,
                    'company name': self.extract_content(tds[1]),
                    'business': self.extract_content(tds[2]),
                    'Listing bourse': self.extract_content(tds[3])
                }
                print(data)

                cnt += 1
                if cnt > 3:
                    break

    def get_segment_list(self, main_tbl):
        seglist = []
        for td in main_tbl.find_all('td'):
            colspan = td.get("colspan")
            if str(colspan) == '2':
                for c in td.contents:
                    text = str(c).strip()
                    if text.lower() == '<br/>':
                        continue

                    seglist.append(text)

        return seglist

    def get_info_segment(self, seglist, segment_text):

        b_segment = False
        segment_arr = []
        for idx, c in enumerate(seglist):
            if c.lower().__contains__("<strong>"):
                b_segment = c.lower().__contains__(segment_text)

            if b_segment:
                segment_arr.append(c)

        return segment_arr[1:]

    def extract_content(self, td_obj):
        if td_obj:
            return str(td_obj.contents[0])
        else:
            return '-'


mse = MarketStockEngine()
mse.fetch_company_list()
# t = Tag()

# url = 'http://stock.vietnammarkets.com/others/ANV/'
# mse.fetch_company_info(url)
# print("*" * 50)
# print()
# url = 'http://stock.vietnammarkets.com/electric-and-electronics-equipment/VBH/'
# mse.fetch_company_info(url)
# print("*" * 50)
# print()
# url = 'http://stock.vietnammarkets.com/paper-and-wood-products/ILC/'
# url = 'http://stock.vietnammarkets.com/communication/EBS/'
# mse.fetch_company_info(url)

# bs = mse.fetch_company_list()
# print("fetch_company_list", "FINISHED")
# mse.parse_page(bs)
# mse = MarketStockEngine()
# mse.parse_page()