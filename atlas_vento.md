Creacion de un Atlas de viento costero de alta resoluci ´ on´
para Galicia combinando WAsP y las salidas del modelo
WRF de MeteoGalicia
1 / 82
Elaborado por:
MeteoGalicia - Departamento de Predicion Num ´ erica: numerico.meteogalicia@xunta.es ´
D3 Applied Technologies - Carlos Otero: carlosotero@d3atech.com
Este desarrollo ha sido finaciando por el proyecto del Espacio Atlantico EnergyMare (INTERREG ´
IV-B, Nr. 2011-1/157).
2 / 82
´Indice
1. Introduccion´ 5
1.1. El modelo WRF-MeteoGalicia . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
1.2. El modelo WAsP . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
2. Metodolog´ıa 8
2.1. Datos de WRF-MeteoGalicia . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
2.2. Dominios WAsP . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
2.3. Generalizacion del viento ´ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
2.4. Configuracion del modelo WAsP ´ . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
3. Resultados 12
3.1. Niveles verticales . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
3.2. Velocidad media anual . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
3.3. Densidad de potencia . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
3.4. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . . . . . . 14
A. Anexo I: Recurso eolico costero en Galicia ´ 15
A.1. Ribadeo . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
A.1.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 16
A.1.2. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . 19
A.2. Burela . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
A.2.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 20
A.2.2. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . 23
A.3. Viveiro . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
A.3.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 24
A.3.2. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . 27
A.4. Ortigueira . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28
A.4.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 28
A.4.2. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . 31
A.5. Valdovino˜ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32
A.5.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 32
A.5.2. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . 35
A.6. A Coruna - Ferrol ˜ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36
A.6.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 36
A.6.2. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . 39
A.7. Arteixo . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 40
A.7.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 40
3 / 82
A.7.2. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . 43
A.8. Laxe . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 44
A.8.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 44
A.8.2. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . 47
A.9. Mux´ıa . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 48
A.9.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 48
A.9.2. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . 51
A.10.Fisterra . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 52
A.10.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 52
A.10.2. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . 55
A.11.Muros - Noia . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 56
A.11.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 56
A.11.2. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . 59
A.12.Arousa . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 60
A.12.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 60
A.12.2. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . 63
A.13.Vigo - Pontevedra . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 64
A.13.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 64
A.13.2. Produccion media anual de energ ´ ´ıa . . . . . . . . . . . . . . . . . . . . . 67
A.14.A Guarda . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 68
A.14.1. Velocidad media anual y densidad de potencia . . . . . . . . . . . . . . . . 68
A.15.Base de datos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 71
B. Anexo II: Verificacion´ 72
B.1. Resultados de la validacion . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 74
B.1.1. Ribadeo . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 74
B.1.2. Burela . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 74
B.1.3. Viveiro . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 75
B.1.4. Ortigueira . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 75
B.1.5. Valdovino˜ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76
B.1.6. A Coruna - Ferrol ˜ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 77
B.1.7. Arteixo . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 77
B.1.8. Laxe . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 78
B.1.9. Muxia . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 78
B.1.10. Muros - Noia . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 79
B.1.11. Arousa . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 79
B.1.12. Vigo - Pontevedra . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 80
B.1.13. A Guarda . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 82
4 / 82
Resumen
El presente informe muestra la metodolog´ıa utilizada para la creacion de un atlas de viento ´
para la costa gallega mediante el uso de la base de datos de simulaciones de prediccion meteo- ´
rologica creada por MeteoGalicia en el periodo 2008-2013. Esta serie de 6 a ´ nos de datos, con ˜
4km de resolucion de malla, nos permite alimentar la herramienta de software WAsP (Wind Atlas ´
Analysis and Application Program), con la que se evalua el recurso e ´ olico a una resoluci ´ on de ´
100 metros. Esto permite obtener los mapas de velocidad media anual, de densidad de potencia
media anual y de los parametros de la distribuci ´ on de Weibull del m ´ odulo de la velocidad del ´
viento. Ademas, se calcula un mapa de la producci ´ on anual de energ ´ ´ıa teniendo en cuenta las
caracter´ısticas de un modelo de aerogenerador ‘Offshore’ generico. ´
El proyecto pretende facilitar el acceso publico a los resultados calculados con lo que se han ´
transformado las salidas del programa WAsP a formato netCDF, compatible con el servidor tipo
Thredds de MeteoGalicia.
1. Introduccion´
El presente proyecto “Creacion de un Atlas de viento costero de alta resoluci ´ on para Galicia com- ´
binando WAsP y salidas del modelo WRF de MeteoGalicia” se basa en el uso de las series de 6
anos completos de datos generados por la ejecuci ˜ on diaria del modelo WRF ( ´ Weather Research and
Forecasting model) en MeteoGalicia. El periodo comprende desde el ano 2008 hasta el a ˜ no 2013. ˜
Estos datos de viento son procesados por la herramienta de software WAsP. Se trata de una de las
herramientas mas utilizadas en la caracterizaci ´ on del viento clim ´ atico en el sector de la energ ´ ´ıa
eolica y calcula los forzamientos en el viento local (monta ´ nas, rugosidad y obst ˜ aculos) para poder ´
estimar un “viento generalizado”, vease el apartado 1.2 . Este viento se utiliza para realizar una ´
extrapolacion horizontal y vertical, a muy altas resoluciones, en las regiones con caracter ´ ´ısticas
climaticas similares. ´
Para la estimacion del viento costero clim ´ atico a una resoluci ´ on espacial de 100 metros, se con- ´
sideran los puntos de malla del modelo WRF como estaciones “virtuales” que nos proporcionan
las series de datos climaticos necesarias. El modelo de meso-escala calcula a 4km de resoluci ´ on el ´
estado de la atmosfera definido por el modelo global GFS. Esto nos permite obtener una descripci ´ on´
de la situacion atmosf ´ erica m ´ as acorde a las caracter ´ ´ısticas locales.
Cabe destacar que para la realizacion de un estudio del clima del viento local, o de si un emplaza- ´
miento es el idoneo para la construcci ´ on de un parque e ´ olico, se requiere como m ´ ´ınimo de un ano˜
de datos ademas de m ´ etodos estad ´ ´ısticos que nos permitan estimar el comportamiento del viento
a largo plazo. Dichos metodos se conocen como LTC ( ´ Long Term Correction) y se aplican para
corregir datos de viento de corto plazo en base a observaciones cercanas con registros de viento de
largo plazo. En nuestro caso se disponen de 6 anos de datos completos y se consideran suficientes ˜
atendiendo a la variabilidad climatica de la regi ´ on en estudio. Se ha optado as ´ ´ı por el uso de las
series originales de datos sin aplicarle la correccion clim ´ atica. ´
A continuacion se describen m ´ as en detalle las caracter ´ ´ısticas de ambos modelos.
1.1. El modelo WRF-MeteoGalicia
La integracion de las ecuaciones matem ´ aticas de la f ´ ´ısica de la atmosfera y la din ´ amica de fluidos a ´
modelos de escala global permite conocer la circulacion general de la atm ´ osfera. Debido a su natu- ´
raleza global y al alto coste de computo, la discretizacion espacial en el modelo GFS est ´ a limitada a ´
una resolucion m ´ axima de hasta 0.5 grados (60 km en latitudes medias). El modelo GFS es muy ´ util ´
para una caracterizacion de la atm ´ osfera a escala sin ´ optica y proporciona valores representativos en ´
regiones con una orograf´ıa homogenea. ´
El modelo regional WRF es una herramienta de “downscaling” dinamico de los modelos globales. ´
Los principios f´ısicos empleados son los mismos que para los modelos globales pero son aplica5 / 82
dos a regiones reducidas. Esto permite resolver nueva fenomenolog´ıa de escala sobre la orograf´ıa
compleja de Galicia.
El modelo proporciona predicciones de las variables atmosfericas en 3 dimensiones e incluye vari- ´
ables como la temperatura, viento, precipitacion, humedad, presi ´ on, flujos t ´ ermicos y flujos de ra- ´
diacion entre otros. La configuraci ´ on del modelo consta de tres dominios de simulaci ´ on anidados ´
con resoluciones de malla de 36km, 12km y 4km.
Figura 1: Dominios d01, d02 y d03 de WRF-MeteoGalicia
La cobertura espacial de los dominios de simulacion se muestra en la Figura ´ 1.
CUMULUS Kain-Fritsch scheme
MICROPHYSICS WSM Single-Moment 6-class scheme
PLANETARY BOUNDARY LAYER Yonsei University scheme (YSU)
LAND SURFACE PHYSICS 5-layer thermal diffusion
LONG AND SHORT WAVE RADIATION Dudhia scheme
Cuadro 1: Configuracion f ´ ´ısica del modelo WRF-MeteoGalicia.
La configuracion f ´ ´ısica del modelo se resume en el Cuadro 1 y es la misma en todos los dominios
de simulacion. ´
El servicio de prediccion realiza 2 ejecuciones diarias del modelo, inicializadas con las salidas del ´
GFS de las 00Z y 12Z, y se obtienen hasta 96 horas simuladas. Con los resultados de las simulaciones MeteoGalicia realiza tareas continuadas de validacion del modelo con los datos obtenidos de ´
su amplia red de estaciones meteorologicas que garantiza la calidad de sus datos. ´
En el estudio “Assessment of Wind Pattern Accuracy from the QuikSCAT Satellite and the WRF
Model along the Galician Coast” (Sousa et al. 2013), se compara el viento obtenido por el modelo
WRF de MeteoGalicia con datos de satelite y de boyas. En el estudio se concluye que los datos del ´
modelo WRF constituyen una herramienta consistente para obtener el viento representativo de la
costa de Galicia ya que muestran buenos resultados al compararlos con observaciones.
6 / 82
1.2. El modelo WAsP
El programa WAsP ha sido disenado para analizar una serie de datos de m ˜ odulo y direcci ´ on del ´
viento y crear un atlas de recurso eolico mediante el uso de modelos de apantallamiento, rugosidad ´
y de topograf´ıa. Para ello se construye una serie de datos de “viento limpio”, o viento generalizado,
eliminando de la serie los efectos causados por la rugosidad de terreno, la presencia de obstacu- ´
los cercanos o la topograf´ıa local. Las condiciones espec´ıficas de la region se resumen en unas ´
“condiciones estandar”, es decir, se calculan los par ´ ametros Weibull ( ´ A y k) para 4 condiciones de
rugosidad del terreno (0.000 m, 0.030 m, 0.100 m, 0.400 m, 1.500 m), 5 alturas de referencia (10
m, 25 m, 50 m, 100 m, 200 m) y 12 sectores azimutales.
A partir del viento generalizado se calcula el viento climatico en cualquier punto de una regi ´ on´
definida realizando el calculo inverso al utilizado para eliminar las condiciones locales. La energ ´ ´ıa
total se puede calcular a partir del viento mediante la curva de potencia de un aerogenerador tipo.
Figura 2: Esquema WAsP
La Figura 2 muestra el esquema de funcionamiento del modelo WAsP que se resume en dos procesos principales:
1. Generalizacion de la serie de datos de viento. ´
2. Extrapolacion horizontal y vertical del viento generalizado a las condiciones de rugosidad, ´
topograf´ıa y obstaculos locales.
7 / 82
Para obtener los mejores resultados se deben tener en cuenta los siguientes puntos:
El punto de referencia, de donde se obtienen los datos de viento, y el area de estudio son ´
tratados con el mismo regimen de vientos. ´
Los datos del punto de referencia deben ser fiables, es decir, debe haber suficiente concordancia con la realidad.
La serie de datos de viento debe ser representativa del clima de la region. ´
2. Metodolog´ıa
Se combina el modelo WRF con el modelo WAsP sumandose as ´ ´ı las ventajas del uso de un modelo
meteorologico de meso-escala con la capacidad de predicci ´ on a micro-escala. El resultado de dicha ´
combinacion mejorar ´ a notablemente los resultados de una simple interpolaci ´ on del modelo WRF. ´
En el siguiente esquema se resume el proceso completo (Figura 3)
Figura 3: Esquema del proceso
2.1. Datos de WRF-MeteoGalicia
Se han seleccionado series de datos de 6 anos completos, 2008-2013, correspondientes a las 24h ˜
simuladas a partir de las 03:00 horas del inicio de la ejecucion del modelos WRF-MeteoGalicia de ´
las 00Z.
00:00 03:00 06:00
GFS 00
09:00 12:00 15:00 18:00 21:00 00:00
24H WRF-MeteoGalicia
03:00
Se inicia la serie de 24 horas a las 03:00 horas, y no a las 00:00 horas, debido a que el modelo WRF
8 / 82
necesita un m´ınimo de pasos de tiempo para generar su propio clima, evitando as´ı los efectos de
baja resolucion de la inicializaci ´ on. ´
2.2. Dominios WAsP
Se han definido 14 regiones, o dominios de WAsP, mostrados en la Figura 3 (derecha). Cada una
de las regiones se corresponde con una climatolog´ıa del viento similar, esto es, que puede ser representada por una serie de viento generalizado comun. Las regiones se han adaptado a la forma ´
de la costa para que contengan, de forma completa, las regiones delimitadas por los accidentes
geograficos costeros m ´ as importantes. ´
2.3. Generalizacion del viento ´
El modelo WAsP define una distribucion de viento generalizada para cada una de las 14 regiones ´
acotadas a lo largo del litoral utilizando 6 anos de datos de una de las celdas del modelo WRF ˜
contenida en cada region. ´
Cada dominio es “alimentado” por una unica serie de observaciones, en este caso, datos de una ´
unica celda del modelo ubicada en el interior de la regi ´ on. Para la selecci ´ on del punto de observa- ´
ciones se han tenido en cuenta los siguientes factores:
Los datos del modelo son calculados a una resolucion de 4km, as ´ ´ı que tanto la topograf´ıa
como la rugosidad son distintas a las predeterminadas por WAsP.
El modelo WAsP por defecto esta dise ´ nado para asimilar observaciones de estaciones meteo- ˜
rologicas, afectadas por entornos reales. ´
Los efectos de topograf´ıa y rugosidad se minimizan en el mar cuanto mayor sea la distancia
a la costa.
Los efectos de la rugosidad se reducen a mayores alturas de toma de datos.
En el proyecto se han seleccionado puntos de malla ubicados en el mar, hacia el centro del dominio
y separados significativamente de la costa, y el nivel vertical del modelo WRF se corresponde con
la altura sobre el nivel del mar de 101 metros. Se ha utilizado esta altura con el objetivo de que los
efectos de la topograf´ıa y la rugosidad sean m´ınimos, y con ello, se minimizen los errores debidos
a las diferencias en la resolucion entre WAsP y WRF. ´
En la Figura 4 se muestra la distribucion de los datos mediante la rosa de los vientos, el histograma ´
y el ajuste Weibull. En la Figura 5, la rosa de los vientos muestra la ubicacion de la celda del modelo ´
WRF-MeteoGalicia seleccionada como punto de observaciones para el dominio llamado “Arteixo”
en WAsP y las frecuencias del viento en dicha ubicacion. ´
9 / 82
Figura 4: Rosa de los vientos, histograma y ajuste Weibull en Arteixo
Figura 5: Punto de toma de datos del modelo WRF-MeteoGalicia
2.4. Configuracion del modelo WAsP ´
Los elementos necesarios para la realizar las simulaciones con WAsP se enumeran a continuacion´
(Figura 6:
1. El paquete de programas que acompanan a WAsP nos facilita la transformaci ˜ on de la base ´
de datos de topograf´ıa del SRTM en mapas con curvas de nivel cada 10 metros con el que se
genera el mapa de topograf´ıa y la rugosidad para cada region. ´
10 / 82
2. Se debe definir una distribucion de viento clim ´ atico generalizado que, como ya hemos co- ´
mentado, se extrae de las series de WRF-MeteoGalicia.
3. Se configuran 7 casos de simulacion para cada regi ´ on, uno por cada altura a la que queremos ´
calcular el recurso eolico. ´
4. Se incluye un modelo de aerogenerador ’offshore’ tipo para que el modelo calcule la energ´ıa
producida al ano en cada punto del dominio. El aerogenerador tiene una altura de buje de ˜
80m por lo que la produccion se calcula para el dominio definido a dicha altura. ´
La Figura 6 muestra un esquema de los componentes que constituyen un ’workspace’ en WAsP.
Figura 6: Esquema de configuracion WAsP ´
El modelo de aerogenerador seleccionado para el calculo de la AEP , “Annual Energy Production”,
es el ’V112-3.0 MW 50Hz’ de Vestas. Se trata de un aerogenerador de 3.0MW de potencia con una
altura de buje de 80 metros disenado para Offshore (Figura ˜ 7).
Figura 7: Curva de potencia y coeficiente de traccion para el aerogenerador ’V112-3.0 MW 50Hz’ ´
11 / 82
3. Resultados
A continuacion se muestra como ejemplo los resultados obtenidos en la velocidad de viento media ´
anual de la region de Arteixo, Figura ´ 8 para los niveles verticales. Ademas, se incluye una repre- ´
sentacion de las variables de velocidad de viento medio anual, densidad de potencia y de producci ´ on´
de energ´ıa media anual para el conjunto de las regiones en estudio al nivel de 80m (Figuras 9 - 11).
En el Anexo I se puede ver un amplio conjunto de representaciones de los resultados para todas
areas. En el anexo II se muestra una validaci ´ on de los resultados comparando los datos estimados ´
por el modelo WasP con las estaciones de MeteoGalicia.
3.1. Niveles verticales
Figura 8: Niveles verticales en la region de Arteixo ´
12 / 82
3.2. Velocidad media anual
Figura 9: Velocidad media del viento a 80m de altura
3.3. Densidad de potencia
Figura 10: Densidad de potencia a 80m de altura
13 / 82
3.4. Produccion media anual de energ ´ ´ıa
Figura 11: Produccion de energ ´ ´ıa anual a 80m de altura para el aerogenerador ‘V112-3.0 MW 50Hz’
de Vestas
14 / 82
A. Anexo I: Recurso eolico costero en Galicia ´
Las representaciones graficas recogidas en este documento para cada una de las regiones costeras ´
son las siguientes (Figura 12):
Velocidad media anual a 10m, 20m, 40m, 60m, 80m, 100m y 120m.
Densidad de potencia media anual a 10m, 20m, 40m, 60m, 80m, 100m y 120m.
Produccion de energ ´ ´ıa media anual a 80m.
En la ultima secci ´ on se detallan las caracter ´ ´ısticas del conjunto de archivos en formato netCDF que
contienen todas las variables calculadas en el proyecto.
Figura 12: Regiones costeras
15 / 82
A.1. Ribadeo
A.1.1. Velocidad media anual y densidad de potencia
Altura = 10m
16 / 82
Altura = 20m
Altura = 40m
Altura = 60m
17 / 82
Altura = 80m
Altura = 100m
Altura = 120m
18 / 82
A.1.2. Produccion media anual de energ ´ ´ıa
19 / 82
A.2. Burela
A.2.1. Velocidad media anual y densidad de potencia
Altura = 10m
20 / 82
Altura = 20m
Altura = 40m
Altura = 60m
21 / 82
Altura = 80m
Altura = 100m
Altura = 120m
22 / 82
A.2.2. Produccion media anual de energ ´ ´ıa
23 / 82
A.3. Viveiro
A.3.1. Velocidad media anual y densidad de potencia
Altura = 10m
24 / 82
Altura = 20m
Altura = 40m
Altura = 60m
25 / 82
Altura = 80m
Altura = 100m
Altura = 120m
26 / 82
A.3.2. Produccion media anual de energ ´ ´ıa
27 / 82
A.4. Ortigueira
A.4.1. Velocidad media anual y densidad de potencia
Altura = 10m
28 / 82
Altura = 20m
Altura = 40m
Altura = 60m
29 / 82
Altura = 80m
Altura = 100m
Altura = 120m
30 / 82
A.4.2. Produccion media anual de energ ´ ´ıa
31 / 82
A.5. Valdovino˜
A.5.1. Velocidad media anual y densidad de potencia
Altura = 10m
32 / 82
Altura = 20m
Altura = 40m
Altura = 60m
33 / 82
Altura = 80m
Altura = 100m
Altura = 120m
34 / 82
A.5.2. Produccion media anual de energ ´ ´ıa
35 / 82
A.6. A Coruna - Ferrol ˜
A.6.1. Velocidad media anual y densidad de potencia
Altura = 10m
36 / 82
Altura = 20m
Altura = 40m
Altura = 60m
37 / 82
Altura = 80m
Altura = 100m
Altura = 120m
38 / 82
A.6.2. Produccion media anual de energ ´ ´ıa
39 / 82
A.7. Arteixo
A.7.1. Velocidad media anual y densidad de potencia
Altura = 10m
40 / 82
Altura = 20m
Altura = 40m
Altura = 60m
41 / 82
Altura = 80m
Altura = 100m
Altura = 120m
42 / 82
A.7.2. Produccion media anual de energ ´ ´ıa
43 / 82
A.8. Laxe
A.8.1. Velocidad media anual y densidad de potencia
Altura = 10m
44 / 82
Altura = 20m
Altura = 40m
Altura = 60m
45 / 82
Altura = 80m
Altura = 100m
Altura = 120m
46 / 82
A.8.2. Produccion media anual de energ ´ ´ıa
47 / 82
A.9. Mux´ıa
A.9.1. Velocidad media anual y densidad de potencia
Altura = 10m
48 / 82
Altura = 20m
Altura = 40m
Altura = 60m
49 / 82
Altura = 80m
Altura = 100m
Altura = 120m
50 / 82
A.9.2. Produccion media anual de energ ´ ´ıa
51 / 82
A.10. Fisterra
A.10.1. Velocidad media anual y densidad de potencia
Altura = 10m
52 / 82
Altura = 20m
Altura = 40m
Altura = 60m
53 / 82
Altura = 80m
Altura = 100m
Altura = 120m
54 / 82
A.10.2. Produccion media anual de energ ´ ´ıa
55 / 82
A.11. Muros - Noia
A.11.1. Velocidad media anual y densidad de potencia
Altura = 10m
56 / 82
Altura = 20m
Altura = 40m
Altura = 60m
57 / 82
Altura = 80m
Altura = 100m
Altura = 120m
58 / 82
A.11.2. Produccion media anual de energ ´ ´ıa
59 / 82
A.12. Arousa
A.12.1. Velocidad media anual y densidad de potencia
Altura = 10m
60 / 82
Altura = 20m
Altura = 40m
Altura = 60m
61 / 82
Altura = 80m
Altura = 100m
Altura = 120m
62 / 82
A.12.2. Produccion media anual de energ ´ ´ıa
63 / 82
A.13. Vigo - Pontevedra
A.13.1. Velocidad media anual y densidad de potencia
Altura = 10m
64 / 82
Altura = 20m
Altura = 40m
Altura = 60m
65 / 82
Altura = 80m
Altura = 100m
Altura = 120m
66 / 82
A.13.2. Produccion media anual de energ ´ ´ıa
67 / 82
A.14. A Guarda
A.14.1. Velocidad media anual y densidad de potencia
Altura = 10m
68 / 82
Altura = 20m
Altura = 40m
Altura = 60m
69 / 82
Altura = 80m
Altura = 100m
Altura = 120m
70 / 82
A.15. Base de datos
Los parametros calculados se presentan en 98 archivos en formato netCDF, uno por cada regi ´ on y ´
altura. El contenido de los archivos netCDF se detalla los siguientes cuadros:
a. Parametros generales: ´
Formato netCDF
Convencion´ CF-1.5
Proyeccion´ UTM-29N
b. Variables:
Variable long name Unidades Descripcion´
x “x coordenate of projection” m Coordenada x en UTM-29N
y “y coordenate of projection” m Coordenada y en UTM-29N
lat “latitude” deg Latitud
lon “longitude” deg Longitud
mws “Mean Wind Speed” ms−1 Velocidad media anual del viento
powdens “Power Density” W m−2 Densidad de potencia
weibA “Weibull A parameter” ms−1 Parametro de escala de Weibull ´
weibK “Weibull K parameter” − Parametro de forma de Weibull ´
aep “Anual Energy Production” W h Produccion media anual de energ ´ ´ıa a 80m
topo “Elevation” m Topograf´ıa
wdfs* “Wind Direction Frequency” − Frecuencia de la direccion del viento por sector ´
Se adjuntan 12 variables “wdfs*”, una por cada sector de direccion (0, 30, 60, 90, 120, 150, 180, ´
210, 240, 270, 300 y 330 grados)
71 / 82
B. Anexo II: Verificacion´
Para la validacion de los resultados obtenidos con el modelo WAsP se utilizaron los datos meteo- ´
rologicos registrados por la red de estaciones meteorol ´ ogicas de MeteoGalicia. ´
Una vez seleccionadas las estaciones disponibles dentro de cada unos de los dominios de calculo, ´
se extrajeron las series temporales tanto para el viento medio como para la direccion del mismo y ´
se comparo con los resultados obtenidos del modelo WasP. ´
En la siguiente tabla se puede observar el listado de estaciones para cada uno de los dominios de
calculo. ´
DOMINIO ESTACION´
VIVEIRO Borreiros (Viveiro)
VIVEIRO Burela (Burela)
VIGOPON Vigo-Campus (Vigo)
VIGOPON Illas C´ıes (Vigo)
VIGOPON Ons (Bueu)
VIGOPON Sanxenxo (Sanxenxo)
VALDOVINHO Punta Candieira (Cedeira)
VALDOVINHO Aldea Nova (Naron) ´
RIBADEO Pedro Mur´ıas (Ribadeo)
ORTIGUEIRA Carino (Cari ˜ no) ˜
MUXIA Camarinas (Camari ˜ nas) ˜
MUXIA A Gandara (Vimianzo) ´
MUROSNOIA Lira (Carnota)
LAXE Malpica (Malpica)
CORUNHA Coruna Dique (Coru ˜ na) ˜
CORUNHA CIS Ferrol (Ferrol)
BURELA Burela (Burela)
ARTEIXO Punta Langosteira (Arteixo)
AROUSA Corrubedo (Ribeira)
AROUSA Coron (Vilanova de Arousa) ´
AROUSA Salvora (Ribeira) ´
AROUSA A Lanzada (O Grove)
AGUARDA Monte Aloia (Tui)
AGUARDA Castro Vicaludo (Oia)
Para cada estacion se extrajo primeramente la serie temporal del viento medio y con ella se hizo el ´
calculo de ese viento medio para todo el periodo de estudio. Ese valor se compar ´ o para cada una ´
de las estaciones seleccionadas con el valor obtenido por el modelo WasP en el punto de malla mas´
proximo a las coordenadas de esa estaci ´ on, siempre teniendo en cuenta que ese punto estuviese en ´
tierra, no en el mar.
En la siguiente figura se puede ver el resultado para cada estacion donde en el eje de ordenadas ´
estan los valores observados y en el eje de abscisas los valores obtenidos por el modelo (Figura ´ 13).
72 / 82
Figura 13: Viento medio Observaciones vs. Modelo
Seguidamente, con los datos de la direccion del viento se representaron las rosas de vientos para ´
cada estacion con la frecuencia de aparici ´ on de cada direcci ´ on estimada por el WasP y los registrados ´
en las estaciones. Se dividio en 12 sectores: ´
SECTOR 1 >345o & <=15o
SECTOR 2 >15o & <=45o
SECTOR 3 >45o & <=75o
SECTOR 4 >75o & <=105o
SECTOR 5 >105o & <=135o
SECTOR 6 >135o & <=165o
SECTOR 7 >165o & <=195o
SECTOR 8 >195o & <=225o
SECTOR 9 >225o & <=255o
SECTOR 10 >255o & <=285o
SECTOR 11 >285o & <=315o
SECTOR 12 >315o & <=345o
Como se puede observar en las graficas, los resultados del WasP tienden a sobreestimar el viento ´
medio en algunas estaciones, aunque no por mas de 2m/s en los peores casos. Mientras, para la ´
direccion del viento, salvo en localidades puntuales, la direcci ´ on observada suele estar en sinton ´ ´ıa
con los datos obtenidos por el modelo.
73 / 82
B.1. Resultados de la validacion
B.1.1. Ribadeo
B.1.2. Burela
74 / 82
B.1.3. Viveiro
B.1.4. Ortigueira
75 / 82
B.1.5. Valdovino˜
76 / 82
B.1.6. A Coruna - Ferrol ˜
B.1.7. Arteixo
77 / 82
B.1.8. Laxe
B.1.9. Muxia
78 / 82
B.1.10. Muros - Noia
B.1.11. Arousa
79 / 82
B.1.12. Vigo - Pontevedra
80 / 82
81 / 82
B.1.13. A Guarda
82 / 82