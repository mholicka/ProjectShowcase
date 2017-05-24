#Done by : Martin Holicka
# Date Commented: July 21st, 2016
# Purpose: to generate the list of files that the SMOS_Compare function will use to generate the raster
# Additional notes: reading the user's manual for this process is reccomended, as it may get confusing.


# needed imports 
import os 
from calendar import monthrange
import datetime
import sys
import math
import collections 
import numpy
import glob
import arcpy
import random


# Arc env variables
arcpy.env.workspace = os.getcwd()
arcpy.env.overwriteOutput = True
spRef = arcpy.SpatialReference('WGS 1984')
arcpy.env.outputCoordinateSystem= spRef


# all needed variables for this script.
valid = False
yearly = False
monthly = False
weekly =False
biweekly = False
exit = False

#variables to identify the time period to be run.
year_to_do= ''
month_to_do =''
type_period=''

# this dicitonary is ordered based on the keys in it.
dict=collections.OrderedDict()

# Empty arrays are formed.
imageArray = numpy.empty((720, 600, 2))
GlobalSMOSAvg = numpy.empty((720,600))


# is this a dryrun to see the dictionary?
# This script was working excellently in testing, but I reccomend doing a dry run to see the dictionary and make sure it sees the files.
test=False


#file that holds all the folders of the years for processing 
script_folder= os.getcwd()
main_folder = os.path.split(script_folder)[0]
fileloc_out = os.path.join(main_folder,'Outputs','FTPGridding')

infile= os.path.join(main_folder,'Outputs','FTPGridding')
outfile= os.path.join(main_folder,'Outputs','GridW_BL')


#//////////FUNCTIONS\\\\\\\\\\\\\\\\\\\\\\\\\\\

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


# first_iso : INPUT -> int(year_iso) 
#Purpose: To get the date that january 4th is on.
# Output: int that returns the difference in days between january 4th in the regular calender and jan 4th on the ISO calender
def first_iso (year_iso):
	jan_4 = datetime.date(year_iso,1,4)
	#print jan_4.isoweekday()-1

	diff = datetime.timedelta(jan_4.isoweekday()-1)
	#print diff

	return jan_4- diff

#iso_greg : INPUT ->int(year_iso),int(week_iso),int (day_iso) 
#Purpose: To get the gregorian date from an ISO date
# Output: int that is the gregorian date in the format YYYYMMDD
def iso_greg(year_iso,week_iso,day_iso):
	start = first_iso(int(year_iso))
	return start +datetime.timedelta(days=int(day_iso)-1,weeks=int(week_iso)-1)
	
#Compare : INPUT ->dictionary(dict),str(type) 
#Purpose: To make the appropriate files and run the SMOS_Compare script as needed
# Output: None	
def compare(dict,type):
	
	# The appropriate folder is created in the output and the SMOS_Compare function is ran.
	# Yearly does not got 1 level deeper, so it runs by itself.
		
	if type == 'yearly':
		print type
		for year in dict :
			filemaker('',os.path.join(outfile,str(type),str(year)))
			print year
			SMOS_Compare(dict[year],year,"",'yearly')
					
	else:
		print type
		for year in dict:
			filemaker('',os.path.join(outfile,str(type),str(year)))
			for dates in dict[year]:
				print year, dates
				SMOS_Compare(dict[year][dates],year,dates,str(type))	
	return None

#SMOS_Compare : INPUT ->list(list),str(year, mnth_week, type) 
#Purpose: Based on the list of files for that speci time period, it averages it all out and makes a new raster.
# Output: A raster for each input list.	

def SMOS_Compare(list,year,mnth_week,type):
	imageArray.fill(0)

	for imageName in list:
		
		# For each image in the list of images, specific data is collected (note the variable names)
		version = os.path.basename(imageName).split("_")[3]
		inputRaster = arcpy.Raster(imageName)
		print inputRaster
		lowerLeft = arcpy.Point(inputRaster.extent.XMin,inputRaster.extent.YMin)
		cellSize = inputRaster.meanCellWidth
		nextImage = arcpy.RasterToNumPyArray(inputRaster, lowerLeft, "", "",  -999)	
		
		# for the raster size, each pixel of each input raster is added together	
		for x in range(720):
			for y in range(600):
				if nextImage[x][y] != -999:
					imageArray[x][y][1] += nextImage[x][y]
					imageArray[x][y][0] += 1
		
		#Once the pixels are all added up, they are averaged out based on the amount of pixels in that stack.
		#If the pixel is 0, it is set to -999, which is NoData
		for x in range(720):
			for y in range(600):
				if imageArray[x][y][0] == 0:
					GlobalSMOSAvg[x][y] = -999
				else:
					GlobalSMOSAvg[x][y] = imageArray[x][y][1] / imageArray[x][y][0]
	
	# the final array is printed 
	print '------GlobalSMOSAvg------------'
	print  GlobalSMOSAvg
	print '------GlobalSMOSAvg ------------'
   
	
	# the output raster is created, and it is stored in memory
	outRaster = arcpy.NumPyArrayToRaster(GlobalSMOSAvg, arcpy.Point(-180,-90), 0.25, 0.25, -999)
	
	# The label of the output raster is assigned, so that everything is nice and neat
	# This is based on the time period. 
	label =''
	if type =='yearly':
		label ='Year_'+str(year)
	elif type =='monthly':
		label=str(year)+'_Month_'+str(mnth_week)
	elif type == 'weekly':
		label=str(year)+'_Week_'+str(mnth_week)
	else:
		label = str(year)+'_BiWeek_'+str(mnth_week)    
		
				
	# The user is notfied that the raster is being saved, and then the file is converted from 64 to 32 bit and saved. 64 bit is deleted.		
	print 'Saving :' +  str(os.path.join(outfile,str(type),"GlobAv_SMUDP2_OPER_{}_{}".format(version,label) + "_WGS84_P6.tif"))
	save_file= os.path.join(outfile,str(type),str(year),"GlobAv_SMUDP2_OPER_{}_{}".format(version,label) + "_WGS84_P6.tif")
	convert_file = os.path.join(outfile,str(type),str(year),"GlobAv_SMUDP2_OPER_{}_{}".format(version,label) + "_WGS84_P6_32b.tif")
	outRaster.save(save_file)
	arcpy.CopyRaster_management(save_file,convert_file,"","","-999","","","32_BIT_FLOAT")
	arcpy.Delete_management(save_file)
	
	

def input_handler(start,end,type):
	#year: yyyy or yyyy_yyyy
	#month : yyyy_mm or yyyy_mm_yyyy_mm
	#weekly : yyyy_mm_dd_yyyy_mm_dd

	
	if not end : end =''
	
	if type =='yearly':
		start = start[:4]
		if end:
			end= '_{}'.format(end[:4])
		
	elif type =='monthly':
		start = "{}_{}".format(start[:4],start[4:6])
		if end :
			end= '_{}_{}'.format(end[:4],end[4:6])
	else:
		start = start = "{}_{}_{}".format(start[:4],start[4:6],start[6:])
		if end :
			end= '_{}_{}_{}'.format(end[:4],end[4:6],end[6:])
	
	return "{}".format(str(start)+str(end))
			
	
	
	
#//////////FUNCTIONS\\\\\\\\\\\\\\\\\\\\\\\\\\\



# if the output file does not exist, it is created.
if not os.path.exists(outfile):
	filemaker('',outfile)


#///////FILE SELECTOR\\\\\\\\\\\\\\\\\\\\\\\\\\\\\	
# The way this works:

'''
Yearly : based on the start and end years, the dicitonary is populated. No checking of consecutivness occurs

Monthly : The months in each year are seperated in each year. No checking of consecutivness occurs

Weekly: The weeks in each year are stored. They are ISO weeks, which are explained in user manual. 
		Consecutivness is checked, so that each week starts on a monday , ends on Sunday and has all 7 days. If any day is missing,
		the week is ignored and the user is notified of this.
		
BiWeekly:Based on the weeks, the biweeks are stored in thier respective years. Once again, these are ISO, and the weeks must be perfectly consecutive
		 This means that week x must be fully complete and week x+1 must be the next monday , or exactly 1 day after the end of the last week.If it not,
		 then the biweek is ignored and execution skips to the beginning of the next biweek.	
		 
REPORTING:

for monthly and yearly, there is no reporting of individual dates, and it will only notify if the month or year is missing.
For weekly and biweekly, the user is notified of the missing week(s) and then the fact that biweek is incomplete.
I would have liked to do an individual reporting system, but time was not on my side.
		 
'''


#NOTES : ['E:\\RUN\\batch\\SCRIPTS\\SMOSGridW_mh_relative.py', 'weekly', '20150325', '20150503']
# that is how sys.argv looks at the call : 
# C:\Python27\ArcGISx6410.1\python.exe -u "E:\RUN\batch\SCRIPTS\SMOSGridW_mh_relative.py"  weekly 20150325 20150503
	

# In case the user inputs an invalid command, this will make sure the command is valid.
while valid == False :
	
	#print sys.argv
	
	# The user is asked of the type of analysis that is to be done : yearly, monthly, weekly or bikweekly.
	#user_input = raw_input('Would you like to do the analysis on a yearly,monthly,weekly, or bikweekly basis. :')
	user_input=sys.argv[1].lower()
	
	# The user's input is then striped and then the appropriate analyis is done.
	user_input = user_input.lower().strip()

	
		
	tifs_in_file = [] # a list for all the tifs in a given folder
	# year, month and time that needs to be done. Each one is for a different analysis.
	year_to_do ='' 
	month_to_do =''
	time_to_do =''
	
	# if the user wishes to the  yearly analysis, they are asked for year or a range of years. 
	if user_input == 'yearly':
		while not valid:
			yearly = True
			#year_to_do = raw_input('Which ISO year would you like to perform the analysis on ? (yyyy or yyyy_yyyy) :')
			year_to_do = input_handler(sys.argv[2],sys.argv[3],sys.argv[1])
			type_period = year_to_do
			year_to_do=year_to_do.split('_')
			
			# if the range of years is not valid (such a 2015-2013) or the year is not valid (Ex: 111111), then an error is returned and the user is asked to re-type the input.
			if len(year_to_do[0])>4 :
				if year_to_do[1] :
					if len(year_to_do[1])>4:
						valid = False
				valid= False
				print 'Please input a valid year'
				continue
			# if the input consits of a range, the validity is verified. 	
			elif len(year_to_do) ==2  :
				valid = datetime.date(int(year_to_do[0]),1,1) < datetime.date(int(year_to_do[1]),1,1)
			else:
				valid= True
			
			# for each year in the range, the  dictionary is populated by the name of the tifs in that year, and then the full path is added.
			# the raster must end in .tif and be the same version as specified.	
			for year in range (int(year_to_do[0]),int(year_to_do[-1])+1):
				path= os.listdir(os.path.join(infile,str(year),'TIF'))
				version = path[0][path[0].find('_P'):path[0].find('_P')+3]
				dict[year]= sorted(filter (lambda x : x.endswith('.tif') and "{}".format(version) in x ,path),key =lambda y : y.split('_')[4])
				dict[year]=map(lambda x : os.path.join(infile,str(year),'TIF',x),dict[year])
				
		
	# if the user wishes to do a monthly analysis, they are asked for the range of months.			
	elif user_input =='monthly':
	
		while not valid:	
			monthly= True
			
			#month_to_do = raw_input('Please specify which month(s) in specific years you would like to preform the analysis on:(yyyy_mm or yyyy_mm_yyyy_mm):')
			month_to_do = input_handler(sys.argv[2],sys.argv[3],sys.argv[1])
			type_period= month_to_do
			month_to_do=month_to_do.split('_')
			
			# if there is only a monthly analysis, the dictionary is populated with all the tifs in that month. 
			# Once again, the input must be tifs and they must be the appropriate verision.
			# only those tifs that fall within the range are added to the analysis.
			if len(month_to_do) == 2 :
				valid =True
				dict[month_to_do[0]]={}
				path= os.listdir(os.path.join(infile,str(month_to_do[0]),'TIF'))
				version = path[0][path[0].find('_P'):path[0].find('_P')+3]
				dict[month_to_do[0]][month_to_do[1]] = sorted(filter (lambda x : x.endswith('.tif') and "{}".format(version) in x and x.split('_')[4][4:6]== str(month_to_do[1]),path) ,key =lambda y : y.split('_')[4])
				dict[month_to_do[0]][month_to_do[1]]=map(lambda x : os.path.join(infile,str(month_to_do[0]),'TIF',x),dict[month_to_do[0]][month_to_do[1]])
			
			# if there is a range of the months, then a new dicitonary is made for each month within the year, and it is populated with the tifs in that year + month range.
			elif len(month_to_do) == 4:
				print month_to_do
				valid = datetime.date(int(month_to_do[0]),int(month_to_do[1]),1) <= datetime.date(int(month_to_do[2]),int(month_to_do[3]),1)
							
				if not valid :
					print 'Please input a valid range of months. '
					continue		
				
				# for each year starting from the first to the last, make a new dictionary in that year.
				for year in range (int(month_to_do[0]),int(month_to_do[2])+1):
					dict[year]={}
					path= os.listdir(os.path.join(infile,str(year),'TIF'))
					version = path[0][path[0].find('_P'):(path[0].find('_P')+3)]
					if year == month_to_do[0]:
						month = month_to_do[1]
					else:
						month =1
					
					
					#grab all the rasters in that month and year and put them into the dictionary.
					while month < 13:
						if year == int(month_to_do[2]) and int(month) == int(month_to_do[3])+1:
							print 'done'
							break
						else:
							if sorted(filter(lambda x : x.endswith('.tif') and int(x.split('_')[4][4:6])== int(month),path) ,key =lambda y : y.split('_')[4]) != []:
								dict[year][month] = sorted(filter(lambda x : x.endswith('.tif') and "_P6" in x  and int(x.split('_')[4][4:6])== int(month),path) ,key =lambda y : y.split('_')[4])
								dict[year][month]=map(lambda x : os.path.join(infile,str(year),'TIF',x),dict[year][month])
							month+=1			
	
	
	# if the user wishes to do a weekly or biweekly analysis, they are asked for the input. 
	# Note: There are a number of edge cases and each needs to be addressed, so the code may be repeated as needed.
	elif user_input== 'weekly' or user_input== 'biweekly':
		weekly = True
		# if the user wishes to do a biweekly analysis, the script will accomodate this.
		if user_input== 'biweekly':
			biweekly = True
		
		# the user is asked for the start and end dates.
		while not valid:
			#print sys.argv[2],sys.argv[3],sys.argv[1]
			time_to_do =input_handler(sys.argv[2],sys.argv[3],sys.argv[1])   # random start of the year  
			#time_to_do= raw_input('Please specify the start and end (yyyy_mm_dd (start) or yyyy_mm_dd_yyyy_mm_dd (start and end):')
			type_period= time_to_do
			#test cases for times
			
			#these variables are used for processing the scripts.			
			time_to_do=time_to_do.split('_')
			name_day_start=''
			name_day_end=''
			
			#based on the input, the appropriate start and end dates are looked at. 	
			if len (time_to_do) ==3 :
				valid= True
				name_day_start=datetime.date(int(time_to_do[0]),int(time_to_do[1]),int(time_to_do[2])).isocalendar()
				name_day_end = datetime.date(int(time_to_do[0]),int(time_to_do[1]),monthrange(int(time_to_do[1]),int(time_to_do[1]))[1]).isocalendar()	
				
			# if the user specifies both a start and end date, this is reflected.	
			elif len(time_to_do)== 6:
				valid = datetime.date(int(time_to_do[0]),int(time_to_do[1]),int(time_to_do[2])) < datetime.date(int(time_to_do[3]),int(time_to_do[4]),int(time_to_do[-1]))
				if not valid :
					print 'The dates selected are not valid. please ensure the second date is after the first.'
					continue	
				name_day_start= datetime.date(int(time_to_do[0]),int(time_to_do[1]),int(time_to_do[2])).isocalendar()
				name_day_end = datetime.date( int(time_to_do[3]),int(time_to_do[4]),int(time_to_do[-1])).isocalendar()
				
				
			else:
				print 'Please input a valid entry'
				valid= False
			
	
		
		name_day_start =(name_day_start[0],name_day_start[1],1) # sets this to the monday of the week 	
		name_day_end = (name_day_end[0],name_day_end[1],7) # goes all the way to the last sunday.
				
		date_start = str(iso_greg(*name_day_start)).replace("-","")#iso equivalent of start 
		date_end = str(iso_greg(*name_day_end)).replace("-","")# iso equivalent of end

		
	
		#if there is no range in the analysis, the tifs in the week are added to the master list.
		if len(time_to_do) ==3 :
			tifs_in_file = filter(lambda x : x. endswith('tif') and "_P6" in x,os.listdir(os.listdir(os.path.join(infile,str(year),'TIF'))))
			
		
		# if there is a range of dates, then all relavant files from all years are added to the master list, and the list is then flattened. 
		else:
			start_yr=date_start[0:4]
			end_yr = date_end[0:4]
			for year in range (int(start_yr),int(end_yr)+1):
				try :
					tifs_in_file.append(filter(lambda x : x. endswith('tif') and "_P6" in x ,os.listdir(os.path.join(infile,str(year),'TIF'))))
					dict[year]=collections.OrderedDict()
				except:
					print "no files for this year:{}, skipping".format(year,)
				
			tifs_in_file = [add_year for first_year in tifs_in_file for add_year in first_year ]
			
		
			


# if the user wishes to do a weekly/bikweekly analysis.	
bad =[] # sometimes, there is no possibility to create a biweek because there is no data for one or both of the weeks.This list will contain those weeks.
if weekly or biweekly:
	valid =False
	#the user is asked for the start and end date.
	
	
	# based off the master list, only those tifs that are within the dates are used.
	tifs = sorted(filter(lambda x : x.split('_')[4]>= date_start and x.split('_')[4] <= date_end,tifs_in_file),key=lambda y : y.split('_')[4])
	
	if tifs ==[]:
		 raise Exception('There are no valid tifs for the dates: {} to {}, please ensure the tifs are present and re-run. '.format(date_start,date_end))
	
	weeks=[] #list containing the weeks
	firstweek =True # Is this the first week of processing?
	next ='' # this will store the the next day
	done= '' # this is the current day
	good = False #a boolean to see if this week is valid
	hasmonday=False # a flag to see if the week has a monday
	weeknum = name_day_start[1] # this is the ISO week number for the first processing week.
	
	
	#For each each raster in the list of applicable rasters.
	for raster in tifs:
		
		# the year, month and day is given	
		year =int(raster.split('_')[4][:4])
		month= int(raster.split('_')[4][4:6])
		day=  int(raster.split('_')[4][6:])
		
		# the start of the month in ISO is established, as well as the current date and the number in the week		
		name_day_start= datetime.date(year,month,1).isocalendar()
		current =datetime.date(year,month,day).isocalendar() 
						
		# If this is the first processing week, the the day is incremented by 1,the week is good, the week list is made, and ther first week flag is set to false.
		if firstweek : 
			next = (datetime.date(year,month,day)+datetime.timedelta(days=1)).isocalendar()
			firstweek=False
			good = True
			weeks=[]
		# If the current date is the next expected date, then this is good and the the next day is established.
		elif current == next:
			 
			good = True
			next = (datetime.date(year,month,day)+datetime.timedelta(days=1)).isocalendar()
		
		# if the date is not the expected date, the script checks if this week has already been reported as missing
		# it checks if it is the week 52, because the current date is in the next year, so the user is notified that the week is incomplete
		# if the week is not 52, then it simply changes processing to the next week and lets the user know the week is incomplete
		else:
			good = False
			if current[1]!= done:
				if current[1]==52:
					print 'Week: {} in year {} is incomplete'.format(current[1],year-1)
					next = (year,1,1)
				else:
					print 'Week: {} in year {} is incomplete'.format(current[1],year) 
					next = (year,current[1]+1,1)
			# the week is reported as noted so that it is skipped when the next raster is checked. 
			# week array is reset
			done=current[1]
			weeks=[]
			
		# if the date is the expected one, then processing goes on 	
		if good:	
			#if the weeknumber is not the most current one, it is switched to be the most current one.
			
			if  weeknum != current[1]:
				weeknum =current[1]
			
			# if the length of the list is 6 and the day of the week is 7, then the week list is added to the dictionary under the year and the week.	
			
			if len(weeks)==6 and current[1]==weeknum:
				# the path to the raster is added to the week list.
				weeks.append(os.path.join(infile,str(year),'TIF',str(raster)))
				
				#2015 has 53 weeks in ISO, and so the "week" of 2016 is actually still in 2015 (See user manual for explanation of ISO week)
				if year == 2016 and weeknum==53:
					dict[2015][weeknum]= weeks
				# the week done and the list is added to the dictionary.
				else:		
					dict[year][weeknum]= weeks
				#Since the week is done, we proceed to the next week. reset everything and proceed.
				hasmonday=False
				weeks =[]
				
			# This checks to see if the week has a monday, and if it does, the week is good. After this, all the other days are appended.	
			elif current[1]==weeknum :
				# If the day is a monday, the path is added, and hasmonday is set to False
				if current[2]== 1:
					hasmonday= True
					weeks.append(os.path.join(infile,str(year),'TIF',str(raster)))
				elif hasmonday:
					weeks.append(os.path.join(infile,str(year),'TIF',str(raster)))
			
				
			
		
	# This ensures that even if a year is empty because the start date is not present, the script will run fine by removing the entry
	badyear=[]
	for year in dict :
		if dict[year]=={}:
			badyear.append(year)
	
	[dict.pop(year,None) for year in badyear]	

	
	#Biweekly utilizes the output of the weekly, and as long as the last of week x + 1= first of week x+1 (sunday to monday), the 2 are put together to a biweek.
	# Biweek code has some repetitions because of different edge cases, mostly related to different years belonging to the same week / 2015 having 53 weeks.
	
	if biweekly:
		#for every year in the dictionary , we are looking at the biweek.
		for year in dict:
			#print year
			bad = [] # weeks will get deleted, so this is a convinent way to store it.
			keys = dict[year].keys()
			week = keys[0]  # This gets all the week numbers in the dictionary in that year.
			#Biweeks are only even numbers so, so if the week is an odd number, it must already belong to a different biweek, so we remove it.
			if week %2 !=0: 
				if len(keys[1:]) >=2:
					bad.append(week)
					week= keys[1]
				else:
					error = 'Cannot proceed because the starting week {},in {} will not create a biweek and there are no biweeks in this list. Please ensure there is valid biweek present.'.format(week,year)
					print error
					dict.pop(year,None)
					continue
			#while the week is less than the number of weeks in the year and there is a weekly list for it:
			while week < max(keys)+1: 
				
				# If the next week does not exist in the weeks, the biweek is deleted ,and the next biweek starts.		
				if week+1 not in keys or week not in keys:
					if week ==52 or week ==53:
						pass
					else:
						bad.append(week)
						bad.append(week+1)
						week +=2
					
				# if the week is 52, this is a special case, because it means that the years are combined, so this happens, and it is named week 52 of the previous year.
				if week ==52:
					if year == 2015:
						try :
							# a new list is made, this new list is given week, and then week +1 is added to it, at which point the week +1 is set for deletion within the dict.
							temp =[]
							temp=dict[year][52]
							temp.extend(dict[year][53])
							dict[year][52]=temp
							bad.append(53)
							del temp
							break
						except:
							print 'Week 52/53 of 2015 is missing'
					else:
						# this gets the dates of the sunday and monday.
						date_special= dict[year][week][-1].split('\\')[-1].split('_')[4]
						sec_date_special= dict[year+1][dict[year+1].keys()[0]][0].split('_')[4]
						
						# if the weeks are perfectly consecutive, the current week + next week are added to the list, which is then flattened into one list. The second week is added for deletion, as it is not needed.						
						if datetime.date(int(date_special[0:4]),int(date_special[4:6]),int(date_special[6:])).toordinal() + 1 == datetime.date(int(sec_date_special[0:4]),int(sec_date_special[4:6]),int(sec_date_special[6:])).toordinal():							
							temp =[]
							temp=dict[year][52]
							temp.extend(dict[year+1][dict[year+1].keys()[0]])
							dict[year][52]=temp
							bad.append(week+1)
							del temp
							break
						else:
							bad.append(week)
							break
						
												
				#If the week exists,is in keys and has the second part of the biweek
				elif week in keys and dict[year][week+1] and week+1 in keys :
					date = dict[year][week][-1].split('\\')[-1].split('_')[4]
					print date
					sec_date = dict[year][week+1][0].split('\\')[-1].split('_')[4]
					# if the biweeks are consecutive, they are combined, flattened and input into the dictionary.
					if datetime.date(int(date[0:4]),int(date[4:6]),int(date[6:])).toordinal() + 1 == datetime.date(int(sec_date[0:4]),int(sec_date[4:6]),int(sec_date[6:])).toordinal():
						temp =[]
						temp=dict[year][week]
						temp.extend(dict[year][week+1])
						dict[year][week]=temp
						bad.append(week+1)
						del temp
						week +=2
						
					# if they are not consecutive, they the next biweek starts.	
					else:
						if dict[year][week+2]:
							week +=2
		
			# The dictionary is purged of all weeks that are bad ( in each specific year)
			for week in bad :
				dict[year].pop(week,None) 
		
		# for all the years, the bad weeks are removed so that there is no useless weeks.	
		years =dict.keys()
		if year+1 in years:
			dict[year+1].pop(1,None)	

# if this is just a dry run, then the dicitonary is ouput and execution stops			
if test:
	#print dict	
	for x in dict:
		for y in dict[x]:
			print x, y
			print dict[x][y]
	sys.exit(1)

#///////FILE SELECTOR\\\\\\\\\\\\\\\\\\\\\\\\\\\\\		

		
# This is the function that will take in the dictionary and run more functions to be able to make the raster.		
if dict != {}:
	compare(dict,user_input)
else:
	e = 'Cannot continue because there are no valid rasters to process'
	raise Exception(e)
				
			
				
	
		
		
		
		
		
		
		
		
		
		
		
		
		
		
			
			
		




		
		
		
			
			
		
							
					
				
					
				
			
	
			
		



