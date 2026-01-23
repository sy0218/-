#!/usr/bin/python3
import hashlib
import random
import psycopg2
from psycopg2.extras import execute_values

def generate_random_korean(min_len=20, max_len=30):
    length = random.randint(min_len, max_len)
    start = int("AC00", 16)
    end = int("D7A3", 16)
    return "".join([chr(random.randint(start, end)) for _ in range(length)])

# PostgreSQL 연결
pg_conn = psycopg2.connect(
    host="192.168.122.59",
    port=5432,
    dbname="job_pro",
    user="sjj",
    password="1234"
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

# 삽입된 hash set
inserted_hashes = set(r[0] for r in inserted_rows)

for href_hash, job_header in job_hash_map:
    if href_hash in inserted_hashes:
        print(f"[PostgreSQL] 삽입 완료 | company={job_header['company']} | title={job_header['title']}")
    else:
        print(f"[PostgreSQL] 중복 데이터 스킵 | href={job_header['href']}")

pg_cur.close()
pg_conn.close()
