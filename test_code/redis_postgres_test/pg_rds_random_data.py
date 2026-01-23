#!/usr/bin/python3
import redis
import hashlib
import random
import psycopg2
from psycopg2.extras import execute_batch


def generate_random_korean(min_len=20, max_len=30):
    length = random.randint(min_len, max_len)
    
    # 한글 음절 유니코드 범위: '가'(0xAC00) ~ '힣'(0xD7A3)
    start = int("AC00", 16)
    end = int("D7A3", 16)
    
    # 랜덤한 한글 문자를 조합하여 리스트 생성
    result = [chr(random.randint(start, end)) for _ in range(length)]
    
    return "".join(result)

# Redis
redis_conn = redis.Redis(
    host="192.168.122.59",
    port=6379,
    db=0,
    password = "1234"
)
redis_key = 'job_set'
redis_pipe = redis_conn.pipeline(transaction=False)


# PostgreSQL
pg_conn = psycopg2.connect(
    host="192.168.122.59",
    port=5432,
    dbname="job_pro",
    user="sjj",
    password="1234"
)
pg_conn.autocommit = False
pg_cur = pg_conn.cursor()

# insert Query
insert_sql = """
INSERT INTO job.job_set (job_set)
VALUES (%s)
"""

total=10000000
pg_batch = []

for i in range(total):
    s = f"https://example.com/job/{i}" + generate_random_korean()
    h = hashlib.sha256(s.encode('utf-8')).hexdigest()

    redis_pipe.sadd(redis_key, h)
    pg_batch.append((h,))

    if (i + 1) % 1000000 == 0:
        # Redis flush
        redis_pipe.execute()
        print(f"Redis Executed at {i + 1}")

        # PostgreSQL flush
        execute_batch(pg_cur, insert_sql, pg_batch)
        pg_conn.commit()

        pg_batch.clear()
        print(f"Postgresql Executed at {i + 1}")

pg_cur.close()
pg_conn.close()
