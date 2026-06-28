# Referencia del firmware de H.J. Berndt (Pocket SI4735 Dual Core Decoder)

> Resumen técnico **en nuestras palabras**, extraído de la web/registro de desarrollo de
> H.J. Berndt (`www.hjberndt.de/dvb/pocketSI4735DualCoreDecoder.html`, 36 páginas, junio 2026)
> y de sus archivos reales recuperados del backup. Sirve como **guía maestra para replicar**
> sus funciones en el fork XE1E. El firmware de Berndt es **binario, sin fuente** → todo se
> reimplementa desde cero. PDF y archivos en `Documents/ats-mini-berndt-backup/`.

## 0. Visión general
- **Firmware V4** para la minirradio SI4732 + ESP32-S3 (pantalla 320×170), enfocado en **SWL** (onda corta).
- Parte del **firmware oficial de marzo 2025** (NO el ats-mini de G8PTN), recompilado y muy ampliado.
- Filosofía: **mostrar la máxima información simultánea** en pantalla; sin WiFi/Internet (todo por serial/USB).
- Probado en **ATS-Mini V1/V3**. No hay V4 oficial ni esquema → todo sobre hardware V1 abierto.
- HW detectado: ESP32-S3 QFN56, **8 MB PSRAM**, 40 MHz, **VID 0x303A / PID 0x1001**, ~2 MB de firmware.

## 1. Modificaciones de hardware

### 1a. Audio para RTTY/CW (sin micrófono — funciona en stock con un puente)
- El ESP32 necesita una entrada analógica desde la salida del amplificador para decodificar audio.
- **Puente de cable: pin 8 del CI amplificador → GPIO11 (IO11) del ESP32-S3.**
- A partir de **volumen ≈ 30** se detectan tonos ~1 kHz. (RTTY/CW son "directos", solo este puente.)

### 1b. Micrófono I2S INMP441 (para SSTV/WeFAX — requiere añadir hardware)
- Módulo **INMP441** (~1,50 €, Ø14 mm) cabe detrás del altavoz en la V1. Mic + ADC; **I2S digital hasta 48 kHz / 14 bits**.
- **Tabla de cableado (clave):**

  | ESP32-S3 | INMP441 |
  |----------|---------|
  | 3.3 V    | VDD |
  | GND      | GND |
  | GND      | L/R |
  | GPIO12   | SCK |
  | GPIO13   | WS  |
  | GPIO14   | SD  |

- ⚠️ Las líneas digitales **GPIO12/13/14 sin blindar causan interferencias** en la radio cuando el decoder I2S está activo. El I2S se inicializa la 1ª vez que se usa un decoder I2S y **queda activo hasta apagar**; si no se usa, no interfiere. Blindar/modificar el cableado lo reduce.

## 2. Arquitectura dual-core
- **Núcleo 1:** radio, pantalla, interacción (encoder). **Núcleo 2:** detector de tonos por software (**algoritmo de Goertzel**), búsqueda EiBi en 2º plano, etc. El núcleo 2 estaba ocioso en el firmware original.

## 3. Menú "11+11" (un clic abre el menú; orden cronológico)
**Originales (1-11):** 01 Volumen · 02 Paso · 03 Modo · 04 BFO · 05 Ancho de banda · 06 AGC/Att · 07 SoftMute · 08 Seek Up (exp.) · 09 Seek Down (exp.) · 10 Banda · 11 Mute.
**Añadidos (12-22):** 12 Retroiluminación · 13 Temporizador (sleep) · 14 Batería · 15 AutoMute · 16 Clásico/Info · 17 Store (guardar) · 18 Recall (recuperar) · 19 **TUNE** · 20 **Decoder** · 21 **Station** · 22 **ETM**.

### 3a. Submenús notables
- **14 Batería:** voltaje / % / off; también temperatura del núcleo ESP en Info.
- **15 AutoMute:** Off · On · POP/TP · POP · News · TP (tráfico) · SNR · RSSI. Usa el valor de **SoftMute** como umbral. Silencia por tipo de programa RDS, SNR o RSSI.
- **16 Clásico/Info:** alterna entre UI original ("Clásico": 1 clic=banda, 2 clics=menú) e UI informativa.
- **19 TUNE:** TUNE FREQ (clásico) · TUNE MEM (recorre memorias, muestra "M05") · TUNE ETM (recorre lista ETM, "E05") · TUNE SEEK · TUNE LOCK (bloquea el encoder, pulsar ~1 s) · mantener pulsado = **NumPad**.
- **20 Decoder:** Off · Tono/BL · RTTY (50bd) · RTTY45 · RTTY75 · Morse · Replay · (V4 I2S) Martin1 · Martin2 · WeFAX.
- **21 Station:** tabla interna de emisoras (escaneos propios del autor); rectángulos amarillos en el dial. Apóstrofe inicial = repetidor; apóstrofe final = esporádica. Exportable/importable.
- **22 ETM:** ver §6.

## 4. Backlight como "selector de funciones oculto" (magic numbers)
El brillo (0–99) **además** activa funciones de desarrollo. Valores **impares** apagan el backlight tras 1 min (ahorro). Muchas se combinan con **Long-Press "Freeze"**.

| Valor | Función |
|-------|---------|
| 20, 50, 90 | Signal tracer (graficador de señal) |
| 30 | ETM continuo en AM (escanea hasta hallar portadora) |
| 32, 33 | Waterfall AM/SSB y FM (pone BFO=0 en SSB) |
| 34, 35 | ETM-Scanner de preescucha (rango escala) FM/AM/USB/LSB |
| 36, 37 | ETM memory-scan FM/AM/USB/LSB |
| 38, 39 | Mini Radio Band Monitor (scanner 5 h) |
| 44 + Freeze | conmuta **Slow/Fast** (ahorro energía) |
| 46, 47 | fuerzan **mono** en FM |
| 48 / 49 | silencia canal estéreo derecho / izquierdo |
| 50 + Freeze | guarda **hardcopy** (bitmap pantalla) a USB |
| 51 + Freeze | exporta `memo.txt` (memorias) |
| 52 + Freeze | exporta `stations.txt` (estaciones firmware) |
| 53 + Freeze | exporta `etm.txt` (lista ETM) |
| 54 + Freeze | exporta `setting.txt`-style settings (línea 9997) |
| 55 + Freeze | activa/muestra `playlist.txt` |
| 60 + Freeze | conmuta **Tint** (vía frecuencia AM 150–30000) |
| 61 + Freeze | conmuta **Inverse** |
| 62 + Freeze | conmuta **Escala de grises / Color** |
| 63 + Freeze | conmuta **TUNE SEEK** on/off |
| 64 + Freeze | cambia frecuencia del detector **1000 ↔ 880 Hz** |
| 66 + Freeze | exporta `logfile.txt` (mensajes RTTY) |
| 66 (FM-ETM) | escaneo ETM-FM desde **65 MHz** |
| 66 / 68 / 70 | terminal Replay del ringbuffer (fuente peq/media/grande) |
| 68 + Freeze | conmuta el "ruido" del detector (umbral avanzado) |

> **Nota:** con `SoftMute=0`, los export 51-55 **muestran el archivo en el terminal** en vez de guardarlo (SoftMute viene en 1 por defecto).

## 5. Decodificadores

### 5a. RTTY / CW (audio por puente GPIO11, sin mic)
- **RTTY** (50 bd), **RTTY45** (45 bd, radioaficionado), **RTTY75** (75 bd). **Morse/CW** con detección de **WPM** (17–32; 7 para NDB).
- **Tono/BL:** el backlight aumenta su brillo al detectar el tono → ayuda a centrar el BFO.
- Frecuencia del detector **1000 Hz** (o 880 Hz = A'). En USB, el **tono más bajo de RTTY debe quedar en 1000 Hz** (±20). Método con/ sin analizador de espectro documentado (app **Spectroid**).
- Modo **LOCKED** (clic en decoder): congela la pantalla (no actualiza batería/hora/señal) salvo el texto que se desplaza, para no perder decodificación.
- **Instant Tuning** (en LOCKED, girar = ±10 Hz para centrar el tono), **Instant Level** (long-press = ajusta volumen sin salir, barra de color arriba), **Advanced Noise Level** (backlight 68, subir umbral de ruido; suele requerir +10 de volumen, p.ej. 37→47).
- **Replay / ringbuffer:** graba en RAM mensajes (RTTY entre `ZCZC`…`NNNN`, Morse en LOCKED, resultados EiBi en AM, texto RDS en FM). Reproducible en terminal (backlight 66/68/70) o exportable a `logfile.txt` / serial `log`.

### 5b. SSTV (color, requiere INMP441)
- **Martin 1** y **Martin 2** (los más usados en Europa); otros modos = colores alterados. Imágenes **320×256 px**; tras 170 líneas hace scroll para las últimas 85.
- Recepción típica **14230 kHz USB**. Opción de pasar a escala de grises si hay demasiado color.
- Long-press = salir del decoder a pantalla completa.

### 5c. WeFAX (mapas meteo grises, requiere INMP441)
- **120 RPM**, escala de grises, pantalla completa. Estaciones: **Pinneberg (DWD) 3853.200 kHz USB** (acceso por ETM), también **Northwood (UK)**.
- 3 estados: **búsqueda** (crujido 300 Hz) → **fase** (sync) → **decodificación**. Se alternan pulsando el encoder; **pulsar 2× seguidas** arranca la imagen; girar mueve el punto de inicio.
- Dato: **tono 2250 Hz = blanco** (lo emite el DWD inactivo).

## 6. ETM (Easy Tuning Mode)
- Escaneo rápido de la banda buscando emisoras con señal/SNR suficiente; resultados en memoria **volátil** (orden ascendente). Marcas amarillas en el dial (brillo = calidad).
- **ETM-FM:** 87–108 MHz, paso 100 kHz, ~30 s (desde 65 MHz con backlight 66).
- **ETM-AM:** en banda ALL empieza en 120m (**2300 kHz**), solo bandas de radiodifusión, ~40 s con paso 5.
- **ETM-SSB:** usa siempre paso AM; BFO debería ser 0.
- **ETM-Scanner** (backlight 34/35): scan silencioso del rango de escala (400 kHz / 4 MHz), sube volumen al hallar señal.
- **ETM memory-scan** (backlight 36/37): escanea las memorias guardadas (muestra "S05"); desde MEM01 escanea todas.
- **Mini Radio Band Monitor** (backlight 38/39): scanner de **5 h** en AM/SSB; gráfico X=tiempo (tramos 15 min, 300 px=300 min), Y=±200 kHz alrededor de la frecuencia (vigila **400 kHz**); marcas amarillas (señal) / azules (fuerte).

## 7. Indicadores de UI (el "ojo mágico" y señal)
- **SIGNAL : RSSI/SNR** (curva verde = RSSI, amarilla = SNR).
- **Stereo-Blend:** "STEREO" solo ≥95% separación; por debajo muestra "nn% STEREO" más pequeño; rojo = piloto presente.
- **AFC / sintonía fina:** **flechas** indican dirección de desviación; **punto central se ilumina como LED** cuando está bien sintonizado y fuerte. Inspirado en receptores de los 70/80 (ojo mágico).
- **Signal tracer:** registra señal/calidad durante 1 min (curva); con RDS la línea vertical es el segundero. Solo con backlight 20/50/90 y sin decoder activo.
- **Save-status:** los **dos puntos** tras "SIGNAL" indican estado guardado; si faltan, hay cambios sin guardar (guardado retardado para reducir escrituras).
- **Reloj grande en FM:** con el mando inactivo y fecha mostrada, los 7-segmentos muestran la **hora** en vez de la frecuencia.

## 8. Waterfall (cascada)
- Representa intensidad sobre el rango de escala (**4 MHz** FM, paso AM en AM/SSB) escaneando continuamente. Útil en Sporadic-E. Backlight 32/33 + ETM. Girar=frecuencia, clic=modo escucha, long-press-soltar=salir. En SSB pone BFO=0.

## 9. EiBi (lista de frecuencias de onda corta)
- Archivo de **texto `eibi.txt`** (de `eibispace.de`, ~10.000 entradas) en el USB-Flash; búsqueda automática al cambiar de frecuencia (lineal, en **Core 2**). Muestra nombre/ubicación del transmisor sobre la frecuencia.
- **`README.txt`** (de eibispace) da las coordenadas de los transmisores → **distancia en km** (naranja si no hay sync horario). Requiere ambos archivos.
- **`home <lat>, <lon>`** en `setting.txt` define la ubicación propia (ej. `home 51.198455, 6.879572`).
- **EiBi-Fast:** cachea los últimos resultados para mostrar sin retardo.
- **Logger:** el ringbuffer también guarda aciertos EiBi (AM) y textos RDS (FM) → `logfile.txt`.

## 10. NumPad (entrada numérica) — TUNE, mantener pulsado >350 ms
- Teclado 3×4 (7-8-9 / 4-5-6 / 1-2-3 / 0-.-↵); el encoder mueve el foco, clic introduce, **Enter** abajo-derecha confirma, **long-press borra** el último carácter.
- Entrada de **frecuencia** (el punto solo en FM; no considera BFO de SSB) y de **fecha/hora** manual (ej. `11.55`, `21.02.1989`) cuando no hay RDS.

## 11. Ahorro de energía Slow/Fast
- 3 estados de reloj del ESP32-S3: **Normal** (arranque) · **Slow** (reloj reducido) · **Fast** (vuelve a normal). Backlight 44 + Freeze conmuta.
- Medición: **~62% más de autonomía** en Slow. `slow 1` en `setting.txt` arranca en ahorro (⚠️ los **decoders solo funcionan en estado Normal**, sin `slow 1`).

## 12. IBP (NCDXF/IARU Beacon Project)
- **18 balizas** mundiales, ciclo de **180 s**. Cada baliza emite su indicativo + portadoras 100/10/1/0,1 W, secuencialmente por **14100, 18110, 21150, 24930, 28200 kHz** (USB), **10 s por frecuencia**, **50 s por baliza**. El firmware calcula la baliza activa por hora UTC + banda y la muestra sobre la frecuencia.

## 13. Modos de pantalla
- **greyscale / inverse / rotate:** archivos vacíos con esos nombres en el USB-Flash (rotate = 180°, encoder a la izquierda).
- **Tint:** colorea el modo grises con un valor de 16 bits ajustado por la frecuencia AM (150–30000), ~60.000 tonos. Solo con grises activo.

## 14. Protocolo serial (9600 bd; sin handshake RTS/DTR — resetea el ESP32-S3)
En FM envía RadioText filtrado; en AM envía RSSI⇥SNR (sin pedirlo). ⚠️ Un **cable de datos USB-C** conectado ralentiza el firmware → usar cable de **solo carga**.

| Comando | Acción |
|---------|--------|
| `1` | Exporta **hardcopy BMP** (320×170×2, ~163.254 bytes, con cabecera BMP) |
| `3` | Conmuta salida serial automática on/off (archivo `noserial` también la suprime) |
| `4` | Exporta memorias MEM (CSV: `mem,freq,band,mode,bfo`) |
| `5` | Exporta lista de estaciones AM |
| `9999` | Importa hasta 64 memorias (1ª línea `9999`) |
| `9998` | Importa lista de estaciones (1ª línea `9998`) |
| `erase` / `del` | Borra listas de usuario, reactiva las internas |
| `user` | Nº de estaciones de usuario activas |
| `log` | Vuelca el ringbuffer (RTTY/EiBi/RDS) |
| `copy <archivo>` | Copia datos serial a un archivo del USB-Flash |
| `type <archivo>` | Muestra un archivo del USB-Flash en el terminal |
| `remove <archivo>` | Borra un archivo del USB-Flash |
| `rename <a> <b>` | Renombra (ej. `rename eibi.txt eibi.tmp` para desactivar EiBi) |

> El fork XE1E usa el comando **`C`** (mayúscula) para screenshot por serial; Berndt usa `1`. Conceptos distintos.

## 15. Modo USB-Flash-Drive (TinyUSB MSC) — mantener encoder pulsado al encender
- La radio se monta como **unidad USB** (⚠️ flash ~>100.000 escrituras; **expulsar tras escribir**). Comunicación móvil por **USB-C OTG**.
- No es un stick con controlador propio; si falla, **formatear desde el PC** (conserva el firmware) o recuperar con WebSerial ESPTool (`targetDRIVE.bin` @ 0x0).

### Archivos en la unidad (formatos)
| Archivo | 1ª línea | Contenido |
|---------|----------|-----------|
| `mem.txt` / `memo.txt` | `9999` | Memorias: `mem,freq,band,mode,bfo` (ej. `18,03741,19,1,1800`) |
| `user.txt` / `stations.txt` | `9998` | Estaciones AM: `freq,nombre` (ej. `6125,Ankara`) |
| `setting.txt` (import) / `settings.txt` (export) | `9997` | Ajustes: `battery 1`, `tint 55000`, `inverse 0`, `greyscale 1`, `home <lat,lon>`, `slow 1`, `seek 0`… |
| `etm.txt` | — | Lista ETM (`idx hora freq nivel`) |
| `eibi.txt` + `README.txt` | — | Lista EiBi + coordenadas de transmisores |
| `playlist.txt` | — | Reproducción: `HH:MM memoria duración` (ej. `09:00 21 60`), chequeo 1×/min |
| `logfile.txt` | — | Log RTTY/EiBi/RDS |
| `greyscale`/`inverse`/`rotate`/`noserial` | (vacíos) | Flags de arranque |
| `hardcopy.bmp` / `capture.bmp` | — | Captura de pantalla |

> **band/mode** en los CSV: `mode` 0=FM 1=LSB 2=USB 3=AM; `band` 19=ALL, etc. (índices internos de Berndt, NO los del fork).

## 16. Flasheo / backup (referencia de Berndt)
- Firmware = **.bin en un Zip (~397k)**, se flashea a **offset 0x0** con WebSerial ESP-Tool (PC) o apps Android (**Serial USB Terminal** + **ESP32_Flash**, chip ESP32-S3, Bootloader Auto OFF).
- **Backup original:** Flash Download Tool / ESPTool, **Read Flash 0x0 size 0x200000** (2 MB).
- Reset/download sin botones: conmutar **DTR + RTS** desde un terminal.

---

## Mapeo a nuestro roadmap (qué replicar)
Ver `ROADMAP.md`. Prioridades visibles de bajo riesgo: numpad, AFC/ojo mágico, longpress-Freeze, stereo-blend, slow/fast, time entry, display modes. Track de datos: EiBi con sitio+distancia (necesita formato texto + README), listas ETM/playlist, logger. Track infra: **migrar a FFat + TinyUSB MSC** (el "drive"). Decoders: RTTY/CW directos (puente GPIO11); SSTV/WeFAX requieren INMP441 (tabla §1b).
