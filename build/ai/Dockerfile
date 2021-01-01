FROM ultralytics/yolov3:latest

COPY ai/ /tmp/

RUN mv -f /tmp/*.sh /usr/local/bin/ \
&& chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /var/bot/ai

CMD ["entrypoint.sh"]
