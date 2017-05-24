
####################################Introduction####################################################################
#Project name : Agmonitor
#Programmed by: Martin Holicka
#Date: November 10th,2015
#Project Purpose: To perform regression on Rapid Eye and Crop Inventory data to verify accuracy.

#Project component: Supplementary script to reproject the RapidEye Rasters to Albers Conic Equal Area

####################################Introduction####################################################################

''' Set-Up ( Imports, File creation, Environment settings)*******************************************************'''

#Directories
home = "E:\Agriculture_CIRE\Inputs"

import os,shutil
import sys
from os import path
import arcpy,datetime
from arcpy import env
from arcpy.sa import *

''' Copying Files to Working Directory***************************************************************************'''

# Needed Variables for this Section
fcList = arcpy.ListFeatureClasses()
tiflst =os.listdir(home)

arcpy.env.workspace = home
arcpy.env.overwriteOutput = True


# The list of all the rasters that start with 'RE' 
rasters_tif=filter(lambda x : (x.endswith('.tif') and x.startswith('RE')),arcpy.ListRasters())

print 'Starting Program'

# For each raster in the inputs, if it is not in Albers Conic Equal Area, it the projection is set.This ensures accurate results.
for raster in rasters_tif :
    desc = arcpy.Describe(raster)
    spatialRef = desc.spatialReference
    if spatialRef.name != 'Albers_Conic_Equal_Area':
        arcpy.ProjectRaster_management(raster,raster[0:15]+".tif","PROJCS['Albers_Conic_Equal_Area',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['false_easting',0.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-96.0],PARAMETER['standard_parallel_1',44.75],PARAMETER['standard_parallel_2',55.75],PARAMETER['latitude_of_origin',40.0],UNIT['Meter',1.0]]","NEAREST","5","#","#","PROJCS['WGS_1984_UTM_Zone_14N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['false_easting',500000.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-99.0],PARAMETER['scale_factor',0.9996],PARAMETER['latitude_of_origin',0.0],UNIT['Meter',1.0]]")
        print 'Done Reprojecting:'+ raster
        os.remove(home+'/'+raster)

#ArcGis creates temporary .xml files during reprojection, so they are deleted.
for xml_file in tiflst:
    if xml_file.endswith('xml'):
        os.remove(home+'/'+xml_file)

print 'Finished,Please run Agmonitor.py '
