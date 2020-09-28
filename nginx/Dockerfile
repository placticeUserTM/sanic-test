FROM nginx:latest

RUN apt update && \
    apt install -y iputils-ping net-tools curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./nginx.conf /etc/nginx/nginx.conf
# COPY ./server.conf /etc/nginx/conf.d/server.conf

EXPOSE 80