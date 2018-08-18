from pprint import pprint

from django.http import JsonResponse

from crawl.models import Company, CompanyInfo


def get_company_info(ticker_symbol, param_name):
    try:
        ci = CompanyInfo.objects.get(ticker_symbol=ticker_symbol, param_name=param_name)
        return ci.param_value
    except:
        return ''

def fetch_companies(request):
    company_list = []
    queryset = []
    queryset = Company.objects.all()
    company_name = request.GET.get('company_name', None)
    industry = request.GET.get('industry', None)
    revenue_gte = request.GET.get('revenue_gte', None)

    if company_name:
        queryset = Company.objects.filter(name__icontains=company_name)

    if revenue_gte:
        queryset = Company.objects.filter(revenue__gte=revenue_gte)

    if industry:
        queryset = Company.objects.filter(business__icontains=industry)

    pprint(queryset.query)
    for c in queryset:
        company_list.append(
            {
                'id': c.id,
                'company_url': c.url,
                'company_name': c.name,
                'company_email': get_company_info(c.ticker_symbol, 'company_email'),
                'company_website': get_company_info(c.ticker_symbol, 'company_website'),
                'company street address': get_company_info(c.ticker_symbol, 'company_address'),
                'country': 'Vietnam',
                'company description': get_company_info(c.ticker_symbol, 'company_description'),
                'company phone number': get_company_info(c.ticker_symbol, 'company_phone_number'),
                'company_revenue': c.revenue,
            }
        )

    pprint(company_list)
    return JsonResponse(
        {
            "status_code": 200,
            "message": "successful",
            "data": company_list
        },
    safe=False)
