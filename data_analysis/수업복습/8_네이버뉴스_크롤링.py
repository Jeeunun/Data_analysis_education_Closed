# %%
# 필요한 모듈 참조
import requests
from bs4 import BeautifulSoup
# %%
# 네이버 뉴스 url
# 정치 100, 경제 101, 사회 102, 생활문화 103, 세계 104, IT과학 105
CATEGORYS = [100,101,102,103,104,105]

# 수집하고자 하는 카테고리 번호
CATEGORY = 103
# 수집하고자 하는 페이지 범위
PAGES = range(1,15)

url =  'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={category}#&date=%2000:00:00&page={page}'

# %%
# 접속 객체 생성
session = requests.Session()

# 접속 객체에 부가정보(header) 삽입하기
session.headers.update({
    'Referer' : "",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
})

# %%
# 주어진 카테고리에 대해 주어진 페이지 범위만큼 정보 수집
for page in PAGES:
    targetURL = url.format(category=CATEGORY, page=page)
    # print(targetURL)

    # 생성한 접속객체를 활용하여 뉴스 목록 페이지에 접속
    r = session.get(targetURL)

    # 접속에 실패한 경우
    if r.status_code != 200:
        # 에러 코드와 에러 메세지 출력
        msg = "[%d Error] %s 에러가 발생함" % (r.status_code, r.reason)
        # 에러를 강제로 생성
        raise Exception(msg)
    
    # 응답결과를 텍스트로 변환
    r.encoding = 'euc-kr'
    soup = BeautifulSoup(r.text)
    # print(soup)

    # 뉴스 기사 제목을 위한 CSS 선택자
    selector = ".sh_text .sh_item _cluster_content #section_body ul li dt a"

    # 뉴스 기사 제목 추출
    headlines = soup.select(selector)
    print(headlines)

    # 각 페이지별로 추출된 뉴스기사의 본문 url
    for h in headlines:
        href = h.attrs['href']

        # 기사 본문에 대한 세부 내용 수집
        if href:
            bodyRes = session.get(href)

            # 접속에 실패한 경우
            if bodyRes.status_code != 200:
            # 에러 코드와 에러 메세지 출력
                msg = "[%d Error] %s 에러가 발생함" % (bodyRes.status_code, bodyRes.reason)
            # 에러를 강제로 생성
                raise Exception(msg)
            
            # 응답결과를 텍스트로 변환
            bodyRes.encoding = 'utf-8'
            bodysoup = BeautifulSoup(bodyRes.text)

            # 제목
            title = bodysoup.select
# %%
    # 