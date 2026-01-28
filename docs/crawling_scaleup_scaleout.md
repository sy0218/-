# 🔍 크롤링 처리시간 개선 & 멀티프로세스
# 🛑 문제 (Problem)
- 디테일 페이지 파싱 1건당 약 **10초** 소요  
- 하루 50,000건 기준 → 총 **138시간 이상 소요**  
- 단일 프로세스 + 단일 크롬 드라이버 → 처리량 부족  
- 기존 대기 방식 : `time.sleep()` → 불필요한 대기 발생  

---
<br>

## ⚙ 트러블슈팅 방법 (Solution)
### 1️⃣ Scale-Up (단일 서버 성능 향상)
- 크롬 드라이버 1개 → **5개 동시 구동**  
- **브라우저 객체 재사용** → 매번 드라이버 생성 오버헤드 제거  
- ProcessPoolExecutor **initializer** 활용 → 워커 프로세스 초기화 시 크롬 드라이버 생성
```python
# 워커 초기화
def init_worker(config_path):
    worker_context["properties"] = Get_properties(config_path)
    worker_context["browser"] = ChromeDriver()
    logger.info(f"Worker 초기화 성공 (PID: {os.getpid()})")
```
---
### 2️⃣ Scale-Out (멀티 컨슈머)
- 컨슈머 3대 운영
- Kafka 병렬 처리 → 처리량 약 3배 향상
```python
# 카프카 컨슈머
while len(batch) < poll_size:
    msg = kafka_consumer.poll(3.0)
```
---
### 3️⃣ 대기 방식 최적화
- 기존 `time.sleep(5)` → **WebDriverWait** 사용
- 페이지 로딩 준비 완료 시점까지 정확히 대기 → 불필요한 대기 제거
```python
# CSS 로딩 대기
browser.wait_css(xpaths["wait"], 10)
```
---
### 4️⃣ 메시지 처리 핵심
- 배너, 본문, 이미지 크롤링
- 이미지 최소 크기/용량 필터링 후 처리
```python
parser = JobParser(browser)
parser.get_response()
banner = parser.get_banner(xpaths["banner"], domain)
body = parser.get_body(xpaths["body"])

images_binary = parser.get_images(
    xpaths["body"], msg_value["href"],
    int(props["img_bypass"]["width"]),
    int(props["img_bypass"]["height"]),
    int(props["img_bypass"]["size"])
)

images = []
for binary_blob, size_kb in images_binary:
    img_hash = DataPreProcessor._hash(binary_blob.hex() + str(size_kb))
    save_path = CopyToLocal.save(
        (props["nfs_path"]["img"], img_hash[0:2], img_hash[2:4], img_hash),
        binary_blob
    )
    images.append(save_path)
```

---
<br><br>

#  📊 결과 (Result)
| 지표 | 기존 처리 | 개선 후 처리 | 개선 포인트 |
|------|-----------|------------|------------|
| **1건 처리 시간** | 10초 | 1초 | 멀티프로세스 + 브라우저 객체 재사용 + Scale-Out |
| **하루 처리량 (50,000건 기준)** | 138시간 | 4.6시간 | Scale-Up × Scale-Out 적용 |
| **크롬 드라이버 동시 수** | 1 | 5 | 브라우저 객체 재사용 |
| **컨슈머 수** | 1 | 3 | Kafka 배치 병렬 처리 |
| **대기 방식** | `time.sleep(5)` | `WebDriverWait` | 불필요한 idle 제거 |

---

#### 💡 요약
- **멀티프로세스 + 브라우저 객체 재사용** → 워커 초기화 비용 최소화, 크롬 드라이버 재사용  
- **Scale-Up / Scale-Out** → 처리량 대폭 향상  
- **WebDriverWait** → 페이지 로딩 정확히 대기 → idle 시간 제거  
- **멀티프로세스 + Kafka 병렬 처리** → 병목 최소화

---

## ⚡ 장점
- 전체 배치 완료 시간 **138시간 → 4.6시간**  
- 크롬 드라이버 재사용 → 메모리·CPU 효율 향상  
- Kafka 배치 병렬 처리 → 처리 병목 최소화

## ⚡ 단점 / 고려 사항
- 멀티프로세스 → 서버 자원(CPU, 메모리) 충분히 필요  
- WebDriverWait → 잘못된 XPath/페이지 지연 시 timeout 필요

---
<br><br>

# 🏆 성과 요약
| 지표 | 기존 | 개선 | 개선 비율 / 효과 |
|------|------|------|----------------|
| **1건 처리 시간** | 10초 | 1초 | **약 90% 단축** |
| **하루 처리 시간** | 138시간 | 4.6시간 | **약 97% 단축** |
| **다중 크롬 드라이버 사용** | 1 | 5 | **5배 동시 처리** |
| **컨슈머 수** | 1 | 3 | **처리량 약 3배 향상** |

---
<br>

## 📌 결론
- **멀티프로세스 + 브라우저 객체 재사용 + Scale-Up/Scale-Out + WebDriverWait** 조합으로 처리 효율 극대화  
- 하루 50,000건 처리 → 약 4.6시간 수준으로 개선  
- **브라우저 객체 재사용이 핵심 포인트**

---
<br>

## ✅ 최종 선택
- **멀티프로세스 + 브라우저 객체 풀 재사용**  
- **WebDriverWait 기반 대기**  
- **Kafka 배치 병렬 처리 + Scale-Out**
---
