#!/usr/bin/python3
import time, re, requests
from common.crawling_class import ChromeDriver, JobParser
from common.job_class import DataPreProcessor
from common.hook_class import RedisHook, KafkaHook
from lxml import etree
from PIL import Image
from io import BytesIO

test_dict = {'domain': 'remember', 'href': 'https://career.rememberapp.co.kr/job/posting/291016', 'company': '한화에너지 컨버전스사업부', 'title': 'HMI 엔지니어 경력', 'msgid': 'd1738e7d1ca4636e1a69137467c8c0c3c09af9bff7d471010a66d87f62f0c9dd'}

browser = ChromeDriver()
browser.get(test_dict['href'])
browser.wait_css("#app-body", 10)

parser = JobParser(browser)
response = parser.get_response()

#fields = {
#    'pay': ['연봉', '보상금'],
#    'location': ['근무지', '근무 장소'],
#    'career': ['경력'],
#    'education': ['학력'],
#    'deadline': ['마감일'],
#    'type': ['직급', '직책']
#}
#result = {}
#
#for field, keywords in fields.items():
#    result[field] = None
#    for kw in keywords:
#        # 1) 바로 다음 span
#        val = response.xpath(
#            f"//div[@class='sc-a34accef-0 cBEpAk']//span[contains(text(), '{kw}')]/following-sibling::span/text()"
#        ).get()
#        if not val:
#            # 2) span 뒤 div 안의 span (deadline 같은 경우)
#            val = response.xpath(
#                f"//div[@class='sc-a34accef-0 cBEpAk']//span[contains(text(), '{kw}')]/following-sibling::div//span/text()"
#            ).get()
#        if val:
#            result[field] = val.strip()
#            break
#
#print(result)
#
#result_test = response.xpath("//div[@class='sc-a34accef-0 cBEpAk']").get()
#parser = etree.HTMLParser()
#tree = etree.fromstring(result_test, parser)
#pretty_html = etree.tostring(tree, pretty_print=True, encoding='unicode')
#print(pretty_html)
# pay
#pay_rp = response.xpath("//div[@class='sc-a34accef-0 cBEpAk']/div[2]//span[@class='sc-111d08f0-2 jANCxD']/text()").get()
# location
#location_rp = response.xpath("//div[@class='sc-a34accef-0 cBEpAk']/div[3]//span[@class='sc-111d08f0-2 jANCxD']/text()").get()
# career
#career_rp = response.xpath("//div[@class='sc-a34accef-0 cBEpAk']/div[4]//span[@class='sc-111d08f0-2 jANCxD']/text()").get()
# education
#education_rp = response.xpath("//div[@class='sc-a34accef-0 cBEpAk']/div[5]//span[@class='sc-111d08f0-2 jANCxD']/text()").get()
# deadline
#deadline_rp = response.xpath("//div[@class='sc-a34accef-0 cBEpAk']/div[6]//span[@class='sc-111d08f0-2 jANCxD']/text()").get()
# type (직급/직책)
#type_rp = response.xpath("//div[@class='sc-a34accef-0 cBEpAk']/div[1]//span[@class='sc-111d08f0-2 jANCxD']/text()").get()

#print(pay_rp, location_rp, career_rp, education_rp, deadline_rp, type_rp)

html = response.xpath("//div[@class='sc-70f5b6f6-0 kXwJGP']").get()

parser = etree.HTMLParser()
tree = etree.fromstring(html, parser)

pretty_html = etree.tostring(tree, pretty_print=True, encoding='unicode')
# html 트리구조 보기
print(pretty_html)
print()

# 텍스트만 추출
text_only = ''.join(tree.itertext())
# 한글, 영어, 숫자, 공백만 남기고 나머지 제거 (이모지, 특수문자 제거)
clean_text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', text_only)
# 연속 공백 정리
clean_text = re.sub(r'\s+', ' ', clean_text).strip()
print(clean_text)


# 이미지 마지막!
img_tags = tree.xpath(".//img")
for img in img_tags:
    src = img.get("src")
    try:
        resp = requests.get(src, timeout=5)
        img_bytes = resp.content # 바이너리 데이터
        img_size_kb = len(img_bytes) / 1024

#        # 이미지 크기 확인
        img_file = Image.open(BytesIO(img_bytes))
        width, height = img_file.size
#
        if width <= 50 or height <= 50 or img_size_kb < 10:
            continue
        print(f"src: {src}, width: {width}, height: {height}, size: {img_size_kb:.2f}")
        print(f"binary data: {img_bytes}")
    except Exception as e:
        print(f"src: {src}, error: {e}")

browser.quit()
