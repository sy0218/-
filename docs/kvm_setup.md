# 🖲️ KVM 기반 Ubuntu 서버 설치

---

## 📌 개요
- Ubuntu 22.04 서버 ISO를 사용한 **KVM 가상 머신 설치 가이드**
- 커스텀 스토리지 레이아웃 및 네트워크 설정
- 설치 완료 후 root 계정 활성화 및 SSH 접속 가능 상태 구성
- 설치 스크립트 및 설정은 SN1 서버 기준

---
<br>

## ⚙️ ISO 다운로드 및 디스크 이미지 생성
```bash
# ISO 이미지 다운로드
wget https://releases.ubuntu.com/22.04/ubuntu-22.04.5-live-server-amd64.iso -O /var/lib/libvirt/boot/ubuntu2204.iso

# 디스크 이미지 생성
qemu-img create -f qcow2 /var/lib/libvirt/images/sn1.qcow2 40G
```

---
<br>

## ⚙️ 가상 머신 설치
```bash
virt-install \
  --name sn1 \
  --ram 7168 \
  --vcpus 3 \
  --os-variant ubuntu22.04 \
  --cdrom /var/lib/libvirt/boot/ubuntu2204.iso \
  --disk path=/var/lib/libvirt/images/sn1.qcow2,format=qcow2 \
  --network network=default \
  --graphics none \
  --console pty,target_type=serial \
  --boot useserial=on
```

---
<br>

## ⚙️ 설치 중 주요 설정
1) GRUB 부트 커맨드 수정 → e 눌러 아래 수정 후 F10
```bash
linux /casper/vmlinuz --- console=ttyS0,115200n8
```
2) 설치 모드: `Continue in basic mode` 선택
3) 업데이트: `Continue without updating`
4) 키보드 레이아웃: `Korean`
5) 서버 선택: `Ubuntu Server`
6) 네트워크 설정 (IPv4):
```yaml
Subnet: 192.168.122.0/24
Address: 192.168.122.60
Gateway: 192.168.122.1
Name servers: 8.8.8.8
```
7) 프록시: 비워두고 `Done`
8) 미러: 자동 설정 후 `Done`

---
<br>

## ⚙️ 저장소 설정 (커스텀 스토리지 레이아웃)
- /data1 ~ /data4: 각각 3G (ext4)
- /home: 1G (ext4)
- /var: 4G (ext4)
- /: 나머지 용량

### ✔ 예시 파티션 👇
```bash
vda     40G
├─vda1   1M
├─vda2   3G ext4   /data1
├─vda3   3G ext4   /data2
├─vda4   3G ext4   /data3
├─vda5   1G ext4   /home
├─vda6   4G ext4   /var
└─vda7  26G ext4   /
```
- 설정 완료 후 `Done > Continue`

---
<br>

## ⚙️ 프로필 설정
- 이름: user
- 서버명: sn1
- 사용자명: user
- 비밀번호: 1234
- Ubuntu Pro 제안 → Skip for now
- SSH 설정 → [X] Install OpenSSH server 체크
- 추가 Snap 설치 → Done
- 설치 완료 후 재부팅 → Reboot Now
> **`Failed unmounting /cdrom` 메시지 후 Enter → 정상 부팅**

---
<br>

## ⚙️ 부팅 후 초기 작업
```bash
# 1. root 계정 활성화
sudo -s
passwd root

# 2. NIC 이름 변경 설정
nano /etc/default/grub
# GRUB_CMDLINE_LINUX_DEFAULT 줄을 아래처럼 수정
GRUB_CMDLINE_LINUX_DEFAULT="net.ifnames=0 biosdevname=0"

# grub 업데이트 및 재부팅
update-grub
reboot
```

### ✔ SSH 접근 확인
```bash
# 콘솔 나가기
Ctrl + ]

# 호스트에서 접근 확인
ping 192.168.122.60
ssh user@192.168.122.60
```
### ✔root 권한 SSH 설정
```bash
sudo su -
passwd root

# sshd config 파일 수정
vi /etc/ssh/sshd_config
# PermitRootLogin yes 추가
sudo systemctl restart sshd
```

---
<br>

## ✅ 결과 확인
- SN1 서버 Ubuntu 22.04 설치 완료
- 커스텀 파티션 구성 완료 (/data1~4, /home, /var, /)
- root 계정 SSH 접속 가능
- 네트워크 및 NIC 이름 설정 완료
- 향후 클러스터 구성 시 기준 서버로 활용 가능
---
