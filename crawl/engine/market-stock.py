import json
import traceback
from datetime import datetime
import grequests
import requests
from bs4 import BeautifulSoup as BSoup

class MarketStockEngine:

    def fetch_company_list(self):
        url = 'http://stock.vietnammarkets.com/vietnam-stock-market.php'
        # url = 'http://stock.vietnammarkets.com/food-processing/ABT/'
        rs = (grequests.get(u) for u in [url])
        result = grequests.map(rs)
        page_content = None
        if len(result) > 0:
            if result[0] is None:
                return "PAGE_NOT_REACHED"
            if result[0].status_code == 200:
                page_content = result[0].content
            else:
                return "SERVER ERROR " + str(result[0].status_code)

        if page_content is None or page_content == '':
            return "PAGE_EMPTY"

        bs = BSoup(page_content, 'html.parser')
        datalist = []
        url2data = {}

        for tag in bs.find_all("p", "r1"):
            for tr in tag.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) != 4:
                    continue # make sure we have 4 columns

                ticker_td = tds[0]
                ticker_a = ticker_td.select("a")
                if ticker_a:
                    ticker_symbol = ticker_a[0].contents[0]
                    url = ticker_a[0].get("href")
                else:
                    continue

                company_name = self.extract_td_content(tds[1])
                data = {
                    'ticker symbol': ticker_symbol,
                    'url': url,
                    'company name': company_name,
                    'business': self.extract_td_content(tds[2]),
                    'Listing bourse': self.extract_td_content(tds[3])
                }
                url2data[url] = data
                datalist.append(data)

        with open('../result/company_index.json', 'w', encoding='utf-8') as f:
            json.dump(datalist, f, ensure_ascii=False)

        profiles = self.fetch_company_profiles(url2data)
        # profiles = self.fetch_company_profiles_slow(url2data)

        with open('../result/company_profiles.json', 'w', encoding='utf-8') as f:
            json.dump(profiles, f, ensure_ascii=False)

        return "OK"

    def fetch_company_profiles(self, url2data):
        profiles = []
        try:
            rs = (grequests.get(u) for u in url2data.keys())
            results = grequests.map(rs)
            for res in results:
                if res.status_code == 200:
                    company_data = url2data[res.url]
                    bs = BSoup(res.content, 'html.parser')
                    main_tbl = bs.find_all("table")[0]
                    profile = self.fetch_company_profile(main_tbl, company_data)
                    profiles.append(profile)
        except:
            pass

        return profiles

    def fetch_company_profiles_slow(self, url2data):
        profiles = []
        try:
            for url in url2data.keys():
                res = requests.get(url)
                if res.status_code == 200:
                    company_data = url2data[res.url]
                    bs = BSoup(res.content, 'html.parser')
                    main_tbl = bs.find_all("table")[0]
                    profile = self.fetch_company_profile(main_tbl, company_data)
                    profiles.append(profile)
        except:
            pass

        return profiles

    def fetch_company_profile(self, main_tbl, company_data):

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

    def extract_td_content(self, td_obj):
        if td_obj:
            return str(td_obj.contents[0])
        else:
            return '-'


if __name__ == 'builtins':
    start = datetime.now()
    print("Started at", start)
    # mse = MarketStockEngine()
    # msg = mse.fetch_company_list()
    # print(msg)
    end = datetime.now()
    print("Ended at", end)
    print("Duration", end-start)


    # Duration 0:27:17.354757

    