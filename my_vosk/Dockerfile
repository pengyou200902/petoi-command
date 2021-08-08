FROM balenalib/rpi-raspbian:latest

WORKDIR /root

COPY docker_script.sh /root/

RUN chmod a+x /root/docker_script.sh \
    && bash /root/docker_script.sh
