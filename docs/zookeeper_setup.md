# 🦓 Ubuntu에서 ZooKeeper 설치 & 환경 구축

---

## 📌 개요
- Ubuntu 환경에서 **ZooKeeper 설치 및 클러스터 초기 구성** 가이드
- Java 설치, 환경 변수 설정, 데이터 디렉토리, `zoo.cfg` 구성 포함
- 로컬 설치 기준으로 작성 (Ansible 없이 직접 실행)

🚀 **Ansible로 자동화된 환경 설정 예시**는 🔗 [`Ansible 레포지토리`](https://github.com/sy0218/Ansible-Multi-Server-Setup)에서 확인하세요!

---
<br>

## ⚙️ Java 설치
```bash
sudo apt update -y
sudo apt install -y openjdk-11-jdk
java -version
```

---
<br>

## ⚙️ 환경 변수 등록
```bash
vi ~/.bashrc

# 추가 내용
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

source ~/.bashrc
```

---
<br>

## ⚙️ ZooKeeper 설치
```bash
# 설치 디렉토리 생성
sudo mkdir -p /application
cd /application

# ZooKeeper 다운로드 및 압축 해제
wget https://archive.apache.org/dist/zookeeper/zookeeper-3.7.2/apache-zookeeper-3.7.2-bin.tar.gz
tar xzvf apache-zookeeper-3.7.2-bin.tar.gz

# 심볼릭 링크 생성
ln -s apache-zookeeper-3.7.2-bin zookeeper
```

---
<br>

## ⚙️ 데이터 디렉토리 및 myid 설정
```bash
mkdir -p /application/id_zookeeper
echo 1 > /application/id_zookeeper/myid
cat /application/id_zookeeper/myi
```

---
<br>

## ⚙️ ZooKeeper 설정 (zoo.cfg)
```bash
vi /application/zookeeper/conf/zoo.cfg
---
tickTime=2000
initLimit=10
syncLimit=5
dataDir=/application/id_zookeeper       # 데이터 디렉토리
clientPort=2181                         # 클라이언트 접속 포트

# ZooKeeper 클러스터 서버 정의
server.1=ap:2888:3888
server.2=s1:2888:3888
server.3=s2:2888:3888
---
```

---
<br>

## ⚙️ 환경 변수 재설정 (ZooKeeper 포함)
```bash
vi ~/.bashrc

# 추가 내용
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export ZOOKEEPER_HOME=/application/zookeeper
export PATH=$JAVA_HOME/bin:$ZOOKEEPER_HOME/bin:$PATH

source ~/.bashrc
```

---
<br>

## ⚙️ ZooKeeper 실행 스크립트
```bash
# ZooKeeper 시작
/Data_project_job/work/zookeeper.sh start

# ZooKeeper 상태 확인
/Data_project_job/work/zookeeper.sh status

# ZooKeeper 종료
/Data_project_job/work/zookeeper.sh stop
```

---
<br>

## ⚙️ systemd 서비스로 ZooKeeper 관리
```bash
# 서비스 파일 예시: /etc/systemd/system/zookeeper-server.service
[Unit]
Description=Zookeeper Server
After=network.target

[Service]
Type=forking
User=root
Group=root
SyslogIdentifier=zookeeper-server
WorkingDirectory=/application/zookeeper
ExecStart=/application/zookeeper/bin/zkServer.sh start
ExecStop=/application/zookeeper/bin/zkServer.sh stop

[Install]
WantedBy=multi-user.target
```
### ✔ 서비스 관리 명령어
```bash
# 서비스 등록 후 실행
sudo systemctl daemon-reload
sudo systemctl enable zookeeper-server
sudo systemctl start zookeeper-server

# 상태 확인
sudo systemctl status zookeeper-server

# 서비스 종료
sudo systemctl stop zookeeper-server
```

---
<br>

## ✅ 참고 사항
- `zoo.cfg`의 `dataDir` 항목에는 **공백 없이** 정확한 경로를 지정해야 합니다.
- 각 서버의 `myid`는 `server.X`의 X 값과 동일해야 하며, `dataDir` 경로 안에 `myid` 파일로 저장되어야 합니다.
- ZooKeeper는 **클러스터(앙상블)** 구성을 위해 `server.1`, `server.2`, … 설정이 필요합니다.
- systemd 서비스로 등록하면 서버 재부팅 시 **자동 시작 및 관리**가 가능합니다.
---
