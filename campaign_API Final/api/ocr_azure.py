import re
import requests
import json
import time
from .fetch import examine_data_api



def ocr_data(img_url):
    print("inside ocr data--->")

    print("url ---> ",img_url)

    # <---- Enter Subscription key ------------->
    subscription_key = ''
    endpoint = 'https://whatsappcognitive.cognitiveservices.azure.com'

    text_recognition_url = endpoint + "/vision/v3.2/read/analyze"

    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    data = {'url': img_url}
    response = requests.post(text_recognition_url, headers=headers, json=data)
    print("resposne ----> ",response.headers)

    try:
        poll = True
        while (poll):
            print("inside while--")
            response_final = requests.get(response.headers["Operation-Location"], headers=headers)
            analysis = response_final.json()
            time.sleep(2)
            if ("analyzeResult" in analysis):
                poll = False
            if ("status" in analysis and analysis['status'] == 'failed'):
                poll = False

        resp = []
        rd = []

        if analysis['status'] == 'succeeded':
            resp = analysis['analyzeResult']['readResults'][0]['lines']
            for i in resp:
                rd.append(i['text'])
    except Exception as e:
        resp = []
        print("exception -> ",e)

    print("status ---> success")

    try:
        response = examine_data_api(resp)
        print("response ----> ",response)
        response = response
    except Exception as e:
        print("exception-------------> ",e)
        response = {}
    
    product      = response.get('prod_list','')
    chemist      = response.get('chem_name','')
    chemist_num  = response.get('chem_num','')
    distributor  = response.get('dist_name','')
    invoice_data = response.get('invoice_list','')

    print("product ----------> ",product,chemist,invoice_data)

    context = {
        'product': product,
        'chemist': chemist,
        'numbers': chemist_num,
        'distributor': distributor,
        'invoice': invoice_data,
        'img_url': img_url,
    }

    return context