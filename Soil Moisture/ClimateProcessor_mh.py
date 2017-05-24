"""Ensure that OSGeo4W is installed and the path in line 34 is adjusted appropriately""" 

import glob
import os
import shutil
import subprocess
import numpy
import arcpy
import ClimateDownloader_MH as CD
import sys
from arcpy.sa import *

#filemaker : INPUT ->str(path),str(wantedpath) 
#Purpose: To make the wanted path from start to finish
# Output: None
def filemaker(path,wantedpath):
	# if the wanted path is empty, function is done
	if wantedpath =='':
		return None
	
	#If parts of the wanted path are in path already, then the new path is made.
	if wantedpath.split('\\')[0] in path :
		newpath= path
	
	#New path is created from the first element in the wanted path. If it is the drive letter, \\ is added.
	else:
	
		newpath= os.path.join(path,wantedpath.split('\\')[0])
		if "\\ " not in newpath:
			newpath = newpath +'\\'
	# if the newpath doesn't exist, it is made
	if not os.path.exists(newpath):
		os.mkdir(newpath)
	# filemaker is re-run on this new path and the rest of the wantedpath
	return filemaker(newpath,"\\".join(wantedpath.split('\\')[1:]))	

arcpy.env.workspace = os.getcwd()
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')

# the variables are set up as needed. 
test =True
type =sys.argv[1] # can be rdps, rdpa, or hrdps based on what is needed.
vars=CD.download(type,True) # This downlaods the files as needed. 
dataTypes = vars

# for each of these days, the output location is made and declared.
for date in os.listdir(os.path.join(os.getcwd(),"{}_Out".format(type))):
	print date
	filemaker(os.path.join(os.getcwd(),"{}_Out".format(type),date),'Output')
	location = os.path.join(os.getcwd(),"{}_Out".format(type),date)
	
	# for each day in the dictonary, the the files are processed.
	for dtype in dataTypes:
		print "Processing:{}".format(dtype)
		curFiles = glob.glob(os.path.join(location, "*{}*.grib2".format(dtype)))
		
		#for each file in each day, the .grib2 file is made into a .tif using GDAL and saved.
		for cF in curFiles:
			#use install path for OSGeo4W
			print "C:\OSGeo4W64\bin\gdal_translate.exe", "-of", "GTiff", cF, cF[:-6] + ".tif"
			if not os.path.exists(os.path.join(location, cF[:-6] + ".tif")):
				subprocess.call([r"C:\OSGeo4W64\bin\gdal_translate.exe", "-of", "GTiff", cF, cF[:-6] + ".tif"]) # <- Change path here to reflect OSGeo4W install 
		
		#the list of all the rasters is made.
		tifList = glob.glob(os.path.join(location, "CMC*{}*.tif".format(dtype)))
		inputs =[]
		
		# If the list of rasters is not emptym the date is taken and the following is calculated:
		'''
		IF this is a temperature reading, we are interested in : max, min and mean, so there are calculated with cell statistics.
		For all the other data types, only the average of the rasters is made and saved.
		'''
		if tifList != []:
			fArr = tifList[0].split("_")
			if not os.path.exists(os.path.join(location,'Output' ,"TempAvg_{}.tif".format(date))) or not os.path.exists(os.path.join(location,'Output',"{0}{1}.tif".format(dtype, date))):
				
				if len(tifList) != 4 and not test:
					DayNotDone= 'All times need to be present! Run this program at the end of the day.There are only: {} files out of 4'.format(len(tifList))
					print DayNotDone
					break
				else:
					
					if "TMP" in dtype:
						max_temp=CellStatistics(tifList,"MAXIMUM",'DATA')
						max_temp.save(os.path.join(location,'Output',"Tempmax_{}.tif".format(date)))
						
						min_temp=CellStatistics(tifList,"MINIMUM",'DATA')
						min_temp.save(os.path.join(location,'Output',"Tempmin_{}.tif".format(date)))
						
						avg_temp =CellStatistics(tifList,"MEAN",'DATA')
						avg_temp.save(os.path.join(location,'Output',"Tempavg_{}.tif".format(date)))
					
					
					
					avg_inputs =CellStatistics(tifList,"MEAN",'DATA')
					avg_inputs.save(os.path.join(location,'Output',"{}_Avg_{}.tif".format(dtype,date)))
					
				
							
			else:
				# If the output already exists, the user is notifed of this and the location.
				print 'Outputs are already processed. Find them in: {}'.format(os.path.join(location,'Output'))
				break



	
