# 📤 Ubuntu에서 Elasticsearch 8.4.2 설치 & 검색엔진 환경 구축

---

## 📌 개요
- Ubuntu 환경에서 **Elasticsearch 클러스터 설치, 노드 설정, 템플릿 및 인덱스 생성** 가이드
- 공고 **제목/본문 색인** 및 **키워드 검색**, **유사 공고 추천** 기능 지원
- 조회 전용 노드(AP) 분리 → 검색 성능 최적화
- `systemd` 기반 서비스 등록으로 안정적 운영

🚀 **Ansible로 자동화된 환경 설정 예시**는 🔗 [`Ansible 레포지토리`](https://github.com/sy0218/Ansible-Multi-Server-Setup)에서 확인하세요!

---
<br>

## ⚙️ Elasticsearch 다운로드 및 설치

```bash
apt-get install -y apt-transport-https
apt-get update -y && apt-get install -y wget curl

echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" > /etc/apt/sources.list.d/elastic-8.x.list
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -

apt-get update
apt-get install -y elasticsearch=8.4.2
```

---
<br>

## ⚙️ Elasticsearch 설정
### 🔹 조회 전용 노드 (ap)
```yaml
cluster.name: job-cluster
node.name: ap

node.roles: []

path.data: /data/esdata
path.logs: /var/log/elasticsearch

network.host: 192.168.122.59
http.port: 9200

discovery.seed_hosts: ["m1", "m2", "s1"]

xpack.security.enabled: false
xpack.security.enrollment.enabled: false
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false
```
---
### 🔹 데이터 노드 (m1, m2, s1)
```yaml
cluster.name: job-cluster
node.name: m1  # ← 노드마다 고유하게 변경

node.roles: []

path.data: /esdata
path.logs: /var/log/elasticsearch

network.host: 0.0.0.0
http.port: 9200

discovery.seed_hosts: ["m1", "m2", "s1"]
cluster.initial_master_nodes: ["m1"]

xpack.security.enabled: false
xpack.security.enrollment.enabled: false
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false
```

---
<br>

## ⚙️ 환경 변수 등록 (필요 시)
```bash
# JAVA_HOME 환경 변수가 필요하면
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

---
<br>

## ⚙️ Elasticsearch 실행
```bash
# systemd 서비스 실행
systemctl start elasticsearch.service
```

---
<br>

## 🔍 노드 상태 확인
```bash
curl -XGET m1:9200/_cat/nodes?v
```
```nginx
# 예시 출력
ip             heap.percent ram.percent cpu load_1m load_5m load_15m node.role   master name
192.168.122.59            2          98   0    0.05    0.10     0.08 -           -      ap
192.168.122.65            2          72   0    0.00    0.02     0.09 cdfhilmrstw -      s1
192.168.122.64            2          77   0    0.00    0.02     0.09 cdfhilmrstw -      m2
192.168.122.63            2          83   0    0.11    0.07     0.09 cdfhilmrstw *      m1
```

---
<br>

## 📄 Elasticsearch 템플릿 생성
- 제목과 본문을 두 글자 단위로 색인 설정
```bash
curl -XPUT "ap:9200/_index_template/job_postings_template" \
-H "Content-Type: application/json" -d '
{
  "index_patterns": ["job_posting*"],
  "priority": 1,
  "template": {
    "settings": {
      "number_of_replicas": 2,
      "analysis": {
        "tokenizer": {
          "two_gram_tokenizer": {
            "type": "ngram",
            "min_gram": 2,
            "max_gram": 2
          }
        },
        "analyzer": {
          "two_gram_analyzer": {
            "type": "custom",
            "tokenizer": "two_gram_tokenizer",
            "filter": ["lowercase"]
          }
        }
      }
    },
    "mappings": {
      "properties": {
        "domain":    { "type": "keyword" },
        "href":      { "type": "keyword" },
        "company":   { "type": "keyword" },
        "title":     { "type": "text", "analyzer": "two_gram_analyzer" },
        "msgid":     { "type": "keyword" },
        "pay":       { "type": "keyword" },
        "location":  { "type": "keyword" },
        "career":    { "type": "keyword" },
        "education": { "type": "keyword" },
        "deadline":  { "type": "date", "format": "yyyy-MM-dd" },
        "body_text": { "type": "text", "analyzer": "two_gram_analyzer" }
      }
    }
  }
}'
```

---
<br>

## 📝 템플릿 확인
```bash
curl -XGET "ap:9200/_index_template/job_postings_template?pretty"
```

---
<br>

## 📦 인덱스 생성
```bash
curl -XPUT "ap:9200/job_posting"
```

---
<br>

## 📊 인덱스 목록 확인
```bash
curl -XGET "ap:9200/_cat/indices"
```
```plaintext
# 예시 출력
green open job_posting tmros60jTieCykNZh4yAHg 1 2 0 0 675b 225b
```

---
<br>

## 🔍 매핑 확인
```bash
curl -XGET "ap:9200/job_posting/_mapping?pretty"
```
```json
# 예시 출력
{
  "job_posting" : {
    "mappings" : {
      "properties" : {
        "body_text" : {
          "type" : "text",
          "analyzer" : "two_gram_analyzer"
        },
        "career" : { "type" : "keyword" },
        "company" : { "type" : "keyword" },
        "deadline" : { "type" : "date", "format" : "yyyy-MM-dd" },
        "domain" : { "type" : "keyword" },
        "education" : { "type" : "keyword" },
        "href" : { "type" : "keyword" },
        "location" : { "type" : "keyword" },
        "msgid" : { "type" : "keyword" },
        "pay" : { "type" : "keyword" },
        "title" : {
          "type" : "text",
          "analyzer" : "two_gram_analyzer"
        }
      }
    }
  }
}
```

---
<br>

## ✅ 참고 사항
- 각 노드의 `node.name`은 **서로 고유하게 설정**해야 합니다.
- `path.data` 경로는 **존재하고 쓰기 권한이 있어야** 합니다.
- 클러스터 환경에서는 `discovery.seed_hosts`에 **모든 데이터 노드**를 포함해야 합니다.
- 조회 전용 노드(AP)는 `node.roles: []` 로 설정하여 **데이터 쓰기 권한을 제한**하면 성능 최적화 가능
- `systemd` 서비스로 등록하면 서버 재부팅 시 **Elasticsearch 자동 시작 및 관리**가 가능합니다.
- 템플릿 생성 시, **인덱스 패턴**과 **analyzer 설정**을 확인하여 검색 정확도를 높일 수 있습니다.
---
