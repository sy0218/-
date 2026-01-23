# 🌐 Ubuntu에서 Selenium + Chrome 설치

---

## 📌 개요
- Ubuntu 환경에서 Selenium + Chrome + ChromeDriver 설치 가이드
- Python에서 Selenium 기반 웹 자동화 테스트 환경 구성
- Chrome 버전에 맞는 ChromeDriver 설치 방법 포함

---
<br>

## ⚙️ 패키지 업데이트 및 Chrome 설치
```bash
# 패키지 목록 업데이트
sudo apt-get update

# Chrome 다운로드
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# 설치
sudo apt install ./google-chrome-stable_current_amd64.deb
```

---
<br>

## ⚙️ ChromeDriver 설치
### ✔ Chrome 버전 확인
```bash
google-chrome --version
```
### ✔ 예시 출력 👇
```nginux
Google Chrome 135.0.7049.95
```
### ✔ 호환되는 드라이버 버전 확인
- Chrome 버전에 맞는 드라이버 확인 👉 [버전 확인 링크](https://github.com/GoogleChromeLabs/chrome-for-testing/blob/main/data/latest-versions-per-milestone-with-downloads.json)
### ✔ ChromeDriver 다운로드 및 압축 해제
```bash
wget https://storage.googleapis.com/chrome-for-testing-public/135.0.7049.95/linux64/chrome-linux64.zip
unzip chrome-linux64.zip
```

---
<br>

## ⚙️ Selenium 설치
```bash
pip install selenium
```

---
<br>

## ⚙️ 설치 확인 예제 (Python)
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# ChromeDriver 경로 지정
service = Service("/path/to/chromedriver")
driver = webdriver.Chrome(service=service)

# 테스트 페이지 접속
driver.get("https://www.google.com")

# 페이지 제목 출력
print(driver.title)

driver.quit()
```

---
<br>

## ✅ 결과 확인
- Ubuntu 환경에서 Chrome + ChromeDriver 설치 완료
- Python Selenium 실행 가능
- 웹 자동화 테스트 환경 구성 완료
- 향후 자동화 크롤러/테스트 스크립트에 활용 가능
---
