# Honeywell RSC Pressure Sensor (SPI) on Raspberry Pi

A lightweight Python driver and example logger for Honeywell **RSC** (TruStability®) pressure sensors interfaced over **SPI** on a Raspberry Pi.

> **Author**: Ziyuan Wang ([wangzi@uw.edu](mailto:wangzi@uw.edu))
> **Copyright**: (c) 2020 University of Washington

---

## Overview

This code communicates with an RSC-series pressure sensor that exposes two SPI-accessible functions:

* **EEPROM interface** (sensor metadata & calibration coefficients)
* **ADC interface** (raw temperature & pressure conversions)

The driver:

* Reads the sensor **EEPROM** to discover model info, serial number, engineering units, pressure range/min, and per-device **calibration coefficients** (offset/span/shape).
* Configures the **ADC** and reads **temperature** and **pressure**.
* Computes **temperature-compensated pressure** in engineering units using Honeywell’s polynomial model and the EEPROM coefficients.
* Provides a simple **`rsc_test()`** routine to log and plot temperature/pressure over time and export a timestamped CSV and PNG plot.

> Tested on Raspberry Pi with `spidev` and `RPi.GPIO`. Requires SPI to be enabled.

---

## Hardware & Wiring

### Raspberry Pi SPI

The code assumes the Raspberry Pi’s **bus 0** with **two chip selects**:

* **CE0 (spidev0.0)** → **EEPROM** (read in **SPI mode 0**)
* **CE1 (spidev0.1)** → **ADC** (used in **SPI mode 1**)

Typical Raspberry Pi SPI pins (BOARD numbering shown for reference):

| Function | Pi BCM | Pi BOARD |
| -------- | -----: | -------: |
| 3V3 / 5V |      — |    1 / 2 |
| GND      |      — | 6 (etc.) |
| SCLK     | GPIO11 |       23 |
| MOSI     | GPIO10 |       19 |
| MISO     |  GPIO9 |       21 |
| CE0      |  GPIO8 |       24 |
| CE1      |  GPIO7 |       26 |

> **Voltage levels**: Many RSC variants are 3.3 V devices. Verify your exact sensor’s supply and logic-level requirements and use appropriate level shifting if needed. Power and pinout must follow your sensor’s datasheet.

> The code sets **BOARD** numbering and configures **pin 7** as an input (`GPIO.setup(7, GPIO.IN)`); this isn’t used elsewhere and may be dropped or repurposed if not needed.

---

## Software Requirements

* Python 3.7+
* Raspberry Pi OS with **SPI enabled** (`sudo raspi-config` → Interface Options → SPI → Enable)
* Packages:

  * `spidev` (SPI access)
  * `RPi.GPIO` (basic GPIO)
  * `pandas` (CSV logging)
  * `matplotlib` (plots)

### Install

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-rpi.gpio
pip3 install spidev pandas matplotlib
```

> You may need to run with `sudo` due to GPIO/SPI access (`sudo python3 your_script.py`).

---

## Quick Start

```python
from hrsc import HRSC  # rename the provided file to hrsc.py or adjust import

sensor = HRSC()

# (Optional) print sensor metadata from EEPROM
sensor.sensor_info()            # catalog, serial, units, checksum, etc.

# (Optional) configure ADC from EEPROM values
sensor.adc_configure()

# Single compensated read (°C, engineering-unit pressure)
T_C, P = sensor.read_temp_pressure()
print(f"Temp: {T_C:.2f} °C, Pressure: {P:.5f} (engineering units)")

# Simple logging test (interactive)
# Prompts for total time (s) and sample interval (s), saves CSV and PNG.
# sensor.rsc_test(rate=20)
```

## API Reference

### Class: `HRSC`

**Constructor**

* `HRSC(i2c=None, **kwargs)`
  Initializes SPI and calls `read_eeprom()`.

**EEPROM / Metadata**

* `read_eeprom()` → `int`
  Reads 512 bytes into the global `sensor_rom`. Low page via CE0/mode 0, high page similarly. Returns 0 on success.
* `sensor_info()` → `int`
  Prints catalog listing, serial number, pressure range/min, units, and checksum parsed from `sensor_rom`.

**ADC / Configuration**

* `adc_configure()` → `int`
  Selects CE1/mode 1, issues ADC reset, writes ADC configuration registers using bytes stored in `sensor_rom`.
* `set_speed(speed:int)` → `int`
  Sets ADC output data rate & digital filter mode (encodes **`reg_dr`** and **`reg_mode`**) for pressure channel and writes the ADC config register.

  Supported entries in code:

  * Sinc4 (mode 0): 20, 45, 90, 175, 330, 600, 1000 (samples/s)
  * Sinc2 (mode 2): 40, 90, 180, 350, 660, 1200, 2000 (samples/s)

**Low-level helpers**

* `conv_to_float(b1,b2,b3,b4)` → `float` (little-endian)
* `conv_to_short(b1,b2)` → `int` (unsigned 16-bit)
* `twos_complement([a,b,c])` → `int` (signed 24-bit)
* `convert_temp(raw_temp:int)` → `float` (°C from raw 24-bit packet)

**Readouts**

* `read_temp()` → `float`
  Configures ADC for temperature channel, reads a 24‑bit sample, converts to °C.
* `read_pressure()` → `int`
  Configures ADC for pressure channel and returns **raw signed 24‑bit counts** (not compensated or scaled).
* `comp_readings(raw_pressure, raw_temp)` → `float`
  Computes compensated pressure in engineering units using polynomial model with coefficients read from EEPROM. (Note: current implementation **re-reads temperature internally** and ignores the `raw_*` arguments.)
* `read_temp_pressure()` → `(float, float)`
  Reads temperature, then pressure, and returns `(temp_C, pressure_eng_units)` using the EEPROM coefficients (Offset/Span/Shape) and `PRange/Pmin`.
* `rsc_test(rate=20)` → `None`
  Interactive logger: prompts for total duration and interval (seconds), samples `read_temp_pressure()`, saves a CSV and a PNG plot.

---

---

## License & Attribution

* Copyright (c) 2020 University of Washington
* Sensor algorithm derived from Honeywell RSC documentation. Check licensing and redistribution constraints for your environment.

**Maintainer**: Ziyuan Wang ([wangzi@uw.edu](mailto:wangzi@uw.edu))
