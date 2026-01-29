#!/usr/bin/bash

# load env
. /work/jsy/job_project/conf/job.conf

start() {
    rm -f "${HD_UPLOAD_STOP_DIR}/${HD_UPLOAD_STOP_FILE}"
    ${HD_UPLOAD_WORK_DIR}/hadoop_upload.sh >> ${HD_UPLOAD_LOG_DIR}/hadoop_upload_$(date +%Y%m%d).log
}

stop() {
    touch "${HD_UPLOAD_STOP_DIR}/${HD_UPLOAD_STOP_FILE}"
}

case "$1" in
    start) start ;;
    stop) stop ;;
esac
