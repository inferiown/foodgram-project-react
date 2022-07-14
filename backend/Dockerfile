FROM python:3.7-slim
COPY ./ /app/
WORKDIR /app/foodgram/
RUN pip3 install -r /app/requirements.txt
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
