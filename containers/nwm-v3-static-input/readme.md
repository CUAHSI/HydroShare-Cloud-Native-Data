## Installation

### Install R Libraries from Conda-Forge

```
mamba install r-devtools \
              r-ncdf4 \
              r-sp \
              r-raster \
              r-stringr
              r-plyr \
              r-ggplot2 \
              r-ggmap \
              r-irkernel \
              r-rgdal \
              jupyter  
```

### Install R-WrfHydro from GitHub

` R -e "devtools::install_github('NCAR/rwrfhydro')" `

### Register that R Jupyter Kernel (optional)


`R -e 'IRkernel::installspec()'`




