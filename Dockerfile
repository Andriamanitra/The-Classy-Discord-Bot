FROM python:3.12-alpine
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY dotenv/ /app/dotenv/
COPY classy_bot/ /app/classy_bot/
COPY data/ /app/data/
CMD ["python3", "-m", "classy_bot"]
