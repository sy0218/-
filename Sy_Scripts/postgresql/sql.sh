#!/usr/bin/bash
. /etc/sy_script
. ${Sy_Dir}/Sy_Scripts/functions.sh

# 인자 개수 확인
if [ -z "$1" ]; then
    echo "Usage: ${0} <query>"
    exit 1
fi

job_sql_exec "${1}"
