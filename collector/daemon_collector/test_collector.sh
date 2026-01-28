#!/usr/bin/bash

# load env
. /work/job_project/conf/job.conf
exec python3 -u ${COLLECTOR_WORK_DIR}/collector.py
