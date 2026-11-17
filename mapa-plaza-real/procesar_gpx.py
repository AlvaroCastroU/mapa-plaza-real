#!/usr/bin/env python3
"""
procesar_gpx.py
================
Procesa las trazas subidas desde OSMTracker al repositorio y genera los datos
que consume el mapa (index.html).

OSMTracker sube a la RAÍZ del repositorio un archivo .zip por traza que contiene:
  - el archivo .gpx (recorrido + waypoints de los botones)
  - las fotografías (.jpg) y audios (.3gpp) tomados durante el recorrido
También se aceptan archivos .gpx sueltos.

Pasos que realiza el script:
  1. Mueve los .zip / .gpx nuevos de la raíz a la carpeta trazas/ y anota quién los subió
     (autor del commit).
  2. Extrae cada traza: copia el GPX a datos/gpx/ y prepara la multimedia para la web
     (fotos reducidas y orientadas en datos/media/, audios convertidos a .mp3).
  3. Lee todos los GPX y genera:
       datos/puntos.geojson  -> un punto por botón presionado (con fotos/audios/notas asociadas)
       datos/trazas.geojson  -> las líneas del recorrido, partidas en tramos según el estado
                                de la acera ("Acera buena" / "Acera dañada")
       datos/resumen.json    -> estadísticas y lista de trazas
Se puede ejecutar cuantas veces se quiera: siempre reconstruye los GeoJSON desde cero.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from math import radians, sin, cos, asin, sqrt
from pathlib import Path
from urllib.parse import unquote_plus

RAIZ = Path(__file__).resolve().parent
DIR_TRAZAS = RAIZ / "trazas"
DIR_DATOS = RAIZ / "datos"
DIR_GPX = DIR_DATOS / "gpx"
DIR_MEDIA = DIR_DATOS / "media"
ARCHIVO_APORTES = DIR_DATOS / "aportes.json"
ARCHIVO_CATEGORIAS = RAIZ / "config" / "categorias.json"

EXT_FOTO = {".jpg", ".jpeg", ".png"}
EXT_AUDIO = {".3gpp", ".3gp", ".m4a", ".mp3", ".amr", ".ogg", ".wav"}
SEGUNDOS_ASOCIAR_MEDIA = 90   # una foto/audio/nota se asocia al botón presionado hasta 90 s antes o después
ANCHO_MAX_FOTO = 1600

NS = {"g": "http://www.topografix.com/GPX/1/1"}


# ----------------------------------------------------------------------------- utilidades
def normalizar(texto: str) -> str:
    """minúsculas y sin tildes, para comparar etiquetas de botones."""
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip().lower()


def id_seguro(nombre: str) -> str:
    base = normalizar(nombre)
    base = re.sub(r"[^a-z0-9._-]+", "_", base).strip("_")
    return base or "traza"


def leer_fecha(texto):
    if not texto:
        return None
    texto = texto.strip().replace("Z", "+00:00")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(texto, fmt).astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ") if dt else None


def distancia_m(lat1, lon1, lat2, lon2):
    r = 6371000
    p1, p2 = radians(lat1), radians(lat2)
    dp, dl = p2 - p1, radians(lon2 - lon1)
    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * r * asin(sqrt(a))


def autor_git(ruta: Path) -> str:
    """Nombre de quien subió el archivo (autor del commit que lo agregó)."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%an", "--", str(ruta.relative_to(RAIZ))],
            cwd=RAIZ, capture_output=True, text=True, timeout=30,
        ).stdout.strip().splitlines()
        return out[-1] if out else "Desconocido"
    except Exception:
        return "Desconocido"


def cargar_json(ruta: Path, por_defecto):
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return por_defecto


def guardar_json(ruta: Path, datos):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")


# ----------------------------------------------------------------------------- paso 1
def recoger_archivos_nuevos(aportes: dict):
    """Mueve los .zip/.gpx de la raíz (donde los deja OSMTracker) a trazas/."""
    DIR_TRAZAS.mkdir(exist_ok=True)
    nuevos = []
    for f in sorted(RAIZ.iterdir()):
        if f.is_file() and f.suffix.lower() in (".zip", ".gpx"):
            autor = autor_git(f)
            destino = DIR_TRAZAS / f.name
            n = 1
            while destino.exists():
                destino = DIR_TRAZAS / f"{f.stem}_{n}{f.suffix}"
                n += 1
            shutil.move(str(f), destino)
            aportes[destino.name] = autor
            nuevos.append(destino.name)
    # trazas que se subieron directamente a trazas/ (por la web de GitHub, por ejemplo)
    for f in DIR_TRAZAS.iterdir():
        if f.name not in aportes and f.suffix.lower() in (".zip", ".gpx"):
            aportes[f.name] = autor_git(f)
    return nuevos


# ----------------------------------------------------------------------------- paso 2
def preparar_foto(origen: Path, destino: Path):
    try:
        from PIL import Image, ImageOps
        with Image.open(origen) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((ANCHO_MAX_FOTO, ANCHO_MAX_FOTO))
            im.save(destino.with_suffix(".jpg"), "JPEG", quality=80, optimize=True)
        return destino.with_suffix(".jpg").name
    except Exception as e:  # si Pillow no está o la imagen falla, se copia tal cual
        print(f"   ! no se pudo optimizar {origen.name}: {e}")
        shutil.copy2(origen, destino)
        return destino.name


def preparar_audio(origen: Path, destino: Path):
    """Los navegadores no reproducen .3gpp: se convierte a .mp3 con ffmpeg."""
    if origen.suffix.lower() in (".mp3", ".ogg", ".wav", ".m4a"):
        shutil.copy2(origen, destino)
        return destino.name
    mp3 = destino.with_suffix(".mp3")
    if shutil.which("ffmpeg"):
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(origen),
                            "-codec:a", "libmp3lame", "-q:a", "5", str(mp3)])
        if r.returncode == 0:
            return mp3.name
    print(f"   ! no se pudo convertir {origen.name} (¿falta ffmpeg?); se copia el original")
    shutil.copy2(origen, destino)
    return destino.name


def extraer_traza(archivo: Path):
    """Devuelve (id_traza, ruta_gpx, {nombre_original_media: nombre_web})."""
    tid = id_seguro(archivo.stem)
    dir_media = DIR_MEDIA / tid
    gpx_destino = DIR_GPX / f"{tid}.gpx"
    mapa_media_json = dir_media / "_media.json"
    DIR_GPX.mkdir(parents=True, exist_ok=True)

    if archivo.suffix.lower() == ".gpx":
        shutil.copy2(archivo, gpx_destino)
        return tid, gpx_destino, {}

    # .zip ya procesado anteriormente -> no se vuelve a convertir la multimedia
    if gpx_destino.exists() and mapa_media_json.exists():
        return tid, gpx_destino, cargar_json(mapa_media_json, {})

    print(f" + extrayendo {archivo.name}")
    medios = {}
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(archivo) as z:
        for info in z.infolist():
            nombre = Path(info.filename).name
            if info.is_dir() or not nombre or nombre.startswith("."):
                continue  # se ignoran carpetas y rutas: se usa solo el nombre del archivo
            ruta = Path(tmp) / nombre
            with z.open(info) as src, open(ruta, "wb") as dst:
                shutil.copyfileobj(src, dst)
        archivos = list(Path(tmp).iterdir())
        gpxs = [f for f in archivos if f.suffix.lower() == ".gpx"]
        if not gpxs:
            print(f"   ! {archivo.name} no contiene ningún .gpx; se ignora")
            return tid, None, {}
        shutil.copy2(gpxs[0], gpx_destino)
        dir_media.mkdir(parents=True, exist_ok=True)
        for f in archivos:
            ext = f.suffix.lower()
            if ext in EXT_FOTO:
                medios[f.name] = preparar_foto(f, dir_media / f.name)
            elif ext in EXT_AUDIO:
                medios[f.name] = preparar_audio(f, dir_media / f.name)
    guardar_json(mapa_media_json, medios)
    return tid, gpx_destino, medios


# ----------------------------------------------------------------------------- paso 3
def texto(el, ruta):
    x = el.find(ruta, NS)
    if x is None:  # GPX sin namespace
        x = el.find(ruta.replace("g:", ""))
    return x.text.strip() if x is not None and x.text else None


def todos(el, ruta):
    r = el.findall(ruta, NS)
    return r if r else el.findall(ruta.replace("g:", ""))


def leer_gpx(ruta: Path):
    raiz = ET.parse(ruta).getroot()
    waypoints = []
    for w in todos(raiz, "g:wpt"):
        enlace = None
        for l in list(todos(w, "g:link")):
            enlace = unquote_plus(l.get("href", "")) or texto(l, "g:text")
        waypoints.append({
            "lat": float(w.get("lat")), "lon": float(w.get("lon")),
            "nombre": texto(w, "g:name") or "",
            "fecha": leer_fecha(texto(w, "g:time")),
            "enlace": enlace,
        })
    segmentos = []
    nombre_traza = None
    for trk in todos(raiz, "g:trk"):
        nombre_traza = nombre_traza or texto(trk, "g:name")
        for seg in todos(trk, "g:trkseg"):
            pts = [(float(p.get("lat")), float(p.get("lon")), leer_fecha(texto(p, "g:time")))
                   for p in todos(seg, "g:trkpt")]
            if len(pts) >= 2:
                segmentos.append(pts)
    return nombre_traza, waypoints, segmentos


def clasificar(nombre, categorias_norm):
    return categorias_norm.get(normalizar(nombre))


def tramos_por_estado(puntos, eventos):
    """Parte un segmento de traza según los botones 'Acera buena' / 'Acera dañada'.
    eventos: lista ordenada de (fecha, estado)."""
    if not eventos or puntos[0][2] is None:
        return [("sin_clasificar", puntos)]
    tramos, actual, estado = [], [], "sin_clasificar"
    i_ev = 0
    for p in puntos:
        nuevo = estado
        while i_ev < len(eventos) and p[2] and eventos[i_ev][0] <= p[2]:
            nuevo = eventos[i_ev][1]
            i_ev += 1
        if nuevo != estado and actual:
            actual.append(p)  # el tramo termina donde empieza el siguiente (sin huecos)
            if len(actual) >= 2:
                tramos.append((estado, actual))
            actual = []
        estado = nuevo
        actual.append(p)
    if len(actual) >= 2:
        tramos.append((estado, actual))
    return tramos


def procesar():
    categorias = cargar_json(ARCHIVO_CATEGORIAS, {})
    cat_norm = {normalizar(k): k for k in categorias}
    aportes = cargar_json(ARCHIVO_APORTES, {})

    nuevos = recoger_archivos_nuevos(aportes)
    print(f"Archivos nuevos: {nuevos or 'ninguno'}")

    puntos_geo, trazas_geo, resumen_trazas = [], [], []
    conteo_cat = {}

    for archivo in sorted(DIR_TRAZAS.glob("*")):
        if archivo.suffix.lower() not in (".zip", ".gpx"):
            continue
        try:
            tid, gpx, medios = extraer_traza(archivo)
            if gpx is None:
                continue
            nombre_traza, wpts, segmentos = leer_gpx(gpx)
        except Exception as e:
            print(f" ! error con {archivo.name}: {e}")
            continue

        autor = aportes.get(archivo.name, "Desconocido")
        fechas = [p[2] for s in segmentos for p in s if p[2]] + [w["fecha"] for w in wpts if w["fecha"]]
        inicio = min(fechas) if fechas else None
        fin = max(fechas) if fechas else None

        # --- separar botones (etiquetas) de multimedia y notas
        etiquetas, multimedia = [], []
        for w in wpts:
            cat = clasificar(w["nombre"], cat_norm)
            if w["enlace"]:
                ext = Path(w["enlace"]).suffix.lower()
                web = medios.get(Path(w["enlace"]).name)
                url = f"datos/media/{tid}/{web}" if web else None
                tipo = "foto" if ext in EXT_FOTO else "audio" if ext in EXT_AUDIO else "otro"
                multimedia.append({**w, "tipo": tipo, "url": url})
            elif cat:
                etiquetas.append({**w, "categoria": cat})
            elif w["nombre"]:
                multimedia.append({**w, "tipo": "nota", "url": None})

        # --- asociar cada foto/audio/nota al botón más cercano en el tiempo
        for w in etiquetas:
            w.update(fotos=[], audios=[], notas=[])
        sueltos = []
        for m in multimedia:
            mejor, dif_min = None, None
            for w in etiquetas:
                if m["fecha"] and w["fecha"]:
                    dif = abs((m["fecha"] - w["fecha"]).total_seconds())
                    if dif <= SEGUNDOS_ASOCIAR_MEDIA and (dif_min is None or dif < dif_min):
                        mejor, dif_min = w, dif
            if mejor is not None and m["tipo"] in ("foto", "audio") and m["url"]:
                mejor["fotos" if m["tipo"] == "foto" else "audios"].append(m["url"])
            elif mejor is not None and m["tipo"] == "nota":
                mejor["notas"].append(m["nombre"])
            else:
                sueltos.append(m)

        def feature(w, categoria, fotos, audios, notas):
            info = categorias.get(categoria, {})
            conteo_cat[categoria] = conteo_cat.get(categoria, 0) + 1
            return {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [round(w["lon"], 7), round(w["lat"], 7)]},
                "properties": {
                    "categoria": categoria,
                    "grupo": info.get("grupo", "Otros"),
                    "color": info.get("color", "#57606a"),
                    "fecha": iso(w["fecha"]) or iso(inicio),
                    "traza": tid, "autor": autor,
                    "fotos": fotos, "audios": audios, "notas": notas,
                },
            }

        for w in etiquetas:
            puntos_geo.append(feature(w, w["categoria"], w["fotos"], w["audios"], w["notas"]))
        for m in sueltos:
            cat = {"foto": "Fotografía", "audio": "Audio", "nota": "Nota"}.get(m["tipo"], "Otro")
            puntos_geo.append(feature(
                m, cat,
                [m["url"]] if m["tipo"] == "foto" and m["url"] else [],
                [m["url"]] if m["tipo"] == "audio" and m["url"] else [],
                [m["nombre"]] if m["tipo"] == "nota" else []))

        # --- líneas de la traza, coloreadas por estado de la acera
        eventos = sorted(
            [(w["fecha"], "buena" if normalizar(w["categoria"]) == "acera buena" else "danada")
             for w in etiquetas if w["fecha"] and normalizar(w["categoria"]) in ("acera buena", "acera danada")],
            key=lambda e: e[0])
        largo_total = 0.0
        for seg in segmentos:
            for estado, pts in tramos_por_estado(seg, eventos):
                largo = sum(distancia_m(a[0], a[1], b[0], b[1]) for a, b in zip(pts, pts[1:]))
                largo_total += largo
                trazas_geo.append({
                    "type": "Feature",
                    "geometry": {"type": "LineString",
                                 "coordinates": [[round(p[1], 7), round(p[0], 7)] for p in pts]},
                    "properties": {"traza": tid, "nombre": nombre_traza or tid, "estado": estado,
                                   "fecha": iso(inicio), "autor": autor, "largo_m": round(largo, 1)},
                })

        resumen_trazas.append({
            "id": tid, "archivo": archivo.name, "nombre": nombre_traza or tid, "autor": autor,
            "inicio": iso(inicio), "fin": iso(fin), "largo_m": round(largo_total, 1),
            "puntos": len(etiquetas) + len(sueltos),
            "fotos": sum(1 for m in multimedia if m["tipo"] == "foto"),
            "audios": sum(1 for m in multimedia if m["tipo"] == "audio"),
            "gpx": f"datos/gpx/{tid}.gpx",
        })
        print(f" - {archivo.name}: {len(etiquetas)} botones, {len(multimedia)} multimedia/notas, "
              f"{len(segmentos)} segmentos, autor={autor}")

    guardar_json(DIR_DATOS / "puntos.geojson", {"type": "FeatureCollection", "features": puntos_geo})
    guardar_json(DIR_DATOS / "trazas.geojson", {"type": "FeatureCollection", "features": trazas_geo})
    guardar_json(ARCHIVO_APORTES, aportes)
    guardar_json(DIR_DATOS / "resumen.json", {
        "actualizado": iso(datetime.now(timezone.utc)),
        "total_trazas": len(resumen_trazas),
        "total_puntos": len(puntos_geo),
        "total_fotos": sum(t["fotos"] for t in resumen_trazas),
        "total_audios": sum(t["audios"] for t in resumen_trazas),
        "personas": sorted({t["autor"] for t in resumen_trazas}),
        "por_categoria": dict(sorted(conteo_cat.items(), key=lambda x: -x[1])),
        "trazas": sorted(resumen_trazas, key=lambda t: t["inicio"] or "", reverse=True),
    })
    print(f"Listo: {len(resumen_trazas)} trazas, {len(puntos_geo)} puntos.")


if __name__ == "__main__":
    os.chdir(RAIZ)
    procesar()
    sys.exit(0)
