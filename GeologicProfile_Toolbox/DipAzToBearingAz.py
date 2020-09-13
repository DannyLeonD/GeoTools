# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# DipAzToBearingAz.py
# Author: Danny Leon Delgado (Servicio Geologico Colombiano), Alejandra Amaya(Servicio Geologico Colombiano), Oscar Munoz (Servicio Geologico Colombiano), Myriam Lopez(Servicio Geologico Colombiano)
# Created on: 2020-08-30 16:40:30.00000
# Description: This tool transforms the values of Dip Azimuth to Bearing Azimuth.
# ---------------------------------------------------------------------------

# Import modules
import arcpy


# Script arguments
strDataFC = arcpy.GetParameterAsText(0)
azDipField = arcpy.GetParameterAsText(1)

# Add field to calculate the bearing azimuth
arcpy.AddField_management(strDataFC,"BearingAz","FLOAT")

## Expresion:
expression = 'AzRum ( !'+str(azDipField)+'! )'

##Code Block:
codeBlock = """def AzRum(AzB):
  if AzB-90 >= 0:
    AzR = AzB-90
    return AzR
  else:
   AzR = 360+(AzB-90)
   return AzR"""

# Calculate th value of bearing azimuth from dip azimuth
arcpy.CalculateField_management(strDataFC,"BearingAz",expression,"PYTHON",codeBlock)