# 🖥️ 운영 서버 다중 클러스터 모니터링

- **목적**: 여러 운영 서버(클러스터) 환경에서 Node Exporter, Prometheus, Grafana를 활용한 모니터링 구축
---
<br>

## 🔹 모니터링 파이프라인 (멀티 서버 환경)
```scss
     ┌─────────────┐
     │ Node Exporter │ (서버1)
     └─────────────┘
             │
             ▼
     ┌─────────────┐
     │ Node Exporter │ (서버2)
     └─────────────┘
             │
             ▼
     ┌─────────────┐
     │ Node Exporter │ (서버3)
     └─────────────┘
             │
             ▼
     ┌─────────────┐
     │ Prometheus  │ (모니터링 서버)
     └─────────────┘
             │
             ▼
     ┌─────────────┐
     │  Grafana    │ (대시보드)
     └─────────────┘
```
```yaml
- Node Exporter: 각 서버에서 CPU, 메모리, 디스크, 네트워크 등 시스템 메트릭 수집  
- Prometheus: Node Exporter 메트릭 스크랩, DB 저장  
- Grafana: Prometheus 데이터를 시각화하여 클러스터 상태 대시보드 제공  
```
---
<br>

## 1️⃣ Node Exporter 셋팅
### 권장 설치 방식
```bash
https://github.com/sy0218/Multi-Server-Setup-Ansible → 레포를 참고하여 Ansible 기반 자동화 설치
```
- **node_exporter service 셋팅 ( 각 서버 )**
```bash
# 서비스용 사용자 생성
useradd -rs /bin/false node_exporter

# 실행 파일 이동
mv node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/

# systemd 서비스 파일 생성
vi /etc/systemd/system/node_exporter.service
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target

# 서비스 등록 및 실행
systemctl daemon-reload
systemctl enable node_exporter   # 부팅 시 자동 시작
systemctl start node_exporter    # 즉시 실행
systemctl status node_exporter   # 상태 확인

# 확인
curl http://localhost:9100/metrics
→ Node Exporter가 9100 포트에서 서버 메트릭 제공
```
---
<br>

## 2️⃣ Prometheus + Grafana 설치 (모니터링 서버)
- **Docker Compose 파일**
```yaml
version: '3'
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - /work/jsy/docker_compose/prometheus_grafana/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    command:
      - "--storage.tsdb.retention.time=2d"
      - "--config.file=/etc/prometheus/prometheus.yml"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```
---
- **Prometheus 설정**
```yaml
global:
  scrape_interval: 10s

scrape_configs:
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['192.168.122.59:9100', '192.168.122.60:9100', '192.168.122.61:9100', '192.168.122.62:9100', '192.168.122.63:9100', '192.168.122.64:9100', '192.168.122.65:9100']
```
##### 🔹 targets에 모니터링할 서버 IP:9100 추가
---
- **Docker Compose 실행**
```bash
docker compose -f prometheus_grafana.yaml up -d
```
---
- **접속**
```bash
Prometheus: http://192.168.56.60:9090
Grafana: http://192.168.56.60:3000
기본 계정: admin / 비밀번호: admin (환경변수 GF_SECURITY_ADMIN_PASSWORD)
```
---
<br>

## 3️⃣ 요약
| 구성 요소         | 역할                                     |
| ------------- | -------------------------------------- |
| Node Exporter | 각 서버의 CPU, 메모리, 디스크, 네트워크 등 시스템 메트릭 수집 |
| Prometheus    | Node Exporter에서 메트릭 스크랩, DB 저장 및 쿼리    |
| Grafana       | Prometheus 데이터를 시각화, 대시보드 제공           |

- 이 구조로 다중 서버/클러스터 환경에서도 한 눈에 운영 상태 모니터링 가능
---
