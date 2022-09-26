FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /app
<<<<<<< HEAD
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
=======
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
>>>>>>> 5fd1498ceb2556063c7c6dee26e6596f70ff871e
