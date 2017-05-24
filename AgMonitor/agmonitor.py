####################################Introduction####################################################################
#Project name : Agmonitor
#Programmed by: Martin Holicka
#Date: November 10th,2015
#Project Purpose: To perform regression on Rapid Eye and Crop Inventory data to verify accuracy.

#Project component: Main processing script.

####################################Introduction####################################################################

####################################Getting Started#################################################################

# The following pre-processing is required to run this script:

# 1- Input training rasters (RapidEye crop type rasters)should not have "NoData"
# 2- Change r_script path to location of the r script. Default :[(Drive):/Agriculture_CIRE/SCRIPTS/regression_analyis.R] .  
# 3- Change the path to where R is installed  
# 4- Change path in the R script to where libraries area installed                  
#   e.g.:
#   x<-.libPaths(c("C:/Users/holickam/Documents/R/win-library/3.2", .libPaths()))   
# 5- Rename all the accurate crop type rasters from RapidEye classification as      
#    RE_YEAR_RapidEyeTileNumber, e.g.: RE_2014_1461818                              
# 6- Ensure that all rasters are in Albers Equal Area (If they are not,please run reproject.py)

# The following files are required
'''
(Drive):/Agriculture_CIRE/Inputs
(Drive):/Agriculture_CIRE/SCRIPTS
-> (Drive):/Agriculture_CIRE/SCRIPTS/agmonitor_commented.py
-> (Drive):/Agriculture_CIRE/SCRIPTS/regression_analyis.R
-> (Drive):/Agriculture_CIRE/SCRIPTS/reproject.py

'''

#Script-generated folders/GDB/files and thier importance
'''
working_db [GDB] - provides a GDB which stores the working files
output_db [GDB]- provides a GDB to store the final result tables
raster_storage[FOLDER]- provides a folder to store files for verification after the completion of the script.
scratch_folder[FOLDER]- This will hold the temporary files created by ArcMap during processing. It is cleaned up at the end.
csvoutput [FILE-CSV]- This is the .csv that R will read from during the analyis.
logfile[FILE-TXT] - Stores the messages of the script run
outlier_removal [FILE-TXT] - Stores the townships that were deleted during outlier removal

'''

# Environment settings
'''
In order to make the calcultations more accurate, the environment settings are set to the following:
- Cellsize of 5, which the same as the RapidEye Raster
- The snapRaster setting is set to the raster of the Crop Inventory (Prevents pixel sliding)
- The output cooridnate system is set to be the same as the RE rasters.
- The extent of the processing is the same as the Crop Inventory raster

This code is also found on line 366

arcpy.env.cellSize=5
arcpy.env.snapRaster=os.path.join(working,CI_Raster) 
arcpy.env.outputCoordinateSystem =os.path.join(working_db,inRasters[0])
arcpy.env.extent = os.path.join(working,CI_Raster)


There is another change in the environment settings to change everything to the mosaic raster's settings.
Once again, this is to ensure accuracy during processing.

Line 461 is the beginning of the environment setting code.

'''

# Conventions used in these comments 
'''
CI= Crop Inventory Data
RE= RapidEye data
GDB= Geodatabase
verifaction folder : see raster_storage[FOLDER] above

training data= all RE rasters
non-training = all data not within the RE rasters

Value_153 will be used as examples. This is canola, and is default target crop

'''

#ADDITIONAL NOTES: The procedure of the R script is written inside the R script and will not be looked at in this file.


####################################Getting Started#################################################################


##################################SET-UP-START############################################################################
# What it does : 1. Sets up the directories that will contain the data, working files, and result.
#                2. The user sets the target crop
# Possible Errors: If there are any errors, the directories need to be changed to match the real location.
#                   DEFAULT: By default: the drive this script should be run from is E. If it is not E, please change it.

#**********************DIRECTORIES**************************
# Where the inputs will be located
home = "E:\Agriculture_CIRE\Inputs"
# A temporary file that will be created to store intermittent tables/rasters
working = "E:\Agriculture_CIRE\working_AgricultureCI_RE"
# Where the output will be stored
output = "E:\Agriculture_CIRE\Done_AgMap"

#Change only if necessary
working_db='E:\Agriculture_CIRE\working_AgricultureCI_RE\working.gdb'
output_db='E:\Agriculture_CIRE\Done_AgMap\CropAreaResults.gdb'
raster_storage='E:\Agriculture_CIRE\Done_AgMap\model_rasters'
shpfile_db='E:\Agriculture_CIRE\Inputs\PreparedINPUTFiles.gdb'
csvoutput=r"E:\Agriculture_CIRE\working_AgricultureCI_RE\rastertable.csv"
scratch_folder = "E:\Agriculture_CIRE\scratchworkspace"
script_file="E:\Agriculture_CIRE\SCRIPTS"
r_script =r"E:\Agriculture_CIRE\SCRIPTS\regression_analyis.R"

#Change to match Rscrtipt.exe path
r_path=r"C:\Program Files\R\R-3.2.2\bin\Rscript.exe"
#r_path = r"C:\Program Files\R\R-3.2.1\bin\Rscript.exe"
#**********************DIRECTORIES**************************


###############################USER INPUT#########################################################

#######################Please input the Crop for Regression:######################################
##################################################################################################
# For new crops not listed here just add it to the end of these lines (e.g. potatoes = '177')

canola='153'
oats='136'
wheat='140'
soybeans ='158'
corn = '147'
cereals = '132'

##################################################################################################
# For run this script for other crops change the following line to the target crop (e.g. for wheat type crop = wheat, for corn it must be crop = corn...)

crop = canola
#######################The names of the script-generated output may be changed####################
################################NOT RECCOMENDED###################################################


#Global Variable:
# The field name of the field which will contain the predicted area.
final_field_name='Levelled_CI_'+str(crop)
common_raster_field = 'RE'
#The name of the Crop Inventory raster
CI_Raster="STB-EOS_2014_CI_MB_30m.tif"
#The name of geodatabase where the Township polygon is stored.
GDB="PreparedINPUTFiles.gdb"



###############################USER INPUT#########################################################

# Imports : These are all the imports that the script will use. Please do not change them.
import os,shutil
import sys
from os import path
import arcpy,datetime
from arcpy import env
from arcpy.sa import *
import csv
from subprocess import call
from subprocess import Popen, PIPE


######################Creation and Declaration of Files and Variables########################

#Create the Output directory
if not os.path.exists(output):
    os.makedirs(output)

#create a directory to hold raster tabulation results (cleans up result file)
if not os.path.exists(raster_storage):
    os.makedirs(raster_storage)

#Create the temp scratch directory
if not os.path.exists(scratch_folder):
    os.makedirs(scratch_folder)

#Create the Working directory
if not os.path.exists(working):
    os.makedirs(working)

# Set environment settings
arcpy.env.scratchWorkspace = scratch_folder
arcpy.env.workspace =shpfile_db

# This will make sure that SA is available,so no errors are returned due to licensing
checkout=False
print'Waiting for Spatial Analyst Licence'
while checkout!=True:
    if arcpy.CheckExtension('Spatial')== 'Available':
        checkout=True
    else:
        checkout=False
arcpy.CheckOutExtension('Spatial')
print 'Got Spatial Analyst'
arcpy.env.overwriteOutput = True


#Setting Up log file.
logfile=open((output+"/00000logfile_CropMapping.txt"),"w")
printer= "Start: "+str(datetime.datetime.now().time())[:-7]
print printer
logfile.write("home = "+home)
logfile.write("\n"+"working = "+working)
logfile.write("\n"+"output = "+output)
logfile.write("\n"+printer)

# A file is opened for writing. Will be explained in the outlier removal section.
outlier_file =open((output+"/Rapideye_with_0_removed.txt"),'w')


# A working geodatabase is created to hold all the working data
if not os.path.exists(working_db):
    arcpy.CreateFileGDB_management(working,'working.gdb')

########################################Function#####################################
# Name: Cleanup
# Purpose: To clean-up the working, script, and scratch folders of any temporary files.
# Inputs: None
# Output : String displaying completion of cleanup.

def cleanup():
    #the list of all the files where temp data could be stored in/
    filelist=[working,script_file,scratch_folder]

    # For each file, go through it, and unless the file ends in .py,.csv, or .R, then remove it.
    
    for folder in filelist :               
        for f in os.listdir(folder):
            file_path = os.path.join(folder,f)
            
            if os.path.isdir(file_path):
                try:
                    
                    shutil.rmtree(file_path,ignore_errors=True)

                except:
                    pass
            else:
                if f.endswith('.csv') or f.endswith('.py') or f.endswith('.R') :
                    pass
                else:
                    try:
                        
                        os.remove(file_path)
                    except:
                        pass
    
    return 'Cleanup completed'
        
   
########################################Function#####################################


##################################SET-UP-END#########################################################################


##################################MAIN-START#########################################################################

''' Copying Files to Working Directory***************************************************************************'''
'''This section will take all the necessary files from the inputs, and transfer them to a working space for further processing'''


# Needed Variables for this Section
fcList = arcpy.ListFeatureClasses()

#Logging Start of copy files.
printer= "Starting to copy input files to working directory: "  +str(datetime.datetime.now().time())[:-7] # print progress update
print printer
logfile.write("\n"+printer)
logfile.flush()


# Copying over Shape files from the list in the Home directory to the working gdb
for shpfile in fcList:

    arcpy.CopyFeatures_management(shpfile_db+'/'+shpfile, working_db+'/'+shpfile)


# This section will copy the needed input rasters (RE to the working GDB
arcpy.env.workspace=home

rasters=arcpy.ListRasters()

for raster in rasters:
    if raster !=CI_Raster:
        arcpy.CopyRaster_management(home+'\\'+raster,working_db+'\\'+raster[:-4])
    else:
        arcpy.CopyRaster_management(home+'\\'+raster,working+'\\'+raster)
      
     


#Logging completion of file copy
printer= "Done Copying needed shape files: "  +str(datetime.datetime.now().time())[:-7] # print progress update
print printer
logfile.write("\n"+printer)
logfile.flush()

''' Creation of File Database + Setting workspace********************************************************************'''
'''This section will create the GDB in which the final results will be stored '''

#Create a new file database to store final tables
if not os.path.exists(output_db):
        arcpy.CreateFileGDB_management(output,'CropAreaResults.gdb')
else:
        pass


''' Extracting of CI raster from RE image extent-Pre-processing****************************************************'''
# What it does : 1. A mosaic of the RE rasters is formed, and then the CI data is extracted from underneath the mosaic
#           
# Possible Errors: NoRasters
#                  Reason: There are no valid rasters among the inputs.
#                  Fix: Ensure that the rasters are valid according to the 'getting started' section.            
#                   


#Logging start of modelling
printer= "Starting ArcGis Modelling: "+str(datetime.datetime.now().time())[:-7] # print progress update
print printer
logfile.write("\n"+printer)
logfile.flush()

arcpy.env.workspace=working_db

# Needed Variables for this Section
rasters_tif=arcpy.ListRasters()


#Creates an error class that will display the errors and in which Township they occur.
class NoRasters(Exception):
    def __str__(self):
        return repr('There are no valid rasters present. Please input valid rasters')

#If there are no errors, then the program can continue, otherwise, the program halts at the error
#Error: No RE rasters provided
if rasters_tif==[]:
    cleanup()
    raise NoRasters
     
else:
    pass

inRasters=[]# the name of the rasters is stored here
mosaic_lst=[]#the name of the rasters + extension is stored here
looped_rasters=[]

#gathering names of the rasters without.tif
inRasters=arcpy.ListRasters()

printer= "Creating Mosaic: "+str(datetime.datetime.now().time())[:-7] # print progress update
print printer
logfile.write("\n"+printer)
logfile.flush()

#In order to make the calcultations more accurate, the environment settings are set to the following:
# Cellsize (5x5) - same as RE raster
#The processing is snapped to the CI raster
# The ooutput coordinate system is set to be the same as the RE raster
# The processing extent is set to be the same as the CI raster.
arcpy.env.cellSize=5
arcpy.env.snapRaster=os.path.join(working,CI_Raster)
arcpy.env.outputCoordinateSystem =os.path.join(working_db,inRasters[0])
arcpy.env.extent = os.path.join(working,CI_Raster)



#Takes in all the RE rasters, and mosaics them into a singular raster
arcpy.MosaicToNewRaster_management(inRasters,working_db,"Mosaic_RE","PROJCS['Albers_Conic_Equal_Area',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['false_easting',0.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-96.0],PARAMETER['standard_parallel_1',44.75],PARAMETER['standard_parallel_2',55.75],PARAMETER['latitude_of_origin',40.0],UNIT['Meter',1.0]]","8_BIT_UNSIGNED","#","1","LAST","FIRST")

printer= "Stored mosaic can be viewed at:"+str(raster_storage+'\\Mosaic_RE.tif')
print printer
logfile.write("\n"+printer)
logfile.flush()

# For verification purposes, a copy of the mosaic is stored in the verification folder.
arcpy.CopyRaster_management(working_db+'\\Mosaic_RE',raster_storage+'\\Mosaic_RE.tif')

printer= "Extracting and tabulating mosaic: "+str(datetime.datetime.now().time())[:-7] # print progress update
print printer
logfile.write("\n"+printer)
logfile.flush()


 #Extract the CI data exactly underneath the RE images 
arcpy.gp.ExtractByMask_sa(working+'/'+CI_Raster,"Mosaic_RE",working_db+'/'+'extracted_CI_mosaic')
#Tabulate Area between the townships and the extracted CI raster (This creates Xi for the regression).

# An area tabulation is preformed using the extracted CI data, and the townships
'''
Specifics

For each unique TWP_ID in the township file, the total area of the target crop will be calculated at 30m resolution.
'''


arcpy.gp.TabulateArea_sa("MB_Townships_PilotSiteAEA", "TWP_ID", 'extracted_CI_mosaic', "Value","extracted_CI_Tabulate", "30")
# Store the extracted CI Tabulate
arcpy.TableToTable_conversion("extracted_CI_Tabulate",raster_storage,"extracted_CI_Tabulate_CI")

    


#Tabulate Area between the townships and the whole CI raster (This is the table that the regression is applied to for all townships including
#the ones without RE (outside the training areas)).
arcpy.gp.TabulateArea_sa("MB_Townships_PilotSiteAEA", "TWP_ID",working+'/'+CI_Raster, "Value","Original_CI_PredTable_Working", "30")
#Store a table for prediction
arcpy.TableToTable_conversion("Original_CI_PredTable_Working",working,"CI_prediction_working")

#This cleans up the final prediction table to show only relevant fields
#Relevant fields: Township ID, RowID(required field), and the target crop.

fields=[f.name for f in arcpy.ListFields("Original_CI_PredTable_Working")]
for field in fields:
    
                if field =="TWP_ID" or field=="Rowid" or field=='VALUE_'+str(crop):
                        pass
                else:
                    try:
                        arcpy.DeleteField_management("Original_CI_PredTable_Working",field)
                    except:
                        pass
                    
clean_final=arcpy.UpdateCursor("Original_CI_PredTable_Working")

# Clean up the final table
# If the target crop is not present in the township, it is deleted
for row in clean_final:
    if row.getValue('VALUE_'+str(crop))==0:
        clean_final.deleteRow(row)
del clean_final,row

# Adding Levelled_CI_(crop number)
# Reason: this will contain the final predicted area of the target crop.
# Type: FLOAT 
arcpy.AddField_management("Original_CI_PredTable_Working",'Levelled_CI_'+str(crop),"FLOAT")



''' Tabulating the area of crop from the Rapideye rasters***************************************************'''
# What it does : 1. This part will tabulate the area of the target crop from the RE data
#                2. The extracted CI and RE data tables are joined together.   
#           
# Possible Errors: There are none programmed into the script. If errors appear, please make sure input files are formatted according to 'getting started'


# Due to a known glitch with tabulate area in ArcGIS, this is a required tool.
arcpy.BuildRasterAttributeTable_management("Mosaic_RE", "Overwrite")

#To ensure accurate results, the Cellsize, raster snapping, coordinate system and extent are set to be the same as the mosaic RE
arcpy.env.cellSize=5
arcpy.env.snapRaster="Mosaic_RE"
arcpy.env.outputCoordinateSystem ="Mosaic_RE"
arcpy.env.extent = "Mosaic_RE"


#Tabulate Area between the townships and the RE raster
arcpy.gp.TabulateArea_sa("MB_Townships_PilotSiteAEA","TWP_ID","Mosaic_RE", "Value", 'Tabulate_all', "5")
     
# Store the RE Tabulate
arcpy.TableToTable_conversion('Tabulate_all',raster_storage,"TL_Mosaic")


 #Join the tables[based on township ID, both extracted CI data and RE data are put together into a single table]
arcpy.JoinField_management('Tabulate_all', "TWP_ID","extracted_CI_Tabulate", "TWP_ID", "TWP_ID;VALUE_110;VALUE_120;VALUE_122;VALUE_130;VALUE_131;VALUE_133;VALUE_135;VALUE_136;VALUE_137;VALUE_138;VALUE_139;VALUE_145;VALUE_146;VALUE_147;VALUE_153;VALUE_154;VALUE_155;VALUE_157;VALUE_158;VALUE_162;VALUE_167;VALUE_174;VALUE_177;VALUE_195;VALUE_196;VALUE_197")
# Store the Joined Table
arcpy.TableToTable_conversion('Tabulate_all',raster_storage,"TL_J_all")

#Logging the completion of the model
printer= "Completed model at :"+str(datetime.datetime.now().time())[:-7] # print progress update
print printer
logfile.write("\n"+printer)


''' Pre-processing of the tables***************************************************'''
# What it does : 1. Cleans up the tabulated table to increase readability and efficiency in later processing
#                2. Sets the fields to be equal everywhere to further increase readbility and efficiency
#                3. Should a township not have a reading in either CI or RE, it is removed, as it is an outlier.
#           
# Possible Errors: There are none programmed into the script. If errors appear, please make sure input files are formatted according to 'getting started'
                   
#Logging the start of the clean-up step
printer= "Setting up tables : "+str(datetime.datetime.now().time())[:-7] # print progress update
print printer

logfile.write("\n"+printer)
logfile.flush()

##########################Must always go crop_RE, then Crop_CI for accurate results#################################
names=['y_RE_'+str(crop),'x_CI_'+str(crop)]
names_final='Original_CI_'+str(crop)
####################################################################################################################

crops=[]

printer= "Started cleanup at:"+str(datetime.datetime.now().time())[:-7] # print progress update
print printer
logfile.write("\n"+printer)
logfile.flush()

# In the tabulated table, if the field is not a required field by Arc(rowID), a target crop field, or the township ID, it is deleted
# If both RE and CI data contains the target crop, then the following naming structure is used by ArcGIS:
'''
Naming: RE- Value_153    CI- VALUE_153_154
'''

fields_mosaic=[f.name for f in arcpy.ListFields('Tabulate_all')]
for field_mosaic in fields_mosaic:
    
    if field_mosaic=="TWP_ID" or field_mosaic=="Rowid":
        pass
    else:
        # 153 is for canola. For other crops change 153 to the class number of the target crop (e.g. soybeans= 158)
        if 'VALUE_'+str(crop) not in field_mosaic:
            try:
                arcpy.DeleteField_management('Tabulate_all',field_mosaic)
            except:
                pass
        else:
            #Because of ArcGIS default naming, the target crop fields are added to a list for renaming.
            crops.append(field_mosaic)



# Into the tabulated table, a new field containing the Township ID is created to create equality
# The original field is deleted.
       
arcpy.AddField_management('Tabulate_all','TWP_ID_S',"TEXT")
arcpy.CalculateField_management('Tabulate_all','TWP_ID_S', "!"+'TWP_ID'+"!","PYTHON")
arcpy.DeleteField_management('Tabulate_all','TWP_ID')
        


# This will change the names of the target crop fields to be easily readable. This comes from the names list
# names=['y_RE_'+str(crop),'x_CI_'+str(crop)]
'''
BEFORE:  RE- Value_153    CI- VALUE_153_154
AFTER:   RE-y_RE_153      CI= x_CI_153
'''               
for field in range(2):
    
    if field == 1:
        naming=names[1]
    else:
        naming=names[0]
    
    arcpy.AddField_management('Tabulate_all',str(names[field]),"DOUBLE")
    arcpy.CalculateField_management('Tabulate_all',naming, "!" + str(crops[field]) + "!","PYTHON")
    arcpy.DeleteField_management('Tabulate_all',crops[field])

    
#Stores the table to the verification folder.
arcpy.TableToTable_conversion('Tabulate_all',raster_storage,"CI_RE_Mosaic")



#Logging the removal of rows not containing the crop.
printer= "Removing rows that do not contain the crops- file location: "+output+"/Rapideye_with_0_removed.txt "
print printer
logfile.write("\n"+printer)
logfile.flush()

#Cleaning up Outliers
clean_outs=arcpy.UpdateCursor('Tabulate_all')

# Clean up the final table
# Should the value of either CI or RE for the target crop in a given township be 0, it is deleted, and it is documented in the removal text file
for row in clean_outs:
    if row.getValue(str(names[0]))==0 or row.getValue(str(names[1]))==0  :
        
        printer= "Removing : " + str(row.getValue('TWP_ID_S')) +' because either CI or RE values  are 0, therefore, it is an outlier.'
        #print printer
        outlier_file.write("\n"+printer)
        outlier_file.flush()
        clean_outs.deleteRow(row)

del clean_outs,row

printer= "Completed clean-up " +" at:"+str(datetime.datetime.now().time())[:-7] # print progress update
print printer
logfile.write("\n"+printer)
logfile.flush()

#The final tabulated table is stored in the output GDB 
arcpy.TableToTable_conversion('Tabulate_all',output_db,'AllRasters_CI_RE')
'''---------------------------------CSV Creation-----------------------------------------------------'''
# In order for R to read the table, a .csv is created containing the final tabulation table

#Needed variables for this section
table='Tabulate_all'
csv_fields=arcpy.ListFields(table)#list fields in the tables
csv_fields_names=[field_csv.name for field_csv in csv_fields]

with open(csvoutput,'w') as csv_writing:
        w=csv.writer(csv_writing,delimiter='|')
        w.writerow(csv_fields_names)
        for row in arcpy.SearchCursor(table):
                #For all fields
                field_vals=[row.getValue(field.name) for field in csv_fields]
                w.writerow(field_vals)
        del row



#Logging the completion of the clean-up step
printer= "Completed cleanup,renaming,appending and storing of all tables : "+str(datetime.datetime.now().time())[:-7] # print progress update
print printer
logfile.write("\n"+printer)
logfile.flush()

'''Regression Analysis and plotting based on table*******************************************************************'''
# What it does : 1.Using R, a regression equation is used to predict the total target crop area in all non-training townships.
#                
#           
# Possible Errors: While there are no errors programmed into the script, please ensure that both r_script and r_path are correct, as that is how
#                  Python will be able to call R to run. 



# Logging start of regression
printer= "Staring crop regression : "+str(datetime.datetime.now().time())[:-7] # print progress update
print printer
logfile.write("\n"+printer)
logfile.flush()


# This will run the R code. Please note that R commenting is inside the r_script file.
p = Popen([r_path, r_script], stdin=PIPE, stdout=PIPE, stderr=PIPE)
output, err = p.communicate(b"input data that is passed to subprocess' stdin")
rc = p.returncode
#print output
#print err

#The output of R  (the slope and intercept ) is taken, changed to a float,and assigned to variables for readability
eq=output.split(" ")
eq=[elem for elem in eq if elem not in ['[1]','']]
eq=map(float,eq[1:])

slope=eq[1]
intercept=eq[0]


crop_val='VALUE_'+str(crop)

# Logging completion of regression
printer= "---------------------------------"
print printer
logfile.write("\n"+printer)
logfile.flush()

printer= "Slope Equation of current regression : y= " + str(slope) + 'x +' + str(intercept)
print printer
logfile.write("\n"+printer)
logfile.flush()

printer= "---------------------------------"
print printer
logfile.write("\n"+printer)
logfile.flush()


#Field manipulation of the final table
'''
Step-by-Step
1. The RE and CI values are joined to the final table from the tabulated table
2. Levelled_CI_153 field is made and populated based on the original data from the CI rasyter and the regression equation.
3. The original crop value field is deleted.


'''

arcpy.JoinField_management("Original_CI_PredTable_Working","TWP_ID",'Tabulate_all','TWP_ID_S',[str(names[0]),str(names[1])])
arcpy.CalculateField_management("Original_CI_PredTable_Working",final_field_name, str(slope) + " * float(!"+crop_val+"!)+ " + str(intercept) ,"PYTHON")
arcpy.AddField_management("Original_CI_PredTable_Working",names_final,"DOUBLE")
arcpy.CalculateField_management("Original_CI_PredTable_Working",names_final, "!" + crop_val + "!","PYTHON")
arcpy.DeleteField_management("Original_CI_PredTable_Working",crop_val)




#Should the final prediction table contain any outlier values (0), they are deleted..
clean_noise=arcpy.UpdateCursor('Original_CI_PredTable_Working')

# Clean up the final table
for row in clean_noise:
    if row.getValue(names_final)<=0:
        row.setNull(final_field_name)
        clean_noise.updateRow(row)
    if row.getValue(names[0])<=0:
        row.setNull(names[0])
        clean_noise.updateRow(row)

del clean_noise,row


# The prediction table is stored.
arcpy.TableToTable_conversion('Original_CI_PredTable_Working',output_db,'Levelled_CI_'+str(crop))


# The function cleanup is run to cleanup the temp files.
cleanup()

# Logging completion of regression
printer= "Completed crop regression : "+str(datetime.datetime.now().time())[:-7] # print progress update
print printer
logfile.write("\n"+printer)
logfile.flush()

##################################MAIN-END#########################################################################

