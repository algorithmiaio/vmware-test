FROM python:2

COPY . /app
WORKDIR /app

RUN pip install --upgrade pyvmomi
RUN pip install --upgrade pipenv

RUN pipenv install --system --deploy

CMD ["python", "main.py"]
