import pandas as pd
import re
import json
import pandas as pd
import requests
import kumihotools #pip3 install git+https://github.com/rel8edto/kumihotools.git
from tqdm import tqdm
from urllib.parse import quote

cate = json.load(open('config.json'))

def get_all_html(urls):
    from bs4 import BeautifulSoup
    from urllib.request import urlopen
    all_html = {}
    for index, rows in urls.iterrows():
        cur_domain = rows['URL']
        try:
            page = urlopen(cur_domain)
            soup = BeautifulSoup(page, 'html.parser')
            all_html[cur_domain] = {}
            all_html[cur_domain]['soup'] = soup.text
            all_html[cur_domain]['url'] = cur_domain
            all_html[cur_domain]['cate_col'] = rows['Category']
        except:
            print(cur_domain,'--error')
    with open("all_html.json", "w") as outfile:
        json.dump(all_html, outfile)
    all_html = json.load(open('all_html.json'))
    return all_html
            
def checkPatterns(cate):
    
    try:
        all_html = json.load(open('all_html.json'))
    except:
        all_html = get_all_html(urls)
        
    urls,cate_col = [],[]
    for k,v in all_html.items():
        urls.append(v['url'])
        cate_col.append(v['cate_col'])

    d = {'urls':urls, 'Category': cate_col}
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
    res.to_csv('patterns_res.csv',index = False)
    
def test(job):
    for parameter in job["parameters"]:
        print(parameter['column'])
    
    
def runAllfunctions(job_list):
    for job in job_list:
        if job['function'] == 'checkPatterns':
            checkPatterns(job)
        if job['function'] == 'test':
            test(job)

def main():
    runAllfunctions(cate['jobs'])


if __name__ == "__main__":
    main()