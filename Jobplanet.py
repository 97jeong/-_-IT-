from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from collections import Counter
from wordcloud import STOPWORDS, WordCloud
from PIL import Image
import csv

def crawl_companyinfo(result):
    for page in range(1, 167):
        cnt = 0
        url = 'https://www.jobplanet.co.kr/companies?industry_id=700&sort_by=review_survey_total_avg_cache&page=%d' %page
        progress = page / 166 * 100
        print('\rprogressbar : %d%%' %progress, end = "")
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        soup = BeautifulSoup(html, 'html.parser')
        tag_article = soup.find('article')
        for company in tag_article.find_all('section'):
            company_name = company.select("dt.us_titb_l3 > a")[0].string
            company_dd = company.find_all('dd')
            company_info_list = list(company_dd)
            company_local = company_info_list[0].select("span.us_stxt_1")[1].string
            company_star_score = company_info_list[2].find('span').string
            company_pay = company_info_list[3].find('strong').string
            cnt = cnt + 1
            rank = (page-1) * 10 + cnt
            result.append([rank] + [company_name] + [company_local] + [company_star_score] + [company_pay])
    return

def local_count(df):
    c_local = df['지역']
    words = []
    for local in c_local:
        words.append(local)
        
    count = Counter(words)
    word_count = dict()
    for tag, counts in count.most_common():
        word_count[tag] = counts

    sorted_Keys = sorted(word_count, key = word_count.get, reverse = True)
    sorted_Values = sorted(word_count.values(), reverse = True)
    plt.bar(range(len(word_count)), sorted_Values, align = 'center')
    font_location = 'C:/Windows/Fonts/AdobeMyungjoStd-Medium.otf'
    font_name = fm.FontProperties(fname=font_location).get_name()
    plt.xticks(range(len(word_count)), sorted_Keys, family = font_name)
    plt.savefig("D:/Code/Python/JobplanetCrawler/Local_chart.jpg")
    plt.show()

    stopwords = set(STOPWORDS)
    wc = WordCloud(font_path = 'AdobeMyungjoStd-Medium', background_color = 'ivory', stopwords = stopwords, width = 800, height = 600)
    cloud = wc.generate_from_frequencies(word_count)
    plt.figure(figsize = (8,8))
    plt.imshow(cloud)
    plt.axis('off')
    cloud.to_file("D:/Code/Python/JobplanetCrawler/Local_cloud.jpg")
    plt.show()

def cause_effect_graph(df):
    score = []
    pay = []
    pay_avg = [0, 0, 0, 0, 0]
    pay_sum = [0, 0, 0, 0, 0]
    score_cnt = [0, 0, 0, 0, 0]
    star_score = [1, 2, 3, 4, 5]
    for i in range(len(df)):
        s = int(df['평점'][i])
        p = int(df['연봉'][i].replace(",", "").strip())
        if s >= 5 :
            s = 5
        elif s >= 4:
            s = 4 
        elif s >= 3:
            s = 3
        elif s >= 2:
            s = 2
        elif s >= 1:
            s = 1
        else :
            s = 0
        score.append(s)
        pay.append(p)
        
        if s == 1:
            pay_sum[0] = pay_sum[0] + p
            score_cnt[0] = score_cnt[0] + 1
        elif s == 2:
            pay_sum[1] = pay_sum[1] + p
            score_cnt[1] = score_cnt[1] + 1
        elif s == 3:
            pay_sum[2] = pay_sum[2] + p
            score_cnt[2] = score_cnt[2] + 1
        elif s == 4:
            pay_sum[3] = pay_sum[3] + p
            score_cnt[3] = score_cnt[3] + 1
        else :
            pay_sum[4] = pay_sum[4] + p
            score_cnt[4] = score_cnt[4] + 1
            
    for i in range (0, 5):
        if score_cnt[i] == 0:
           score_cnt[i] = 1
        pay_avg[i] = pay_sum[i] / score_cnt[i]

    plt.bar(star_score, pay_avg)
    plt.savefig("D:/Code/Python/JobplanetCrawler/pay_starscore_chart.jpg")
    plt.show()
    
def main():
    try:
        df = pd.read_csv('D:/Code/Python/JobplanetCrawler/jobplanet.csv', encoding = 'cp949')
    except:
        result = []
        print('Crawling ...')
        crawl_companyinfo(result)
        tbl = pd.DataFrame(result, columns = ('평점순위', '회사명', '지역', '평점', '연봉'))
        tbl.to_csv('D:/Code/Python/JobplanetCrawler/jobplanet.csv', encoding = 'cp949', mode = 'w', index = False)
        del result[:]
        df = pd.read_csv('D:/Code/Python/JobplanetCrawler/jobplanet.csv', encoding = 'cp949')

    local_count(df)
    cause_effect_graph(df)
    
    

if __name__ == '__main__':
    main()
