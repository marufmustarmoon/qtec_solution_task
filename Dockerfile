
FROM python:3.10-slim


WORKDIR /app


COPY requirements.txt .


RUN pip install -r requirements.txt


COPY . .


EXPOSE 8010


ENV DJANGO_DEBUG=False
ENV DB_NAME=qtec_solution
ENV DB_HOST=dpg-cncfdh6g1b2c739hi7e0-a.singapore-postgres.render.com
ENV DB_USER=qtec_solution
ENV DB_PASSWORD=Ri1PdXYyQ9dfwSAOXylTYz5ATCjVW4tr


CMD python manage.py migrate && gunicorn --config conf/gunicorn.conf.py myblog.wsgi --preload

