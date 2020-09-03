FROM python:3.7-buster
RUN groupadd --gid 1004 deploy \
    && useradd --home-dir /home/deploy --create-home --uid 1004 \
        --gid 1004 --shell /bin/sh --skel /dev/null deploy
WORKDIR /home/deploy
COPY ./  ./
RUN chown -R deploy:deploy /home/deploy
USER deploy
RUN pip install --no-cache-dir -r requirements.txt --user
ENV PATH="/home/deploy/.local/bin:${PATH}"
CMD ["python3", "./receiver.py"]
# CMD ["python","app.py"]