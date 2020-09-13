# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# GeologicProfile.py
# Author: Danny Leon Delgado (Servicio Geologico Colombiano), Alejandra Amaya(Servicio Geologico Colombiano), Oscar Munoz (Servicio Geologico Colombiano), Myriam Lopez(Servicio Geologico Colombiano)
# Created on: 2020-08-30 16:40:30.00000
# Description: This tool make the tectonic profile through intersections and interpolations between the input parameters.
# ---------------------------------------------------------------------------

# Import modules
import arcpy

# Script arguments
planProfileLineFC = arcpy.GetParameterAsText(0)
planStrDataFC = arcpy.GetParameterAsText(1)
geologyFC = arcpy.GetParameterAsText(2)
DEM = arcpy.GetParameterAsText(3)
exaggerationVal = arcpy.GetParameterAsText(4)
dissolveGeologyField = arcpy.GetParameterAsText(5)
outGeologicProfile = arcpy.GetParameterAsText(6)
outStrDataProfile = arcpy.GetParameterAsText(7)


# Environment settings
mxd = arcpy.mapping.MapDocument("CURRENT")  
df = arcpy.mapping.ListDataFrames(mxd, "*")[0] 
arcpy.CheckOutExtension("Spatial")
sr = arcpy.Describe(planProfileLineFC).spatialReference # Adignación del sistema de coordenadas

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# Generate the start point of the Plan Profile Line and calculate their coordinates
startPoint = arcpy.FeatureVerticesToPoints_management(planProfileLineFC, 'in_memory\startPointDataT', "START")
arcpy.AddXY_management(startPoint)
    
#Process to draw geological profile

startXYArray = [] # Array to stock the start point coordinates (X and Y)

# Loop the cursor to append the X and Y values to startXYArray
startCursor= arcpy.SearchCursor(startPoint)  
for row in startCursor:
    xCoordVal = row.POINT_X
    yCoordVal = row.POINT_Y
    startXYArray.append(xCoordVal)
    startXYArray.append(yCoordVal)

del startCursor

xStart = startXYArray[0] 
yStart = startXYArray[1]

# Generate points along the plan profile line each 6 meters and calculate their coordinates
pointsAlongLine = arcpy.GeneratePointsAlongLines_management(planProfileLineFC, 'in_memory\pointsAlongLineT', "DISTANCE", "6 meters", "", "END_POINTS")
arcpy.AddXY_management(pointsAlongLine)

# Add Distance field and calculate the distance between start point and each generated point
arcpy.AddField_management(pointsAlongLine, "Distance", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(pointsAlongLine, "Distance", "math.sqrt( ( !POINT_X! - "+str(xStart) +")**2 + ( !POINT_Y! - "+str(yStart) +")**2 )", "PYTHON_9.3", "")

# Join Geology attributes to points along the plan profile line
geologyPoints = arcpy.SpatialJoin_analysis(pointsAlongLine, geologyFC, 'in_memory\geologyPointsT', "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "INTERSECT", "", "")

# Interpolate the points along the plan profile line with the DEM
geologyPoints3D = arcpy.InterpolateShape_3d(DEM, geologyPoints, 'in_memory\geologyPoints3DT', "", "1", "BILINEAR", "DENSIFY", "0", "EXCLUDE")

# Add X Y Z Coordinates
arcpy.AddXY_management(geologyPoints3D)

# Recalculate Y coordinate to draw the profile
arcpy.CalculateField_management(geologyPoints3D, "POINT_Y", "!POINT_Z! * "+str(exaggerationVal)+"", "PYTHON_9.3", "")

# Make the Geology Profile Points through the profile Distance vs Heigh and export to Feature Class or Shapefile
geologyProfilePointsLyr = arcpy.MakeXYEventLayer_management(geologyPoints3D, "Distance", "POINT_Y",  'in_memory\geologyProfilePointsLyrT', sr, "")
geologyProfilePoints = arcpy.CopyFeatures_management(geologyProfilePointsLyr, 'in_memory\geologyProfilePointsT', "", "0", "0", "0")

# Generate line whit the Geology Profile Points
line3D = arcpy.PointsToLine_management(geologyProfilePoints, 'in_memory\line3DT', "", "", "NO_CLOSE")

# Split the line with each point
splitLine3D = arcpy.SplitLine_management(line3D, 'in_memory\splitLine3DT')

# Add geology attributes to profile line and dissolve by dissolve field
splitGeologyLine3D = arcpy.SpatialJoin_analysis(splitLine3D, geologyProfilePoints, 'in_memory\splitGeologyLine3DT', "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "INTERSECT", "", "")
geologyProfile3D = arcpy.Dissolve_management(splitGeologyLine3D, outGeologicProfile, dissolveGeologyField, "", "MULTI_PART", "DISSOLVE_LINES")


addLayer = arcpy.mapping.Layer(outGeologicProfile)
arcpy.mapping.AddLayer(df, addLayer, "TOP") # Add layer to data frame

# Delete temporal data
arcpy.DeleteFeatures_management('in_memory\startPointDataT')
arcpy.DeleteFeatures_management('in_memory\pointsAlongLineT')
arcpy.DeleteFeatures_management('in_memory\geologyPointsT')
arcpy.DeleteFeatures_management('in_memory\geologyPoints3DT')
arcpy.DeleteFeatures_management('in_memory\geologyProfilePointsT')
arcpy.DeleteFeatures_management('in_memory\line3DT')
arcpy.DeleteFeatures_management('in_memory\splitLine3DT')
arcpy.DeleteFeatures_management('in_memory\splitGeologyLine3DT')
arcpy.DeleteFeatures_management('in_memory\geologyProfilePointsLyrT')
arcpy.Delete_management('in_memory\geologyProfilePointsLyrT')

# Process to draw structural data in geologic profile

# Add X and Y Coordinates
arcpy.AddXY_management(planStrDataFC)

# Add Distance field and calculate the distance between start point and each structural data in plan profile line
arcpy.AddField_management(planStrDataFC, "Distance", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(planStrDataFC, "Distance", "math.sqrt( ( !POINT_X! - "+str(xStart) +")**2 + ( !POINT_Y! - "+str(yStart) +")**2 )", "PYTHON_9.3", "")

# Interpolate the structural data in plan profile line with the DEM
strData3D = arcpy.InterpolateShape_3d(DEM, planStrDataFC, 'in_memory\strData3dT', "", "1", "BILINEAR", "DENSIFY", "0", "EXCLUDE")

# Add X Y Z Coordinates
arcpy.AddXY_management(strData3D)

# Recalculate Y coordinate to draw the structural data in profile line
arcpy.CalculateField_management(strData3D, "POINT_Y", "!POINT_Z! * "+str(exaggerationVal)+"", "PYTHON_9.3", "")

# Make the structural data in profile line through the Distance vs Heigh and export to Feature Class or Shapefile
strDataProfileLyr = arcpy.MakeXYEventLayer_management(strData3D, "Distance", "POINT_Y", 'in_memory\strDataProfileLyrT', sr, "")
StrDataProfile = arcpy.CopyFeatures_management(strDataProfileLyr, outStrDataProfile, "", "0", "0", "0")


addLayer = arcpy.mapping.Layer(outStrDataProfile)
arcpy.mapping.AddLayer(df, addLayer, "TOP") # Add layer to data frame

# Delete temporal data
arcpy.DeleteFeatures_management('in_memory\strData3dT')
arcpy.DeleteFeatures_management('in_memory\strDataProfileLyrT')

arcpy.Delete_management('in_memory\strDataProfileLyrT')