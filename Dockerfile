FROM python:3

# Install locales (if not installed by default)
RUN apt-get update && apt-get install -y locales && \
    locale-gen pt_BR.UTF-8 && \
    dpkg-reconfigure locales

# Set the locale environment variables
ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR:pt
ENV LC_ALL pt_BR.UTF-8

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
RUN cd /app

CMD ["flask", "--app", "flaskr", "run", "--debug", "--host=0.0.0.0"]