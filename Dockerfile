FROM python:3.6
RUN ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
ADD . /code
WORKDIR /code
CMD ["python", "app.py"]
