FROM pandas/pandas:pip-minimal

RUN pip install \
    s3fs \
    fsspec \
    xarray \
    zarr \
    dask['distributed'] \
    geopandas \
    rioxarray \
    boto3 \
    netcdf4 \
    typer 

RUN mkdir /input /output 
COPY entry.py /srv/entry.py
WORKDIR /srv
ENTRYPOINT ["python", "entry.py"]
