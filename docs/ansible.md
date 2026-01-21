# 🔍 Ansible Multi-Server Setup
> 🔗 **GitHub Repository:**  
> **[https://github.com/sy0218/Ansible-Multi-Server-Setup](https://github.com/sy0218/Ansible-Multi-Server-Setup)**
---
<br><br>

## 📌 프로젝트 목적
다중 서버/클러스터 환경에서 인프라와 빅데이터 프레임워크 구축을 **자동화**하여  
시간과 노력을 단축하고 **효율성을 높이는 것**을 목표로 합니다.

초기에는 셸 스크립트를 이용한 자동화를 시도했으나,  
신규 기능 추가 시 작업량이 많고 **멱등성(idempotency) 구현, 유지보수, 재사용성 측면에서 한계**가 존재했습니다.

이를 개선하기 위해 **Ansible**을 도입하여, 서버 환경 구성과 테스트 환경 셋업을  
**효율적이고 재사용 가능하게 자동화**하도록 설계했습니다.

---
<br><br>

# 🛑 문제 (Problem)
- 다중 서버/클러스터 환경에서 **리눅스 환경 구성 및 서비스 설치에 많은 시간과 노력 소요**  
- 테스트 환경 반복 시 **수동 작업 오류 발생 가능성 증가**  
- 셸 스크립트 기반 자동화는 **재사용성과 유지보수가 떨어지고**, 신규 자동화 개발 시 **작업량 과다**
---
## 💡 Ansible 사용 이유 (Why Ansible)
- **멀티 서버/클러스터 동시 구성 가능** → 반복 작업 최소화  
- **역할(Role) 단위 모듈화** → 재사용성 및 유지보수 용이  
- **멱등성(idempotency) 보장** → 반복 실행 시 상태 일관성 유지  
- 셸 스크립트 대비 **비즈니스 로직 반영과 확장성 뛰어남**
---
## ⚙ 해결 방법 (Solution)
- **Ansible 플레이북 + 역할(Role) 구조** 사용 → 서버 환경 설정, 패키지 설치, 클러스터 구성 자동화  
- 반복 테스트 환경 구축 시 **같은 플레이북 재사용 가능**  
- 역할별로 기능을 **모듈화** → 신규 자동화 개발 시 작업량 최소화  
---
<br><br>

# 📊 결과 (Result)
## 1️⃣ 자동화 모듈(Role) 그룹화 및 적용 현황
### 🖥 기본 OS 설정 (22개)
| Role (모듈) | 주요 기능/설명 |
|-------------|----------------|
| control | 제어 노드 기본 설정 |
| root_password | 루트 계정 패스워드 설정 |
| packages | 공통 필수 패키지 설치 |
| pip_packages | Python 패키지 설치 |
| nicname | 네트워크 인터페이스 이름 통일 |
| cloud_init | cloud-init 비활성화 |
| ufw | 방화벽(UFW) 비활성화 |
| locale_ko | 로케일 한국어 설정 |
| ssh_root_login | SSH 루트 로그인 설정 |
| timezone | 시간대 설정 |
| ntp | 시간 동기화 설정 |
| open_files | 오픈 파일 수 제한 설정 |
| logrotate | 로그 로테이션 설정 |
| shell_default | 기본 쉘 설정 변경 |
| java | Java 설치 및 환경 설정 |
| disable_swap | 스왑 비활성화 |
| package_version_lock | 패키지 버전 고정 |
| package_update_lock | 자동 업데이트 비활성화 |
| bash_common | 공통 Bash 설정 |
| ssh_keygen | SSH 키 생성 및 배포 |
| etc_hosts | /etc/hosts 자동 구성 |

### ⚙ 애플리케이션/서비스 설치 (10개)
| Role (모듈) | 주요 기능/설명 |
|-------------|----------------|
| docker | Docker 설치 |
| zookeeper | ZooKeeper 설치 |
| kafka | Kafka 설치 |
| postgresql | postgresql 설치 및 Docker 실행 |
| redis | Redis 설치 및 Docker 실행 |
| hadoop | Hadoop 설치 |
| elasticsearch | Elasticsearch 설치 |

---

## 2️⃣ 자동화 모듈 총 집계
| 그룹 | 역할(Role) 수 |
|------|----------------|
| 기본 OS 설정 | 22 |
| 애플리케이션/서비스 설치 | 7 |
| **총합** | 29개 |

---

## 3️⃣ 성과 요약
✅ **29개 모듈 자동화** → OS 초기 설정부터 미들웨어/서비스 설치까지  
✅ **반복 테스트 환경 구축 가능** → Ansible 플레이북 한 번으로 안정적 수행  
✅ **재사용성, 유지보수 용이성, 멱등성 보장 향상**  
✅ **서버 환경 구축 시간과 노력 대폭 감소**

---
