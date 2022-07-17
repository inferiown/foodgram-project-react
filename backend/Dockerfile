FROM python:3.7-slim
COPY ./backend/ /app/
WORKDIR /app/foodgram/
RUN python3 -m pip install -r /app/requirements.txt
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]

