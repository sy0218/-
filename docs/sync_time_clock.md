# ⏰ 클러스터 서버 시간 & 클럭 동기화 (AP 기준)

---

## 📌 개요
- 클러스터 전체 서버를 **AP 서버 기준**으로 시간 동기화  
- NTP 서버(`0.kr.pool.ntp.org`) 연동  
- 타 서버는 systemd-timesyncd 데몬 **중지 및 비활성화**  
- 정기적 시간 동기화는 **Crontab + 스크립트** 활용  

---
<br>

## ⚙️ AP 서버 설정
### 1️⃣ 시간대 및 서비스 활성화
```bash
timedatectl set-timezone Asia/Seoul
timedatectl  # 변경 확인

apt-get update
apt-get install -y systemd-timesyncd

systemctl enable systemd-timesyncd
systemctl start systemd-timesyncd
systemctl status systemd-timesyncd
```
### 2️⃣ NTP 서버 지정
- `/etc/systemd/timesyncd.conf` 수정
```ini
NTP=0.kr.pool.ntp.org
#FallbackNTP=ntp.ubuntu.com
#RootDistanceMaxSec=5
PollIntervalMinSec=86400
PollIntervalMaxSec=86400
```
```bash
systemctl restart systemd-timesyncd
timedatectl status  # 동기화 상태 확인
```

---
<br>

## ⚙️ 타 서버 설정 (sn1, sn2, sn3, m1, m2, s1)
```bash
# 모든 동기화 데몬 중지 및 비활성화
systemctl stop chrony ntp systemd-timesyncd
systemctl disable chrony ntp systemd-timesyncd
```
> **⚠️ AP 서버 기준으로 동기화되도록 타 서버는 모든 동기화 서비스 중지**

---
<br>

## 🛠 클러스터 시간 동기화 스크립트
- `sync_time_clock.sh`
```bash
#!/usr/bin/bash
. /etc/sy_script
. ${Sy_Dir}/Sy_Scripts/functions.sh

# 서버 목록
SERVERS=(sn1 sn2 sn3 m1 m2 s1)
ALL_SERVERS=(ap sn1 sn2 sn3 m1 m2 s1)

# AP 서버 기준 타 서버 시간/클럭 동기화
for SERVER in "${SERVERS[@]}";
do
    log_info "[Start] ${SERVER} time and clock rsync ..."
    ssh ${SERVER} "date -s \"$(date '+%Y-%m-%d %H:%M:%S')\" && hwclock -w"
    log_info "[End] ${SERVER} time and clock rsync ..."
    echo ""
done

# 전체 서버 시간 확인
for SERVER in "${ALL_SERVERS[@]}";
do
    log_info ">>> ${SERVER}:"
    ssh ${SERVER} "date '+%Y-%m-%d %H:%M:%S'"
done
```

---
<br>

## ⏰ 정기적 동기화 (Crontab)
```cron
# 매일 0시, 12시 클러스터 시간/클럭 동기화
0 0,12 * * * /work/jsy/Sy_Scripts/sync_time_clock.sh >> /work/jsy/job_project/logs/sync_time_clock_$(date +\%Y\%m\%d_\%H).log 2>&1
```

---
<br>

## ✅ 결과 확인
- AP 서버 기준 전체 서버 시간/하드웨어 클럭 정확히 동기화
- 타 서버 systemd-timesyncd 비활성화로 시간 충돌 방지
- Crontab으로 하루 2회 자동 동기화 수행
- 동기화 상태 확인: `timedatectl status` 또는 스크립트 로그
---
