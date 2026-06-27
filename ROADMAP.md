# ATS Mini — Roadmap de mejoras (fork XE1E)

Fork de [esp32-si4732/ats-mini](https://github.com/esp32-si4732/ats-mini) (MIT, forks bienvenidos).

- **Hardware objetivo:** ATS Mini **V4B** (ESP32-S3 + SI4732).
- **Base de partida:** firmware ats-mini v2.35.
- **Objetivo:** añadir/mejorar funciones (NO priorizar decoders) y **optimizar el receptor**.
- **Referencia de funciones:** firmware "Pocket SI4735 Dual Core Decoder" de HJ Berndt
  (http://www.hjberndt.de/dvb/pocketSI4735DualCoreDecoder.html) — solo binario, sin fuente;
  sirve como referencia de comportamiento, todo se reimplementa desde cero.
- **Nota decoders:** SSTV/WEFAX requieren añadir un micrófono I2S **INMP441**; RTTY/CW son directos.
  No es la prioridad actual.

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
- [ ] **afc** — indicador de centrado AFC
- [ ] **band** — marcas de borde de banda en AM
- [ ] **longpress** — long-press "Freeze" + menú por pulsación larga
- [ ] **greyscale / tint** — Greyscale / Inverse / Rotate / Tint de pantalla
- [ ] **zeit** — reloj grande en FM
- [ ] **blend** — indicador de stereo-blend / mono forzado
- [ ] **instantlevel** — nivel de señal instantáneo

### 🟡 Medias (lógica/datos)
- [ ] **etm / etl / etlmem** — escáner ETM + listas de memoria (auto-construir listas)
- [ ] **playlist** — reproducción secuencial de estaciones
- [ ] **transmitter** — ubicación del transmisor EiBi + distancia
- [ ] **ibp** — soporte IBP (faros de propagación)
- [ ] **time** — entrada manual de hora/fecha con numpad, band-monitor
- [ ] **noise / plotter** — medición avanzada de ruido + plotter de señal
- [ ] **logger** — logger de búsquedas EiBi/RDS
- [ ] **sporadic** — protocolo Sporadic-E, exportar listas como texto

### 🔴 Difícil (infraestructura)
- [ ] **drive** — modo USB Flash Drive (TinyUSB MSC) → exportar `logfile.txt`, `settings.txt`

### ⏸️ Decoders (aplazados — requieren INMP441 para SSTV/WEFAX)
- [ ] rtty / cw (directos) · [ ] sstv · [ ] wefax · [ ] replay (ring buffer RTTY)

## 3. Track: optimización del receptor
- [ ] Auditar defaults y lógica de AGC / softmute / AVC / ancho de banda
- [ ] Revisar SSB patch y calibración
- [ ] Calidad de audio

---

## Próximos pasos (retomar aquí)
1. **Validar build + flash tal cual en la V4B** — confirmar perfil (`esp32s3-ospi` vs `esp32s3-qspi`,
   según PSRAM octal/quad de la V4B) y el ciclo `make build` / `make upload`.
2. Primera tanda de victorias fáciles: **numpad + afc + longpress**.

### Build (del Makefile, en `ats-mini/`)
```bash
make build                 # arduino-cli compile -e -p esp32s3-ospi
make upload PORT=COM_x     # flashea por USB
```
Flags útiles: `LILYGO_SI473X`, `HALF_STEP`, `DEBUG`, niveles de potencia BLE/WiFi.
