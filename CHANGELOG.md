# VLT PCB Changelog

## [Rev 3] - 2026-03-25 (In Progress)

### Changed
- **MCU migration: RP2350B → STM32H723VGT6** — RP2350B version moved to obsolete/outdated
- **External 16MB flash** added for storage (GIF, profiles, etc.)

### Notes
- Rev 1–2 (RP2350B-based) are now considered obsolete
- Moving forward with STM32H723VGT6 as the production MCU

---

## [Rev 2] - 2026-02-27 (Obsolete — RP2350B)

### Added
- **NTC thermistor** — temperature sensing circuit with voltage divider
- **ERM haptic motor** (ERM1) — 10mm coin motor with BSS138 MOSFET gate driver on GP21
- **MicroSD card slot** (MSD-1-A, CUI Devices) — push-in / auto-eject, SMD, 1.8mm height
- **4-pin FPC connector** (0.5mm pitch) — for capacitive touch panel (CTP)
- **Ferrite beads** — 0603 (600R) and 0805 for power rail filtering
- **1N4148WT protection diode**
- **Test point** (1mm pad) for debug probing
- **Split spacebar support** — HE45 CapsLock position gets alternate 1.75u stabilizer footprint (`SW_MX_HE_90deg_1.75u_STP_1.5_4layer`)
- New via size (0.6mm / 0.2mm drill) for tighter routing
- `wiring.cpp` reference file documenting full MUX-to-sensor-to-key mapping (MUX1–MUX6, 81 keys)

### Changed
- **Major PCB layout rework** — near-complete re-route of all traces and component placement
- **Sensor schematic overhaul** — all 81 hall effect sensors relabeled with key names (e.g., `HE45_CapsLock_STP`, `HE75_Space`)
- **4-layer stackup** — switch footprints updated to 4-layer variants (`SW_MX_HE_90deg_1u_4layer`)
- **Resistor package migration** — reorganized mix of 0402 and 0603 passives (100R, 1K, 10K, 100K, 15pF)
- **DRC rules relaxed** — min text height 0.5→0.2mm, min text thickness 0.08→0.02mm, min via diameter 0.5→0.45mm
- LED sub-sheet minor adjustments

### Notes
- Board is nearly complete — layout, schematic, and component placement close to final
- One sensor position marked DNP (do not populate)

---

## [Rev 1] - Initial Revisions (committed locally)

### 4e0a914 — Multiple LEDs for spacebar
- Added multiple LED footprints for spacebar illumination

### 8ee7076 — Remapped pins, added MPR121
- Pin remapping across MCU
- Added MPR121 capacitive touch controller to schematic

### 429e964 — Changed WS2812B pin
- RGB_DATA_IN moved from GP3 to GP21

### 0b3a9f6 — Changed encoder pinout
- Encoder A: GP16 → GP15
- Encoder B: GP14 → GP15
- Encoder SW: GP15 → GP16

### d8d17cf — Initial VLT hardware
- First KiCad project commit (schematic, PCB, sub-sheets: sensors, LEDs)
