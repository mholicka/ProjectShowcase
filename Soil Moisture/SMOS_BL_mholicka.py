
# needed imports
import datetime
import glob
import numpy
import arcpy
import os
import time
import sys
import automapper_setup_argv as weekfinder
import subprocess



# Arcpy env variables and numpy settings.
arcpy.env.overwriteOutput = True
spRef = arcpy.SpatialReference('WGS 1984')
numpy.seterr(all='ignore')
arcpy.env.outputCoordinateSystem = spRef


# Location of all the files is established.
script_folder= os.getcwd()
main_folder = os.path.split(script_folder)[0]
infile= os.path.join(main_folder,'Outputs','GridW_BL')
type =sys.argv[1]
start =sys.argv[2]
end = sys.argv[3]


#getfiles : INPUT ->str(file),str(type) 
#Purpose:to get the files for the different years for each type based on the input
# Output: list of rasters
'''
Example: year = 2015, week = 5 so it will search for week_5 in all years.
'''
def getfiles(file,type):
	x="_".join(file.split('_')[5:7])
	rasters=[]
	for year in os.listdir(os.path.join(infile,type)):
		rasters.append(glob.glob(os.path.join(infile,type,year, "GlobAv_SMUDP2_OPER*{}_*.tif".format(x))))
	rasters = [raster for year in rasters for raster in year ]
	return rasters

#getfiles : INPUT -> path
#Purpose: to take in the raster and transform it into an array 
# Output: numpy array of the raster
def makearray(raster):
	inputRaster = arcpy.Raster(raster)
	lowerLeft = arcpy.Point(inputRaster.extent.XMin,inputRaster.extent.YMin)
	
	#The reason that the value is this way is because of the equation (lastweek_tif * 0.75) + (thisweek_tif * 0.25)
	# This makes the calculation a bit more accurate.
	
	nextImage = arcpy.RasterToNumPyArray(inputRaster, lowerLeft, "", "", 0.00000000000000000000000000000001)
	return nextImage

#getfiles : INPUT -> str(path),str(type),str(year),str(anom_folder),bool(done)
#Purpose: take in the raster path and then if the condition is met, make the LT raster, else just return the array
# Output: None or Numpy array
def makeLT_raster(path,type,year,anom_folder,done):
	week_name = glob.glob(path)[0]
	print 'Using:{}'.format(week_name)
	week_raster = makearray(week_name)
	
	# if the LT is not made and the week is 14 (first week in the growing season) or if the month is April:
	#	it makes the LT raster with the nodata, and then saves.
	if not done and (int(anom_folder.split('_')[-1])==14 or (type == 'monthly' and int(anom_folder.split('_')[-1])==4)):
		if 'SMDiffAvg_LT_' in week_name:
			week_LT_name = week_name
		else:
			week_LT_name=week_name.replace('SMDiffAvg_','SMDiffAvg_LT_')
		week_raster[week_raster==0.00000000000000000000000000000001]=-999
		week_raster = arcpy.NumPyArrayToRaster(week_raster, arcpy.Point(-180,-90), 0.25, 0.25, -999)
		week_raster.save(os.path.join(os.path.join(infile,type,year,'Anomalies',anom_folder,os.path.basename(week_LT_name))))
				
	else:
		#  just return the array.
		return week_raster
		
	
#getlongterm : INPUT -> str(week),str(type)
#Purpose: to make the LT rasters based on the equation for the Long term rasters.
# Output: None	
def getlongterm(week,type):
	print week
	getweek =week.split('\\')[-1].split('_')[4:7]
	str= "_".join(getweek[1:])
	if type != 'biweekly':
		lastweek ="{}_{}".format(getweek[1],int(getweek[2])-1)
	else:	
		lastweek ="{}_{}".format(getweek[1],int(getweek[2])-2)
	
	
	if type != 'monthly':
		condition = int(getweek[-1]) >=14 and int(getweek[-1]) <=47
	else:
		condition = int(getweek[-1]) >=4 and int(getweek[-1]) <=11
	
	'''
	The condition is eiher weeks 14 to 47 or months 4 to 11
	
	If the conditon is met, then it checks if it is week 14 or month 4, the LT raster is made.
	If the week is not the first, the rasters from this and last week (Ex: week 15 is this week and week 14 is last week),
	and then the LT raster is made from the equation: (lastweek_tif * 0.75) + (thisweek_tif * 0.25)
	
	'''
	
	if condition :
		if int(getweek[-1])==4 or int(getweek[-1])==14:
			print 'Generating first Long-Term'
			thisweek_tif = makeLT_raster(os.path.join(infile,type,getweek[0],'Anomalies',str,'SMDiffAvg_*.tif'),type,getweek[0],str,False)
					
		elif os.path.exists(os.path.join(infile,type,getweek[0],'Anomalies',lastweek)):
			thisweek_name = os.path.basename(glob.glob(os.path.join(infile,type,getweek[0],'Anomalies',str,'SMDiffAvg_SMUDP2*.tif'))[0])
			thisweek_tif = makeLT_raster(os.path.join(infile,type,getweek[0],'Anomalies',str,'SMDiffAvg_SMUDP2*.tif'),type,getweek[0],str,True)
			lastweek_tif = makeLT_raster(os.path.join(infile,type,getweek[0],'Anomalies',lastweek,'SMDiffAvg_LT_SMUDP2*.tif'),type,getweek[0],lastweek,True)
			
			print 'Calculating Long-Term Difference using LT from :{}'.format(lastweek)
			
			LtDiffAvg = (lastweek_tif * 0.75) + (thisweek_tif * 0.25)
			LtDiffAvg[LtDiffAvg ==0.00000000000000000000000000000001 ] = -999
			LtDiffAvg = arcpy.NumPyArrayToRaster(LtDiffAvg, arcpy.Point(-180,-90), 0.25, 0.25, -999)
			LtDiffAvg.save(os.path.join(os.path.join(infile,type,getweek[0],'Anomalies',str,os.path.basename(thisweek_name.replace('SMDiffAvg_','SMDiffAvg_LT_')))))		
		# if there is not image for the previous week, the error is returned and the user is notifed of the issue.
		else:
			if type =='weekly': name = 'week'
			elif type =='biweekly': name = 'BiWeek'
			else: name ='Month'
			error = "This {0} is not the first of the growing season (Month 4/ week 14), and the previous {0}'s LTDiff is missing.Please ensure that {0}'s:{1} LT_Diff is present and re-run.".format(name,lastweek)
		
			raise Exception(error)
	else:
		print 'Longterm averages are only calculated for the growing season (week/biweek 14-47)'
	
	




# for each year (if yearly) or each type of analysis, the master list is pulled of the files that will be used.
for year in os.listdir(os.path.join(infile,type)):	
	
	
	# the folder that will contain the baselines is declared.	
	if not os.path.exists(os.path.join(infile,type,'Baseline')):
		os.mkdir(os.path.join(infile,type,'Baseline'))
	baseline_folder = os.path.join(infile,type,'Baseline')
	done =False
	
	if year=='Baseline':
		continue
	
	if int(year) >= int(start[:4]) and  int(year) <= int(end[:4]):
		print 'Processing:' +str(year)
	else:
		continue
	
	
	if os.path.isdir(os.path.join(infile,type,year)):
		
		fileList = glob.glob(os.path.join(infile,type,year,'*.tif'))
	#print fileList
	
	if type == 'weekly': name= 'Week'
	elif type == 'biweekly': name = 'BiWeek'
	elif type == 'monthly' : name ='Month'
	
	if type == 'monthly':
		temp = ['Month_{}'.format(start[4:6]),'Month_{}'.format(end[4:6])]
		cuttoff=13
	else:
		temp = [weekfinder.weekfinder(start,type)[5:],weekfinder.weekfinder(end,type)[5:]]
		if year != 2015: cuttoff = 52
		else : cuttoff =52
	
	list = ["{}_{}".format(name,temp[0].split('_')[-1])]
	
	end_temp = int(temp[1].split('_')[-1])
	week_num = int(temp[0].split('_')[-1])
	
	#print week_num,end_temp
	
		
	while week_num <= end_temp:
		if week_num == cuttoff:
			list.append("{}_{}".format(name,week_num))
			week_num =1
		else:
			list.append("{}_{}".format(name,week_num))
			week_num+=1

	#print list	
	
					
	if str(type) == 'yearly':
		fileList=sorted(fileList,key=lambda x : int(x.split('\\')[-1].split('_')[5]))
	else:
		fileList= filter(lambda x : "_".join(os.path.basename(x).split('\\')[-1].split('_')[5:7]) in list,sorted(fileList,key=lambda x : int(x.split('\\')[-1].split('_')[6])))
	
	
	if fileList != []:
		# A new array is made.
		outArr = numpy.empty((720, 600, 4))
		
		# this new array is populated with the avg, min, max of the pixels and the value of the pixel is taken.
		for x in range(720):
			for y in range(600):
				outArr[x][y] = [0.0,0, 101, -1] #avg, min, max
			
		# for every image in the filelist, certain values are extracted.
		for imageName in fileList:
			
			
			avg_files= getfiles(os.path.basename(imageName),type)
			fileName = os.path.basename(imageName)
			fileparts= fileName.split('_')
			
			
			for raster in avg_files :
				#print raster
				inputRaster = arcpy.Raster(raster)
				lowerLeft = arcpy.Point(inputRaster.extent.XMin,inputRaster.extent.YMin)
				nextImage = arcpy.RasterToNumPyArray(inputRaster, lowerLeft, "", "",  -9999)
				
				# based on the value of each field in the array, the appropriate action is taken :
				# the pixel is not blank: the pixel in the final array adds the value to it, and the avg goes up by 1 to account for this.
				#						  If the outarr[3]  still has no value,it is assigned the value of that pixels.
				#						  If the pixel value is greater than the current pixel value in the final array, it becomes that greater value.
				#						  If the max is still 101, then the max becomes the value of the pixel
				#						  If the pixel value is greater then the current max, the current max becomes that pixel's value.		
				#
				
				for x in range(720):
					for y in range(600):
						if nextImage[x][y] != -9999:
							outArr[x][y][0] += nextImage[x][y] #total of all values in that point.
							outArr[x][y][1] += 1 #total number of no data pixels.
							
							if outArr[x][y][3] == -1:
								outArr[x][y][3] = nextImage[x][y]
								
							elif nextImage[x][y] > outArr[x][y][3]:
								outArr[x][y][3] = nextImage[x][y]
								
							if outArr[x][y][2] == 101:
								outArr[x][y][2] = nextImage[x][y]
							elif nextImage[x][y] < outArr[x][y][2]:
								outArr[x][y][2] = nextImage[x][y]
	
		
		
			#print outArr
		
			#Baseline arrays are established
			BaselineMin = numpy.zeros((720,600), numpy.dtype('float32'))
			BaselineMax = numpy.zeros((720,600), numpy.dtype('float32'))
			BaselineAvg = numpy.zeros((720,600), numpy.dtype('float32'))
			
			
			# the baseline arrays are now made	
			for x in range(720):
				for y in range(600):
					# if the avg of the pixel is still 0, then the baseline has NoData
					if outArr[x][y][1] == 0:
						BaselineAvg[x][y] = -999
						BaselineMin[x][y] = -999
						BaselineMax[x][y] = -999
					else:
					# the avg, min and max of the pixel are assigned to the appropriate baseline array
						BaselineAvg[x][y] = float(outArr[x][y][0]) / float(outArr[x][y][1])
						BaselineMin[x][y] = outArr[x][y][2]
						BaselineMax[x][y] = outArr[x][y][3]                        

			BaselineAvgR = arcpy.NumPyArrayToRaster(BaselineAvg, arcpy.Point(-180,-90), 0.25, 0.25, -999)
			BaselineAvgR.save(os.path.join(baseline_folder,"BaselineAvg_{0}_{2}_{3}_WGS84_P6.tif".format(fileName[7:13],year,str(fileparts[5]),str(fileparts[6]))))
				
			BaselineMaxR = arcpy.NumPyArrayToRaster(BaselineMax, arcpy.Point(-180,-90), 0.25, 0.25, -1)
			BaselineMaxR.save(os.path.join(baseline_folder,"BaselineMax_{0}_{2}_{3}_WGS84_P6.tif".format(fileName[7:13],year,str(fileparts[5]),str(fileparts[6]))))
				
			
			BaselineMinR = arcpy.NumPyArrayToRaster(BaselineMin, arcpy.Point(-180,-90), 0.25, 0.25, 101)
			BaselineMinR.save(os.path.join(baseline_folder,"BaselineMin_{0}_{2}_{3}_WGS84_P6.tif".format(fileName[7:13],year,str(fileparts[5]),str(fileparts[6]))))
			print "Finished Generating baselines for :{}_{} \n".format(str(fileparts[5]),str(fileparts[6]))
			
					
			print os.path.join(infile,type,year,'Anomalies','{}_{}'.format(fileparts[5],fileparts[6]))
			
			# for each file that needs to be processed, the anomalies are made.			
			for anomaly in avg_files:
				fileparts_a=os.path.basename(anomaly).split('_')
				type_a= fileparts_a[5] 
				num_a = fileparts_a[6]
				
				year = anomaly.split('\\')[-2]
				save_file = os.path.join(infile,type,year,'Anomalies','{}_{}'.format(type_a,num_a))
				weekfinder.filemaker('',save_file)				
				
				print 'Saving Anomalies to :{}'.format(save_file)
				print 'using:{}'.format("_".join(fileparts_a))

				label =''
				#Creating the needed arrays
				percentile = numpy.zeros((720,600), numpy.dtype('float32'))
				PctAvg = numpy.zeros((720, 600), numpy.dtype('float32'))
				DiffAvg = numpy.zeros((720, 600), numpy.dtype('float32'))
				LtDiffAvg = numpy.zeros((720, 600), numpy.dtype('float32'))
				
				inputRaster = arcpy.Raster(anomaly)
				lowerLeft = arcpy.Point(inputRaster.extent.XMin,inputRaster.extent.YMin)
				nextImage = arcpy.RasterToNumPyArray(inputRaster, lowerLeft, "", "",  -999)
				
				# the percentile, percent average, and difference form avg are calculated.
				percentile = ((nextImage - BaselineMin) / (BaselineMax - BaselineMin)) * 100
				PctAvg = (nextImage / BaselineAvg) * 100
				DiffAvg = nextImage - BaselineAvg
				
				# for each of the rasters, there is a need to set the nodata values.
				percentile[percentile ==0 ] = -999
				PctAvg[PctAvg == 0] = -999
				DiffAvg[DiffAvg == 0.0] = -999
				DiffAvg[DiffAvg < -100] = -999
				
				#The name of the raster is made and stored for each for each anomalies
				'''
				PercOut: The percentile of the 
				DiffOut: The difference from the multi-year average.
				pctOut:" The percentage difference of the pixel value.
				'''
				label='{}_{}_{}_{}_WGS84_P6.tif'.format(fileparts_a[1],fileparts_a[4],fileparts_a[5],fileparts_a[6])
				
				percOut = arcpy.NumPyArrayToRaster(percentile, arcpy.Point(-180,-90), 0.25, 0.25, -999)
				percOut.save(os.path.join(save_file,"SMPercentile_{}".format(label)))
				
				diffOut = arcpy.NumPyArrayToRaster(DiffAvg, arcpy.Point(-180,-90), 0.25, 0.25, -999)
				diffOut.save(os.path.join(save_file,"SMDiffAvg_{}".format(label)))
				
				pctOut = arcpy.NumPyArrayToRaster(PctAvg, arcpy.Point(-180,-90), 0.25, 0.25, -999)
				pctOut.save(os.path.join(save_file,"SMPctofAvg_{}".format(label)))
				
			getlongterm(imageName,type)	
			print '\n'

				
