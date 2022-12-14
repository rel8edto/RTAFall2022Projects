import pandas as pd
import re
import json
import pandas as pd
import requests
from urllib.parse import quote
import kumihotools #pip3 install git+https://github.com/rel8edto/kumihotools.git
from bs4 import BeautifulSoup
from urllib.request import urlopen
cate = json.load(open('/home/rlin/ad sites/config.json'))
urls_df = pd.read_csv('/home/rlin/ad sites/urls.csv')

def get_all_html(urls_df):

    kumi = kumihotools.Kumi()
    all_html = {}
    urls_df.columns = ['URL']
    for i, row in urls_df.iterrows():
        cur_domain = row['URL']
        if not cur_domain:
            continue
        try:
            cur_domain = kumihotools.toDomain(cur_domain)
            domainid = quote(cur_domain.replace('/', '_'))
            res = requests.get(f'http://elastic:foxhouse@10.8.1.245:9200/foxhouse/_doc/{domainid}')
            data = res.json()
            htmlraw = data.get('_source',{}).get('htmlraw','')
            all_html[cur_domain] = {}
            all_html[cur_domain]['soup'] = htmlraw
            all_html[cur_domain]['url'] = cur_domain
            if str(data.get('found')).lower() == 'false':
                try:
                    page = urlopen(cur_domain)
                    soup = BeautifulSoup(page, 'html.parser')
                    all_html[cur_domain] = {}
                    all_html[cur_domain]['soup'] = soup.text
                    all_html[cur_domain]['url'] = cur_domain
                except:
                    print(cur_domain,'--error')
        except Exception as e:
            #print(e)
            continue
    return all_html
            
def checkPatterns(cate,urls_df):
    
    try:
        all_html = json.load(open('all_html1.json'))
    except:
        all_html = get_all_html(urls_df)
        
    urls = []
    for k,v in all_html.items():
        urls.append(v['url'])

    d = {'urls':urls}
    res = pd.DataFrame(data=d)
    
    for name,v in cate['parameters'].items():
        temp_res = []
        for key, value in all_html.items():
            found = False
            for pattern in v['patterns']:
                if found:
                    break
                if re.search(pattern, value['soup']):
                    temp_res.append('found')
                    found = True

            if not found:
                temp_res.append('not found')
            
        res[name] = temp_res
    print(res)
    res.to_csv('/home/rlin/ad sites/patterns_res.csv',index = False)
    
def test(job):
    for parameter in job["parameters"]:
        print(parameter['column'])
    
    
def runAllfunctions(job_list):
    for job in job_list:
        if job['function'] == 'checkPatterns':
            checkPatterns(job,urls_df)
        if job['function'] == 'test':
            test(job)

def main():

    runAllfunctions(cate['jobs'])


if __name__ == "__main__":
    main()