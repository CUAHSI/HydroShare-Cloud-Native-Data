FROM r-base:4.1.1

RUN apt update \
 && apt-get remove binutils -y \
 && apt install -y \
 curl \
 libcurl4 \
 libssl-dev \
 libxml2-dev \
 libgdal-dev \
 proj-bin \
 netcdf-bin \
 nco \
 build-essential \ 
 libfontconfig1-dev \
 libharfbuzz-dev \ 
 libfribidi-dev \
 gfortran \
 && rm -rf /var/lib/apt/lists/*

#####################################
# Install R Packages and R-WRFHYDRO #
#####################################
Run R -e "install.packages('remotes')"

Run R -e "install.packages(c('ncdf4', 'raster'))" \
    && curl -fsSL https://api.github.com/repos/NCAR/rwrfhydro/tarball/HEAD -o /tmp/rwrfhydro.tar.gz \
    && R -e "remotes::install_local('/tmp/rwrfhydro.tar.gz', dependencies=T)" \
    && rm -rf /tmp/downloaded_packages 

#####################
# Install Miniconda # 
#####################
# Set an environment variable for conda to store configuration settings
# that can be accessed by all system users.  
ENV CONDA_PATH=/opt/miniconda

# Update the PATH environment variable by adding the bin directory 
# inside the directory specified above. 
ENV PATH=$CONDA_PATH/bin:$CONDA_PATH/condabin:$PATH

# Install conda
RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
 && sh Miniconda3-latest-Linux-x86_64.sh -b -p $CONDA_PATH \
 && rm -f Miniconda3-latest-Linux-x86_64.sh 

# Install python dependencies
RUN conda install -y -c conda-forge \
    gdal \
    pyproj \
    xarray \
    shapely \
    pyshp \
    typer

########################
# Subsetting operation #
########################
# scripts: contains R subsetting scritps from rwrfhydro
# output: empty directory to put subsetting output.
# 	  this should be used to mount and external dir into the container
# domain: empty dir for data that will be subset
# 	  this should be used to mount input data into the container

# Make directories
RUN mkdir /srv/scripts /srv/output /srv/domain

# Add subsetting scripts
COPY subset_domain.R /srv/scripts/subset_domain.R
COPY Utils_ReachFiles.R /srv/scripts/Utils_ReachFiles.R
COPY entry.py /srv/entry.py

# Define the container's default execution command
WORKDIR /srv
ENTRYPOINT ["python", "-u", "entry.py"]
