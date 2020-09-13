
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# PrintAuxLines.py
# Author: Danny Leon Delgado (Servicio Geologico Colombiano), Alejandra Amaya(Servicio Geologico Colombiano), Oscar Munoz (Servicio Geologico Colombiano), Myriam Lopez(Servicio Geologico Colombiano)
# Created on: 2020-08-30 16:40:30.00000
# Description: This tool draw the dip and auxiliar lines to continue make the geologic profile.
# ---------------------------------------------------------------------------

# Import modules
import arcpy

# Script arguments
strDataFC = arcpy.GetParameterAsText(0)
outDipFC = arcpy.GetParameterAsText(1)
outAuxFC = arcpy.GetParameterAsText(2)

# Environment settings
mxd = arcpy.mapping.MapDocument("CURRENT")  # Se define como predefinido el MXD actual
df = arcpy.mapping.ListDataFrames(mxd, "*")[0] # Asignación del dataframe a la variable df
arcpy.CheckOutExtension("Spatial")
sr = arcpy.Describe(strDataFC).spatialReference

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# Make the Dip Lines to continue whit the profile elaboration
outlines = []
cursor1= arcpy.SearchCursor(strDataFC)
for row1 in cursor1:
    Bzm = (row1.getValue("AparentDip"))
    Bz1 = 270 - Bzm
    Bz2 = Bzm + 90
    Bz3 = Bzm + 180
    I_D = (row1.getValue("I_D"))
    xi = (row1.getValue("Distance"))
    yi = (row1.getValue("POINT_Z"))
    start = arcpy.PointGeometry(arcpy.Point(xi,yi), sr)
    if Bzm == 0 and I_D == " ":
        end = start.pointFromAngleAndDistance(Bz3,500,"PLANAR")
    elif I_D == "Izq" and Bzm != 0:
        end = start.pointFromAngleAndDistance(Bz1,500,"PLANAR")
    else:
        end = start.pointFromAngleAndDistance(Bz2,500,"PLANAR")
    outlines.append(arcpy.Polyline(arcpy.Array([start.centroid,end.centroid]),sr))
arcpy.CopyFeatures_management(outlines,'in_memory\Aux1')
dipLinesFC = arcpy.SpatialJoin_analysis('in_memory\Aux1',strDataFC,outDipFC)

addLayer = arcpy.mapping.Layer(outDipFC)
arcpy.mapping.AddLayer(df, addLayer, "TOP") # Add layer to data frame

# Make the Dip Lines to continue whit the profile elaboration
outlines2 = []
cursor2= arcpy.SearchCursor(strDataFC)
for row2 in cursor2:
    Bzm = (row2.getValue("AparentDip"))
    Bz1 = 360 - Bzm
    Bz2 = Bzm
    I_D = (row2.getValue("I_D"))
    xi = (row2.getValue("Distance"))
    yi = (row2.getValue("POINT_Z"))
    start = arcpy.PointGeometry(arcpy.Point(xi,yi), sr)
    if I_D == "Izq":
        end = start.pointFromAngleAndDistance(Bz1,500,"PLANAR")
    elif I_D == "Der":
        end = start.pointFromAngleAndDistance(Bz2,500,"PLANAR")
    else:
        end = start
    outlines2.append(arcpy.Polyline(arcpy.Array([start.centroid,end.centroid]),sr))
auxLines = arcpy.CopyFeatures_management(outlines2,outAuxFC)

addLayer = arcpy.mapping.Layer(outAuxFC)
arcpy.mapping.AddLayer(df, addLayer, "TOP") # Add layer to data frame

# Delete temporal data
arcpy.DeleteFeatures_management('in_memory\Aux1')