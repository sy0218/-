#!/usr/bin/bash

# load env
. /work/job_project/conf/job.conf

start() {
    rm -f "${CONSUMER_STOP_DIR}/${CONSUMER_STOP_FILE}"
    exec python3 -u ${CONSUMER_WORK_DIR}/consumer.py
}

stop() {
    touch "${CONSUMER_STOP_DIR}/${CONSUMER_STOP_FILE}"
}

case "$1" in
    start) start ;;
    stop) stop ;;
esac
