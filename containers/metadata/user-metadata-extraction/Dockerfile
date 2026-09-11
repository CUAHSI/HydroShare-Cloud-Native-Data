
FROM python:3.12.8-bullseye 

# set the working directory to /opt
WORKDIR /opt

# move files into the container
COPY requirements.txt requirements.txt
COPY api api
COPY entry.py entry.py
COPY .env .env

# install python dependencies
RUN pip install -r requirements.txt

# execute the entry.py script
ENTRYPOINT ["python", "entry.py"]


