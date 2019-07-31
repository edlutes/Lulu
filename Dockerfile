FROM python:3.6

EXPOSE 5000

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app .

CMD ["python", "-u", "app.py"]
