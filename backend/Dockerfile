FROM python:3.8

WORKDIR /code

COPY backend /code/backend

RUN pip install -r backend/requirements.txt

CMD [ "python", "backend/app.py" ] 