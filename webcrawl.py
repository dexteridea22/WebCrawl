import re
import xlsxwriter
import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import  urljoin
import pandas as pd
from socket import timeout
from urllib.error import HTTPError, URLError
import socket
import logging

base_url='http://www.agriculture.gov.au'
url='http://www.agriculture.gov.au/pests-diseases-weeds/plant#identify-pests-diseases'
#Local Image download path
Image_download_path='C:\\Users\\D\\Crawl\\Images\\'
#request html
try:
    html = urlopen(url, timeout=1000)
except (HTTPError, URLError) as error:
    logging.error('Data of cannot be retrieved because %s\nURL: %s', error, url)
except timeout:
    logging.error('socket timed out - URL %s', url)
else:
    logging.info('Access successful.')

soup=BeautifulSoup(html.read(),'lxml')

subSoup=soup.find_all('li',class_='flex-item')

disease = []
links =   []
Secure_any_suspect_specimens = []
Origin = []

url1='http://www.agriculture.gov.au'
#Storing Downloaded Images with local path
workbook = xlsxwriter.Workbook('Hyperlinks_to_images.xlsx')
worksheet = workbook.add_worksheet('Hyperlinks')
worksheet.set_column('A:A', 30)

i = 1 #counter for writing download image path in excel 
#iterate over each pests/dieases to fetch data
for li in subSoup:
    for a in li.findAll('a'):
          # print(a.text)
          disease.append(a.text)
     
    for img in li.findAll('img'):

          urllib.request.urlretrieve(url1+img['src'],'Images'+'\\'+a.text.replace('\n','').replace('/','-')+'.jpg')
          links.append(url1+img['src'])
          worksheet.write_url('A'+str(i), Image_download_path+a.text.replace('\n','')+'.jpg')
          i += 1
    for a in li.findAll('a',href=True):           
      
       url=urljoin(base_url,a['href'])#get absolute url
      #fetching Origin 
       try:
          html = urlopen(url, timeout=1000)
       except (HTTPError, URLError) as error:
          logging.error('Data cannot be retrieved because %s\nURL: %s', error, url)
       except timeout:
          logging.error('socket timed out - URL %s', url)
       else:
          logging.info('Access successful.')
       # print(html.getcode())
       if html.getcode() != 200:
          Origin.append('Unknown')
          continue
       soup_link=BeautifulSoup(html.read(),'lxml')
       subSoup_link=soup_link.find_all('div',class_='pest-header-content')
       # print(subSoup_link)
       if len(subSoup_link) == 0 :#No Origin Found
          Origin.append('Unknown') 
       for s in subSoup_link:
            s =s.find(lambda tag:tag.name=="p" and "Origin" in tag.text)
            s = s.text.replace('\n','').replace(' ','') 
            Origin.append((re.search(r'Origin:(.*)Distribution:', s)).group(1))


    for a in li.findAll('a',href=True):           
    #   # print (a['href']) 
        #Special Cases with No fields  
        if a['href'].find('www.planthealthaustralia.com') >= 0 :
           Secure_any_suspect_specimens.append('Unknown')
           continue
        if a['href'] == 'https://www.daf.qld.gov.au/forestry/pests-and-diseases/termites':
           Secure_any_suspect_specimens.append('Unknown')
           continue 
        if a['href'] == '/import/arrival/pests/japanese-sawyer-beetle':
           Secure_any_suspect_specimens.append('Unknown')
           continue 
        if a['href'] =='/pests-diseases-weeds/forestry-timber#field-guide-to-exotic-pests-and-diseases-dutch-elm-disease':
           Secure_any_suspect_specimens.append('Unknown')
           continue
        #Fetch  secure any suspect specimens
        url2=base_url+a['href']+'#secure-any-suspect-specimens'

        # print(url)
        try:
            html = urlopen(url2, timeout=1000)
        except (HTTPError, URLError) as error:
            logging.error('Data cannot be retrieved because %s\nURL: %s', error, url)
        except timeout:
            logging.error('socket timed out - URL %s', url)
        else:
            logging.info('Access successful.')
        # print(html)
        soup_link=BeautifulSoup(html.read(),'lxml')
        # print(soup_link)
        subSoup_link=soup_link.find_all('div',class_='hide')
      
        
        Secure_any_suspect_specimens.append(subSoup_link[len(subSoup_link)-1].text)

    # break     
#Hypelinks Workbook    
workbook.close()

#Panda data frame writing to excel
my_dict= {'Disease/Pests':disease,'Links':links,'Origin':Origin,'Secure any suspect specimens':Secure_any_suspect_specimens}
df =  pd.DataFrame(my_dict,columns=['Disease/Pests','Links','Origin','Secure any suspect specimens'])
# print(df)

df.to_excel('PlantPest_Diseases.xlsx',index=None,header=True)

