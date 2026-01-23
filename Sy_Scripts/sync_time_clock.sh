#!/usr/bin/bash
. /etc/sy_script
. ${Sy_Dir}/Sy_Scripts/functions.sh


## 전역변수 ##
SERVERS=(sn1 sn2 sn3 m1 m2 s1)
ALL_SERVERS=(ap sn1 sn2 sn3 m1 m2 s1)

for SERVER in "${SERVERS[@]}";
do
        log_info "[Start] ${SERVER} time and clock rsync ..."

        ssh ${SERVER} "date -s \"$(date '+%Y-%m-%d %H:%M:%S')\" && hwclock -w"

        log_info "[End] ${SERVER} time and clock rsync ..."
        echo ""
done

for SERVER in "${ALL_SERVERS[@]}";
do
    log_info ">>> ${SERVER}:"
    ssh ${SERVER} "date '+%Y-%m-%d %H:%M:%S'"
done
