FROM python:3.7
LABEL maintainer 'Chris Collins <collins.christopher@gmail.com>'

COPY job.py /job.py

CMD [ "python", "/job.py" ]
