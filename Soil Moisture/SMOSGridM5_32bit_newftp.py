
#ll needed imports
import datetime
import glob
import numpy
import csv
import arcpy
import math
import os
import time
import ftplib
import zipfile
import shutil
import subprocess
import sys
import ast

# Arcpy environment variables.
arcpy.env.workspace = os.getcwd()
arcpy.env.overwriteOutput = True
spRef = arcpy.SpatialReference('WGS 1984')
arcpy.env.outputCoordinateSystem= spRef


#filemaker : INPUT ->str(path),str(wantedpath) 
#Purpose: To make the wanted path from start to finish
# Output: None
def filemaker(path,wantedpath):
	if wantedpath =='':
		return None
	
	if wantedpath.split('\\')[0] in path :
		newpath= path
	else:
		#print "\n"
		newpath= os.path.join(path,wantedpath.split('\\')[0])
		if "\\ " not in newpath:
			newpath = newpath +'\\'
	if not os.path.exists(newpath):
		os.mkdir(newpath)
	return filemaker(newpath,"\\".join(wantedpath.split('\\')[1:]))	
	 
#Establishes the file location and a variable to check if the  input file is valid.
fileloc_in =''
valid = False 

# The start and end date are declared here
# Similarly, the period and FTP access established


'''fDate = raw_input("Please input the first date (yyyymmdd): ")
lDate = raw_input("Please input the last date (yyyymmdd): ")
period = raw_input("Please input the period: ")
strMode = raw_input("Would you like to extract & convert to TXT (yes or no): ")'''
fDate = sys.argv[1]
lDate = sys.argv[2]
period = '1'
dlftp = bool(ast.literal_eval(sys.argv[3]))

# was the processing done already? If the .DBLs have been converted to .txt, setting this to True will skip it, saving a ton of time.
done = False

# The paths to the files are declared. They are all relative to the script_folder
script_folder= os.getcwd()
main_folder = os.path.split(script_folder)[0]
fileloc_out = os.path.join(main_folder,'Outputs','FTPGridding')


# The user is shown the output location for the results.
print fileloc_out

# Using Filemaker, the files to store each year are created.
for year in [fDate[:4],lDate[:4]]:
	filemaker('',os.path.join(fileloc_out,year))

		
#Start and end dates are declared as dates
sDate = datetime.date(int(fDate[0:4]), int(fDate[4:6]), int(fDate[6:])) 
eDate = datetime.date(int(lDate[0:4]), int(lDate[4:6]), int(lDate[6:]))

# If the FTP needs to be accessed:
if not dlftp:
    
	#Get into the FTP and navigate to the appropriate folder.
	
	ftp = ftplib.FTP("smos-diss.eo.esa.int")
	print ftp.login("Catherine.Champagne", "Aafc222!")
	print ftp.getwelcome()
	tempSDate = sDate
	#ftp.cwd("SMOS/L2SM/MIR_SMUDP2/")
	
	# while the date is before the end date: use cwd to navigate to that day's folder on the FTP
	while (tempSDate <= eDate):
		print 'Attempting day: {}'.format(tempSDate)
		try :	
			ftp.cwd("/SMOS/L2SM/MIR_SMUDP2/")
		except EOFError:
			print 'There is an issue, relogging....'
			ftp = ftplib.FTP("smos-diss.eo.esa.int")
			ftp.quit()
			ftp = ftplib.FTP("smos-diss.eo.esa.int")
			print ftp.login("Catherine.Champagne", "Aafc222!")
			print ftp.getwelcome()
			tempSDate = sDate	
			
		
		
		if tempSDate.month < 10:
			tempSDateMonth = "0" + str(tempSDate.month)
		else:
			tempSDateMonth = str(tempSDate.month)
           
		if tempSDate.day < 10:
			tempSDateDay = "0" + str(tempSDate.day)
		else:
			tempSDateDay = str(tempSDate.day)
		
		ftp.cwd(str(tempSDate.year))
		ftp.cwd(str(tempSDateMonth))
		ftp.cwd(str(tempSDateDay))
		fileList = ftp.nlst()
		
		
		
		# Based on the files in the list for that day, the .ZIPs are copied to the created ZIP folder for each day in each year.
		# If the ZIPs have been downloaded, they are ignored and shown that they are done.
		# The ftp is cwd to the top dir and the date is increased by one. 
		
		if not os.path.exists(os.path.join(fileloc_out,str(tempSDate.year),"ZIP")):
				os.mkdir(os.path.join(fileloc_out,str(tempSDate.year),"ZIP"))
				
		#if the TXT directory does not exit, it  is made.
		if not os.path.exists(os.path.join(fileloc_out,str(tempSDate.year),"TXT")):
			os.mkdir(os.path.join(fileloc_out,str(tempSDate.year),"TXT"))
		
		for nextFile in fileList:
				
			if not os.path.exists(os.path.join(fileloc_out,str(tempSDate.year),"ZIP",nextFile)):
				with open(os.path.join(fileloc_out,str(tempSDate.year),"ZIP", nextFile), 'wb') as f:
					ftp.retrbinary("RETR "+ nextFile, f.write)
			
			
				print "{}: processing".format(nextFile)
			else:
				print "{}:already done".format(nextFile)
				
		tempSDate += datetime.timedelta(days=1)
		
	# The FTP is exited when everything is done.
	ftp.quit()
	
	fileSdate=sDate
	
	while (fileSdate<=eDate):	
		
		#print str(fileSdate).replace('-','')
		print 'Processing date :{}'.format(str(fileSdate).replace('-',''))
		

		# For every downloaded zip file, if it is not empty, the.dbl file is extracted into the TXT dir to be changed to txt later. 	
		for zippedFile in glob.glob(os.path.join(fileloc_out,str(fileSdate.year),"ZIP","*_{}*.zip".format(str(fileSdate).replace('-','')))):
			print zippedFile
			try:
				with zipfile.ZipFile(zippedFile, 'r') as curZip:
					for fileName in curZip.namelist():
						if fileName[-4:] == '.DBL':
							curZip.extract(fileName, os.path.join(fileloc_out,str(fileSdate.year),"TXT"))
			except:
				print "There was an issue with the zip file (zipfile is empty) :  {}".format(zippedFile)
		
		# the most time consuming element of the entire script is skipped if it has been done already.
		# If it has not been done yet, it is run on the .dbls inside the directory.
		if not done:
			
			#for dblFile in glob.glob(os.path.join(fileloc_out,str(tempSDate.year),"TXT","*.dbl")):
			for dblFile in glob.glob(os.path.join(fileloc_out,str(fileSdate.year),"TXT","*_{}*.dbl".format(str(fileSdate).replace('-','')))):
				
				#print os.path.exists(dblFile.replace('.DBL','.TXT')),dblFile.replace('.DBL','.TXT')
				
				if not os.path.exists(dblFile.replace('.DBL','.TXT')) :
					subprocess.call([os.path.join(script_folder, "udp2ascii_rwapi.exe"), dblFile])
				else:
					print 'already proccessed:{}'.format(dblFile)
				

		# for every dbl file inside the TXT directory, it is deleted.	
		for dblFile in glob.glob(os.path.join(fileloc_out,str(fileSdate.year), "TXT", "*.dbl")):
			os.remove(dblFile)
		
		# Since the TIFs will be stored, the TIF directory is made as needed in the appropriate year.
		#if not os.path.exists(os.path.join(fileloc_out,str(fileSdate.year), "TIF")):
			#os.mkdir(os.path.join(fileloc_out,str(fileSdate.year), "TIF"))	
			
		fileSdate += datetime.timedelta(days=1)
	
		
	#The filepath that the rasters will be made from is the output path of this section.		
	filepath_in = fileloc_out
	
	
else:
	filepath_in = fileloc_out

#The main part of the script starts.
#The time and location are shown to the user.		
		
print filepath_in
print "Start Time:"
print time.ctime()

# For each date as needed:
while (sDate <= eDate):		
	
	
	
	# The output location is given based on what option was chosen previously(FTP or no)	
	if not dlftp:
		filepath_out = os.path.join(filepath_in,str(sDate.year))
	else:
		filepath_out = os.path.join(fileloc_out,str(sDate.year))
	
	
	if not os.path.exists(os.path.join(filepath_out,'TIF',"GlobAv_SMUDP2_OPER_620_{}_025K_32b_P6.tif".format(str(sDate).replace('-','')))):
	
		# Months are named as needed.	
		if sDate.month < 10:
			sDateMonth = "0" + str(sDate.month)
		else:
			sDateMonth = str(sDate.month)
		
		if sDate.day < 10:
			sDateDay = "0" + str(sDate.day)
		else:
			sDateDay = str(sDate.day)
		
		#The current date is established
		curDate = str(sDate.year) + sDateMonth + sDateDay
		
		
		#The Swathlist is given, and if is is empty,this means that the date does not exist in this run and is skipped.
		swathList = glob.glob(os.path.join(filepath_in,str(sDate.year),'TXT',"SM_*_MIR_SMUDP2_" + curDate + "*.TXT"))
		if swathList ==[]:
			print "No text file found for date :{} ,skipping\n".format(curDate)
			sDate = sDate+datetime.timedelta(1)
			continue
		#Number of swaths is established.
		numSwaths = len(swathList)
		
		# a new array is made of 720x600
		GlobalSMOS = numpy.empty((720, 600, 2))
		
		#The array is populated as [0,0]
		for x in range(720):
			for y in range(600):
				GlobalSMOS[x][y] = [0, 0]
		
		# The user is shown what time the raster input was started.	
		print "raster input Start : {} ".format(time.ctime())
		
		# FOr each processing swath, if they have any of the flags (see user manual) in any row, then the soil mositure is set to be -999 (later translated to NoData)
		for i in range(numSwaths):
			print swathList[i]
			with open(swathList[i], 'rb') as f:
				reader = csv.DictReader(f)
				try :
					for row in reader:
						# If the row is outside of the target area, it is skipped.
						if float(row[' Longitude'])  >= -30:
							continue
						elif (float(row[' Soil_Moisture']) == -999 or int(row[' FL_SNOW_MIX']) == 1 or int(row[' FL_SNOW_WET']) == 1 or int(row[' FL_SNOW_DRY']) == 1 or int(row[' FL_FROST']) == 1 or int(row[' FL_RAIN']) == 1):
							row[' Soil_Moisture'] = -999
						else:
							row[' Soil_Moisture'] = float(row[' Soil_Moisture']) * 100
							#print "new-Soil_Moisture:{}-FL_SNOW_MIX':{}-FL_SNOW_WET:{}-FL_SNOW_DRY:{}-FL_FROST:{}-FL_RAIN:{}\n".format(str(row[' Soil_Moisture']).strip(), row[' FL_SNOW_MIX'],row[' FL_SNOW_WET'] ,row[' FL_SNOW_DRY'],row[' FL_FROST'],row[' FL_RAIN'])
						
						#The lat, long integers and pixels are found.
						latInt = int(str(float(("%.2f" % float(row[' Latitude']))) * 100).split('.')[0])
						lonInt = int(str(float(("%.2f" % float(row[' Longitude'])))  * 100).split('.')[0])
						latPix = int(math.fabs((latInt - 8999)) / 25)
						lonPix = int((lonInt + 17999) / 25)
						
						# if the soil moisture has a value, it is assigned to the array. 
						if float(row[' Soil_Moisture']) != -999:
							GlobalSMOS[latPix][lonPix][1] += float(row[' Soil_Moisture'])
							GlobalSMOS[latPix][lonPix][0] += 1
				
				# In the case that some files would stop processing, they are skipped.
				# NOTE: This should not happen, but during testing, there were some corrupted files, and this is a long process, so one bad file shouldnt stop everything
				# 		Re-running the unpacking may solve it ( this is what I did)
				except:
					print 'This Text file: {} was unable to be processed,please check documentation for potential reasons'.format(swathList[i])
						
		# a new array is made. NoData is established if needed, and the soil mositure is divided by the total amount of non- no Data pixels.			
		GlobalSMOSAvg = numpy.empty((720,600))
		for x in range(720):
			for y in range(600):
				if GlobalSMOS[x][y][0] == 0:
					GlobalSMOSAvg[x][y] = -999
				else:
					GlobalSMOSAvg[x][y] = GlobalSMOS[x][y][1] / GlobalSMOS[x][y][0]
								
		
		# The rasters are shown to have been done
		# The file name and location are specified. 
		# Normally, they are saved as 64 bits, but this was incorrect, so they are changed to 32 bit floats.
		print "raster input Finish : {} ".format(time.ctime())
		fileName = os.path.basename(swathList[i])
		type_date = fileName[12:18] + "_" + fileName[3:7] + "_" + fileName[51:54] + "_" + fileName[19:27]
		outRaster = arcpy.NumPyArrayToRaster(GlobalSMOSAvg, arcpy.Point(-180,-90), 0.25, 0.25, -999)  
		filemaker('',os.path.join(filepath_out, 'TIF'))
		save_file = os.path.join(filepath_out, 'TIF',"GlobAv_{}_025K_P6.tif").format(type_date)
		save_file_out = os.path.join(filepath_out,'TIF' ,"GlobAv_{}_025K_32b_P6.tif").format(type_date)
		print "saving Start : {} ".format(time.ctime())
		outRaster.save(save_file)
		print "saving end - transfering start : {} ".format(time.ctime())
		arcpy.CopyRaster_management(save_file,save_file_out,"","","-999","","","32_BIT_FLOAT")
		print "transfering finish - Start Delete : {} ".format(time.ctime())
		arcpy.Delete_management(save_file)
		print "Delete Finish : {}  ".format(time.ctime())
		
		# This notes that the raster is done processing, and a new one will be started.
		print " \n Start again : {}  \n  ----- \n ".format(time.ctime())
	else:
		
		print '{} is done.'.format(sDate)
	
	# the date is increased by one.
	
	sDate += datetime.timedelta(days=int(period))
	
	
	

#This lets the user know how long raster creation took.	
print "End Time:  "
print time.ctime()
