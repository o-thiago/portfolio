+++
title = "fifine-rgb: Linux USB Hardware Controller"
description = "A lightweight Linux hardware utility to control and customize RGB illumination modes on Fifine USB microphones via raw HID protocols."
date = 2025-02-15
weight = 5

[extra]
category = "Systems / Hardware"
github = "https://github.com/o-thiago/fifine-rgb"
stack = ["C / Rust", "Linux HID", "libusb", "Hardware Protocols", "Nix Flakes"]
+++

## Overview

Many modern USB peripheral devices lack native Linux configuration software, requiring Windows utilities for simple actions such as setting illumination color or turning off bright LED rings.

**`fifine-rgb`** is a native Linux CLI utility and protocol reverse-engineering project enabling direct control over USB HID feature reports for Fifine microphones.

---

## Technical Details

- **USB HID Feature Reports:** Intercepted and mapped raw USB vendor packets sent by proprietary configuration suites using Wireshark and `usbmon`.
- **Direct Protocol Communication:** Implemented cross-platform raw HID report transmission via `libusb` and `hidraw` without requiring bloated third-party vendor drivers.
- **Nix Flake Integration:** Packaged as a standalone Nix package with custom udev rules for rootless device access.

```bash
# Example usage:
fifine-rgb --mode static --color 00E5FF
fifine-rgb --mode breathe --speed slow
fifine-rgb --off
```
