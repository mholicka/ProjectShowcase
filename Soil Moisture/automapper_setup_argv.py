import os 
import sys
import datetime
import calendar
import shutil
import glob
import subprocess
import collections

#filemaker : INPUT ->str(path),str(wantedpath) 
#Purpose: To make the wanted path from start to finish
# Output: None
def filemaker(path,wantedpath):
	if wantedpath =='':
		return None
	
	if wantedpath.split('\\')[0] in path :
		newpath= path
	else:
		newpath= os.path.join(path,wantedpath.split('\\')[0])
		if ":" in newpath:
			newpath="{}/".format(newpath)
	if not os.path.exists(newpath):
		os.mkdir(newpath)
	return filemaker(newpath,"\\".join(wantedpath.split('\\')[1:]))


#Weekfinder: INPUT -> datetime object (date), str(type)
#Purpose: to find the iso week/ biweek based on the date.
#Output: String(strDate)
def weekfinder(date,type):
	strDate=''
	date= datetime.date(int(date[:4]),int(date[4:6]),int(date[6:]))
	date = date.isocalendar()
	
	if 'bi' in str(type):
		if date[1] % 2 !=0:
			#print date
			date = (date[0],date[1]-1,date[2])
		#print date
		strDate ='{}_BiWeek_{}'.format(date[0],date[1])
	else:
		strDate='{}_Week_{}'.format(date[0],date[1])
	
	return strDate
	
#Weekfinder: INPUT -> datetime object (start,end),Str(type,loc),Bool(anom)
#Purpose: based on the needed dates, the appropriate rasters are loaded for mapping.
#Output: OrderedDict(dict)
def filefinder(start,end,type,loc,anom,LT):
	#The start and end years are found.
	#Dicitonaries and lists are made. 
	years =[start[:4],end[:4]]
	temp =[]
	dict=collections.OrderedDict()
	rasters=[]
	print anom
	
	
	#for year in years:
	#print os.listdir(os.path.join(loc,type,year))

	#if the type is weekly or biweekly, then the iso week is found and the dictionary is populated based on the dates.
	if type =='weekly' or type=='biweekly' :
		
		#If the start and end years are not the same, the procedure changes a bit.  
		if years[0]!=years[1]:
			
			
			for year in range(int(years[0]),int(years[1])+1):
				print year							
				
				#if the current year is not the end year, the year is used all the way until the last day of that year. 
				if int(year) != int(years[1]):
					
					end_local = "".join(str(year)+'12'+str(calendar.monthrange(int(year),12)[1]))
					temp= [weekfinder(start,str(type)),weekfinder(end_local,str(type))]
					
					print os.path.join(loc,type,str(year))
					
					# Making sure the year is empty.
					try :
						input=  filter(lambda x: x.endswith('.tif'),os.listdir(os.path.join(loc,type,str(year))))
					except:
						print 'This year is empty,skipping'
						continue
				
					#if the year is not 2015 and the week is 1, then the end is the last week of that year. 
					if int(temp[1].split('_')[2]) ==1 and int(year)!= 2015:
						temp[1]='{}_{}_52'.format(year,type)
					
					#If the year is 2015, and the analysis ends on week  52 and the year is not he start year, the week is set to 1
					if int(temp[0].split('_')[2]) == 52 and int(year)!= years[0]:
						temp[0]='{}_{}_1'.format(year,type)
						
					
					#The start date is given.	
					start= datetime.date(int(end_local[0:4]),int(end_local[4:6]),int(end_local[6:]))
							
					if int(year) == 2015:
						start += datetime.timedelta(days=7)
					else:
						start += datetime.timedelta(days=1)
									
					start = "".join(str(start).split('-'))
				else:
					# if the processing year is the last one, the master list is made of all files. 
					temp= [weekfinder(start,str(type)),weekfinder(end,str(type))]
					if temp[0].split('_')[0]!=temp[1].split('_')[0] and temp[0].split('_')[2]== '52' or temp[0].split('_')[2]== '53' :
						temp[0]="{}_{}_{}".format(int(temp[0].split('_')[0])+1,temp[0].split('_')[1],1)
					input=  filter(lambda x: x.endswith('.tif'),os.listdir(os.path.join(loc,type,str(year))))
					
					
				#if anomalies are not to be mapped, the dictionary is populated based on the weeks and biweeks that are in analysis
				if not anom:
					rasters=([x for x in input if int(x.split('_')[6]) >= int(temp[0].split('_')[2]) and int(x.split('_')[6]) <= int(temp[1].split('_')[2])])
					rasters=[os.path.join(loc,type,str(year),x) for x in rasters]
					dict[year]=rasters
				
				else:
					# If anomalies are to be mapped, the appropriate anomoly rasters are set up for being mapped. 
					anomdir= os.listdir(os.path.join(loc,type,str(year),'Anomalies'))
					paths=[x for x in anomdir if int(x.split('_')[1])>=int(temp[0].split('_')[2]) and int(x.split('_')[1])<=int(temp[1].split('_')[2])]
					

					paths= [os.path.join(os.path.join(loc,type,str(year),'Anomalies'),file) for file in paths]
					rasters=[]
					for path in paths:
						if not LT:
							files=filter(lambda x: x.endswith('.tif') and 'SMDiffAvg' in x and "LT" not in x, os.listdir(path))
						else:
							files=filter(lambda x: x.endswith('.tif') and 'SMDiffAvg' in x and "LT" in x, os.listdir(path))
						for file in files:
							rasters.append(os.path.join(path,file))
						dict[year]=rasters
							
							
				
		else:
			# if the start and end years are the same, the weeks are found. 
			temp= [weekfinder(start,str(type)),weekfinder(end,str(type))]	
		
			
			#The master list is made up.
			input=  filter(lambda x: x.endswith('.tif'),os.listdir(os.path.join(loc,type,years[0])))
			#print input	
								
			
			# If anomalies are not be mappped, the dicitonary is populated with the normal rasters. 
			if not anom:
				dict[years[0]]=[os.path.join(os.path.join(loc,type,years[0],x)) for x in input if int(x.split('_')[6]) >= int(temp[0].split('_')[2]) and int(x.split('_')[6]) <= (temp[1].split('_')[2])]

			else:
			# This will populate the anomalies based on the date. 
				rasters=[]
				anomdir= os.listdir(os.path.join(loc,type,str(years[0]),'Anomalies'))
				#print temp, anomdir
				paths=[x for x in anomdir if int(x.split('_')[1])>=int(temp[0].split('_')[2]) and int(x.split('_')[1])<=int(temp[1].split('_')[2])]
				#print paths

				paths= [os.path.join(os.path.join(loc,type,str(years[0]),'Anomalies'),file) for file in paths]
				for path in paths:
					if not LT:
						files=filter(lambda x: x.endswith('.tif') and 'SMDiffAvg' in x and "LT" not in x, os.listdir(path))
					else:
						files=filter(lambda x: x.endswith('.tif') and 'SMDiffAvg' in x and "LT" in x, os.listdir(path))
					for file in files:
						rasters.append(os.path.join(path,file))
					dict[years[0]]=rasters
		
		#If the dicitonay is empty, the user is notified. 	
		if dict== {}:
			print 'no rasters found'
		else:
			return dict
	else:
		#if the analysis is not needing to be in iso, it is simply populated based on the year 
		rasters=[]
		for year in range(int(years[0]),int(years[1])+1):
			print (int(start[4:6]),int(end[4:6]))
			if not anom:
				temp =  filter(lambda x: x.endswith('.tif'),os.listdir(os.path.join(loc,type,str(year))))
				for month in range (int(start[4:6]),int(end[4:6])+1):	
					rasters=glob.glob(os.path.join(loc,type,str(year),'GlobAv_*_Month_{}*.tif'.format(month)))
			else:
				for month in os.listdir(os.path.join(loc,type,str(year),'Anomalies')):
					if int(month.split('_')[1]) >= int(start[4:6]) and int(month.split('_')[1]) <= int(end[4:6]):
						if not LT:
							rasters.append(glob.glob(os.path.join(loc,type,str(year),'Anomalies',month,'SMDiffAvg_SMUDP2_*.tif')))
						else:
							rasters.append(glob.glob(os.path.join(loc,type,str(year),'Anomalies',month,'SMDiffAvg_LT*.tif')))
			dict[year] = rasters
			del rasters
		return dict
		
			
				
# all folders are declared and the list is made. 
script_folder= os.getcwd()
main_dir= os.path.split(script_folder)[0]
loc = os.path.join(main_dir,'Outputs','GridW_BL')	
mxd_dir_in=os.path.join(main_dir,'Automapper','MXDs')
mxd_dir=os.path.join(main_dir,'Automapper','Input_Template')
auto_dir = os.path.join(main_dir,'Automapper')	
test=False
files =[]

#Run: INPUT -> Str(type),DatetimeObject(start, end), Bool(anom)
#Purpose: Set everything up for mapping.
#Output: Dicitionary.
def run (type,start,end,anom,LT):
	
	if not test:
		
		#Thsi dictionary is populated based on date.	
		dict2 = filefinder(start,end,type,loc,bool(anom),LT)
		
		
		# based on the analysis type, certain names are declared (these will be used to find the templates.)
		if type == "weekly":

			strMXD_Interval = "Week"
			strMXD_Scale = "National"
			strTIF_Interval = "Week"
			strNetwork_Interval = "weekly"
			
		elif type == "biweekly":
		  
			strMXD_Interval = "2Weeks"
			strMXD_Scale = "National"
			strTIF_Interval = "Bi-week"
			strNetwork_Interval = "biweekly"
			
		elif type == "monthly":
			
			strMXD_Interval = "Month"
			strMXD_Scale = "NorthAmerica"
			strTIF_Interval = "Month"
			strNetwork_Interval = "monthly"


		# transfering the files to needed dirs
		if os.path.exists(os.path.join(auto_dir,'Input_Image')):
			shutil.rmtree(os.path.join(auto_dir,'Input_Image'))
			
		if os.path.exists(os.path.join(auto_dir,'Input_Template')):
			shutil.rmtree(os.path.join(auto_dir,'Input_Template'))
		
		filemaker('',os.path.join(auto_dir,'Input_Template'))
		
		#The inpus_image directory is popualted with all the needed rasters. 
		for year in dict2:
			filemaker('',os.path.join(auto_dir,'Input_Image',str(year)))
			
			
			for raster in dict2[year]:
				if type == 'monthly': raster = raster[0]
				if not os.path.exists(os.path.join(auto_dir,'Input_Image',str(year),raster.split('\\')[-1])):
					shutil.copy(raster,os.path.join(auto_dir,'Input_Image',str(year),raster.split('\\')[-1]))
				
		if  anom:
			#The mxd templates are copied to the appropriate directory
			if not os.path.exists(os.path.join(mxd_dir,'SM_Template_DifAvg_{}_{}.mxd'.format(strMXD_Scale,strMXD_Interval))):
				
				if LT: temp = 'SM_Template_DifAvg_LT_{}_{}.mxd'.format(strMXD_Scale,strMXD_Interval)
				else:  temp = 'SM_Template_DifAvg_{}_{}.mxd'.format(strMXD_Scale,strMXD_Interval)		
				
				print temp	
				
				mxd = glob.glob(os.path.join(mxd_dir_in,temp))[0]
				print mxd
				shutil.copy(mxd,os.path.join(mxd_dir,temp))
		else:
			if not os.path.exists(os.path.join(mxd_dir,'SM_Template_{}_{}.mxd'.format(strMXD_Scale,strMXD_Interval))):
				
				mxd = glob.glob(os.path.join(mxd_dir_in,'SM_Template_{}_{}.mxd'.format(strMXD_Scale,strMXD_Interval)))[0]
				shutil.copy(mxd,os.path.join(mxd_dir,'SM_Template_{}_{}.mxd'.format(strMXD_Scale,strMXD_Interval)))
				
		
		print("Executing: Maps Automator\n")   
		return dict2
		
					
		
		
		
			







