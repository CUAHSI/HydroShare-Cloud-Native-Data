# AORC V 1.1 Forcing Collection 

## Summary

This directory contains a solution for collecting Analysis of Record for Calibration (AORC) meteorological forcing data for a region of interest defined by a Shapefile. This code use the `Xarray`, `Dask`, and `GeoPandas` libraries to collect and process data and save the results to a local NetCDF file. The source of the AORC v1.1 data is the (NWM Retrospective Forcing)[s3://noaa-nwm-retrospective-3-0-pds] cloud bucket hosted on Amazon Web Services (AWS). 

## Description of Files

- `entry.py`: A python script that performs the AORC data collection, processing, and saving to NetCDF. This script has been designed to function as the entrypoint to a Docker container, however it can also be called directly using it's CLI interface.

```
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    start_date       START_DATE:[%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]  start of the date range for which data will be collected [default: None]    │
│                                                                                  [required]                                                                  │
│ *    end_date         END_DATE:[%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]    end of the date range for which data will be collected [default: None]      │
│                                                                                  [required]                                                                  │
│ *    shapefile        PATH                                                       path to shapefile [default: None] [required]                                │
│      bucket_url       [BUCKET_URL]                                               path to S3 bucket [default: s3://noaa-nwm-retrospective-3-0-pds]            │
│      output_file      [OUTPUT_FILE]                                              local file path to save the collected forcing data [default: forcing.nc]    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --n-workers                        INTEGER  Number of dask workers to use for computation [default: 2]                                                       │
│ --worker-memory                    INTEGER  Maximum amount of memory in GB that will be available to each worker [default: 4]                                │
│ --verbose          --no-verbose             Turn on verbose stdoout [default: no-verbose]                                                                    │
│ --help                                      Show this message and exit.                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

- `Dockerfile`: A recipe for compiling the code into a container. 
- `requirements.txt`: A list of Python installation requirements needed to run the code.
- `build-docker.sh`: A helper script written in `bash` for invoking the Docker build operation.
- `test`: A directory of test scripts and data for validating that the code is working as expected.
