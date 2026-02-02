# ⚡ Green Energy Sentinel
**Sistema de Inteligencia Geoespacial para la Gestión de Riesgos en Parques Eólicos**

Este proyecto utiliza Big Data y Machine Learning para analizar la interacción entre la infraestructura eólica de Galicia y los fenómenos meteorológicos extremos (rayos), detectando ineficiencias de ubicación y proponiendo nuevos emplazamientos seguros.

## 🚀 Resultados Clave (2023)
*   **105,554 Rayos Analizados:** Base de datos real de MeteoGalicia (Enero-Diciembre 2023).
*   **Hipótesis de Atracción Confirmada:** Las turbinas eólicas mostraron una densidad de impactos **32% superior** a su entorno inmediato (Efecto Punta).
*   **Identificación de Riesgos:** Se detectaron **27 Clusters de Alto Riesgo** y 5 infraestructuras críticas con >50 impactos directos anuales.

## 🛠️ Arquitectura Técnica
El proyecto se estructura en 3 módulos de Python:

### 1. `analyze_risk.py` (The Detective)
*   **Función:** Descarga histórica masiva y Clustering.
*   **Algoritmo:** DBSCAN (Density-Based Spatial Clustering).
*   **Output:** `maps/mapa_riesgo_anual_2023.html` (Heatmap de zonas peligrosas).

### 2. `final_audit.py` (The Auditor)
*   **Función:** Validación estadística y cruce con infraestructura.
*   **Datos:** Vectorial de OpenStreetMap (Turbinas) + Rayos 2023.
*   **Output:** `reports/informe_final_cientifico.csv` (Ranking de parques "malditos").

### 3. `propose_sites.py` (The Architect)
*   **Función:** Algoritmo de prospección de "Zonas de Oro".
*   **Lógica:** (Viento Alto + Acceso Red) - (Riesgo Rayos) = Ubicación Óptima.
*   **Output:** `maps/propuesta_ubicaciones_seguras.html`.

## 📂 Estructura de Archivos
```
Green_enegry_sentinel/
├── maps/                   # Visualizaciones Interactivas (HTML)
├── reports/                # Auditorías y CSVs de valor
├── src/                    # Código Fuente Python
└── README.md               # Documentación
```

## 🌍 Visualización
Para ver los resultados, abra los archivos `.html` de la carpeta `maps/` en su navegador web.
