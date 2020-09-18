FROM 10.32.42.225:5000/python:3.7-buster
WORKDIR /home/deploy
COPY ./  ./
USER root
RUN pip install --no-cache-dir -r requirements.txt --user --proxy="http://proxy.charite.de:8080/"
ENV PATH="/home/deploy/.local/bin:${PATH}"
CMD ["python3", "./main.py"]
# CMD ["python","app.py"]
