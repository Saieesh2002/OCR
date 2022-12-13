from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from binascii import a2b_base64
import os
from pathlib import Path
import re
import requests
import json
import time
from django.conf import settings



def examine_data_api(resp):
    print("inside examine_data api")
    resp = resp
    # print("resp --------> ",resp)
    rd = []
    for i in resp:
        rd.append(i['text'])

    # print("resp -------> ",resp)
    print("rd ---------> ",rd)  
    

    #<-------------------------- product detail:name/qty --------------------------------------->
    prod = {}
    prod_list = []
    i_q = ''
    i_n = ''

    for i in rd:
        if re.search("qty|qnty|quantity|qty.|onty|otv|gty|oty", i, re.IGNORECASE):
            # print(i)
            if len(i.split(' ')) < 3:
                i_q = rd.index(i)
                i_n = i_q + 1
                # i_p = i_q - 1
                break
            else:
                i_q = rd.index(i)
                i_n = i_q + 1


    print("indexes -----> ",i_q,i_n)



    cq = resp[i_q]
    cn = resp[i_n]
    # cp = resp[i_p]

    print("cq ----> ",cq)
    print("\ncn ----> ",cn)
    # print("c3 ----> ",cp)

    for i in cq['words']:
        if re.search("qty|qnty|quantity|onty|qty.|otv|gty|oty", i['text'], re.IGNORECASE):
            x_min = i['boundingBox'][0]-5
            x_max = i['boundingBox'][2]+10


    print("\nx ---> ",x_min,x_max)
    i_c = []
    rd_copy = rd
    for i in rd_copy:
        if re.search("omez|nise|dmez|mise", i, re.IGNORECASE) and not re.search("ultranise", i, re.IGNORECASE):
            i_c.append(rd_copy.index(i))
            if re.search("omez|dmez", i, re.IGNORECASE) and re.search("dsr|osr|d sr|d sk|-d|use|der", i, re.IGNORECASE):
                prod['name'] = "OMEZ D SR"
            elif re.search("omez o|dmez o|dmezo|dmez d|omez d", i, re.IGNORECASE):
                prod['name'] = "OMEZ D"
            elif re.search("omez|dmez", i, re.IGNORECASE):
                prod['name'] = "OMEZ"
            elif re.search("nise|mise", i, re.IGNORECASE):
                prod['name'] = "NISE"
            prod['qty'] = ''
            prod_list.append(prod)
            rd_copy.pop(rd_copy.index(i))
            prod = {}
            # break
            
    print("prod_list name updated ---> ",prod_list)
    print("i_c updated            ---> ",i_c)

    prod_list_len = 0
    for index in i_c:
        
        cc = resp[index]
        dict_index = 0


        y_min = cc['boundingBox'][1] if cc['boundingBox'][1] < cc['boundingBox'][3] else cc['boundingBox'][3]
        y_max = cc['boundingBox'][5] if cc['boundingBox'][5] > cc['boundingBox'][7] else cc['boundingBox'][7]



        print("\ny ----> ",y_min,y_max)



        for k in resp:
            for i in k['words']:
                if x_min <= (i['boundingBox'][0]+i['boundingBox'][2])/2 <= x_max and y_min <= (i['boundingBox'][1]+i['boundingBox'][5])/2 <= y_max:
                    print("\ni (1)-----> ",i)
                    if i['confidence'] > .3:
                        prod_list[prod_list_len]['qty'] = i['text'].replace('/','').replace('\\','')
                        dict_index += 1
        if not prod_list[prod_list_len]['qty']:
            for k in resp:
                for i in k['words']:
                    if x_min <= (i['boundingBox'][0]+i['boundingBox'][2])/2 <= x_max and y_min-10 <= (i['boundingBox'][1]+i['boundingBox'][3])/2 <= y_max+10:
                        print("\ni (2)-----> ",i)
                        if i['confidence'] > .3:
                            prod_list[prod_list_len]['qty'] = i['text'].replace('/','').replace('\\','')
                            dict_index += 1
        if not prod_list[prod_list_len]['qty']:
            for k in resp:
                for i in k['words']:
                    if x_min <= (i['boundingBox'][0]+i['boundingBox'][2])/2 <= x_max and y_min-20 <= (i['boundingBox'][1]+i['boundingBox'][3])/2 <= y_max+20:
                        print("\ni (3)-----> ",i)
                        if i['confidence'] > .3:
                            prod_list[prod_list_len]['qty'] = i['text'].replace('/','').replace('\\','')
                            dict_index += 1
        prod_list_len += 1
        
    print("prod_list final ----> ",prod_list)

#<-------------------------- product detail:name/qty --------------------------------------->

#<-------------------------- invoice detail:amount/number/date --------------------------------------->

    # Invoice number------------------------>


    inv_num = ''
    invn_index = ''
    for i in rd:
        if not re.search("billed|biiled to|gst invoice|tax invoice", i, re.IGNORECASE) and re.search("invoice number|invoice no|bill no|inv no|inv.no|bill|gst inv:|gstinv:|Tov . No|tnv.no|memo no|inv.", i, re.IGNORECASE):
            if i.upper() != 'INVOICE' and i.upper() != 'CREDIT BILL':
                print("\n i---------------<< ",i)
                invn_index = rd.index(i)
                break

    print("invn_index ----> ",invn_index)


    try:
        if re.search('\d',rd[invn_index]) and 'DATE' not in rd[invn_index].upper() :
            inv_num = rd[invn_index].upper().replace('INVOICE NUMBER','').replace('INVOICE NO','').replace('BILL NO','').replace('INV NO','').replace('INVNO','').replace('INV.NO','').replace('BILL','').replace('GST INV:','').replace('GSTINV:','').replace('TNV.NO','').replace('INV.','').replace('.','').replace(':','').replace('TOV  NO','').replace('MEMO NO','')
            print("inv_num (1) --------> ",inv_num)
        elif re.search('\d',rd[invn_index+1]) and 'DATE' not in rd[invn_index+1].upper():
            print("inv_num inside---> ",rd[invn_index+1])
            inv_num = rd[invn_index+1].replace('.','').replace(':','')
    except Exception as e:
        print("Exception not inv------------> ",e)


    if not inv_num and invn_index:
        invn_box = resp[invn_index]
        print("invn_box ----> ",invn_box ,"\n" ,resp[invn_index+1])
        x_min = ''
        x_max = ''
        y_min = ''
        y_max = ''
        for i in invn_box['words']:
            print("i(1)---->",i)
            if re.search("invoice number|invoice no|bill no|inv no|inv.no|bill|gst inv|memo|", i['text'], re.IGNORECASE):
                x_min = i['boundingBox'][0]-5
                x_max = i['boundingBox'][2]+10
                y_min = i['boundingBox'][1]-5
                y_max = i['boundingBox'][5]+2
        if not x_min:
            x_min = invn_box['boundingBox'][0]-5
            x_max = invn_box['boundingBox'][2]+10
            y_min = invn_box['boundingBox'][1]-7
            y_max = invn_box['boundingBox'][5]+2   
            
        print("\nx,y -----> ",x_min,x_max,y_min,y_max) 

        for k in resp:
            for i in k['words']:
                if x_max+10 <= (i['boundingBox'][0]+i['boundingBox'][2])/2 <= x_max+80 and y_min <= (i['boundingBox'][1]+i['boundingBox'][3])/2 <= y_max:
                    print("i(2) ---> ",i)
                    if re.search('\d',i['text']):
                        print("\ninv_num in reg -----> ",i['text'])
                        inv_num = i['text'].replace('-','')

        if not inv_num:
            for k in resp:
                for i in k['words']:
                    if x_min <= (i['boundingBox'][0]+i['boundingBox'][2])/2 <= x_max and y_max <= (i['boundingBox'][1]+i['boundingBox'][3])/2 <= y_max+5:
                        if re.search('\d',i['text']):
                            print("\inv_num in reg if-----> ",i['text'])
                            inv_num = i['text']


    # Invoice number------------------------>

    # Invoice date-------------------------->


    date = ''
    date_index = ''
    for i in rd:
        if not re.search("due date", i, re.IGNORECASE):
            if re.search("date|inv date|dated|invoice date|bill date|inv.dt", i, re.IGNORECASE):
                print("\n i---------------<< ",i)
                date_index = rd.index(i)
                break

    print("date_index ----> ",date_index)
    print("date_index ----> ",rd[date_index])
    print("date_index ----> ",rd[date_index+1])


    try:
        if re.search('([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])|(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])',rd[date_index]):
            date = re.search('([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])|(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])',rd[date_index])[0]
            print("date (1) --------> ",date)
        elif re.search('([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])|(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])',rd[date_index+1]):
            date = re.search('([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])|(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])',rd[date_index+1])[0]
            print("date inside---> ",date)
        elif not date:
            invdate_box = resp[date_index]
            print("invdate_box ----> ",invdate_box)
            x_min = ''
            x_max = ''
            y_min = ''
            y_max = ''
            for i in invdate_box['words']:
                print("i date(1)---->",i)
                if re.search("date|inv date|dated|invoice date|bill date|inv.dt", i['text'], re.IGNORECASE):
                    x_min = i['boundingBox'][0]-5
                    x_max = i['boundingBox'][2]+10
                    y_min = i['boundingBox'][1]-5
                    y_max = i['boundingBox'][5]+2
            if not x_min:
                x_min = invdate_box['boundingBox'][0]-5
                x_max = invdate_box['boundingBox'][2]+10
                y_min = invdate_box['boundingBox'][1]-5
                y_max = invdate_box['boundingBox'][5]+5
                
            print("\nx,y -----> ",x_min,x_max,y_min,y_max)

            for k in resp:
                for i in k['words']:
                    if x_max+10 <= (i['boundingBox'][0]+i['boundingBox'][2])/2 <= x_max+80 and y_min <= (i['boundingBox'][1]+i['boundingBox'][3])/2 <= y_max:
                        print("i date(2) ---> ",i)
                        if re.search('\d',i['text']):
                            print("\ndate in box block(1) -----> ",i['text'])
                            date = i['text']

            if not date:
                for k in resp:
                    for i in k['words']:
                        if x_min <= (i['boundingBox'][0]+i['boundingBox'][2])/2 <= x_max and y_max <= (i['boundingBox'][1]+i['boundingBox'][3])/2 <= y_max+5:
                            if re.search('\d',i['text']):
                                print("\date in box block(2)-----> ",i['text'])
                                date = i['text']
            
    except Exception as e:
        print("Exception ------------> ",e)

    # date = ''

    if not date:
        for i in rd:
            if re.search('([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])|(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])',i):
                date = re.search('([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])|(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])',i)[0]
                print("date (2) --------> ",date)
                print("date (3) --------> ",re.search('([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])|(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])',i)[0])
                break
                
    invoice_list = {'inv_num': inv_num.strip(), 'date': date}
    # Invoice date-------------------------->

#<-------------------------- invoice detail:amount/number/date --------------------------------------->

#<-------------------------- chemist detail:name --------------------------------------->
    # chemist name ---------------------->
    chem_name = ''
    chem_list = []

    try:
        for i in rd:
            if re.search("m/s|to|party", i, re.IGNORECASE) and re.search("pharma|pharmacy|chemist|medical|med", i, re.IGNORECASE) and not re.search("agency|agencies|pvt.|ltd.|distributor", i, re.IGNORECASE):
                print("chemist name(0) ----> ",i)
                i = i.upper()
                chem_name = i.replace('M/S','').replace('PARTY','').replace(',','').replace('.','').replace('CUSTOMER','').replace(':','')
                chem = chem_name.split(' ')
                cl = []
                if len(chem) > 1:
                    for i in chem:
                        if 'TO' in i and len(i) == 2:
                            pass
                        else:
                            cl.append(i)
                chem_name = ' '.join(cl)
                break
                            
    except Exception as e:
        print("Exception ----> ",e)

    if not chem_name:
        for i in rd:
            if re.search("pharma|pharmacy|chemist|agencies|agency|distributor|medical|med|pvt.|ltd.|ENTERPRISE", i, re.IGNORECASE):
                chem_list.append(i)
                # break
        
        if len(chem_list) > 1:
            if re.search("pharma|pharmacy|chemist|medical|med", chem_list[1], re.IGNORECASE) and not re.search("agency|agencies|pvt.|ltd.|ENTERPRISE", chem_list[1], re.IGNORECASE):
                print("chemist name(1) ----> ",chem_list[1])
                chem_name = chem_list[1].replace('M/S','').replace('PARTY','').replace('.','')
                chem = chem_name.split(' ')
                cl = []
                if len(chem) > 1:
                    for i in chem:
                        if 'TO' in i and len(i) == 2:
                            pass
                        else:
                            cl.append(i)
                    chem_name = ' '.join(cl)

    # for contact number
    number = []
    for i in rd:
        num = re.findall(r"[\d]{10}", i)
        if len(num) > 0 and int(num[0][0])>5:
            number.append(','.join(num))
    chem_num = ','.join(number)
    # chemist name ---------------------->

#<-------------------------- chemist detail:name --------------------------------------->

#<-------------------------- distributor detail:name --------------------------------------->
    dist_name = ''
    dist_list = []

    try:
        for i in rd:
            if re.search("pharma|pharmacy|chemist|medical|med|drug", i, re.IGNORECASE) and re.search("agency|agencies|pvt.|ltd.|distributor|enterprise|nterprise|sales|pharmaceutical|meditrade|private|limited|associate|surgical|house|hall", i, re.IGNORECASE):
                print("distributor name(0) ----> ",i)
                dist_name = i.upper().replace('.','')
                break
                            
    except Exception as e:
        print("Exception ----> ",e)

    if not dist_name:
        for i in rd:
            if re.search("pharma|pharmacy|chemist|agencies|agency|distributor|medical|med|pvt.|ltd.|ENTERPRISE|nterprise|sales|pharmaceutical|meditrade|private|limited|associate|house|hall", i, re.IGNORECASE):
                dist_list.append(i)
                # break
        
        if len(dist_list) > 1:
            if re.search("agency|agencies|pvt.|ltd.|ENTERPRISE|sales|pharmaceutical|meditrade|associate|house|hall", dist_list[0], re.IGNORECASE):
                print("distributor name(1) ----> ",dist_list[0])
                dist_name = dist_list[0].replace('.','')

#<-------------------------- chemist distributor:name --------------------------------------->

    return {
        'prod_list' : prod_list,
        'chem_name': chem_name.strip(),
        'chem_num' : chem_num,
        'dist_name': dist_name.strip(),
        'invoice_list': invoice_list,
        }