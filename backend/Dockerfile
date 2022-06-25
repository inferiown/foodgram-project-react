FROM python:3.7-slim
COPY ./ /app
RUN pip install -r /app/requirements.txt
WORKDIR /app/foodgram/
CMD python manage.py runserver 0:8000
