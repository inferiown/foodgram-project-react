FROM python:3.7-slim
WORKDIR /app/foodgram/
COPY ./ /app
RUN pip install -r /app/requirements.txt/
CMD python manage.py runserver 0:8000
