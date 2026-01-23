#!/usr/bin/bash

# load env
. /work/job_project/conf/job.conf

start() {
    rm -f "${COLLECTOR_STOP_DIR}/${COLLECTOR_STOP_FILE}"
    exec python3 -u ${COLLECTOR_WORK_DIR}/collector.py
}

stop() {
    touch "${COLLECTOR_STOP_DIR}/${COLLECTOR_STOP_FILE}"
}

case "$1" in
    start) start ;;
    stop) stop ;;
esac
