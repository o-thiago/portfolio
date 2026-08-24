+++
title = "Urchin 34-Key Split Keyboard ZMK Firmware"
description = "High-performance, ultra-compact firmware architecture for 34-key split columnar ergonomic keyboards powered by ZMK and Zephyr RTOS."
date = 2025-05-15
weight = 2

[extra]
category = "Firmware / Embedded"
github = "https://github.com/o-thiago/urchin-zmk-firmware"
stack = ["ZMK Firmware", "Zephyr RTOS", "C", "Devicetree", "BLE Wireless"]
+++

## Overview

The **Urchin** is an ultra-minimalist, 34-key split ergonomic mechanical keyboard featuring a 3x5 columnar stagger matrix with 2 thumb keys per hand.

This project implements a complete, highly optimized firmware layout using the **ZMK Firmware** framework (based on Zephyr RTOS) written in C and Devicetree overlays.

---

## Technical Architecture

Operating a full keyboard on only 34 keys without hand fatigue requires deep computational layering:

- **Home-Row Modifiers (HRMs):** Modifiers (`Shift`, `Ctrl`, `Alt`, `Super`) are embedded into the home row keys (`A`, `S`, `D`, `F` and `J`, `K`, `L`, `;`) using bilateral tapping-term algorithms and permissive hold timers to prevent misfires.
- **Hardware-Level Key Combos:** Pressing adjacent keys simultaneously triggers specific symbols and actions (e.g., `Q + W` = `Escape`, `O + P` = `Backspace`), cutting thumb and finger travel by over 60%.
- **Layer Switching & Sticky Keys:** Dedicated navigational, numeric, symbolic, and media layers accessible via momentary thumb key taps.
- **Ultra-Low Latency BLE Power Management:** Configured power profiling for Nordic nRF52840 microcontrollers, achieving months of battery life on tiny LiPo cells.

---

## Layout Visualization

```
/* 34-Key Matrix Layout Overview */
    Left Hand                  Right Hand
[ Q  W  E  R  T ]          [ Y  U  I  O  P ]
[ A  S  D  F  G ]          [ H  J  K  L  ; ]  <-- Home-row Mods
[ Z  X  C  V  B ]          [ N  M  ,  .  / ]
      [ NAV SYM ]          [ SPC NUM ]
```

---

## Engineering Takeaways

- Microcontroller pin mapping, matrix scanning, and debouncing algorithms in embedded C.
- Hardware abstraction layers and Device Tree syntax within Zephyr RTOS.
- Human-computer ergonomics and typing velocity optimization.
