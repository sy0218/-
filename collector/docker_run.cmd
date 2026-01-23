docker run -d -it \
  --name collector \
  -v /work/job_project:/work/job_project \
  -v /etc/localtime:/etc/localtime:ro \
  -v /etc/timezone:/etc/timezone:ro \
  ubuntu:22.04
