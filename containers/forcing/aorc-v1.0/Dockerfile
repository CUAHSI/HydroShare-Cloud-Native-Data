FROM python:3.11-slim

WORKDIR /srv

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt
RUN mkdir /srv/output
COPY entry.py /srv/entry.py

ENTRYPOINT ["python", \ 
	    "-u", \
	    "entry.py"]
CMD ["--help"]
