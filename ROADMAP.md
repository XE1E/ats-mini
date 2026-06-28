# ATS Mini — Roadmap de mejoras (fork XE1E)

Fork de [esp32-si4732/ats-mini](https://github.com/esp32-si4732/ats-mini) (MIT, forks bienvenidos).

- **Hardware objetivo:** ATS Mini **V4B** (ESP32-S3 + SI4732).
- **Base de partida:** firmware ats-mini v2.35.
- **Objetivo:** añadir/mejorar funciones (NO priorizar decoders) y **optimizar el receptor**.
- **Referencia de funciones:** firmware "Pocket SI4735 Dual Core Decoder" de HJ Berndt
  (http://www.hjberndt.de/dvb/pocketSI4735DualCoreDecoder.html) — solo binario, sin fuente;
  sirve como referencia de comportamiento, todo se reimplementa desde cero.
  - **Arquitectura dual-core de Berndt:** un núcleo del ESP32-S3 gestiona radio + DSP, el otro
    el motor de decodificación + UI → tuning fluido y decodificación estable en HF saturada.
  - La web oficial es HTTP con certificado autofirmado (no fetchable por herramienta); detalles
    confirmados vía releases documentados en DXR Electronics Bits (vu3dxr.in).
- **Nota decoders:** SSTV/WEFAX requieren añadir un micrófono I2S **INMP441**; RTTY/CW son directos.
  No es la prioridad actual.
- **Alcance legal:** objetivo = paridad de **funciones/comportamiento** reimplementadas desde cero
  (base MIT). NO redistribuir ni desensamblar el binario de Berndt.

### Información pendiente de recopilar
- [ ] Capturas/fotos/vídeo de **cada pantalla y menú** de Berndt (insumo #1 para clonar UI exacta).
      Los posts de Facebook del grupo están tras login; hay que descargar las imágenes a mano.
- [ ] Versión exacta del binario de Berndt y hardware destino (V3 vs V4B).
- [ ] HW V4B: ¿PSRAM **octal (ospi)** o **quad (qspi)**? ¿Lleva/llevará **INMP441**?
- [ ] Parámetros medibles: anchos RTTY, umbrales CW, tamaño/rango del waterfall, campos EiBi mostrados.

---

## 1. Ya presente en el base v2.35 (lo obtenemos "gratis")

- EiBi (búsqueda + base de datos), Seek (normal + EiBi), Scan con gráfico RSSI/SNR
- 99 memorias, frecuencias con nombre (FT8/SSTV/CB)
- RDS completo: PS, RadioText, PI, PTY, Clock-Time + sync NTP
- Fast-tune (aceleración encoder), softmute, AGC, AVC, squelch, calibración por banda/modo
- 8 temas, 2 layouts (Default / S-Meter grande), S-meter + SNR, indicador estéreo, icono de guardado
- WiFi (5 modos + web UI), BLE (ad-hoc/HID), control serial (incluye captura de pantalla)
- Almacenamiento NVS (Preferences) + LittleFS (EiBi)

## 2. Nuevo de HJ Berndt — por dificultad

### 🟢 Fáciles (UI/display, bajo riesgo)
- [ ] **numpad** — entrada de frecuencia por teclado numérico
- [~] **afc** — indicador de centrado AFC (IMPLEMENTADO, pendiente verificación visual).
      Usa `rx.getCurrentAfcRailIndicator()` (bit AFCRL); etiqueta "AFC" arriba-derecha
      (x319,y30): color acento = centrado, color warn = descentrado. Solo FM/AM con señal.
- [ ] **band** — marcas de borde de banda en AM
- [ ] **longpress** — long-press "Freeze" + menú por pulsación larga
- [ ] **greyscale / tint** — Greyscale / Inverse / Rotate / Tint de pantalla
- [ ] **zeit** — reloj grande en FM
- [ ] **blend** — indicador de stereo-blend / mono forzado
- [ ] **instantlevel** — nivel de señal instantáneo

### 🟡 Medias (lógica/datos)
- [ ] **waterfall** — cascada/espectro extendido de **400 kHz** como analizador (mini-SDR);
      picos nítidos, distinción ruido vs. portadora. (Pieza visual estrella de Berndt.)
- [ ] **etm / etl / etlmem** — escáner ETM + listas de memoria (auto-construir listas)
- [ ] **playlist** — reproducción secuencial de estaciones
- [ ] **transmitter** — EiBi: ubicación del transmisor en texto claro + **coordenadas geográficas**
      + **cálculo de distancia en km** al transmisor
- [ ] **ibp** — soporte IBP (faros de propagación)
- [ ] **time** — entrada manual de hora/fecha con numpad (sin depender de RDS), band-monitor;
      útil para tests de recepción a mediodía / pruebas de campo
- [ ] **noise / plotter** — medición avanzada de ruido + plotter de señal
- [ ] **logger** — logger de búsquedas EiBi/RDS
- [ ] **sporadic** — protocolo Sporadic-E, exportar listas como texto
- [ ] **powersave** — modo **Slow/Fast** que ajusta el clock del ESP32-S3 manteniendo el control
      de radio → ~**62% más autonomía** en modo económico (medición de Berndt)

### 🔴 Difícil (infraestructura)
- [ ] **drive** — modo USB Flash Drive (**confirmado TinyUSB MSC** sobre FFat en el binario de
      Berndt: strings `TinyUSB MSC`/`USB_MSC` + rastros Windows en su FFat) → exportar
      `logfile.txt`, `settings.txt`, `hardcopy.bmp`. NOTA: Berndt **no** tiene protocolo serial
      "ad hoc"; saca datos/capturas montando el dispositivo como **unidad USB**. Su screenshot
      es la función `Hardcopy` → `/hardcopy.bmp`. (El fork usa serial `C` en su lugar.)

### ⏸️ Decoders (aplazados — requieren INMP441 para SSTV/WEFAX)
- [ ] **rtty / cw** (directos) — variantes **RTTY45, RTTY75** y modo **TONE/BL**; decodificación
      interna con texto en pantalla, sin PC externa
- [ ] sstv · [ ] wefax · [ ] replay (ring buffer RTTY)

## 3. Track: optimización del receptor
- [ ] Auditar defaults y lógica de AGC / softmute / AVC / ancho de banda
- [ ] Revisar SSB patch y calibración
- [ ] Calidad de audio

---

## 4. Hallazgos del análisis del binario de Berndt (2026-06-27)

Backup completo de su flash (8 MB) volcado por esptool y analizado por strings.
SHA256 (prefijo): `c232743c8c05fc…`. Compilado con **ESP-IDF v4.4.5 / core ESP32 2.0.x**
(el fork apunta a 3.3.10 — divergencia de toolchain). ID: `----- DUALCORE ----`, `www.hjberndt.de`.

### Confirmado (presente en el binario)
- **Decoders:** `Morse`, `RTTY`, `RTTY45`, `RTTY75`, `Tone/BL`, `SSTV`, `WeFAX` — todos.
  Strings: `1000 HZ TONE RTTY DECODER`, `WeFAX DECODER`.
- **Audio digital:** el **driver I2S de IDF está enlazado** (+ referencias ADC/PDM) → Berndt
  captura audio por I2S. Refuerza que el path de audio existe en hardware stock (RTTY/CW firmware-only).
  ⚠️ Falta confirmar *físicamente* si el I2S del SI4732 va al ESP32 en la V4B, o si usa INMP441.
- **EiBi = fichero de texto `/eibi.txt`** (NO binario): líneas tipo `5195,DRA5 cw/ry`, `7165,SSTV`,
  ` 1332,Galati` (sitio del transmisor) → habilita ubicación + distancia (` km`) + tag de modo.
- **Filesystem = FATFS (FFat), NO LittleFS.** Strings `/ffat`, `/format_ffat`, `Format Success/Failed`.
  Esto es la base del **modo USB MSC ("drive")** y de la config en texto plano.
- **UI confirmada:** `AFC on/off`, `ETM` / `ETM-List`, `Slow`/`Fast` (powersave), `GreyScale`,
  `Inverse`, `TINT`, `/rotate`, `/freeze`, `Force Mono`, `%2d%% STEREO` (stereo-blend),
  `Memory-0..99`, `Band-0..21`, `%02d:%02d UTC`, `%4.1fV` (batería).

### Ficheros en su FFat (config/datos en texto plano)
`/eibi.txt` · `/etm.txt` · `/playlist.txt` · `/logfile.txt` · `/mem.txt` · `/memo.txt` ·
`/memories` · `/stations.txt` · `/user.txt` · `/settings.txt` · `/hardcopy.bmp` (screenshot) ·
`/greyscale` · `/inverse` · `/rotate` · `/freeze`

### Funciones NUEVAS halladas (no estaban en el roadmap)
- [ ] **alarm** — `Alarm` + `Alarm Test` (despertador/temporizador)
- [ ] **buzzer** — `Buzzer` (¿beep de teclas / Morse sidetone?)
- [ ] **detectfrq** — `Detect frq` (autodetección de frecuencia/modo)
- [ ] **infomode** — `Info Mode` (pantalla de info)
- [ ] **hardcopy** — captura de pantalla a `/hardcopy.bmp` en el FS

### Decisión arquitectónica abierta
El fork usa **LittleFS + `schedules.bin` (binario)**; Berndt usa **FFat + ficheros de texto**.
Para paridad real (USB MSC, eibi.txt con sitios, listas editables) probablemente convenga
**migrar a FFat** o añadir una partición FAT. Evaluar antes de empezar el track `drive`.

---

## Próximos pasos (retomar aquí)
0. **Hardware conectado:** ATS mini en **COM7** (ESP32-S3 USB Serial/JTAG nativo,
   `VID_303A` Espressif / `PID_1001`). Confirmado el 2026-06-27.
1. ✅ **HECHO (2026-06-27): build + flash + boot validados en la V4B.** PSRAM embebida 8MB →
   perfil correcto **`esp32s3-ospi`**. Compila limpio (flash 9%, RAM 19%) y arranca la UI del fork.
   Toolchain: `C:\Users\xe1ee\arduino-cli\arduino-cli.exe` (core 3.3.10 instalado).
2. **(SIGUIENTE)** Primera tanda de victorias fáciles: **numpad + afc + longpress**.

### Build (del Makefile, en `ats-mini/`)
```bash
make build                 # arduino-cli compile -e -p esp32s3-ospi
make upload PORT=COM7      # flashea por USB (puerto detectado)
```
Flags útiles: `LILYGO_SI473X`, `HALF_STEP`, `DEBUG`, niveles de potencia BLE/WiFi.

---

## Continuar en otra PC (handoff 2026-06-27)

> La **memoria de Claude es local** a cada PC (`~/.claude/...`), NO viaja por git. Este
> ROADMAP es la fuente de verdad portable. En la PC nueva: `git clone`/`git pull` este fork.

### 1. Instalar toolchain (no está en la PC nueva)
```bash
# arduino-cli (binario único). En Windows: descargar y descomprimir
#   https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip
# Compilar con el perfil instala SOLO el core 3.3.10 + librerías automáticamente:
arduino-cli compile --profile esp32s3-ospi --export-binaries <ruta>/ats-mini
arduino-cli upload  -m esp32s3-ospi -p <PUERTO> <ruta>/ats-mini
```
- **El puerto COM será DISTINTO** en la otra PC. Detectarlo: buscar el dispositivo
  `VID_303A` / `PID_1001` (ESP32-S3). En Windows PowerShell:
  `Get-CimInstance Win32_PnPEntity | ? {$_.Name -match 'COM\d+'}`
- Perfil correcto = **`esp32s3-ospi`** (V4B con PSRAM embebida 8MB octal).

### 2. Backup de Berndt + fotos (NO están en git — no-redistribuir)
Copiar manualmente (USB/nube) el archivo **`ats-mini-berndt-handoff.zip`** que contiene:
- `berndt-firmware-full-8MB-2026-06-27.bin` (SHA256 `C232743C8C05FCA6…`) — para restaurar
  Berndt con: `esptool --chip esp32s3 -p <PUERTO> -b 921600 write_flash 0x0 <bin>`
- `reference-photos/` — 5 fotos del ojo mágico de Berndt (referencia de diseño).

### 3. Estado actual del trabajo
- ✅ **AFC (texto)** implementado y flasheado — versión provisional, **se reemplaza** por el ojo mágico.
- 🔄 **Ojo mágico (Elemento B de Berndt)** en diseño. Lab interactivo en **`tools/magic-eye-lab.html`**
  (abrir en navegador). Variante **D = estilo Berndt**: SIGNAL rssi/snr + barra de centrado con
  cursor gris + flechas/punto + rampa de nivel.
- ⚠️ **PENDIENTE DE PULIR (feedback del usuario):** la variante D del lab **aún no clava las
  proporciones de las fotos** — revisar contra `reference-photos/` (grosor de barra, ancho/posición
  del cursor gris, tamaño de flechas y punto, layout). Preguntar al usuario qué difiere más.
- Datos del chip para el ojo mágico: `getCurrentRSSI()`, `getCurrentSNR()`,
  `getCurrentSignedFrequencyOffset()` (int8 kHz, solo FM), `getCurrentPilot()`.
- **Estado del dispositivo:** el fork está flasheado y `Settings → USB Port = Ad hoc` quedó
  ACTIVADO (persiste en NVS) → la captura por serial funciona. (El binario de Berndt está en el backup.)

---

## 6. Herramientas de desarrollo (carpeta `tools/`)

### 🖼️ Captura del display REAL (clave para el diseño de UI)
El firmware vuelca el framebuffer por serial con el comando `C` (requiere `USB Port = Ad hoc`).
Esto da una imagen **pixel-perfect** de lo que se ve — la verdad final para iterar la UI.
```powershell
# COM port distinto por PC: Get-CimInstance Win32_PnPEntity | ? {$_.Name -match 'COM\d+'}
powershell -File tools/capture-screenshot.ps1 -Port COM7 -OutDir .
#  -> screenshot.hex + screenshot.png  (usa tools/hex2png.py para convertir)
```
Flujo de diseño: **editar → compilar → flashear → `capture-screenshot.ps1` → revisar PNG → ajustar.**
BMP del firmware = RGB565, byte-swap (htons), filas bottom-up (ver `Remote.cpp::remoteCaptureScreen`).

### 📦 Extraer archivos del backup de Berndt (FFat)
`tools/parse_parts.py <dump.bin>` lista la tabla de particiones. La FFat de Berndt está en
`0x290000` (1408 KB, FAT12). Carvear esa región a `.img` y abrir con **7-Zip** (`7z x part.img`).

## 7. Referencias REALES de Berndt (extraídas del backup, en el handoff zip)

`Documents/ats-mini-berndt-backup/berndt-ffat-files/` — sus ficheros reales (formatos para clonar):
- **`settings.txt`** (magic `9997`) — modelo de ajustes de Berndt. Campos: `menu, bandwidthSSB/AM/FM,
  stepSSB/AM/FM, mode, battery, decoder, automute, band, store, station, volume, agcFM/AM/SSB,
  softmute, bfo, frequency, backlight, tint, inverse, greyscale, home <lat,lon>, slow, seek`.
  → Confirma features: `decoder, automute, tint, inverse, greyscale, slow (powersave), seek`, y
  **`home 51.198467, 6.879189`** = coords para calcular **distancia al transmisor**.
- **`user.txt` / `stations.txt`** (magic `9998`) — frecuencias con nombre: `freq,nombre`
  (WWV + canales CB 1-40). Formato de listas de estaciones de Berndt.
- **`etm_1.txt`** — resultado ETM: lista rankeada `idx hora freq(kHz) nivel`. Formato del escáner ETM.
- (No había `hardcopy.bmp` en el volcado → para SU UI usamos las fotos en `reference-photos/`.)
