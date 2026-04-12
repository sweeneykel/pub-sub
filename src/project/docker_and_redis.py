# PowerShell → docker CLI → Docker Engine (started by Docker Desktop)
# PS COMMAND: Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
# PS COMMAND: docker run -d -p 6379:6379 --name redis-server redis
# -d runs in detached mode (background)
# -p 6379:6379 maps ports (left host my machine, right redis in docker container)
# --name redis-server names the continer "redis-server"
# redis:latest is image name in docker
# PS COMMAND: docker ps       list all containers currently running
# PS COMMAND: docker stop redis-server
# PS COMMAND: docker start redis-server