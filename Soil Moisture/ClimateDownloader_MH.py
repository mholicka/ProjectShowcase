import glob 
import urllib
import os
import shutil
import sys

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

# The dictionary is declared with the instructions for each type.
# Key is the type of analysis, and within each key is the website to download from , the specifific types of data and the folderes to download from..
#Example: the website to download rdps data is given, the types of data to download are ['SNOD_SFC_0', 'TSOIL_SFC_0', 'TSOIL_DBLL_100', 'SOILW_DBLY_10', 'TMP_TGL_2', 'ICEC_SFC_0']
#         and the data is to be downloaded from the folders: "00/000", "06/000", "12/000", "18/000"
dict={}
dict['rdps']=['http://dd.weather.gc.ca/model_gem_regional/10km/grib2/',['SNOD_SFC_0', 'TSOIL_SFC_0', 'TSOIL_DBLL_100', 'SOILW_DBLY_10', 'TMP_TGL_2', 'ICEC_SFC_0'],"00/000", "06/000", "12/000", "18/000"]
dict['hrdps']=["http://dd.weatheroffice.gc.ca/model_hrdps/continental/grib2/",['SNOD_SFC_0', 'TSOIL_SFC_0', 'TSOIL_DBLL_100', 'SOILW_DBLY_10', 'TMP_TGL_2', 'ICEC_SFC_0'],"00/000", "06/000", "12/000", "18/000"]
dict['rdpa']=['http://dd.weather.gc.ca/analysis/precip/rdpa/grib2/polar_stereographic/',['APCP-024-0700cutoff'],"24/"]

# If the Out directory for that type exists, it is deleted to prevent issues.
if os.path.exists(os.path.join(os.getcwd(),'{}_Out'.format(type))):
	shutil.rmtree(os.path.join(os.getcwd(),'{}_Out'.format(type)))

	
#download:INPUT ->str(type),bool(redownload)
#purpose: to download the files for analysis , and to set up the climate processor script. 
# Output : List  
def download(type,redownload):
	# If there is no need to re-download the data, the analysis types are just returned. 
	if not redownload: return dict[type][1]
	else:
		# for every time folder in the dict, the file is downloaded and saved. 
		# The data is saved to a temporary file,  line by line, and then the final file is saved in the dictory.
		for time in dict[type][2:]:
			url = dict[type][0]
			print "Processing: {0}{1}".format(url,time)
			urllib.urlretrieve("{0}{1}".format(url,time),os.path.join(os.getcwd(),'temp'))
			with open(os.path.join(os.getcwd(),'temp'),'r') as temp:
				for x in temp.readlines():
					if "a href" in x :
						split_url=x.split(" ")[7]
						link= split_url[split_url.find('">')+2:split_url.find('2<')+1]
						for ftype in dict[type][1] : 
							if link .split('_')[0]=='CMC' and ftype in link:
								print link
								date= link.split("_")[-2][:-2]
								
								filemaker('',os.path.join(os.getcwd(),'{}_Out'.format(type),date))
								urllib.urlretrieve("{0}{1}/{2}".format(url, time, link), os.path.join(os.getcwd(),'{}_Out'.format(type),date,link))
			# temporary file is deleted,as it is no longer needed.
			os.remove(os.path.join(os.getcwd(),'temp'))	
			print 'Done, Please see results in :{}'.format(os.path.join(os.getcwd(),'{}_Out'.format(type)))
		# The end result is the list of analysis types (ex: ['SNOD_SFC_0', 'TSOIL_SFC_0', 'TSOIL_DBLL_100', 'SOILW_DBLY_10', 'TMP_TGL_2', 'ICEC_SFC_0'] for hrdps) 
		return dict[type][1]


					
				
				
					
				
					
					
			
				
		
		
