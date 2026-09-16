Fork of Temporary-File-Share-API for uploading short lived small files.

### Set up the server:
https://www.kamatera.com/knowledgebase/how-to-operate-a-linux-server-on-kamatera/

### Install docker:
https://docs.docker.com/engine/install/ubuntu/
docker.sources contents from params:
```bash
Suites: noble
Architectures: amd64
```
### Install the API:
```bash
cd /home
git clone https://github.com/ThomasMountainborn/vermillionsync.git
cp .env.example .env
docker compose -–build -d
```

### Set up HTTPS: 
https://medium.com/@sanjeevsanju929/deploy-fastapi-with-docker-nginx-and-https-on-ubuntu-server-b03f269b4b3d

### Updating:
```bash
docker stop $(docker ps -q)
cd /home/vermillionsync
git pull
docker compose up -d –-build (-d makes it run in the background, -–build makes it build the changes)
```

## License

MIT