FROM python:3.7-buster
WORKDIR /home/deploy
COPY ./  ./
RUN pip install --no-cache-dir -r requirements.txt --user
ENV PATH="/home/deploy/.local/bin:${PATH}"
CMD ["python3", "./main.py"]
# CMD ["python","app.py"]
