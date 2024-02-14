FROM python:slim-bullseye

RUN apt update && apt install -y \
    git \
    vim \ 
    libgdal-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /srv

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

RUN mkdir /srv/output
#RUN mkdir /srv/output/restart
#RUN mkdir /srv/output/lakeout
#RUN mkdir /srv/output/streamout
RUN mkdir /srv/input


COPY entry.py /srv/entry.py
COPY cfe_realization.py /srv/cfe_realization.py
COPY ngen-routing-template.yaml /srv/ngen-routing-template.yaml

ENTRYPOINT ["python", \
            "entry.py"]

