# 👁️‍🗨️ Ubuntu 기반 다중 서버 클러스터 모니터링 구축 

---

## 📌 개요
- Ubuntu 환경에서 **다중 운영 서버**를 대상으로 **Node Exporter, Prometheus, Grafana**를 활용한 모니터링 환경 구축 가이드
- 단일 모니터링 서버에서 **여러 서버 메트릭 통합 수집 및 시각화**
- Docker Compose 기반으로 **Prometheus + Grafana** 구성
> 🚀 **Ansible 기반 Node Exporter 자동 설치 예시**는  
> 🔗 https://github.com/sy0218/Multi-Server-Setup-Ansible 참고

>💡 **설명**: 이 가이드는 설치 순서대로 진행하면  
> 다중 서버 환경에서 CPU / 메모리 / 디스크 / 네트워크 상태를  
> Grafana 대시보드로 한눈에 확인할 수 있도록 구성되어 있습니다.

---
<br>

## 🧩 모니터링 아키텍처
```scss
     ┌─────────────┐
     │ Node Exporter │ (서버1)
     └─────────────┘
             │
     ┌─────────────┐
     │ Node Exporter │ (서버2)
     └─────────────┘
             │
     ┌─────────────┐
     │ Node Exporter │ (서버N)
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
- Node Exporter: 각 서버의 시스템 메트릭(CPU, 메모리, 디스크, 네트워크) 수집
- Prometheus: Node Exporter 메트릭 스크랩 및 시계열 데이터 저장
- Grafana: Prometheus 데이터를 기반으로 대시보드 시각화
```

---
<br>

## ⚙️ Node Exporter 설치 (각 운영 서버)
- 서비스용 사용자 생성 → `useradd -rs /bin/false node_exporter`
- 실행 파일 이동 → `mv node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/`
### ✔ systemd 서비스 등록
```bash
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
```
### ✔ 서비스 실행
```bash
systemctl daemon-reload
systemctl enable node_exporter
systemctl start node_exporter
systemctl status node_exporter
```
### ✔ 동작 확인 → `curl http://localhost:9100/metrics`

---
<br>

## ⚙️ Prometheus + Grafana 설치 (모니터링 서버)
### ✔ Docker Compose
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
<br>

## ⚙️ Prometheus 설정
```yaml
global:
  scrape_interval: 10s

scrape_configs:
  - job_name: 'node_exporter'
    static_configs:
      - targets:
        - '192.168.122.59:9100'
        - '192.168.122.60:9100'
        - '192.168.122.61:9100'
        - '192.168.122.62:9100'
        - '192.168.122.63:9100'
        - '192.168.122.64:9100'
        - '192.168.122.65:9100'
```

---
<br>

## ⚙️ Docker Compose 실행
```bash
docker compose -f prometheus_grafana.yaml up -d
```

---
<br>

## ⚙️ 접속 정보
### ✔ 포트 포워딩 / NAT 구성 예시 ( VPN → 내부 모니터링 서버 )
```bash
# ===== Grafana (3000) 포트 DNAT =====
iptables -t nat -A PREROUTING -p tcp -s 10.0.0.0/24 --dport 3000 \
  -j DNAT --to-destination 10.1.2.3:3000

iptables -t nat -A POSTROUTING -p tcp -d 10.1.2.3 --dport 3000 \
  -j MASQUERADE

iptables -I FORWARD -p tcp -d 10.1.2.3 --dport 3000 -j ACCEPT
iptables -I FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT


# ===== Prometheus (9090) 포트 DNAT =====
# PREROUTING: VPN 내부망 → AP 서버
iptables -t nat -A PREROUTING -p tcp -s 10.0.0.0/24 --dport 9090 \
  -j DNAT --to-destination 10.1.2.3:9090

# POSTROUTING: 응답 패킷 NAT
iptables -t nat -A POSTROUTING -p tcp -d 10.1.2.3 --dport 9090 \
  -j MASQUERADE

# FORWARD: 9090 포트 허용
iptables -I FORWARD -p tcp -d 10.1.2.3 --dport 9090 -j ACCEPT
iptables -I FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
```
### ✔ UI 접속
```bash
Prometheus: http://192.168.56.60:9090
Grafana:    http://192.168.56.60:3000

ID / PW
admin / admin
```

---
<br>

## ⚙️ Grafana 대시보드
- Data Source: Prometheus
- 사용자 환경에 맞는 대시보드 생성~


---
<br>

## ✅ 요약

| 구성 요소        | 역할                                   |
|------------------|----------------------------------------|
| **Node Exporter** | 각 서버의 CPU, 메모리, 디스크, 네트워크 등 시스템 메트릭 수집 |
| **Prometheus**   | Node Exporter 메트릭 스크랩 및 시계열 데이터 저장 |
| **Grafana**      | Prometheus 데이터를 시각화하여 클러스터 상태 대시보드 제공 |

---
