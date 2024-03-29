#!/usr/bin/env Rscript --vanilla

# This script is to cutout a domain off the National Water Model given the x, y vlaues of the bounding box.

# Inputs:
  # myPath : The location in which author wants to save the cutout files 
  # The y_south, y_north, x_west, x_east : bounding x, and y s
  # The name of the files that the user wants to cutout
  # dxy : the multplier between the routing and LSM grid, for example if LSM is at 1 km, and routing is at 250 meter, dxy would be 4

# Output:
  # The cutout files
  # A copy of this script in the directory
  # 2 script for cutting out the Forcing files

# Authors:
  # Arezoo Rafieei Nasab (arezoo@ucar.edu)
  # Aubrey Dugger (adugger@ucar.edu)
  # edited by Anthony Castronova (acastronova@cuahsi.org) & Danielle Tijerina (dtijerina@cuahsi.org) August 2018


library(rwrfhydro)
library(ncdf4)
source("Utils_ReachFiles.R")
library(data.table)

# Test with
#y south: 382582.18746
#y north: 367584.87840
#x west: 1720355.72762
#x east: 1734488.45260

subsetBbox <- function(guid, y_south, y_north, x_west, x_east, domain_path, out_path) {

    # guid: unique identifier used to name the output 
    # Specify the clip bounding coordinates
    # they are the x, y values with respect to the projection specified above.
    # For example, the y_south is the y value of the most southern part of the domain you want to subset have
    # in the lambert conformal conic projection used in the National Water Model (in meters)


    # Specify the path to your new subset domain files
    myPath <- paste0(out_path,"/", guid)
    # Specify the path to the FULL DOMAIN files 
#    domainPath <- "/home/acastronova/www.nco.ncep.noaa.gov/pmb/codes/nwprod/nwm.v1.2.2/parm/domain"
    domainPath <- domain_path
    
    cat("std:output path: ", myPath)
    cat("std:domain path: ", domainPath)

    # Projection for bounding coordinates. This needs to be a PROJ4 string 
    # (e.g., "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs").
    coordProj <- "+proj=lcc +lat_1=30 +lat_2=60 +lat_0=40.0000076293945 +lon_0=-97 +x_0=0 +y_0=0 +a=6370000 +b=6370000 +units=m +no_defs"
    
    
    # Specify the clip bounding coordinates: they are the x, y values with respect to the projection specified above.
    # For example, the y_south is the y value of the most southern part of the domain you want to subset have
    # in the lambert conformal conic projection used in the National Water Model (in meters)
    #
    cat("std:R Inputs")
    cat("std:y south (IN):", y_south, sep=' ')
    cat("std:y north (IN):", y_north, sep=' ')
    cat("std:x west: (IN)", x_west, sep=' ')
    cat("std:x east: (IN)", x_east, sep=' ')
    
    # Multiplier between routing grid and LSM grid
    # (e.g., 1-km LSM and 250-m routing means a value of 4)
    dxy <- 4
    
    # Number of cells to buffer
    cellBuff <- 4
    
    #******  Specify the path to the ORIGINAL (full extent) domain files: *****************
    
    # Path to the Routing domain file
    fullHydFile <- paste0(domainPath, "/Fulldom_hires_netcdf_250m.nc")
    
    # Path to the Geogrid file
    fullGeoFile <- paste0(domainPath, "/geo_em.d01_1km.nc")
    
    # Path to the Wrfinput file
    fullWrfFile <- paste0(domainPath, "/wrfinput_d01_1km.nc")
    
    # Path to the Routelink file
    fullRtlinkFile <- paste0(domainPath, "/RouteLink_NHDPLUS.nc")
    
    # Path to the Spatial Weights file
    fullSpwtFile <- paste0(domainPath, "/spatialweights_250m_all_basins.nc")
    
    # Path to the Ground Water Bucket parameter file
    fullGwbuckFile <- paste0(domainPath, "/GWBUCKPARM_CONUS.nc")
    
    # Path to the Soil Properties parameter file
    fullSoilparmFile <- paste0(domainPath, "/soil_veg_properties_ASM.nc")
    
    # Path to the hydro2D file , set this to NULL if you do not have a hydro 2D file
    fullHydro2dFile <- paste0(domainPath, "/HYDRO_TBL_2D.nc")
    
    # Path to the geo spatial file required for the new outputting option
    # geoSpatialFile <- paste0(domainPath, "/GEOGRID_LDASOUT_Spatial_Metadata.nc")
    geoSpatialFile <- paste0(domainPath, "/WRF_Hydro_NWM_geospatial_data_template_land_GIS.nc")
    
    
    #************************************************************************************************************************************************
    #             No need to modify anything from here 
    #***********************************************************************************************************************************************
    
    # creat the outPath if does not exist.
    dir.create(myPath)
    
    # Specify the NEW (subset extent) domain files:
    
    # Routing domain file
    subHydFile <- paste0(myPath, "/Fulldom_hires.nc")
    
    # Geogrid domain file
    subGeoFile <- paste0(myPath, "/geo_em.d01.nc")
    
    # Wrfinput file
    subWrfFile <- paste0(myPath, "/wrfinput_d01.nc")
    
    # Route link file
    subRtlinkFile <- paste0(myPath, "/Route_Link.nc")
    
    # Spatial weights file
    subSpwtFile <- paste0(myPath, "/spatialweights.nc")
    
    # GW Bucket parameter file
    subGwbuckFile <- paste0(myPath, "/GWBUCKPARM.nc")
    
    # Soil parameter file
    subSoilparmFile <- paste0(myPath, "/soil_properties.nc")
           
    #Hydro 2d file
    subHydro2dFile <- paste0(myPath, "/hydro2dtbl.nc")
    	
    # geo Spatial file
    subGeoSpatialFile <- paste0(myPath, "/GEOGRID_LDASOUT_Spatial_Metadata.nc")
    
    # Coordinate parameter text file
    subCoordParamFile <- paste0(myPath, "/params.txt")
    
    # Forcing clip script file
    subScriptFile <- paste0(myPath, "/script_forcing_subset.txt")
    
    
    ################ PROCESSING #####################
    
    ################ CALCULATE INDICES
    
    
    
    # Setup coordinates df
    coords <- data.frame(id=c(1,2,3,4), lat=c(y_south, y_north, y_north, y_south),
            lon=c(x_west, x_west, x_east, x_east))



    # Create temp geogrid tif
#    cat("\nCreate temp geogrid tif...", sep='')
    tmpfile <- tempfile(fileext=".tif")
    ExportGeogrid(fullGeoFile, "HGT_M", tmpfile)
    geohgt <- raster::raster(tmpfile)
    file.remove(tmpfile)

    # Generate spatial coords
#    cat("\nGenerate spatial coords...")
    sp <- sp::SpatialPoints(data.frame(x=coords[,"lon"], y=coords[,"lat"]))
    raster::crs(sp) <- coordProj
    sp_proj <- sp::spTransform(sp, crs(geohgt))
    geoindex <- as.data.frame(raster::rowColFromCell(geohgt, raster::cellFromXY(geohgt, sp_proj)))
    geoindex$we <- geoindex$col
    
    # Change row count from N->S to S->N
#    cat("\nChange row count from N->S to S->N")
    geoindex$sn <- dim(geohgt)[1] - geoindex$row + 1
    geoindex$id <- coords[,"id"]
    
    # Get subsetting dimensions
#    cat("\nGet subsetting dimensions...")
    geo_w <- min(geoindex[,"we"])
    geo_e <- max(geoindex[,"we"])
    geo_s <- min(geoindex[,"sn"])
    geo_n <- max(geoindex[,"sn"])
    hyd_w <- (geo_w-1)*dxy+1
    hyd_e <- geo_e*dxy
    hyd_s <- (geo_s-1)*dxy+1
    hyd_n <- geo_n*dxy
    hyd_min <- (min(geoindex$row)-1)*dxy+1
    hyd_max <- max(geoindex$row)*dxy
    geo_min <- min(geoindex$row)
    geo_max <- max(geoindex$row)
    
    cat('std:\nR Dimensions')
    cat('std:Geo Xwest', geo_w)
    cat('std:Geo Xeast', geo_e)
    cat('std:Geo Ynorth', geo_n)
    cat('std:Geo Ysouth', geo_s)
    cat('std:\nHyd Xwest', hyd_w)
    cat('std:Hyd Xeast', hyd_e)
    cat('std:Hyd Ynorth', hyd_n)
    cat('std:Hyd Ysouth', hyd_s)
    
    # Get relevant real coords for new bounds
    cat("\nGet relevant real coords for new bounds...")
    geo_min_col <- min(geoindex[,"col"])
    geo_max_col <- max(geoindex[,"col"])
    geo_min_row <- min(geoindex[,"row"])
    geo_max_row <- max(geoindex[,"row"])
    rowcol_new <- data.frame(id=c(1,2,3,4), row=c(geo_max_row, geo_min_row, geo_min_row, geo_max_row),
            col=c(geo_min_col, geo_min_col, geo_max_col, geo_max_col))
    rowcol_new_buff <- data.frame(id=c(1,2,3,4), row=c(geo_max_row+cellBuff, geo_min_row-cellBuff, geo_min_row-cellBuff, geo_max_row+cellBuff),
            col=c(geo_min_col-cellBuff, geo_min_col-cellBuff, geo_max_col+cellBuff, geo_max_col+cellBuff))
    sp_new_proj <- xyFromCell(geohgt, raster::cellFromRowCol(geohgt, rowcol_new$row, rowcol_new$col), spatial=TRUE)
    sp_new_proj_buff <- xyFromCell(geohgt, raster::cellFromRowCol(geohgt, rowcol_new_buff$row, rowcol_new_buff$col), spatial=TRUE)
    sp_new_wrf <- sp::coordinates(sp::spTransform(sp_new_proj, "+proj=longlat +a=6370000 +b=6370000 +no_defs"))
    sp_new_nad83 <- sp::coordinates(sp::spTransform(sp_new_proj, "+proj=longlat +ellps=GRS80 +datum=NAD83 +no_defs"))
    sp_new_buff_wrf <- sp::coordinates(sp::spTransform(sp_new_proj_buff, "+proj=longlat +a=6370000 +b=6370000 +no_defs"))
    sp_new_buff_nad83 <- sp::coordinates(sp::spTransform(sp_new_proj_buff, "+proj=longlat +ellps=GRS80 +datum=NAD83 +no_defs"))
    
    ################# SUBSET DOMAINS
    
    # NCO starts with 0 index for dimensions, so we have to subtract 1
    
    # ROUTING GRID
    cat('\nSubset ROUTING GRID...')
    if (!is.null(fullHydFile)) {
    
       if  (!file.exists(fullHydFile)) stop(paste0("The fullHydFile : ", fullHydFile, " does not exits"))
       cmd <- paste0("ncks -O -d x,", hyd_w-1, ",", hyd_e-1, " -d y,", hyd_min-1, ",", hyd_max-1, " ", fullHydFile, " ", subHydFile)
#       print(cmd)
       system(cmd)
    } else {
#    cat('skipping')
    }
    
    # Geo Spatial File 
    cat('\nSubset Geo Spatial File...')
    if (!is.null(geoSpatialFile)) {
       if (!file.exists(geoSpatialFile)) stop(paste0("The geoSpatialFile :", geoSpatialFile, " does not exits"))
       cmd <- paste0("ncks -O -d x,", geo_w-1, ",", geo_e-1, " -d y,", geo_s-1, ",", geo_n-1, " ", geoSpatialFile, " ", subGeoSpatialFile)
    #   print(cmd)
       system(cmd)
    } else {
#    cat('skipping')
    }
    
    
    # GEO GRID
    
    # Dimension subsetting
    cat('\nSubset Geo Grid...')
    cmd <- paste0("ncks -O -d west_east,", geo_w-1, ",", geo_e-1, " -d south_north,", geo_s-1, ",", geo_n-1, 
    	       " -d west_east_stag,", geo_w-1, ",", geo_e, " -d south_north_stag,",geo_s-1, ",", geo_n, " ",
    		fullGeoFile, " ", subGeoFile)
    system(cmd)
    #print(cmd)
    
    # This part is been added by Kevin s request to provide the corner_lons and corner_lats as the GIS tools need
    # with the WPS standards
    
    # Read the 2D corner coordinates
#    cat('\nRead the 2D corner lat coordinates...')
    corner_lats <- c()
    for (ncVarName in c('XLAT_M', 'XLAT_U', 'XLAT_V', 'XLAT_C')) {
            if (ncVarName %in% names(rwrfhydro::ncdump(subGeoFile, quiet = TRUE)$var)) {
                a = rwrfhydro::ncdump(subGeoFile, variable = ncVarName, quiet = TRUE)
                corners = c(a[1,1], a[1, ncol(a)], a[nrow(a), ncol(a)], a[nrow(a), 1])
                rm(a)
            }else{
                corners = c(0,0,0,0)
    	}
            corner_lats = c(corner_lats, corners)                           # Populate corner_lats lis
    }
    
    cat('\nRead the 2D corner lon coordinates...')
    corner_lons <- c()
    for (ncVarName in c('XLONG_M', 'XLONG_U', 'XLONG_V', 'XLONG_C')) {
            if (ncVarName %in% names(rwrfhydro::ncdump(subGeoFile, quiet = TRUE)$var)) {
                a = rwrfhydro::ncdump(subGeoFile, variable = ncVarName, quiet = TRUE)
                corners = c(a[1,1], a[1, ncol(a)], a[nrow(a), ncol(a)], a[nrow(a), 1])
                rm(a)
            }else{
                corners = c(0,0,0,0)
            }
            corner_lons = c(corner_lons, corners)                           # Populate corner_lats lis
    }
    
    
    # Attribute updates
    cat('\nUpdating attributes...')
    cmd <- paste0("ncatted -h -a WEST-EAST_GRID_DIMENSION,global,o,l,", geo_e-geo_w+2, " ", subGeoFile)
    system(cmd)
    cmd <- paste0("ncatted -h -a SOUTH-NORTH_GRID_DIMENSION,global,o,l,", geo_n-geo_s+2, " ", subGeoFile)
    system(cmd)
    cmd <- paste0("ncatted -h -a WEST-EAST_PATCH_END_UNSTAG,global,o,l,", geo_e-geo_w+1, " ", subGeoFile)
    system(cmd)
    cmd <- paste0("ncatted -h -a SOUTH-NORTH_PATCH_END_UNSTAG,global,o,l,", geo_n-geo_s+1, " ", subGeoFile)
    system(cmd)
    cmd <- paste0("ncatted -h -a WEST-EAST_PATCH_START_STAG,global,d,,, ", subGeoFile)
    system(cmd)
    cmd <- paste0("ncatted -h -a SOUTH-NORTH_PATCH_START_STAG,global,d,,, ", subGeoFile)
    system(cmd)
    cmd <- paste0("ncatted -h -a WEST-EAST_PATCH_END_STAG,global,d,,, ", subGeoFile)
    system(cmd)
    cmd <- paste0("ncatted -h -a SOUTH-NORTH_PATCH_END_STAG,global,d,,, ", subGeoFile)
    system(cmd)
    cmd <- paste0("ncatted -h -a i_parent_end,global,o,l,", geo_e-geo_w+2, " ", subGeoFile)
    system(cmd)
    cmd <- paste0("ncatted -h -a j_parent_end,global,o,l,", geo_n-geo_s+2, " ", subGeoFile)
    system(cmd)
    #cmd <- paste0("ncatted -h -a corner_lons,global,o,f,", sp_new_wrf[1,1], " ", subGeoFile)
    #system(cmd)
    #cmd <- paste0("ncatted -h -a corner_lats,global,o,f,", sp_new_wrf[1,2], " ", subGeoFile)
    #system(cmd)
    
    cmd <- paste0("ncatted -O -a corner_lons,global,o,f,", paste(corner_lons, collapse  = ","), " ", subGeoFile)
    system(cmd)
    cmd <- paste0("ncatted -O -a corner_lats,global,o,f,", paste(corner_lats, collapse  = ","), " ", subGeoFile)
    system(cmd)
    
    
    #HYDRO_TBL_2D GRID
    cat('\nSubset HYDRO_TBL_2D GRID...')
    if (!is.null(fullHydro2dFile)) {
    
       if (!file.exists(fullHydro2dFile)) stop(paste0("The fullHydro2dFile : ", fullHydro2dFile, " does not exits"))
      
       # Dimension subsetting
       #DIMENSION IS CURRENTLY north_south.. may change this after talking with Wei 04/28/2017
       cmd <- paste0("ncks -O -d west_east,", geo_w-1, ",", geo_e-1, " -d south_north,", geo_s-1, ",", geo_n-1, " ", fullHydro2dFile, " ", subHydro2dFile)
    #   print(cmd)
       system(cmd)
    } else {
 #   cat('skipping')
    }
    
    # WRFINPUT GRID
    cat('\nSubset WRFINPUT GRID...')
    if (!is.null(fullWrfFile)) {
    
      if (!file.exists(fullWrfFile)) stop(paste0("The fullWrfFile : ", fullWrfFile, " does not exits"))
    
      cmd <- paste0("ncks -O -d west_east,", geo_w-1, ",", geo_e-1, " -d south_north,", geo_s-1, ",", geo_n-1, " ", fullWrfFile, " ", subWrfFile)
    #  print(cmd)
      system(cmd)
      # Attribute updates
      cmd <- paste0("ncatted -h -a WEST-EAST_GRID_DIMENSION,global,o,l,", geo_e-geo_w+2, " ", subWrfFile)
      system(cmd)
      cmd <- paste0("ncatted -h -a SOUTH-NORTH_GRID_DIMENSION,global,o,l,", geo_n-geo_s+2, " ", subWrfFile)
      system(cmd)
    } else {
#    cat('skipping')
    }
    
    ################# SUBSET PARAMS
    cat('\nSubset Route Link and Spatial Weights...')
#    browser()
    if (!is.null(fullSpwtFile) & !is.null(fullRtlinkFile)) {
    
      if (!file.exists(fullSpwtFile)) stop(paste0("The fullSpwtFile : ", fullSpwtFile, " does not exits"))
      if (!file.exists(fullRtlinkFile)) stop(paste0("The fullRtlinkFile : ", fullRtlinkFile, " does not exits"))
    
       # Identify catchments to keep
       cat('\n-> Identify catchments to keep...')
       fullWts <- ReadWtFile(fullSpwtFile)
       keepIdsPoly <- subset(fullWts[[1]], fullWts[[1]]$i_index >= hyd_w & fullWts[[1]]$i_index <= hyd_e &
           			fullWts[[1]]$j_index >= hyd_s & fullWts[[1]]$j_index <= hyd_n)

    #   keepIdsPoly <- unique(keepIdsPoly$IDmask)  !!! this was commented out since I have added the below check to make sure all the basin falls in the cutout domain
#       cat('done')
    
       # keep only those basins that are fully within the cutout doamin
       cat('\n-> keep basins within the cutout domain...')
       FullBasins <- as.data.table(keepIdsPoly)
       FullBasins <- FullBasins[, .(sumBas = sum(weight)), by = IDmask] # find How much of the basins are in the cutout domain

       keepIdsPoly <- FullBasins[sumBas > .999]$IDmask
       
    # ----->
    
       fullRtlink <- ReadLinkFile(fullRtlinkFile)
       keepIdsLink <- subset(fullRtlink, fullRtlink$lon >= min(sp_new_buff_nad83[,1]) & fullRtlink$lon <= max(sp_new_buff_nad83[,1]) &
       			fullRtlink$lat >= min(sp_new_buff_nad83[,2]) & fullRtlink$lat <= max(sp_new_buff_nad83[,2]))
    #   keepIdsLink <- subset(fullRtlink, fullRtlink$x >= x_west & fullRtlink$x <= x_east &
    #                         fullRtlink$y >= y_south & fullRtlink$y <= y_north)
       keepIdsLink <- unique(keepIdsLink$link)
    
       keepIds <- unique(c(keepIdsPoly, keepIdsLink))
    
       # SPATIAL WEIGHT
       cat('\n-> process spatial weights...')
       subWts <- SubsetWts(fullWts, keepIdsPoly, hyd_w, hyd_e, hyd_s, hyd_n)
       file.copy(fullSpwtFile, subSpwtFile, overwrite = TRUE)
       UpdateWtFile(subSpwtFile, subWts[[1]], subWts[[2]], subDim=TRUE)
    
       # ROUTE LINK
       cat('\n-> process route link...')
       subRtlink <- subset(fullRtlink, fullRtlink$link %in% keepIds)
       subRtlink$to <- ifelse(subRtlink$to %in% unique(subRtlink$link), subRtlink$to, 0)
       # reorder the ascendingIndex if ascendingIndex exists in the variables
       if ("ascendingIndex" %in% names(subRtlink)) subRtlink$ascendingIndex <- (rank(subRtlink$ascendingIndex) - 1)
       file.copy(fullRtlinkFile, subRtlinkFile, overwrite = TRUE)
       UpdateLinkFile(subRtlinkFile, subRtlink, subDim=TRUE)
    
    } else {
#    cat('skipping')
    }
    
    # GWBUCK PARAMETER
    cat('\nSubset GWBUCK parameters...')
    if (!is.null(fullGwbuckFile)) {
    
       if (is.null(fullSpwtFile) | is.null(fullRtlinkFile)) {
          stop("To subset the fullSpwtFile, you need fullSpwtFile and fullRtlinkFile")
       }
       if (!file.exists(fullGwbuckFile)) stop(paste0("the fullGwbuckFile : ", fullGwbuckFile, " does not exits"))
       fullGwbuck <- GetNcdfFile(fullGwbuckFile, quiet=TRUE)
       subGwbuck <- subset(fullGwbuck, fullGwbuck$ComID %in% keepIdsPoly)
       subGwbuck$Basin <- seq(1, nrow(subGwbuck), 1)
       file.copy(fullGwbuckFile, subGwbuckFile, overwrite = TRUE)
       UpdateGwbuckFile(subGwbuckFile, subGwbuck, subDim=TRUE)
    } else {
#    cat('skipping')
    }
    
    # SOIL PARAMETER
    cat('\nSubset Soil parameters...')
    if (!is.null(fullSoilparmFile)) {
    
        if (!file.exists(fullSoilparmFile)) stop(paste0("the fullSoilparmFile : ", fullSoilparmFile, " does not exits"))
        cmd <- paste0("ncks -O -d west_east,", geo_w-1, ",", geo_e-1, " -d south_north,", geo_s-1, ",", geo_n-1, " ", fullSoilparmFile, " ", subSoilparmFile)
        system(cmd)
    } else {
#    cat('skipping')
    }
 
    ################# CREATE SCRIPT FILES
    
    # Save the coordinate parameter file
    cat('\nSave the coordinate parameter file...')
    coordsExport <- data.frame(grid=c("hyd_sn", "hyd_ns", "geo_sn", "geo_ns"),
                                imin=c(hyd_w, hyd_w, geo_w, geo_w),
                                imax=c(hyd_e, hyd_e, geo_e, geo_e),
                                jmin=c(hyd_s, hyd_min, geo_s, geo_min),
                                jmax=c(hyd_n, hyd_max, geo_n, geo_max),
                                index_start=c(1,1,1,1))
    write.table(coordsExport, file=subCoordParamFile, row.names=FALSE, sep="\t")
    
    # Save the forcing subset script file
    cat('\nSave the forcing subset script file...')
    #ncksCmd <- paste0("ncks -d west_east,", geo_w-1, ",", geo_e-1, " -d south_north,", geo_s-1, ",", geo_n-1, " ${OLDFORCPATH}/${i} ${NEWFORCPATH}/${i}")
    ncksCmd <- paste0("ncks -d west_east,", geo_w-1, ",", geo_e-1, " -d south_north,", geo_s-1, ",", geo_n-1, " ${i} ${NEWFORCPATH}/${i##*/}")
    fileConn <- file(subScriptFile)
    writeLines(c("#!/bin/bash",
    		"OLDFORCPATH='PATH_TO_OLD_FORCING_DATA_FOLDER'",
    		"NEWFORCPATH='PATH_TO_NEW_FORCING_DATA_FOLDER'",
    		"for i in `ls $OLDFORCPATH`; do",
    		"echo ${i##*/}",
    		ncksCmd,
    		"done"),
    		fileConn)
    close(fileConn)
        
    # copy this script to the myPath dir, so the user haev from what files this cutout has been generated, and what are the options.
    
    # file.copy(from = paste0(getwd(), "/subset_domain.R"), to = paste0(myPath, "/subset_domain.R"), overwrite = TRUE)

    # copy in README

    file.copy(from = paste0(getwd(), "/README.md"), to = paste0(myPath, "/README.md"), overwrite = TRUE)
    
#    cat('\n---------------')
#    cat('\nSCRIPT COMPLETE')
#    cat('\n---------------\n\n')

    return(myPath)
}


# this is the "main" function that allows this script to be
# called using Rscript with arguments.
if (identical (environment (), globalenv ())) {
    args = commandArgs(trailingOnly=TRUE)
    coords <- as.numeric(args[c(2,3,4,5)])


#    # REMOVE ME!!! This is only for testing.
#    #(guid, y_south, y_north, x_west, x_east) 
#    res = suppressWarnings(subsetBbox( 'asdfdgf',
#                                      469282,
#                                      499010,
#                                      1671021,
#                                      1703533));

    
    if (length(args) == 7) {
        # invoke the subsetting function
        res = suppressWarnings(subsetBbox( args[1], coords[1], coords[2], coords[3], coords[4], args[6], args[7]))
        print(res)
    } else {
        print('Incorrect number of arguments')
    }
    

}
