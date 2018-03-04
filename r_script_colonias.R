library(dplyr)
library(ggmap)
library(maptools)

file_name = 'C:/Users/jesus/OneDrive/Documentos/GitHub/Final-Project-CS-Winter-2018/Data/Colonias/Colonias.dbf'
colonias = read.dbf(file_name)
summary(colonias)
area_colonias = readShapePoly('C:/Users/jesus/OneDrive/Documentos/GitHub/Final-Project-CS-Winter-2018/Data/Colonias/Colonias.shp')
plot(subset(area_colonias, ST_NAME == 'DISTRITO FEDERAL'))

delegaciones = col_df %>%
group_by(MUN_NAME) %>%
summarise()

colonias_list = col_df %>%
group_by(SETT_NAME) %>%
summarise()