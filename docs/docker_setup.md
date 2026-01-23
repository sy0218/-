# 🐳 Ubuntu에서 Docker 설치 & 환경 구축 (Ansible 자동화)

---

## 📌 개요
- Ubuntu 환경에서 **Docker Engine 설치 및 환경 구성** 가이드
- 로컬 설치 기준으로 작성 (Ansible 없이 직접 실행)
- Docker `data-root` 경로 커스텀 설정 및 서비스 활성화
> 🚀 **Ansible로 자동화된 환경 설정 예시**는 🔗 [`Ansible 레포지토리`](https://github.com/sy0218/Ansible-Multi-Server-Setup)에서 확인하세요!

>💡 **설명**: 이 가이드는 설치 순서대로 따라 하면 바로 Docker를 사용할 수 있도록 구성되어 있습니다.

---
<br>

## ⚙️ 패키지 업데이트
```bash
apt-get update
apt-get upgrade -y
```
> 💡 **설명**: 시스템 패키지를 최신 상태로 유지하는 것은 의존성 문제를 예방하고 안정적인 설치를 위해 필수입니다.

---
<br>

## ⚙️ Docker 설치에 필요한 패키지 설치 (keyrings 방식)
```bash
apt-get install -y \
  ca-certificates \
  curl \
  gnupg \
  software-properties-common
```
> 💡 **설명**: Docker 설치 전 필요한 필수 패키지들입니다. 인증서, GPG 키 처리, 저장소 관리에 필요합니다.

---
<br>

## ⚙️ keyrings 디렉토리 생성
```bash
mkdir -p /etc/apt/keyrings
chmod 755 /etc/apt/keyrings
```
> 💡 **설명**: GPG 키를 안전하게 저장할 디렉토리 생성. 권한 설정은 시스템 보안을 위해 중요합니다.

---
<br>

## ⚙️ Docker GPG 키 추가
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```
> 💡 **설명**: Docker 공식 패키지 서명을 검증할 GPG 키를 추가합니다. 신뢰할 수 있는 저장소에서만 설치되도록 보장합니다.


---
<br>

## ⚙️ Docker 공식 APT 저장소 추가
```bash
echo \
  "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
> 💡 **설명**: Ubuntu 패키지 관리자에 Docker 공식 저장소를 등록합니다. 이제 apt로 최신 Docker 패키지를 설치할 수 있습니다.

---
<br>

## ⚙️ Docker 저장소 반영
```bash
apt-get update
```
> 💡 **설명**: 새로 추가한 Docker 저장소 정보를 시스템에 반영합니다.

---
<br>

## ⚙️ Docker Engine 설치
```bash
apt-get install -y docker-ce docker-ce-cli containerd.io
```
> 💡 **설명**: Docker Engine과 CLI, 컨테이너 런타임(containerd)을 설치합니다. 설치 후 바로 컨테이너를 실행할 수 있습니다.

---
<br>

## ⚙️ Docker data-root 디렉토리 생성 (커스텀 경로)
```bash
mkdir -p /data/docker
chmod 711 /data/docker
```
> 💡 **설명**: Docker 컨테이너와 이미지 데이터를 저장할 디렉토리를 커스텀 경로로 생성합니다. 디폴트 `/var/lib/docker` 대신 사용 가능합니다.

---
<br>

## ⚙️ Docker daemon.json 설정
```bash
mkdir -p /etc/docker
tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "data-root": "/data/docker"
}
EOF
```
> 💡 **설명**: Docker 데몬이 사용할 루트 경로를 `daemon.json`에서 지정합니다. 커스텀 `data-root` 적용을 위해 필수입니다.

---
<br>

## ⚙️ Docker 서비스 활성화 및 실행
```bash
systemctl enable docker
systemctl start docker
systemctl status docker
```
> 💡 **설명**: Docker를 시스템 서비스로 등록하고, 부팅 시 자동 시작되도록 활성화합니다. 정상적으로 동작하는지 상태 확인도 포함합니다.

---
<br>

## ✅ 결과 확인
```bash
docker info
docker run hello-world
```
>💡 **설명**: 설치 확인 단계입니다. docker info로 시스템 정보를 확인하고, hello-world 컨테이너 실행으로 정상 동작 여부를 테스트합니다.
---
