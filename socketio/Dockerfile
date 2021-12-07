FROM python:3.7-buster
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && apt-get update && \
apt-get install -y vim-tiny less && ln -s /usr/bin/vim.tiny /usr/bin/vim && rm -rf /var/lib/apt/lists/*
RUN groupadd --gid 1004 deploy \
    && useradd --home-dir /home/deploy --create-home --uid 1004 \
        --gid 1004 --shell /bin/sh --skel /dev/null deploy
WORKDIR /home/deploy
COPY .  ./
RUN chown -R deploy:deploy /home/deploy
USER deploy
# RUN chmod +x /home/deploy/gunicorn_starter.sh
RUN pip install --no-cache-dir -r requirements.txt --user
ENV PATH="/home/deploy/.local/bin:${PATH}"
# CMD ["./gunicorn_starter.sh"]
CMD python run.py
