#!/usr/bin/bash
. /etc/sy_script
. ${Sy_Dir}/Sy_Scripts/functions.sh

# 인자 개수 확인
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <src_path> <dst_path>"
    exit 1
fi

SRC_PATH="$1"
DST_PATH="$2"

## 전역변수 ##
SERVERS=(sn1 sn2 sn3 m1 m2 s1)

## SCP 실행 ##
for SERVER in "${SERVERS[@]}";
do
	log_info "Start.. Copying ${SRC_PATH} -> ${SERVER}:${DST_PATH}"
	 scp -r "$SRC_PATH" "${SERVER}:${DST_PATH}"
	log_info "End..   Copying ${SRC_PATH} -> ${SERVER}:${DST_PATH}"
        echo
	echo
done
