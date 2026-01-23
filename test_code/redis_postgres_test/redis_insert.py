#!/usr/bin/python3
import redis
import hashlib
import random

def generate_random_korean(min_len=20, max_len=30):
    length = random.randint(min_len, max_len)
    start = int("AC00", 16)
    end = int("D7A3", 16)
    return "".join([chr(random.randint(start, end)) for _ in range(length)])

# Redis 연결
redis_conn = redis.Redis(
    host="192.168.122.59",
    port=6379,
    db=0,
    password="1234"
)
redis_key = 'job_set'
redis_pipe = redis_conn.pipeline(transaction=False)

total = 10000
job_headers = []

for i in range(total):
    s = f"https://example.com/job/{i}" + generate_random_korean()
    h = hashlib.sha256(s.encode('utf-8')).hexdigest()
    job_headers.append({'href': s, 'hash': h, 'company': f'Company{i}', 'title': f'Title{i}'})
    redis_pipe.sadd(redis_key, h)

# Redis flush
redis_info = redis_pipe.execute()

# 중복 체크 및 출력
for job_header, flag in zip(job_headers, redis_info):
    if flag == 0:
        print(f"[Redis] 중복 데이터 스킵 | href={job_header['href']}")
    else:
        print(f"[Redis] 캐시 추가 완료 | company={job_header['company']} | title={job_header['title']}")
