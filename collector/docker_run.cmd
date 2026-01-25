docker run -d -it \
  --name collector \
  -v /etc/localtime:/etc/localtime:ro \
  -v /etc/timezone:/etc/timezone:ro \
  ubuntu:22.04
