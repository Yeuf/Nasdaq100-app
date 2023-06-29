# nasdaq-app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 8501

ENTRYPOINT ["streamlit", "run"]

CMD ["nasdaq100-app.py"]