FROM python:2.7
ENV PYTHONUNBUFFERED 1

RUN mkdir /run/service
WORKDIR /run/service

ADD requirements /run/service/requirements
RUN pip install -r requirements/develop.txt

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
