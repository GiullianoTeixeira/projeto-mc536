FROM python:3-alpine
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 5000
RUN cd /app

ENV PYTHONIOENCODING=utf-8
ENV LC_ALL C.UTF-8

CMD ["flask", "--app", "flaskr", "run", "--debug", "--host=0.0.0.0"]