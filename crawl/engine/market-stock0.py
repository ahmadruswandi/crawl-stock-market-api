import json
from multiprocessing import Pool
from multiprocessing import cpu_count
from pprint import pprint
import traceback
from io import BytesIO

from bs4 import BeautifulSoup as BSoup, Tag, NavigableString
import pycurl

# exec(open('market-stock.py').read())

class MarketStockEngine:


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
        # bs = BSoup(data, 'xml.parser')
        cnt = 0
        datalist = []
        profilelist = []
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

                if ticker_symbol == '-':
                    continue

                company_name = self.extract_content(tds[1])
                print("Processing ...", ticker_symbol, company_name)
                data = {
                    'ticker symbol': ticker_symbol,
                    'url': url,
                    'company name': company_name,
                    'business': self.extract_content(tds[2]),
                    'Listing bourse': self.extract_content(tds[3])
                }

                profile = self.fetch_company_profile(data)
                if profile is None:
                    continue

                profilelist.append(profile)
                datalist.append(data)
                cnt += 1
                # if cnt > 1:
                #     break


        # with open('company_index.json', 'w', encoding='utf-8') as f:
        #     json.dump(datalist, f, ensure_ascii=False)
        #
        # with open('company_profiles.json', 'w', encoding='utf-8') as f:
        #     json.dump(profilelist, f, ensure_ascii=False)

    def fetch_company_profile(self, company_data):

        try:
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(pycurl.URL, company_data['url'])
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(pycurl.HTTPHEADER, ['Accept: application/json', 'X-Requested-By:MyClient'])
            c.setopt(pycurl.VERBOSE, 0)
            c.perform()
            c.close()
            data = buffer.getvalue()
            data = data.decode("utf-8")
            bs = BSoup(data, 'html.parser')

            main_tbl = bs.find_all("table")[0]
        except:
            return None

        financial_data = self.get_financial_data(main_tbl)

        company_profile_td = main_tbl.find_all("td")[0]

        seglist = self.get_segment_list(main_tbl)
        auditing_company = self.get_info_segment(seglist, "auditing company")
        business_registration = self.get_business_reg(seglist)
        business_summary = self.get_info_segment(seglist, "business summary")

        clist = []
        for c in company_profile_td.contents:
            text = str(c).strip()
            if text.lower() == '<br/>':
                continue
            clist.append(text)

        address = clist[2]
        phone1, phone2 = clist[3], clist[4]
        email, website = clist[5], clist[6]

        profile = {
            "company name": company_data['company name'],
            "url": company_data['url'],
            "company_address": address,
            "country": "Vietnam",
            "company_description": business_summary,
            "company_phone_number": [phone1, phone2],
            "company_industry": company_data['business'],
            "company_website": website,
            "company_email": email,
            "revenue": '-' if financial_data is None else financial_data['Market Cap'],
            "ticker symbol": company_data['ticker symbol'],
            "financial summary": financial_data,
            # "business registration": {"established licence": "", "business license": ""},
            "business registration": business_registration,
            # "auditing company": {"company_name": "", "address": "", "phone_number": "", "other...": "..."}
            "auditing company": auditing_company
        }

        return profile

    def get_business_reg(self, seglist):
        br = self.get_info_segment(seglist, "business registration")

        try:
            br_data = {'established license': '', 'business license': ''}
            for b in br:
                arr = b.split(":")
                if len(arr) == 2:
                    if arr[0] == 'Established License':
                        br_data['established license'] = arr[1]
                    if arr[0] == 'Business License':
                        br_data['business license'] = arr[1]
        except:
            pass

        return br_data

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


    def get_financial_data(self, main_tbl):
        financial_tbl = main_tbl.find_all("table")[0]
        financial_data = {}
        for tr in financial_tbl.find_all("tr"):
            try:
                label = str(tr.find_all("td")[0].contents[0]).strip()
                value = str(tr.find_all("td")[1].contents[0]).strip()
                label = label.replace("<strong>", "")
                label = label.replace(":</strong>", "")
                financial_data[label] = value
            except:
                # traceback.print_exc()
                pass

        return financial_data

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


from datetime import datetime
start = datetime.now()
mse = MarketStockEngine()
mse.fetch_company_list()

# pool = Pool(cpu_count() * 2)
# with pool as p:
#     records = p.map(parse, cars_links)

end = datetime.now()
print("Duration", end-start)
# with open('company_profiles.json') as f:
#     data = json.load(f)


urls = [
# 'http://stock.vietnammarkets.com/general-industries/BBS/'
]

# url = 'http://stock.vietnammarkets.com/others/ANV/'
# url = 'http://stock.vietnammarkets.com/electric-and-electronics-equipment/VBH/'
# url = 'http://stock.vietnammarkets.com/paper-and-wood-products/ILC/'
# url = 'http://stock.vietnammarkets.com/communication/EBS/'

# Duration 0:27:17.354757