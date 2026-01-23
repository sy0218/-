#!/usr/bin/bash
. /etc/sy_script
. ${Sy_Dir}/Sy_Scripts/functions.sh
. ${Sy_Dir}/Sy_Scripts/conf/server.properties

# 인자가 없거나 공백이면 종료
if [ -z "$1" ]; then
    echo "${0} 인자가 없습니다. (start | stop | status)"
    exit 1
fi

ZK_OPT="$1"
ZK_bin="${ZOOKEEPER_HOME}/bin"

case "${ZK_OPT}" in
    start|stop)
        for ip in ${zookeeper_ip}
        do
            log_info "[Zookeeper] ${ip} systemctl ${ZK_OPT}"
            ssh ${ip} "systemctl ${ZK_OPT} zookeeper-server"
            echo
        done
        ;;

    status)
        for ip in ${zookeeper_ip}
        do
            log_info "[Zookeeper] ${ip} status"
            ssh ${ip} "${ZK_bin}/zkServer.sh status"
            echo
        done
        ;;

    *)
        echo "지원하지 않는 명령어입니다: ${ZK_OPT}"
        echo "사용법: $0 {start|stop|status}"
        exit 1
        ;;
esac
