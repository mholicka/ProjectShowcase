# -*- coding: utf-8 -*-

'''
Created by Omar Dzinic (Omar.Dzinic@agr.gc.ca)
March 11, 2014
Updated: November 28, 2014

Last modified by: Patrick Rollin on 2015/03/05
'''


'''Imports'''
import arcpy 
import arcpy.mapping as arcm
import os
import sys
from shutil import copyfile
import datetime
import re
import automapper_setup_argv as automapper_setup
import ast 
import collections



#Variables are made. Mapsetup is the dictionary.
#start, end, anom
type =sys.argv[1]
anom = bool(ast.literal_eval(sys.argv[4]))
LT = bool(ast.literal_eval(sys.argv[5]))
mapsetup=automapper_setup.run(type,sys.argv[2],sys.argv[3],anom,LT)


arcpy.env.overwriteOutput=True

'''Directories'''
main_dir = str(automapper_setup.auto_dir)#os.path.dirname(os.path.realpath(__file__))
print main_dir
img_dir_in = os.path.join(main_dir, "Input_Image")                                             # Directory for input image
template_dir = os.path.join(main_dir, "Input_Template")                                     # Directory for input template
vector_dir = os.path.join(main_dir, "Input_Vectors")    
                                    # Directory for shapefiles

img_lst = mapsetup

if not os.path.exists(os.path.join(main_dir, "Output")):                                    # Check to see if output folder exists and creates one if not
    os.makedirs(os.path.join(main_dir, "Output"))
	
out_dir = os.path.join(main_dir, "Output")                                                  # Directory for output mxd and pdf

if not anom:
	automapper_setup.filemaker('',os.path.join(out_dir,str(type),"MXD"))
	out_dir =  os.path.join(out_dir, str(type))  
	
else:
	automapper_setup.filemaker('',os.path.join(out_dir,'Anomalies',str(type),"MXD"))
	out_dir =  os.path.join(out_dir, 'Anomalies', str(type))  
	

mapDir = os.path.join(out_dir, "MXD")

print out_dir

for year in img_lst:
	if not os.path.exists(os.path.join(out_dir,str(year))):
		automapper_setup.filemaker('',os.path.join(out_dir,str(year)))
		
	img_dir =os.path.join(img_dir_in,str(year))
	for img in img_lst[year]:
		
		if type =='monthly' : img = img[0]
		'''Constants'''
		in_img = str(img.split('\\')[-1])
		print "Input image is {0}".format(in_img)

		in_template = os.listdir(template_dir)[0]
		fixedTemplate = os.path.join(out_dir, in_template)
		print "Input template is {0}".format(in_template)

		print "The output directory is {0}".format(out_dir)
		
		copyfile(os.path.join(template_dir, in_template), fixedTemplate)   # Copies template from the template directory to output
		mxd = arcpy.mapping.MapDocument(fixedTemplate)                     # Copied template to be used in script

		listDframe = arcm.ListDataFrames(mxd)                                                   # Loop through all of the data frames
		for frame in listDframe:                                                                # in the template and finds the Climate
			if (frame.name == "Climate Map"):                                                   # Map data frame
				testDframe = frame


		englishMonth = ['January', 'February', 'March', 'April', 'May', 'June', 'July',         # List of months
						'August', 'September', 'October', 'November', 'December']               # in English for date                                                                                                                                         

		frenchMonth = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',         # List of months
					   'août', 'septembre', 'octobre', 'novembre', 'décembre']                   # in French for date

		totalDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]                            # List of total days for every month

		monthlyText = "{0} 1 - {1}, {2} / 1 - {1} {3}, {2}"
		biweeklyText = "Week {0} and {1} ({2} {3} - {4} {5}), {6} / Semaine {0} et {1} ({3} {7} au {5} {8}), {6}"
		weeklyText = "Week {0} ({1} {2} - {1} {3}), {4} / Semaine {0} ({5} {6} au {5} {7}), {4}"
		difweeklyText = "Week {0} ({1} {2} - {8} {3}), {4} / Semaine {0} ({5} {6} au {9} {7}), {4}"

		smmonthlyOut = "SMOS_SM_{0}_Month{1}_NorthAmerica"
		smbiweeklyOut = "SMOS_SM_{0}_BiWeek{1}_National"
		smweeklyOut = "SMOS_SM_{0}_Week{1}_25D_National"
		
		davgmonthlyOut = "SMOS_DiffAvgSM_{0}_{1}_Month"
		davgbiweeklyOut = "SMOS_DiffAvgSM_{0}_{1}_BiWeek"
		davgweeklyOut = "SMOS_DiffAvgSM_{0}_{1}Week"
		
		'''Set data paths'''
		# Procedure fixes the data sources of layers to prevent the layers from "missing" in ArcMap
		# after using template on another computer

		print "Fixing data sources"

		for lyr in arcm.ListLayers(mxd):                                                        # Loops through all layers in the template
			#print lyr.dataSource
			name = str(lyr)                                                                     # Name of current layer in loop
			arcm.RemoveLayer(testDframe, lyr)                                                   # Removes the layer from the data frame
			if ((lyr.dataSource).endswith(".tif")):                                             # Checks to see if layer is a tiff image to prevent compatibility
				#print img_dir,in_img
				lyr.replaceDataSource(img_dir, "RASTER_WORKSPACE", in_img)                      # issues with changing the data source. Then changes the data source
			else:
				lyr.replaceDataSource(vector_dir, "SHAPEFILE_WORKSPACE", name)                  # Changes data source of shapefiles
			arcm.AddLayer(testDframe, lyr, "AUTO_ARRANGE")                                      # Adds the updated layer to the data frame
		
		print 'Fixing Title'
		
		splitFname = in_img.split("_")
		if(splitFname[0] == "GlobAv"):
			if LT: 
				yearNum = int(splitFname[5])
				type_nm = splitFname[6]
				week = int(splitFname[7])
			else:
				yearNum = int(splitFname[4])
				type_nm = splitFname[5]
				week = int(splitFname[6])
		elif(splitFname[0] == "SMDiffAvg"):
			if LT:
				yearNum = int(splitFname[3])                                                            # Extracts the year number from the image name
				type_nm= splitFname[4]
				week = int(splitFname[5])
			else:
				yearNum = int(splitFname[2])                                                            # Extracts the year number from the image name
				type_nm= splitFname[3]
				week = int(splitFname[4])
		
		for txt in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
			if txt.name == "Week Info":
				dateText = txt
		
		
				
		def iso_year_start(iso_year):                                                           # The Gregorian calendar date of the first day of the given ISO year
			fourth_jan = datetime.date(iso_year, 1, 4)
			delta = datetime.timedelta(fourth_jan.isoweekday() - 1)
			return fourth_jan - delta 

		def iso_to_gregorian(iso_year, iso_week, iso_day):                                      # Gregorian calendar date for the given ISO year, week and day
			year_start = iso_year_start(iso_year)
			return year_start + datetime.timedelta(days=iso_day - 1, weeks=iso_week - 1)	

		#The start date of the week is declared. 
		start=iso_to_gregorian(yearNum,week,1)
		
		
		#depending on the type of analysis, the name and end is modified,
		if LT : week = "{}_{}".format(week,'LT')
		if 	type_nm =='Week':
			end = start + datetime.timedelta(days=6)
			if not anom:
				fnameOut= smweeklyOut.format(yearNum,week)
			else:
				fnameOut= davgweeklyOut.format(yearNum,week)
		elif type_nm =='BiWeek':
			end = start + datetime.timedelta(days=13)
			if not anom:
				fnameOut= smbiweeklyOut.format(yearNum,week)
			else:
				fnameOut= davgbiweeklyOut.format(yearNum,week)
		else:
			#they are it the same month, so it doesnt matter
			
			
			if type_nm == 'Month':
				number=4
				if LT: number=5 
			else:
				number=6
				if LT: number=7
			
			start =datetime.date(yearNum,int(splitFname[number]),1)
			end = start
			if not anom:
				
				fnameOut= smmonthlyOut.format(yearNum,week)
			else:
				if not LT:
					fnameOut= davgmonthlyOut.format(yearNum,week)
				else:
					fnameOut= davgmonthlyOut.format(yearNum,week)
		
		
		#titlemaker: INPUT -> DatetimeObject(start, end), Str(type)
		#Purpose: To make the title based on what the dates are. 
		#Output: String
		def titlemaker(start,end,type):
			#the start and end months are declared. 
			mnth_s = int(str(start).split('-')[1]) -1
			mnth_e = int(str(end).split('-')[1]) -1
			
			#The start and end months are declared in the english and french language. 
			start_mnth=[englishMonth[mnth_s]]
			end_mnth= [englishMonth[mnth_e]]
			start_mnth_fr=[frenchMonth[mnth_s]]
			end_mnth_fr= [frenchMonth[mnth_e]]
			
							
			
			#Based on the type, the text is populated. Weekly and Biweekly have the week/biweek and the dates. This has year crossover. 
			if type =='weekly':
				en = "Week {0}, {7} ({1} {2}, {3} - {4} {5}, {6} ) ".format(week,str(start_mnth[0]),start.day,start.year,str(end_mnth[0]),	end.day,end.year,yearNum)
				fr = "Semaine {0}, {7} ({1}, {2} {3} - {4} {5}, {6} ) ".format(week,str(start_mnth_fr[0]),start.day,start.year,str(end_mnth_fr[0]),end.day,end.year,yearNum)

			elif type == 'biweekly':
				en = "BiWeek {0}, {2} ({3} {4}, {5} - {6} {7}, {8})  ".format(week,int(week)+1, yearNum ,str(start_mnth[0]),start.day,start.year,str(end_mnth[0]),end.day,end.year,)
				fr = "Bimensuel {0}, {7} ({1}, {2} {3} au {4} {5}, {6} ) ".format(week,str(start_mnth_fr[0]),start.day,start.year,str(end_mnth_fr[0]),end.day,end.year,yearNum)
				 
			else:
				en= "{0} 1 - {1},{2} ".format(start_mnth[0],totalDays[mnth_s],start.year )
				fr= "1 - {1} {0} ,{2} ".format(start_mnth_fr[0],totalDays[mnth_s],start.year )

			return "{}/ {}".format(en,fr)
		
		if LT : week = week.split('_')[0]
		dateText.text=str(titlemaker(start,end,type))
		
			
		mxd.save()                                                                              # Saves the template copy
		copyfile(fixedTemplate, os.path.join(mapDir, "{0}.mxd".format(fnameOut)))
		print "Exporting PDF to {0} \n".format(os.path.join(out_dir,str(year),fnameOut))
		arcpy.mapping.ExportToPDF(mxd, os.path.join(out_dir,str(year), fnameOut))                        # Exports map to PDF
		del mxd
