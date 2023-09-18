# %%
# 필요한 모듈 참조
import requests
from bs4 import BeautifulSoup

# %%
# IT/과학 : 105, 경제 : 101, 사회 : 102, 생활/문화 : 103, 세계 : 104, 정치 : 100
CATEGORIES = [105, 101, 102, 103, 104, 100]

CATEGORY = 105

# 수집하고자하는 페이지 범위
PAGES = range(51, 101)

# 네이버 뉴스 URL
URL = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={category}#&date=%2000:00:00&page={page}'

# %%
# 접속 객체 생성
session = requests.Session()

# 접속객체에 부가정보(header) 삽입하기
session.headers.update({
    "Referer": "",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
})

# %%

# 수집한 뉴스기사의 수를 저장할 변수
counter = 1

# 수집한 뉴스기사를 저장할 파일명
fileName = "./{myname}_naver_news_{category}_{counter}.txt"

# 주어진 카테고리에 대해 주어진 페이지 범위만큼 뉴스 수집
for page in PAGES:
    targetUrl = URL.format(category=CATEGORY, page=page)
    # print(targetUrl)
    
    # 생성한 접속객체를 활용하여 뉴스 목록 페이지에 접속
    r = session.get(targetUrl)
    
    # 접속에 실패한 경우
    if r.status_code != 200:
        # 에러코드와 에러메시지 출력
        msg = "[%d Error] %s 에러가 발생함" % (r.status_code, r.reason)
        # 에러를 강제로 생성시킴
        raise Exception(msg)
    
    # 응답결과를 텍스트로 변환
    r.encoding = "euc-kr"
    soup = BeautifulSoup(r.text)
    #print(soup)
    
    # 뉴스 기사 제목을 위한 CSS 선택자
    selector = ".sh_item .sh_text .sh_text_headline, #section_body ul li dl dt a"
    
    # 뉴스기사 제목 추출
    headlines = soup.select(selector)
    #print(headlines)
    
    # 각 페이지별로 추출된 뉴스기사의 본문 URL
    for h in headlines:
        href = h.attrs["href"]
        
        # 기사 본문에 대한 세부 내용 수집
        if href:
            print(href)
            bodyRes = session.get(href)
            
            # 접속에 실패한 경우
            if bodyRes.status_code != 200:
                # 에러코드와 에러메시지 출력
                msg = "[%d Error] %s 에러가 발생함" % (bodyRes.status_code, bodyRes.reason)
                # 에러를 강제로 생성시킴
                raise Exception(msg)
            
            bodyRes.encoding = "utf-8"
            bodySoup = BeautifulSoup(bodyRes.text)
            
            # 제목
            title = bodySoup.select("#title_area span")[0].text
            print(title)
            
            # 본문
            content = bodySoup.select("#dic_area")[0]
            
            # 본문 요소에 포함되어 있는 불필요 항목 제거
            for target in content.find_all("span", {"class": "end_photo_org"}):
                target.extract()
                
            for target in content.find_all("strong", {"class": "media_end_summary"}):
                target.extract()
                
            for target in content.find_all("table", {"class": "nbd_table"}):
                target.extract()
                
            for target in content.find_all("div", {"class": "highlightBlock"}):
                target.extract()
                
            for target in content.find_all("div", {"style": "display:none;"}):
                target.extract()
                
            for target in content.find_all("br"):
                target.replace_with("\n")
                
            contentBody = content.text.strip()
            
            with open(fileName.format(myname="han", category=CATEGORY, counter=counter), "w", encoding="utf-8") as f:
                f.write(title)
                f.write("\n\n")
                f.write(contentBody)
                
            counter += 1
            
            print("%d news article crawled" % counter)
    
# %%
