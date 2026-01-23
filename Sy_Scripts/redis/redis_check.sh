#!/bin/bash
. /etc/sy_script
. ${Sy_Dir}/Sy_Scripts/functions.sh

set -e

# 1. 초기 입력
echo -n "관리할 Redis 컨테이너명을 입력하시오: "
read CONTAINER_NAME

if [ -z "${CONTAINER_NAME}" ]; then
    log_error "컨테이너명이 입력되지 않았습니다."
    exit 1
fi

if ! docker ps --filter "name=${CONTAINER_NAME}" --filter "status=running" | grep -q "${CONTAINER_NAME}"; then
    log_error "컨테이너 '${CONTAINER_NAME}'이(가) 실행 중이 아니거나 존재하지 않습니다."
    exit 1
fi

echo -n "Redis 패스워드를 입력하시오: "
read -s REDIS_PASS
echo ""

# 2. 연결 테스트 (공통 함수 사용)
if ! run_redis "${CONTAINER_NAME}" "${REDIS_PASS}" ping | grep -q "PONG"; then
    log_error "Redis 인증 실패 또는 연결 불가!"
    exit 1
fi

log_info "컨테이너 [${CONTAINER_NAME}] 인증 성공."

# 3. 메인 루프
while true; do
    echo ""
    echo "------------------------------------------"
    echo "    Redis (${CONTAINER_NAME}) 관리 도구"
    echo "------------------------------------------"
    echo "1) DB 확인 (Select)"
    echo "2) 모든 키 목록 조회 (KEYS *)"
    echo "3) 키 멤버 확인 (SMEMBERS)"
    echo "4) 키 개수 확인 (SCARD)"
    echo "5) 데이터 일부 조회 (SSCAN)"
    echo "6) 특정 값 존재 여부 확인 (SISMEMBER)"
    echo "7) 키 삭제 (DEL)"
    echo "8) 키 메모리 사용량 확인 (MB)"
    echo "q) 종료"
    echo "------------------------------------------"
    read -p "메뉴 번호를 선택하세요: " choice

    case $choice in
        1)
            read -p "확인할 DB 번호를 입력하세요: " db_num
            if [ -n "${db_num}" ]; then
                log_info "DB ${db_num}번 선택 및 연결 확인"
                run_redis "${CONTAINER_NAME}" "${REDIS_PASS}" select "${db_num}"
            else
                log_error "DB 번호 누락"
            fi
            ;;
        2)
            log_info "전체 키 목록 조회"
            run_redis "${CONTAINER_NAME}" "${REDIS_PASS}" KEYS "*"
            ;;
        3)
            read -p "확인할 Redis Key를 입력하세요: " key_name
            if [ -n "${key_name}" ]; then
                log_info "${key_name} 모든 값 확인 (SMEMBERS)"
                run_redis "${CONTAINER_NAME}" "${REDIS_PASS}" SMEMBERS "${key_name}"
            else
                log_error "Key 누락"
            fi
            ;;
        4)
            read -p "개수를 확인할 Redis Key를 입력하세요: " key_name
            if [ -n "${key_name}" ]; then
                log_info "${key_name} 전체 개수 확인 (SCARD)"
                run_redis "${CONTAINER_NAME}" "${REDIS_PASS}" SCARD "${key_name}"
            else
                log_error "Key 누락"
            fi
            ;;
        5)
            read -p "조회할 Redis Key를 입력하세요: " key_name
            if [ -n "${key_name}" ]; then
                log_info "${key_name} 일부 조회 (SSCAN 0)"
                run_redis "${CONTAINER_NAME}" "${REDIS_PASS}" SSCAN "${key_name}" 0
            else
                log_error "Key 누락"
            fi
            ;;
        6)
            read -p "대상 Redis Key를 입력하세요: " key_name
            read -p "확인할 '값(Value)'을 입력하세요: " search_val
            if [ -n "${key_name}" ] && [ -n "${search_val}" ]; then
                log_info "${key_name} 내에 '${search_val}' 존재 여부 확인"
                RESULT=$(run_redis "${CONTAINER_NAME}" "${REDIS_PASS}" SISMEMBER "${key_name}" "${search_val}")
                [ "$RESULT" == "1" ] && echo ">> [1] 이미 존재" || echo ">> [0] 없음"
            else
                log_error "Key/Value 누락"
            fi
            ;;
        7)
            read -p "삭제할 Redis Key를 입력하세요: " key_name
            if [ -n "${key_name}" ]; then
                read -p "정말 '${key_name}'을(를) 삭제하시겠습니까? (y/n): " confirm
                if [ "$confirm" = "y" ]; then
                    log_info "${key_name} 삭제 완료"
                    run_redis "${CONTAINER_NAME}" "${REDIS_PASS}" DEL "${key_name}"
                fi
            else
                log_error "Key 누락"
            fi
            ;;
        8)
            read -p "메모리 사용량을 확인할 Redis Key를 입력하세요: " key_name
            if [ -n "${key_name}" ]; then
                log_info "${key_name} 메모리 사용량 확인 (bytes)"
                RESULT=$(run_redis "${CONTAINER_NAME}" "${REDIS_PASS}" MEMORY USAGE "${key_name}")

                if [ -z "$RESULT" ] || [ "$RESULT" = "(nil)" ]; then
                    echo ">> 키가 존재하지 않거나 메모리 정보를 가져올 수 없습니다."
                else
                    echo ">> ${key_name} memory usage: ${RESULT} bytes"
                    echo ">> 약 $(echo "scale=2; ${RESULT}/1024" | bc) KB"
                    echo ">> 약 $(echo "scale=2; ${RESULT}/1024/1024" | bc) MB"
                fi
            else
                log_error "Key 누락"
            fi
            ;;
        q|Q)
            log_info "스크립트를 종료합니다."
            break
            ;;
        *)
            log_error "잘못된 선택입니다."
            ;;
    esac
    
    echo ""
    read -p $'\e[32m계속하려면 엔터를 누르세요...\e[0m' temp
done
