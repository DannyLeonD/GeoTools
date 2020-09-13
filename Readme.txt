# ---------------------------------------------------------------------------
# GeologicProfileTool
# Author: Danny Leon Delgado (Servicio Geologico Colombiano), Alejandra Amaya(Servicio Geologico Colombiano), 
	  Oscar Munoz (Servicio Geologico Colombiano), Myriam Lopez(Servicio Geologico Colombiano)

# Description: This tool make the tectonic profile through intersections and interpolations between the input parameters.
# ---------------------------------------------------------------------------



This tool can be implemented in ESRI´s ArcGIS software through the compilation of geoprocess tools
in automated models and scripts developed in Python. SAGCS toolbox contains four scripts and two 
optional automation models. Through these components, the faults, folds and structural data are 
projected on plane section line, all this data are interpolated with the selected DEM (Digital Elevation Model) 
and then are projected to a X Y plane in which the dip and the auxiliary lines are drawn to start the geological interpretation.
At the end of the tool implementation, the interpretive process of construction of the geological profile must be started. 
This process must be carried out manually and with the expert judgment of the professional in charge of the product's elaboration.

The SAGCS tool is composed of a series of geo-processes grouped into four scripts developed in Python, 
that must be executed according to next order: (1) Dip Direction (Dip Azimuth) to Strike Direction (Bearing Azimuth) (Optional);
 (2) Structural Data to Profile Line; (3) Geologic Profile; (4) Aux Profile Lines. There are two automated optional models to 
generate specific products: (a) Geological Profile (Optional) and (b) Str Data to Profile (Optional). The ArcGIS Spatial Analyst 
and 3D Analyst extensions are required.

Before starting the tool implementation, the user must select the structural data (points) that can be useful for interpretation, 
the structural data cannot be located more than 5 kilometers from the profile line.

***
It is important to verify that all the Feature and Raster layers are in the same projected coordinate system, note that the tool does not work with 
data in geographic coordinate system.

