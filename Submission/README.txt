
Keisuke Yokota: Responsible for draw.py, crawler0.py, crawler1.py, 
				crawler2.py

Aleister Monfort: Responsible for cleaning_data.py, crawler.py

Jesus Ramirez: Complementary_variables.py, util_compvar.py, 
			   merged_output.py, get_delegaciones_shape.py

*** Folder: 'Final_Product' ***
draw.py: You can draw a map with data on housing prices and other information
	 such as crime, school, or earthquake damages, using the function “draw” in this python file.
	 You will need to install python library “folium” by using a command
	 “pip install folium” in the linux command line.
	 All you need to do is to run “python3 draw.py” in linux command line, then you will get
         a message with an instruction on how to produce a map.
	 After getting the message, please follow the instructions.


delegacion.geojson: Json file containing geographical data of delegation
		   (municipality) in Mexico City


neighborhood.geojson: Json file containing geographical data of neighborhood
		      in Mexico City


integrate.csv: CSV file containing information other than housing prices.
	       It contains data such as:
	        * Number of Markets
	        * Number of Schools
	        * Number of Hospitals
	        * Buldings w/ damage from 09-19-17 earthquake
	        * Number of robberies
		* Number of home robberies (burglaries)
		* Number of murders
		* Number of transit stops
		* Average temperature
		* Population
		* OBJECTID (unique id to each neighborhood)
		* MUN_NAME (delegacion (municipality) name)
		* SETT_NAME (neighborhood name)
		* Number of robberies outside home


house rent.csv: CSV file containing information on housing price data.
	       It contains data as follows:
	        * OBJECTID (unique id to each neighborhood)
		* SETT_NAME (neighborhood name)
		* price


house sale.csv: CSV file containing information on housing price data.
	       It contains data as follows:
	        * OBJECTID (unique id to each neighborhood)
		* SETT_NAME (neighborhood name)
		* price



apartment rent.csv: CSV file containing information on housing price data.
	       It contains data as follows:
	        * OBJECTID (unique id to each neighborhood)
		* SETT_NAME (neighborhood name)
		* price


apartment sale.csv: CSV file containing information on housing price data.
	       It contains data as follows;
	        * OBJECTID (unique id to each neighborhood)
		* SETT_NAME (neighborhood name)
		* price


*** Folder 'Raw_Data' ***

Complememtary_variables.py: In this python file we make the computation of 
	complementary variables (different from real estate prices) at the
	neigborhood level. In Mexico, neighborhood desagregation is not common, 
	most of the variables reported by the government are grouped by 
	municipalities, but in some cases they publish files with metadata 
	that includes some georeference. We use those georeferences to obtain 
	statistics by neighborhood. The CSV files created by this python 
	file are:

		* eqdamage_by_colonia.csv: CSV file with number of buildings with 
		  		any damage caused by the earthquake of september 19th of 
		  		2017 in Mexico City by neighborhood.

		* home_robbery_by_colonia.csv: CSV file with number of home robberies 
		  		reported by neighborhood.

        	* robbery_by_colonia.csv: CSV file with number of robberies reported
          		by neighborhood.

        	* murder_by_colonia.csv: CSV file with number of murders reported 
          		by neighborhood.

        	* hospitals_by_colonia.csv: CSV file with number of hospital located
          		in each neighborhood.

		* schools_by_colonia.csv: CSV file with number of schools located in 
		  		each neighborhood.

        	* markets_by_colonia.csv: CSV file with number of markets located in 
          		each neighborhood.

		* stations_by_colonia.csv: CSV file with number of public transit 
		  		stops located in each neighborhood.

		* temp_by_colonias.csv: CSV file with interpolated average temperature 
		  		by neighborhood.

	In this file we use the library called 'Geopandas' that can be installed
	in VM machines with this code '$ sudo pip3 install geopandas'.

	The inputs required by this python file are stored in a folder named 
	'Official_data', that is stored in a flash drive, that contains the 
	following files and folders:
		* Colonias (folder): Contains the shapefile with the neighborhoods 
		  of Mexico. 
		  - Source: National Institute of Statistics and Geography (2015), Mexico.
		  		    'http://datamx.io/dataset/colonias-mexico/resource/\
		  		     7b5a3b0a-4405-48d6-a4eb-d9f13bb50d3a'

		* Manzanas (folder): Contains statistics at block level in Mexico City.
		  - Source: National Institute of Statistics and Geography (2010), Mexico.
		   			By request.

		* points (folder): Information about services and infraestruture available
						   with point georeferences.
		  - Source: National Institute of Statistics and Geography (2017), Mexico.
		  			'http://www.beta.inegi.org.mx/app/biblioteca/ficha.html?upc\
		  			 =889463171829' 

		* temp_pol (folder): Information about observed temperatures in monitoring
		  stations in Mexico City and its location.
		   - Source: Mexico City Government (2015).
		              'http://www.aire.cdmx.gob.mx/default.php?opc=%27aKBhnmE=&r=\
		               aHR0cDovLzE0OC4yNDMuMjMyLjExMjo4MDgwL29wZW5kYXRhL2FudWFsZXN\
		               faG9yYXJpb3MvbWV0ZW9yb2xvZ8OtYV8yMDE1LmNzdg=='
		
		* crime-lat-long.csv: Crimes reported in Mexico City with georeferences.
		  - Source: Mexico City Government (2016).
		  			'https://data.diegovalle.net/hoyodecrimen/cuadrantes.csv.zip'
		
		* damage_p.csv: Information about the damages registered in Mexico City 
		  				as a result of the earthquake of 09-19-2017.
		  - Source: Federal Government of Mexico (2017).
		             'https://docs.google.com/spreadsheets/d/1ijleBcHJH_\
		              3V2nbMeXTjH4hTDYsjcdodYvHqhTc8C8c/edit?ts=59c52b3a#gid=0'
		
		* t_stations.csv: Information about the location of public transit stations
						  in Mexico City.
		  - Source: Mexico City Government (2015).
		  			 'http://datos.labcd.mx/dataset/932d9f5c-f74f-46a8-9f69-fcb066b20a59/\
		  			  resource/b11f16da-506d-4da4-9c1d-210921d88e5c/download/st25.02.2015\
		  			   .csv'
	Finally, it is important to point out that the variables 'path' and 'output_path' indicates
	the route to input and outputs folders, so they have to be modified if this python file is
	run in a different directory.

util_compvar.py: Auxiliary functions used in 'Complementary_variables.py'

merged_output.py: In this file we create a unique dataframe and csv 
	file that is the input to produce the maps of complementary variables. 
	This task could be done directly in 'Complementary_variables.py',
	but it takes about two hours to produce some of the dataframes and
	files needes; so we do the merge in a different file. This file
	produce 'integrate.csv' file previously described.

get_delegaciones_shape.py: This file creates a shapefile for neighborhoods 
	of Mexico City based in shape file for neighborhoods in all the country.

* Subfolder 'Real_state'
crawler0.py: Scraps the website 'centrury21.com.mx'.
crawler1.py: Scraps the website 'metroscubicos.com'.
crawler2.py: Scraps the website 'icasas.mx'.
crawler3.py: Scraps the website 'inmuebles24.com'.
 
clean_data.py: Cleans the datasets coming from the websites, inmuebles24 
	(four datasetsets), and from metroscubicos.com, icasas.mx, centrury21.com.mx. 
	It also matches neighborhoods from the property records coming from the 
	websites, with the official neighborhood names coming from the neighborhood 
	shapefiles.
	To run it you neet to install fuzzywuzzy package doing 'sudo pip3 install fuzzywuzzy'
	By running clean_data.py, you will generate the csv files at the neighborhood
	level with median prices.
	It generates four files: 
		- house_rent_median.csv
		- house_sale_median.csv
		- appartment_rent_median.csv
		- appartment_sale_median.csv

	These files are used to produce the maps in draw.py