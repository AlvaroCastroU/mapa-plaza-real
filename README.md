# Mapa temático: accesibilidad y confort peatonal en Plaza Real

Mapa colaborativo y dinámico de **Plaza Real (Alajuela, Costa Rica)** construido con datos capturados en campo con **OSMTracker for Android**.
Curso **Sistemas de Información Geográfica** – III Evaluación.

- 🗺️ **Mapa público:** https://alvarocastrou.github.io/mapa-plaza-real/
- 📘 **Guía de mapeo para público general:** [GUIA_MAPEO.md](GUIA_MAPEO.md)
- 🔘 **Disposición de botones:** https://github.com/AlvaroCastroU/osmtracker-android-layouts/tree/master/layouts/accesibilidad_plaza_real

## Cómo funciona

```
OSMTracker (celular) ──«Subir a GitHub»──▶ .zip en la raíz del repo (GPX + fotos .jpg + audios .3gpp)
                                              │  push
                                              ▼
                          GitHub Actions (.github/workflows/procesar.yml)
                                              │  python procesar_gpx.py
                                              ▼
            trazas/  ← zips archivados        datos/puntos.geojson  (botones + multimedia)
            datos/gpx, datos/media            datos/trazas.geojson  (recorridos por estado de acera)
                                              datos/resumen.json    (estadísticas)
                                              │  commit + despliegue
                                              ▼
                         GitHub Pages ──▶ index.html (Leaflet) lee los GeoJSON
```

## Contenido del repositorio

| Archivo | Para qué sirve |
|---|---|
| `index.html` | Mapa (Leaflet): clúster de marcadores, mapa de calor, recorridos coloreados por estado de la acera, popups con foto/audio/nota, filtros por categoría y **filtro temporal** (oculta trazas antiguas + botón «Mostrar todas»). |
| `procesar_gpx.py` | Lee los `.zip`/`.gpx`, extrae puntos, trazas y multimedia; optimiza fotos y convierte audios `.3gpp` a `.mp3`; genera los GeoJSON. |
| `.github/workflows/procesar.yml` | Ejecuta el script en cada `push`, guarda los datos y publica el sitio en GitHub Pages. |
| `config/categorias.json` | Categorías de botones (grupo, color y símbolo en el mapa). |
| `GUIA_MAPEO.md` | Guía de mapeo para público general. |

## Puesta en marcha (una sola vez)

1. Crear el repositorio **público** `mapa-plaza-real` y subir estos archivos.
2. **Settings → Pages → Build and deployment → Source: «GitHub Actions»**.
3. **Settings → Actions → General → Workflow permissions: «Read and write permissions»**.
4. **Settings → Collaborators**: agregar a cada integrante del grupo (para que pueda subir trazas desde OSMTracker).
5. Pestaña **Actions** → «Procesar trazas y publicar mapa» → **Run workflow** (primera publicación).

Probar localmente: `pip install -r requirements.txt && python procesar_gpx.py && python -m http.server`, luego abrir http://localhost:8000.
