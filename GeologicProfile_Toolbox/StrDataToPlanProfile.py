# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# StrDataToPlanProfile.py
# Author: Danny Leon Delgado (Servicio Geologico Colombiano), Alejandra Amaya(Servicio Geologico Colombiano), Oscar Munoz (Servicio Geologico Colombiano), Myriam Lopez(Servicio Geologico Colombiano)
# Created on: 2020-08-30 16:40:30.00000
# Description: This tool calculate the apparent dip in the selected structural data and project the data to the plan profile line.
# ---------------------------------------------------------------------------

# Import modules
import arcpy

# Script arguments
strDataFC = arcpy.GetParameterAsText(0)
profileFC = arcpy.GetParameterAsText(1)
azRumField = arcpy.GetParameterAsText(2)
dipField = arcpy.GetParameterAsText(3)
faultFC = arcpy.GetParameterAsText(4)
foldFC = arcpy.GetParameterAsText(5)
outFC = arcpy.GetParameterAsText(6)


# Environment settings
mxd = arcpy.mapping.MapDocument("CURRENT") 
df = arcpy.mapping.ListDataFrames(mxd, "*")[0] 
arcpy.CheckOutExtension("Spatial")
sr = arcpy.Describe(strDataFC).spatialReference

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# Add coordinates X and Y to Structural Data Feature Layer
arcpy.AddXY_management(strDataFC)

outlines = [] # Array to stock the temporal line projections of structural data

# Add bearing azimuth to plan profile line
arcpy.AddGeometryAttributes_management(profileFC, 'LINE_BEARING', 'METERS', '#', sr)

# Define cursor to loop the Structural Data Feature Layer
cursor1= arcpy.SearchCursor(strDataFC)

# Loop the cursor and append the temporal line projections in outlines array
for row1 in cursor1:
    Bz = (row1.getValue(dipField))
    Az = (row1.getValue(azRumField))
    Az2 = Az + 180
    xi = (row1.getValue("POINT_X"))
    yi = (row1.getValue("POINT_Y"))
    start = arcpy.PointGeometry(arcpy.Point(xi,yi), sr)
    end = start.pointFromAngleAndDistance(Az,5000,"PLANAR")
    end2 = start.pointFromAngleAndDistance(Az2,5000,"PLANAR")
    outlines.append(arcpy.Polyline(arcpy.Array([start.centroid,end.centroid]),sr))
    outlines.append(arcpy.Polyline(arcpy.Array([start.centroid,end2.centroid]),sr))
    arcpy.CopyFeatures_management(outlines,'in_memory\Aux1')
del cursor1

# Define cursor to loop the Plan Profile Line Feature Layer
cursor2= arcpy.SearchCursor(profileFC)  

# Adjust the value in case the azimuth is greater than 180
for row in cursor2:
    azVal = row.BEARING
    if azVal > 180:
        azVal = azVal - 180
        arcpy.FlipLine_edit(profileFC)
    arcpy.AddMessage("Bearing azimuth profile line: " + str(azVal))
    arcpy.CalculateField_management(profileFC,"BEARING",str(azVal), "PYTHON", "#")

arcpy.SpatialJoin_analysis('in_memory\Aux1',strDataFC,'in_memory\Aux2') # Join the Structural Data attributes to the temporal projection lines
arcpy.Intersect_analysis([profileFC,'in_memory\Aux2'],'in_memory\Aux5',"ALL","","POINT") # Capture the intersection points to project the structural data in the plan profile line

# Project the intersection points in case there are faults and/or folds

if foldFC != '' and faultFC != '':
    arcpy.Intersect_analysis([profileFC,foldFC],'in_memory\Aux3',"ALL","","POINT")
    arcpy.Intersect_analysis([profileFC,faultFC],'in_memory\Aux4',"ALL","","POINT")
    arcpy.Merge_management(['in_memory\Aux3','in_memory\Aux4','in_memory\Aux5'],'in_memory\Aux6')
    arcpy.DeleteFeatures_management('in_memory\Aux3')
    arcpy.DeleteFeatures_management('in_memory\Aux4')
elif foldFC == '' and faultFC != '':
    arcpy.Intersect_analysis([profileFC,faultFC],'in_memory\Aux4',"ALL","","POINT")
    arcpy.Merge_management(['in_memory\Aux4','in_memory\Aux5'],'in_memory\Aux6')
    arcpy.DeleteFeatures_management('in_memory\Aux4')
elif foldFC != '' and faultFC == '':
    arcpy.Intersect_analysis([profileFC,foldFC],'in_memory\Aux3',"ALL","","POINT")
    arcpy.Merge_management(['in_memory\Aux3','in_memory\Aux5'],'in_memory\Aux6')
    arcpy.DeleteFeatures_management('in_memory\Aux3')
else:
    arcpy.CopyFeatures_management('in_memory\Aux5','in_memory\Aux6')


# Identify the kind of angle to calculate the aparent Dip in each structural data (Except Faults and Folds)
arcpy.AddField_management('in_memory\Aux6',"I_D","TEXT")
arcpy.MakeFeatureLayer_management('in_memory\Aux6', "DE_Corte")
arcpy.SelectLayerByAttribute_management("DE_Corte","NEW_SELECTION",'"'+str(azRumField)+'"'+'>= "BEARING" AND'+ '"'+str(azRumField)+'"'+'<( "BEARING" +180)')
arcpy.CalculateField_management("DE_Corte","I_D",'"Izq"',"PYTHON")
arcpy.SelectLayerByAttribute_management("DE_Corte","NEW_SELECTION",'"'+str(azRumField)+'"'+'< "BEARING" OR'+'"'+str(azRumField)+'"'+'>=( "BEARING" +180)')
arcpy.CalculateField_management("DE_Corte","I_D",'"Der"',"PYTHON")


arcpy.AddField_management("DE_Corte","Angle","FLOAT")
arcpy.SelectLayerByAttribute_management("DE_Corte","NEW_SELECTION",'"'+str(azRumField)+'"'+'< "BEARING"')
arcpy.CalculateField_management("DE_Corte","Angle",'!BEARING!- !'+str(azRumField)+'!',"PYTHON")
arcpy.SelectLayerByAttribute_management("DE_Corte","NEW_SELECTION",'"'+str(azRumField)+'"'+'> "BEARING" AND'+'"'+str(azRumField)+'"'+'<= 180')
arcpy.CalculateField_management("DE_Corte","Angle",'!'+str(azRumField)+'!- !BEARING!',"PYTHON")
arcpy.SelectLayerByAttribute_management("DE_Corte","NEW_SELECTION",'"'+str(azRumField)+'"'+'> "BEARING" AND 270 >='+ '"'+str(azRumField)+'"'+'AND'+'"'+str(azRumField)+'"'+' > 180')
arcpy.CalculateField_management("DE_Corte","Angle",'!BEARING!-( !'+str(azRumField)+'!-180)',"PYTHON")
arcpy.SelectLayerByAttribute_management("DE_Corte","NEW_SELECTION",'"'+str(azRumField)+'"'+'> "BEARING" AND 360 >='+'"'+str(azRumField)+'"'+'AND'+'"'+str(azRumField)+'"'+'> 270')
arcpy.CalculateField_management("DE_Corte","Angle",'(!'+str(azRumField)+'!-180)-!BEARING!',"PYTHON")
arcpy.SelectLayerByAttribute_management("DE_Corte","NEW_SELECTION",'"'+str(azRumField)+'"'+'= 0')
arcpy.CalculateField_management("DE_Corte","Angle",'(180-!BEARING!)',"PYTHON")
arcpy.SelectLayerByAttribute_management("DE_Corte","CLEAR_SELECTION")

# Calculate the aparent Dip
arcpy.AddField_management("DE_Corte","AparentDip","FLOAT")
arcpy.CalculateField_management("DE_Corte","AparentDip",'math.degrees(math.atan(math.tan( (!'+str(dipField)+'!*math.pi)/180 )*math.sin(( !Angle! *math.pi)/180 ) ) )',"PYTHON")
strDataPlan = arcpy.MultipartToSinglepart_management("DE_Corte",outFC)

addLayer = arcpy.mapping.Layer(outFC)
arcpy.mapping.AddLayer(df, addLayer, "TOP") # Add layer to data frame


# Delete temporal data
arcpy.DeleteFeatures_management('in_memory\Aux1')
arcpy.DeleteFeatures_management('in_memory\Aux2')
arcpy.DeleteFeatures_management('in_memory\Aux5')
arcpy.DeleteFeatures_management('in_memory\Aux6')

arcpy.Delete_management("DE_Corte")