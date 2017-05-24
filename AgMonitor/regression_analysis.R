####################################Introduction###########################################################
#Project name : Agmonitor
#Programmed by: Martin Holicka
#Date: November 10th,2015
#Project Purpose: To perform regression on Rapid Eye and Crop Inventory data to verify accuracy.

#Project component: Script for performing and visualizing the regression of the CI vs RE input from Agmonitor.py

####################################Introduction###########################################################



setwd ("E:\\Agriculture_CIRE\\working_AgricultureCI_RE")
# Edit the folowing path depending on the computer
x<-.libPaths(c("C:/Users/holickam/Documents/R/win-library/3.2", .libPaths()))
#if (!require("pacman")) install.packages("pacman"); library(pacman)
#p_load(MASS,influence.ME)
library(MASS)
library(influence.ME)
cropareatable <- read.table("rastertable.csv", header=T, sep="|")
outfile<-"E:\\Agriculture_CIRE\\Done_AgMap\\R_Output\\RegressionSummary.txt "
graphfile<-"E:\\Agriculture_CIRE\\Done_AgMap\\R_Output\\graphs\\"

if (!dir.exists("E:\\Agriculture_CIRE\\Done_AgMap\\R_Output"))
{
  dir.create("E:\\Agriculture_CIRE\\Done_AgMap\\R_Output")
}
if(!dir.exists("E:\\Agriculture_CIRE\\Done_AgMap\\R_Output\\graphs"))
{
  dir.create("E:\\Agriculture_CIRE\\Done_AgMap\\R_Output\\graphs")
}


###############################USER INPUT##########################################

# Select the critical z score and set crit_z to be the variable of your chosen CI.
#DEFAULT: 99% confidence interval
crit_0.99<-2.58
crit_0.98<-2.33
crit_0.95<-1.96
crit_0.90<-1.645

crit_z<-crit_0.99

# source : http://www.math.armstrong.edu/statsonline/5/5.3.2.html



###################################################################################

# This will decide if only rlm is used or if outliers are removed.
# comment out the option that you do not want. DEFAULT: True

#outlier_removal=FALSE
outlier_removal=TRUE

#######################Type of Outlier Removal#####################################
#Choices:
#'cooks_dffits' <------------DEFAULT
#'confidenceIntervals'

type_removal<-'confidenceIntervals'

###############################USER INPUT##########################################



##############################FUNCTION#############################################
# Name: naming 
# inputs: tab_data( the table that is being looked at)
# Purpose: get the data for all relevant fields on a table 
#         Relevant fields: Township ID, RE Data, CI Data
# Output: List of all relevant data
naming<-function(tab_data){
  x<-(colnames(tab_data))
  id_town<-tab_data[, x[2]]
  re <-tab_data[, x[3]]
  ci<-tab_data[, x[4]]
  result<-list(id_town=id_town,re=re,ci=ci)
  return (result)
}

# Name: regression
# inputs: indata_table(the table that is being looked at)
# Purpose:Perform all robust linear regression tasks and output 
#    Output: List of all regression data
regression<-function(indata_table){
  data_vals<-naming(indata_table)
  robustlinreg <- rlm(data_vals$re~data_vals$ci)
  coeff<-summary(robustlinreg)$coefficients
  r_val<-round (cor (data_vals$re,data_vals$ci),5)
  eq<-c(coeff[1,1],coeff[2,1])
  final_regression<-list(data_vals=data_vals,robustlinreg=robustlinreg,coeff=coeff,r_val=r_val,eq=eq)
  return (final_regression)
}


##############################FUNCTION##############################################

####################################################################################
################################MAIN################################################
####################################################################################

mainname<-'blank'
# naming of the variables (used for graph title)

if (crit_z == crit_0.99)
{
  mainname<-'CI: 99 %'
} else if (crit_z == crit_0.98)
{
  mainname<-'CI: 98 %'
}else if (crit_z == crit_0.95)
{
  mainname<-'CI: 95 %'
}else 
{
  mainname<-'CI: 90 %'
}




#######################Robust Linear Regression codeblock###########################

# This creates the entire robust linear regression for the cropareatable
outliers<-regression(cropareatable)

# Paste all relevant regression information to the outfile.
sink(outfile)
writeLines(paste('Robust linear Regression - Possible outliers not removed'))
writeLines('--------------------------------------------------------')
summary(outliers$robustlinreg)
writeLines(paste('R-Value:',outliers$r_val))
writeLines(paste('Equation of the line: y=',outliers$eq[2],'x +',outliers$eq[1] ))
writeLines('--------------------------------------------------------')
writeLines('')
writeLines('')
writeLines('')
sink()


# A visual image(graph) is created in the  output directory 
png(filename=paste(graphfile,'CIvsRE_outliers.png'))
plot_x<-plot (outliers$data_vals$re~outliers$data_vals$ci, data=cropareatable, col=4, cex=1, pch=16,main =paste('CI vs RE Regression- Possible outliers'),xlab='Crop Inventory Reading',ylab='Rapideye Reading')
abline(a=1, b=1, col = 3, lty=2)
abline(outliers$robustlinreg, col="blue")
x<-dev.off()

#Residuals are added to the cropareatable for further outlier detection
cropareatable$residual<-outliers$robustlinreg$residuals

#adding a graph of the qqplots, as well as a line.
png(filename=paste(graphfile,'qqnorm.png'))
norm_plot<-qqnorm(outliers$robustlinreg$residuals)
qqline(outliers$robustlinreg$residuals)
x<-dev.off()
#adding a graph of the residuals, as well as a line at 0.
png(filename=paste(graphfile,'residuals.png'))
resplot<-plot(outliers$robustlinreg$residuals,main='Residuals of CI vs RE')
abline(h=0,col='Blue')
x<-dev.off()


# In the case of only RLM, the result of this code is the equation of the line from RLM, but it the user wishes to remove the outliers, the output are the coefficients given from the rlm of the table with removed possible outliers.
if(!outlier_removal){
  
  print(outliers$eq)
  
}


strSummary<-writeLines("")
strRound<-""
strText<-""
strType<-""


if(outlier_removal){
  
  if(type_removal=='cooks_dffits')
  {
    ######################DFFITS and Cook's Distance##################################
    #Taking the table created from just the RLM, this will attempt to remove potential outliers using cooks distance or DFFITS(See reference below) 
    
    ###########################REFERENCE############################################
  #cook's distance : D>4/n n=number of rows, D is cooks distance [lower D = possible outlier.]
  #DFFITs: abs(dffits_i)>2*sqrt((p+1)/n) n= number of rows, p is number of coefficients (2) and dffits is calculated.
  ###########################REFERENCE############################################    

    
    #creates the regression(needs to be lm)
    linreg_croptable <- lm(outliers$data_vals$re~outliers$data_vals$ci)
    
    
    #Using the output from the regression, calculates a cutoff value for cook's distance 
    #The following operations occur:
    # 1. A dffits value is calculated for the linear regression of the RE and CI variable
    # 2. Only those values that are greater than 1 are kept 
    # 3. N and P values are assigned
    # 4. Using the forumla that is detailed above, The dffits value is calculated for this regression
    
    
    dffits_i<-dffits(linreg_croptable)
    dffits_i[abs(dffits_i)>1]
    n<-length(linreg_croptable$residuals)
    p<-length(linreg_croptable$coefficients)
    dffits_i[abs(dffits_i)>2*sqrt((p+1)/n)]
    
    #The cutoff value is stored, and the column with the values is added.
    cutoff <- dffits_i
    cropareatable$dffits<-cooks.distance(linreg_croptable)
    #Should any values be less than the cuttof, they are set to NA
    
    # Create another table to backup the original values of the cropareatable
    #cropareatable_original <- cropareatable
    
    
        #should the user want to user want to use 4/n as the cutoff, they may comment the top line, and may uncomment the bottom line. 
    cropareatable$dffits[cropareatable$dffits>cutoff]<- NA
    #previous Version of cuttofs
    #cropareatable$dffits[cropareatable$dffits<cutoff]<- NA
    #cropareatable$dffits[cropareatable$dffits<(4/n)]<-NA
    
    
    
    #plotting DDFITS
    png(filename=paste(graphfile,'DFFITS.png'))
    nooutliers_dffits<-plot(x = 1:n, y = dffits_i, xlab = "Observation number", ylab = "DFFITS", main ="DFFITS vs. observation Number", panel.first = grid(col ="gray", lty = "dotted"), ylim = c(min(-1, -2*sqrt(p/n), min(dffits_i)), max(1, 2*sqrt(p/n),max(dffits_i))))
    abline(h = 0, col = "darkgreen")
    abline(h = c(-2*sqrt(p/n), 2*sqrt(p/n)), col = "red",lwd = 2)
    abline(h = c(-1,1), col = "darkred", lwd = 2)
    #identify(x = 1:n, y = dffits_i)
    x<-dev.off()
    
    
    
    # Plotting Cooks Distance
    png(filename=paste(graphfile,'CooksDistance.png'))
    nooutliers_cooks<-plot(x=1:n,y=cropareatable$dffits,xlab='Observation Number',ylab='Cook`s Distance',main='Cook`s vs observation Number',panel.first = grid(col='gray',lty='dotted'),ylim=c(0,qf(p=0.5,df1=p,df2=linreg_croptable$df.residual)))
    abline(h=0,col='darkgreen')# Creates a horizontal line at y=0
    abline(h=qf(p=0.5,df1=p,df2=linreg_croptable$df.residual),col='red',lwd=2)
    #identify(x=1:n,y=cropareatable$cooks)
    x<-dev.off()
    
    #A new table , with all potential outliers removed is created. 
    cropareatable_nooutliers<-na.omit(cropareatable) 
    ######################DFFITS and Cook's Distance##################################
    
  }else
  {
    ######################Robust Linear Regression codeblock###########################
    
    #################Robust Linear Regression with outlier Removal Codeblock###########
    ####This codeblock will only run if the user  sets outlier_removal to be TRUE.####
    
    # By setting the crit_z variable in the user input section, the user can set the Confidence interval to be used. Documentation regarding the critical z-scores is located in the user_input section, but will also be repeated here for reference
    
    ###########################REFERENCE############################################
    #99% Confidence interval crit_z<-2.58
    #98% Confidence interval crit_z<-2.33
    #95% Confidence interval crit_z<-1.96
    ###########################REFERENCE############################################  
    
    
    #######################Upper and Lower CI############################################
    #####################################################################################
    # Code for finding the upper and lower confidence intervals
    err<- stats::predict(outliers$robustlinreg,se=TRUE)
    cropareatable$ucl<-err$fit + crit_z *err$se.fit
    cropareatable$lcl<-err$fit - crit_z *err$se.fit
    
    #######################Upper and Lower CI############################################
    #####################################################################################  
    
    #based on the CI,predicted outliers are marked to be set to FALSE
    cropareatable$outliers<-(cropareatable$lcl>= outliers$data_vals$re |outliers$data_vals$re >= cropareatable$ucl)
    #predicted outliers based on CI are set to be NA, and exported into a new table, which does not take the NA values
    cropareatable$outliers[cropareatable$outliers == TRUE] <-NA
    cropareatable_nooutliers<-na.omit(cropareatable)
    
    #######################Robust Linear Regression codeblock###########################
    
  }
  
  #Using either of the outlier removal techniques described, a new regression is formed.
  remoutlier_regress<-regression(cropareatable_nooutliers)
  
  
  # graph is created for visual representation to the user. It is stored in the output directory.
  png(filename=paste(graphfile,'Nooutliers_',type_removal,'.png'))
  nooutliers_ci<-plot (remoutlier_regress$data_vals$re~remoutlier_regress$data_vals$ci, data=cropareatable, col=4, cex=1, pch=16,main =paste('CI vs RE Regression- Outliers Removed'),xlab='Crop Inventory Reading',ylab='Rapideye Reading')
  abline(a=1, b=1, col = 3, lty=2)
  abline(remoutlier_regress$robustlinreg, col="blue")
  y<-dev.off()
  
  # Relevant values are set for output to the regression text file.
  #Values: Summary of robust linear regression, r value of regression, and equation of the line.
  strType<-paste('Robust linear Regression: ',type_removal,'-Possible Outliers Removed')
  strSummary<-summary(remoutlier_regress$robustlinreg)
  strRound<-paste('R-Value:',remoutlier_regress$r_val)
  strText<-paste('Equation of the line: y=', remoutlier_regress$eq[2],'x +',remoutlier_regress$eq[1] )
  
  #Equation of Regression line is recorded for further processing in Python
  print(remoutlier_regress$eq)
  #remoutlier_regress$eq
}

# All relevant data is written to an output file based on user preference.
sink(outfile,append=TRUE)
writeLines(strType)
strSummary
writeLines(strRound)
writeLines(strText)
sink()
