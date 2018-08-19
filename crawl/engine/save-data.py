import json
import re
from pprint import pprint

from crawl.models import Company, CompanyInfo


class SaveMarketStock:

    def read_json_file(self):

        # prepare listing bourse
        bourse_map = {}
        with open('../result/company_index.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for idx, d in enumerate(data):
                try:
                    bourse_map[d['ticker symbol']] = d['Listing bourse']
                except:
                    bourse_map[d['ticker symbol']] = '-'

        with open('../result/company_profiles.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for idx, d in enumerate(data):
                d['listing_bourse'] = bourse_map[d['ticker symbol']]
                self.save(d, idx+1)


    def save(self, data, idx):
        ticker_symbol = data['ticker symbol']
        try:
            company = Company.objects.get(ticker_symbol=ticker_symbol)
        except:
            company = Company()

        company.id = idx
            
        company.ticker_symbol = ticker_symbol
        company.url = data['url']
        company.business = data['company_industry']
        company.listing_bourse = data['listing_bourse']
        company.name = data['company name']
        revenue = re.sub(r'\D', "", data['revenue'])
        company.revenue = revenue
        company.save()
        for key in data.keys():
            # print(key, data[key])
            self.save_company_info(ticker_symbol, key, data[key])

    def save_company_info(self, ticker_symbol, param_name, param_value):
        try:
            ci = CompanyInfo.objects.get(ticker_symbol=ticker_symbol, param_name=param_name)
        except:
            ci = CompanyInfo(ticker_symbol=ticker_symbol, param_name=param_name)

        try:
            ci.param_value = param_value
            ci.save()
        except:
            print(len(param_value))


sms = SaveMarketStock()
sms.read_json_file()