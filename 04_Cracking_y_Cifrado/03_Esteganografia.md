---
title: Esteganografía
pubDate: 2026-05-22
---

## ¿Qué es la Esteganografía?
La **esteganografía** es el arte de ocultar información dentro de otros archivos (portadores) de manera que su existencia sea imperceptible. A diferencia de la criptografía, donde el mensaje es ilegible pero visible, en la esteganografía el mensaje parece no existir.

### Propósito en Ciberseguridad
1.  **Exfiltración de Datos:** Sacar información de una red sin levantar sospechas (ej: dentro de una imagen de logo).
2.  **CTFs y Forense:** Encontrar pistas o flags ocultas en archivos aparentemente normales.
3.  **Marcas de Agua:** Identificar la autoría de un archivo de forma invisible.

---

## 🛠️ Herramientas por Formato

| Formato de Archivo | Herramienta Recomendada | Propósito |
| :--- | :--- | :--- |
| **JPG, BMP, WAV** | `steghide` | Ocultar/Extraer con contraseña. |
| **PNG, BMP** | `zsteg` | Detectar datos en bits LSB. |
| **Cualquiera** | `binwalk` | Encontrar archivos embebidos dentro de otros. |
| **Cualquiera** | `exiftool` | Analizar metadatos del archivo. |
| **Audio (WAV, MP3)** | `Sonic Visualizer` | Ver datos en el espectrograma. |

---

## 🚀 Metodología de Análisis

### 1. Metadatos (Exiftool)
Lo primero es revisar la información descriptiva del archivo (autor, GPS, comentarios).
```bash
exiftool imagen.jpg
```

### 2. Archivos Ocultos con Steghide
Muy común en archivos JPG y de audio. Suele requerir una contraseña.
```bash
# Ver información (sin extraer)
steghide info archivo.jpg

# Extraer el contenido oculto
steghide extract -sf archivo.jpg
```

### 3. Búsqueda de Archivos Embebidos (Binwalk)
Detecta si un archivo contiene a otro (ej: un `.zip` al final de un `.png`).
```bash
# Listar contenido
binwalk archivo.png

# Extraer todo automáticamente
binwalk -e archivo.png
```

### 4. Análisis de Bits LSB (Zsteg)
Específico para archivos PNG y BMP. Analiza los bits menos significativos.
```bash
# Escaneo automático de todas las combinaciones
zsteg -a imagen.png
```

### 5. Análisis Visual de Capas (Stegsolve)
Herramienta visual para ver planos de bits que el ojo humano no detecta.
1.  `java -jar stegsolve.jar`
2.  Abrir la imagen.
3.  Cambiar los planos con las flechas laterales.

---

## 🎹 Esteganografía en Audio
Si tienes un archivo de audio que suena extraño, abre **Sonic Visualizer**.
1.  Importa el archivo.
2.  **Layer ➔ Add Spectrogram**.
3.  Busca texto o códigos QR dibujados en las frecuencias.

> **Tip:** Si nada de esto funciona, abre el archivo con un editor hexadecimal (`hexeditor` o `xxd`) y busca cadenas de texto legibles al principio o al final de la cabecera del archivo.
