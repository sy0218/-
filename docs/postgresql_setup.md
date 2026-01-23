# 💾 Ubuntu에서 PostgreSQL 설치 & 데이터베이스 구축

---

## 📌 개요
- Ubuntu 환경에서 **PostgreSQL 설치 및 Docker 기반 데이터베이스 환경 구성** 가이드
- 데이터베이스, 사용자, 스키마, 권한 설정 포함
- 로컬 설치 기준으로 작성 (Ansible 없이 직접 실행)

🚀 **Ansible로 자동화된 환경 설정 예시**는 🔗 [`Ansible 레포지토리`](https://github.com/sy0218/Ansible-Multi-Server-Setup)에서 확인하세요!

---
<br>

## ⚙️ 1. PostgreSQL Docker 컨테이너 실행
```bash
docker run --name job_postgres \
  -v /Data_project_job/docker_image/postgres/pgdata:/var/lib/postgresql/data \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=1234 \
  -d postgres:14
```
- `-v` 옵션: 호스트와 컨테이너 간 데이터 볼륨 매핑
- `-p 5432:5432`: 로컬 포트 5432와 컨테이너 포트 5432 연결
- `-e POSTGRES_PASSWORD=1234`: postgres 기본 계정 비밀번호 설정

---
<br>

## ⚙️ PostgreSQL 접속 확인
```bash
psql -U postgres -h localhost -p 5432
```

---
<br>

## ⚙️사용자 및 데이터베이스 생성
```sql
-- 사용자 생성
CREATE USER sjj WITH PASSWORD '1234';
CREATE USER hive WITH PASSWORD '1234';

-- job_pro 데이터베이스 생성
CREATE DATABASE job_pro OWNER sjj;

-- job_pro 데이터베이스 접속
\c job_pro

-- 스키마 생성 및 권한 설정
CREATE SCHEMA job AUTHORIZATION sjj;
CREATE SCHEMA hive AUTHORIZATION hive;

-- 권한 부여
GRANT ALL ON DATABASE job_pro TO sjj;
GRANT SELECT ON ALL TABLES IN SCHEMA hive TO sjj;
```

---
<br>

## ✅ 결과 확인
- Docker 기반 **PostgreSQL 컨테이너 실행 완료**
- 데이터베이스, 사용자, 스키마 생성 완료
- 스키마별 권한 설정 완료
- 로컬 서버 기준 **애플리케이션/테스트 환경** 구성 가능
---
