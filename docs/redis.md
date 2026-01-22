# 🔍 Redis vs RDB 성능 테스트
## 🔗 **테스트 환경**
- **저장 데이터** : Redis / PostgreSQL → 30,000,000 건  
- **조회 / 삽입 데이터** : 10,000 건  
- **모니터링 도구** : Node Exporter + Prometheus + Grafana  
- **측정 기준** : Grafana max 값 기준 기록  
---

## 📌 테스트 목적
- 대용량 중복 데이터 삽입 및 조회 시 **Redis와 PostgreSQL 성능 차이**를 수치 기반으로 확인하고, 각 기술의 **효율성과 한계**를 명확히 이해하기 위함입니다.
---
<br><br>

# 🛑 문제 (Problem)
- **RDB 사용 시** 대용량 중복 조회/삽입에 **디스크 I/O 병목** 발생 가능  
- **Redis 캐시 사용 시** 메모리 기반 처리로 **효율적**이지만, 영속성/데이터 복구 제한 존재  
- 테스트를 통해 **서버 부하, I/O, CPU 컨텍스트 스위치** 차이를 비교
---
<br>

## ⚙ 테스트 환경 및 Grafana 모니터링
### 🔹 Grafana 쿼리 & 간단 설명
| 지표 | Grafana 쿼리 | 설명 |
|------|---------------|------|
| **디스크 I/O Wait** | `avg by(instance) (rate(node_cpu_seconds_total{mode="iowait", instance="192.168.122.59:9100"}[1m])) * 100` | CPU가 디스크 I/O 완료를 기다리는 시간 비율, 높을수록 **I/O 병목 발생** |
| **Disk Write Throughput** | `sum by(instance) (rate(node_disk_written_bytes_total{device="vda", instance="192.168.122.59:9100"}[1m]))` | 초당 디스크 쓰기량, RDB가 디스크 중심이라 상대적으로 **높음** |
| **Context Switch** | `rate(node_context_switches_total{instance="192.168.122.59:9100"}[1m])` | CPU가 프로세스 전환하는 횟수, 많을수록 **시스템 부하 증가** |
| **Load Average** | `node_load1{instance="192.168.122.59:9100"}` | CPU/IO 대기 포함 부하, 1분 평균 값 |

---
<br>

## ⚙ 테스트 방법 (Solution)
### 1️⃣ PostgreSQL(RDB) 테스트 코드
```python
#!/usr/bin/python3
import hashlib, random, psycopg2
from psycopg2.extras import execute_values

def generate_random_korean(min_len=20, max_len=30):
    length = random.randint(min_len, max_len)
    start, end = int("AC00", 16), int("D7A3", 16)
    return "".join([chr(random.randint(start, end)) for _ in range(length)])

pg_conn = psycopg2.connect(
    host="192.168.122.59", port=5432, dbname="job_pro", user="sjj", password="1234"
)
pg_conn.autocommit = False
pg_cur = pg_conn.cursor()

total = 10000
job_hash_map = []
for i in range(total):
    s = f"https://example.com/job/{i}" + generate_random_korean()
    h = hashlib.sha256(s.encode('utf-8')).hexdigest()
    job_hash_map.append((h, {'href': s, 'company': f'Company{i}', 'title': f'Title{i}'}))

values = [(r[0],) for r in job_hash_map]
sql = """
INSERT INTO job.job_set (job_set)
VALUES %s
ON CONFLICT (job_set) DO NOTHING
RETURNING job_set
"""
inserted_rows = execute_values(pg_cur, sql, values, fetch=True)
pg_conn.commit()
pg_cur.close()
pg_conn.close()
```
<br>

### 2️⃣ Redis 테스트 코드
```python
#!/usr/bin/python3
import redis, hashlib, random

def generate_random_korean(min_len=20, max_len=30):
    length = random.randint(min_len, max_len)
    start, end = int("AC00", 16), int("D7A3", 16)
    return "".join([chr(random.randint(start, end)) for _ in range(length)])

redis_conn = redis.Redis(host="192.168.122.59", port=6379, db=0, password="1234")
redis_key = 'job_set'
redis_pipe = redis_conn.pipeline(transaction=False)

total = 10000
job_headers = []

for i in range(total):
    s = f"https://example.com/job/{i}" + generate_random_korean()
    h = hashlib.sha256(s.encode('utf-8')).hexdigest()
    job_headers.append({'href': s, 'hash': h, 'company': f'Company{i}', 'title': f'Title{i}'})
    redis_pipe.sadd(redis_key, h)

redis_info = redis_pipe.execute()
```
---
<br><br>

# 📊 결과 (Result)
| 지표                   | PostgreSQL (10:10) | Redis (10:20) | 설명                                      |
| --------------------- | ----------------- | ------------- | --------------------------------------- |
| **디스크 I/O Wait**      | 0.148             | 0.02          | CPU가 I/O 완료 대기 시간 비율, RDB는 디스크 접근 많음 |
| **Disk Write Throughput**| 1,337,591 B/s     | 17,203 B/s    | 초당 디스크 쓰기량, RDB가 디스크 중심이라 훨씬 높음 |
| **Context Switch**       | 1,284             | 879           | CPU 컨텍스트 스위치 빈도, RDB가 더 자주 발생 |
| **Load Average**         | 0.15              | 0.04          | CPU/IO 대기 포함 부하, Redis가 훨씬 낮음 |

#### 💡 요약
- **Redis**는 **메모리 기반 처리**로 인해 I/O Wait와 디스크 쓰기량이 RDB 대비 압도적으로 낮음  
- CPU 컨텍스트 스위치와 부하도 낮아 **대규모 조회/삽입 환경에 최적화**
---

## ⚡ Redis 장점
- 메모리 기반으로 **읽기/쓰기 성능 매우 우수**  
- **중복 체크 및 삽입 처리 빠름**  
- RDB 대비 **서버 부하 낮음**  
## ⚡ Redis 단점
- **메모리 한계** → 데이터 용량 증가 시 비용 상승  
- 단일 서버 사용 시 **메모리 장애 시 데이터 손실 가능**  

---
<br><br>


# 🏆 성과 요약
| 지표                   | PostgreSQL    | Redis      | 개선 비율 / 효율                    |
| --------------------- | ------------- | ---------- | ----------------------------- |
| **디스크 I/O Wait**      | 0.148         | 0.02       | 약 **86% 감소** (CPU 대기 시간 감소) |
| **Disk Write Throughput**| 1,337,591 B/s | 17,203 B/s | 약 **98.7% 감소** (디스크 쓰기량 감소) |
| **Context Switch**       | 1,284         | 879        | 약 **31% 감소** (CPU 컨텍스트 전환 감소) |
| **Load Average**         | 0.15          | 0.04       | 약 **73% 감소** (CPU/IO 부하 감소) |


#### 💡 요약
- Redis는 **메모리 기반 처리**로 RDB 대비 전체적으로 **70~98% 수준에서 부하와 I/O 효율 향상**  
- CPU/디스크 부담이 크게 줄어 **대규모 삽입/조회 환경에서 압도적 성능 우위**  
- 메모리 한계 및 장애 대비는 필요하지만, **캐시용 저장소로 최적화 시 최적 선택**
---
<br>

## 📌 결론
- 대용량 중복 데이터 삽입/조회에는 Redis가 훨씬 효율적 → 디스크 I/O 및 CPU 부하 감소, 처리 속도 향상

### 💡 목적 기준 선택 이유
- URL + 타이틀 기준 이미 중복된 헤더는 Redis 캐시에만 존재하고 카프카에 프로듀싱하지 않음
- 즉, 영속적 저장소가 아닌 **캐시용 저장소로서 성능 최적화 목적**
- 디스크 기반 RDB 대비 100%는 아니지만 **--save 옵션** 사용으로 최소한의 영속성 및 복구 보장
---
<br>

## ✅ 최종 선택
- **Redis 선택 → 대규모 조회/삽입 효율 극대화 + 서버 부하 최소화**
---
