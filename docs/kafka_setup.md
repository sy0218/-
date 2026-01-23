# 📡 Ubuntu에서 Apache Kafka 설치 & 환경 구축

---

## 📌 개요
- Ubuntu 환경에서 **Kafka 클러스터 설치, 브로커 설정, Python 프로듀서 사용법** 가이드
- 로컬 설치 기준으로 작성 (Ansible 없이 직접 실행)

🚀 **Ansible로 자동화된 환경 설정 예시**는 🔗 [`Ansible 레포지토리`](https://github.com/sy0218/Ansible-Multi-Server-Setup)에서 확인하세요!

---
<br>

## ⚙️ Kafka 다운로드 및 설치
```bash
wget https://archive.apache.org/dist/kafka/3.6.2/kafka_2.13-3.6.2.tgz
tar -xvf kafka_2.13-3.6.2.tgz -C /application/
ln -s /application/kafka_2.13-3.6.2 /application/kafka
```

---
<br>

## ⚙️ Kafka 로그 디렉토리 생성
```bash
mkdir -p /logs/kafka_log
```

---
<br>

## ⚙️ Kafka 설정 (server.properties)
```bash
vi /application/kafka/config/server.properties
```
```properties
broker.id=1
log.dirs=/logs/kafka_log
listeners=PLAINTEXT://0.0.0.0:9092
advertised.listeners=PLAINTEXT://192.168.56.60:9092
zookeeper.connect=192.168.56.60:2181,192.168.56.61:2181,192.168.56.62:2181
group.initial.rebalance.delay.ms=3000
```

---
<br>

## ⚙️ 환경 변수 등록
```bash
vi /root/.bashrc

export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export ZOOKEEPER_HOME=/application/zookeeper
export KAFKA_HOME=/application/kafka
export PATH=$JAVA_HOME/bin:$ZOOKEEPER_HOME/bin:$KAFKA_HOME/bin:$PATH

source ~/.bashrc
```

---
<br>

## ⚙️ Kafka 및 ZooKeeper 실행
```bash
# ZooKeeper 실행
/Data_project_job/work/zookeeper.sh start

# Kafka 실행
kafka-server-start.sh -daemon /application/kafka/config/server.properties
```

---
<br>

## ⚙️ Kafka 상태 확인
```bash
# 포트 리스닝 확인
netstat -tuln | grep 9092

# 브로커 API 버전 확인
kafka-broker-api-versions.sh --bootstrap-server 192.168.56.60:9092
```

---
<br>

## ⚙️ Kafka 종료
```bash
kafka-server-stop.sh
```

---
<br>

## ⚙️ Kafka Python 사용법
```bash
pip install kafka-python==2.1.5
```
> **버전 호환:** https://github.com/dpkp/kafka-python/releases

---
<br>

## ⚙️ systemd 서비스로 Kafka 관리
```bash
# 서비스 파일 예시: /etc/systemd/system/kafka-server.service
[Unit]
Description=kafka-server
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/application/kafka
ExecStart=/application/kafka/bin/kafka-server-start.sh /application/kafka/config/server.properties
ExecStop=/application/kafka/bin/kafka-server-stop.sh

[Install]
WantedBy=multi-user.target
```
### ✔ 서비스 관리 명령어
```bash
# 서비스 등록 및 실행
sudo systemctl daemon-reload
sudo systemctl enable kafka-server
sudo systemctl start kafka-server

# 상태 확인
sudo systemctl status kafka-server

# 서비스 종료
sudo systemctl stop kafka-server
```

---
<br>

## ✅ 참고 사항
- Kafka 브로커별 `broker.id`는 **서로 고유하게 설정**해야 합니다.
- `log.dirs` 경로는 **존재하고 쓰기 권한이 있어야** 합니다.
- 클러스터 환경에서는 `zookeeper.connect`에 **모든 ZooKeeper 서버**를 포함해야 합니다.
- systemd 서비스로 등록하면 서버 재부팅 시 **Kafka 자동 시작 및 관리**가 가능합니다.
---
