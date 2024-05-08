FROM python:slim-bullseye

RUN apt update && apt install -y \
    git \
    vim \ 
    libgdal-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /srv

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

# Install NGEN-CAL and T-ROUTE configurations
RUN git clone --depth 1 https://github.com/NOAA-OWP/ngen-cal.git /srv/ngen-cal
RUN git clone --depth 1 https://github.com/NOAA-OWP/t-route.git /srv/t-route
RUN cd /srv/ngen-cal/python/ngen_conf && pip install .
RUN cd /srv/t-route/src/troute-config && pip install .


RUN mkdir /srv/output
RUN mkdir /srv/input


COPY entry.py /srv/entry.py
COPY config_generators /srv/config_generators

ENTRYPOINT ["python", \
            "entry.py"]

