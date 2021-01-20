#-*- coding:utf-8 -*-
import requests
import re
import time
import ast
import glob
import shutil
import codecs
import os
import urllib.request
from bs4 import BeautifulSoup
import pandas as pds
from urllib import parse
import csv_gspread

#저장속도가 느리다면 아래 !@#$ 표시된 print 부분을 주석처리해주세요.
date_list = ['20190927','20210111','20210112'] #해당 부분에 추출하실 날짜를 "20190101","20190102" 형식으로 모두 입력해주세요.
category = '패션·잡화' #형식으로 맞춰주세요
page_list = []#패션-잡화 부분의 모든 상품페이지 주소가 담길 리스트
all_list = [] #최종 결과값이 저장 될 리스트
save_list = []#크롤링 후 결과가 저장 될 리스트
remove_list = [] #최종 중복제거 후 csv로 저장 될 리스트

class WebRequest: # 웹과 관련된 함수 클래스
    def get_bs_obj(url): # 웹에서 소스코드를 받아오는 함수
        result=requests.get(url)
        bs_object=BeautifulSoup(result.content,"html.parser")
        return bs_object

    def download(uri, file_name = None): # 이미지 다운로드 함수
        try:
            url = uri

            outpath = os.path.dirname(os.path.realpath(__file__)) + "\\image\\"
            outfile = file_name

            if not os.path.isdir(outpath):
                os.makedirs(outpath)

            # download
            urllib.request.urlretrieve(url, outpath+outfile)
        except Exception as e:
             return ("404 Error")
        else:
            return ("complete!")

    def get_pageData(date): # 크롤링 함수
            url="http://hsmoa.com/?date="+str(date)+"&site=&cate=" + category
            bs_object=WebRequest.get_bs_obj(url)
            save_list.append(['Date','time', 'corpus','category', 'title','price','link','error'])
            all_list.append(['Date','time', 'corpus','category', 'title','price','link','error'])
            divclass = bs_object.find_all("div",{"class":re.compile("^" + category)})
            for url in divclass:
                page_list.append(url.select('a')[0].get('href'))

                sametime_block = url.find("div",{"class":"sametime-block"})

                if sametime_block:

                    all_sametime_block = sametime_block.find_all("a",{"class":re.compile("^" + category)})
                    for a_class in all_sametime_block:
                        if 'href' in a_class.attrs:
                            page_list.append(a_class.attrs['href'])

            for result in page_list:
                bs_object = WebRequest.get_bs_obj("http://hsmoa.com" + result)

                titles = bs_object.find_all("meta",{"property":"og:title"})
                for txt in titles:
                    title = txt.get('content')

                product_images = bs_object.find_all("meta",{"property":"og:image"})

                for image in product_images:
                    image_url = image.get('content') #이미지 링크를 가져옴
                    #print(title)
                    #print(image_url)
                    image_result = ""#WebRequest.download(image_url,title.replace("[","").replace("]","").replace("/","").replace("|","").replace("\\","").replace(":","").replace("*","").replace("?","").replace("<","").replace(">","").replace("\"","") + ".png")
                    # 다운로드 후, 윈도우에서 정한 파일명으로 사용할 수 없는 문자 필터링
                    
                    #time.sleep(0.3) # 일시적인 0.3 sleep
                    

                price_score = bs_object.find('div',{'class':'font-24 c-red strong'}).text

                price =  price_score.replace("\n","").replace(" ","")

                Airtime = bs_object.find_all('td',{'style':'color: #222; font-size: 14px; vertical-align: top;  letter-spacing: -1px; line-height:18px;'})

                if Airtime:
                    shop_corpus = Airtime[0].get_text().replace("\n","").replace(" ","")
                    airtime_result = Airtime[1].get_text().replace("\n","").replace(" ","")
                else:
                    Airtime = bs_object.find_all('span',{'class':'c-gray font-20'})
                    result_airtime = Airtime[0].get_text().split(' ')
                    shop_corpus = result_airtime[1]
                    airtime_result = result_airtime[2]
                    
                dt_parse = airtime_result.split('일')  
                Date_result = dt_parse[0] + '일'
                time_result = dt_parse[1]
                
                save_list.append([Date_result,time_result,shop_corpus,category,title,price,"http://hsmoa.com/" + result,""])
                all_list.append([Date_result,time_result,shop_corpus,category,title,price,"http://hsmoa.com/" + result,""])

class EtcFunction: #기타 함수 클래스
    def convert_str(x):
        if type(x) is str:
            return "'" + x + "'"
        else:
            return str(x)

    def csvSave(list_item): #csv를 저장하는 소스코드
        outpath = os.path.dirname(os.path.realpath(__file__)) + "\\Result\\"

        if not os.path.isdir(outpath):
            os.makedirs(outpath)
            
        data = pds.DataFrame(list_item)
        data.columns = ['Date','time', 'corpus','category', 'title','price','link','error']
        data.head()
        data.to_csv(outpath + 'Crollwing_result_' + str(date_num)+'.csv',index=False,encoding='utf-8')
        save_list.clear()
        page_list.clear()

    def AddCsv():
        outpath = os.path.dirname(os.path.realpath(__file__)) + "\\Result\\"
        input_file = outpath # csv파일들이 있는 디렉토리 위치
        output_file = outpath + 'Crollwing_result.csv' # 병합하고 저장하려는 파일명
        frame = pds.DataFrame()

        allFile_list = glob.glob(os.path.join(input_file, 'Crollwing_result_*')) # glob함수로 Crollwing_result_로 시작하는 파일들을 모은다
        print(allFile_list)
        allData = [] # 읽어 들인 csv파일 내용을 저장할 빈 리스트를 하나 만든다
        for file in allFile_list:
            allData.append(pds.read_csv(file,index_col=None,header=0)) # 빈 리스트에 읽어 들인 내용을 추가한다

        frame = pds.concat(allData, axis=0, ignore_index=True) # concat함수를 이용해서 리스트의 내용을 병합
        # axis=0은 수직으로 병합함. axis=1은 수평. ignore_index=True는 인데스 값이 기존 순서를 무시하고 순서대로 정렬되도록 한다.
        frame.to_csv(output_file, index=False) # to_csv함수로 저장한다. 인데스를 빼려면 False로 설정

        for file in allFile_list:
            os.remove(file)

        time.sleep(2)

    def EncodeCSV():
        outpath = os.path.dirname(os.path.realpath(__file__)) + "\\Result\\"
        infile = codecs.open(outpath + 'Crollwing_result.csv', 'r', encoding='utf-8')
        outfile = codecs.open(outpath + 'Crollwing_result_encode.csv', 'w', encoding='euc-kr')
         
        for line in infile:
             line = line.replace(u'\xa0', ' ')    # 가끔 \xa0 문자열로 인해 오류가 발생하므로 변환
             outfile.write(line)
         
        infile.close()
        outfile.close()

        os.remove(outpath + 'Crollwing_result.csv')

#메인함수 부분입니다.        
if __name__=='__main__':
    for date_num in date_list: # 추출할 날짜 리스트를 반복
        WebRequest.get_pageData(date_num)
        csv_gspread.WORKSHEET_NAME = str(date_num) # 이 부분에 생성한 스프레드시트의 WorkSheet이름을 설정해주세요.
        csv_gspread.df_start(save_list)
        save_list.clear()
        page_list.clear()
        print('[!]' + str(date_num) + '작업 완료')

    csv_gspread.WORKSHEET_NAME = 'Total List' # 이 부분에 생성한 스프레드시트의 WorkSheet이름을 설정해주세요.
    csv_gspread.df_start(all_list)
    all_list.clear()
    print("[!] 모든 작업 완료")





