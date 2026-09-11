FROM cuahsi/wrfhydro-subset:v2

######################################################################
# Dependencies are inherited from cuahsi/wrfhydro-subset:v2 because  #
# the deprecation of rgdal in the latest version of R makes the      #
# build process fail. After trying several versions of the r-base    #
# image and several ways to install dependencies, it was decided     #
# that this was the best way to update the logic in entry.py         #
######################################################################

########################
# Subsetting operation #
########################
# scripts: contains R subsetting scritps from rwrfhydro
# output: empty directory to put subsetting output.
# 	  this should be used to mount and external dir into the container
# domain: empty dir for data that will be subset
# 	  this should be used to mount input data into the container

# Add subsetting scripts
COPY scripts /srv/scripts
COPY entry.py /srv/entry.py

# Define the container's default execution command
WORKDIR /srv
ENTRYPOINT ["python", "-u", "entry.py"]
