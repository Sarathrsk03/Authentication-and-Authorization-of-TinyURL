FROM python:3.9 

WORKDIR /code 

COPY ./requirements.txt /code/requirements.txt 

COPY ./templates /code/templates

COPY ./app.py /code/app.py 

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["fastapi", "run", "app:app.py", "--port", "7860"]