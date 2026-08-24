+++
title = "toof-os: Tailored NixOS for UNIR's DACC Station Console"
description = "A bespoke, declarative NixOS operating system engineered to power the DACC Station arcade/console hardware at UNIR (Federal University of Rondônia)."
date = 2025-06-01
weight = 1

[extra]
category = "NixOS / Systems"
author = "@o-thiago"
github = "https://github.com/o-thiago/ToofOS"
stack = ["Nix Flakes", "NixOS", "Raspberry Pi 4", "DACC Station (UNIR)", "nix-ld", "SDL2", "Wayland", "Linux Kernel"]
+++

## Overview

**`toof-os`** is a bespoke, declarative operating system engineered with **NixOS** and **Nix Flakes** specifically to power the **DACC Station**—a custom gaming console and arcade station developed at the **Department of Computer Science (DACC) of the Federal University of Rondônia (UNIR)**.

The **DACC Station** serves as an interactive hardware showcase station for students to run, test, and play games developed within academic coursework and research (featuring engines like Godot, SDL2, Unity, Java, and custom C/C++ runtimes). `toof-os` acts as the dedicated operating system running on Raspberry Pi 4 ARM64 single-board computers that boots straight into the DACC Station console environment.

---

## Architectural Highlights & Engineering Decisions

### 1. Dedicated DACC Station Integration & Autostart
- Integrates the custom C++/SDL2 DACC Station launcher suite (`dacc-ui`, `process-manager`, `log-server`) communicating via Unix domain sockets (`/tmp/dacc-station.sock` and `/tmp/gameman.sock`).
- Automatically bootstraps through SDDM Wayland session management directly into the station frontend upon boot.

### 2. Universal Game Runtime via `nix-ld` (Steam-Runtime Inspired)
To allow students to plug in and run dynamically linked game binaries built with diverse game engines (Godot, Unity, SDL2, Java) without requiring every single game to be packaged as a Nix derivation, `toof-os` preconfigures a comprehensive **`nix-ld`** runtime containing:
- **Graphics & Drivers:** Mesa, Vulkan loader, libGL, libdrm, Wayland, and X11 compatibility libraries.
- **Audio & Media:** PipeWire, ALSA with 32-bit support, PulseAudio, and SDL2 multimedia suites (`SDL2_image`, `SDL2_mixer`, `SDL2_ttf`, `SDL2_gfx`).
- **Multi-version JRE:** Bundled Temurin Java runtimes (JRE 8, 11, 17, 21, 25).

### 3. Low-Latency Gaming & Performance Tuning
- **Process Scheduling:** Integrated `ananicy-cpp` paired with CachyOS rulesets for real-time CPU nice and I/O priority management to eliminate frame stuttering.
- **Audio Priority:** Enabled `rtkit` for real-time low-latency PipeWire audio threads.
- **Governor:** Configured `cpuFreqGovernor = "performance"` to prevent dynamic clock throttling during gameplay.
- **Memory Optimization:** Enabled `zramSwap` with 50% memory allocation for smooth operation on 8GB Raspberry Pi boards.

### 4. Hardware Acceleration & Controller Support
- Built on Broadcom VC4 DRM drivers and hardware graphics overlays.
- Driver support for **Xbox Wireless Controllers** via `xpadneo` and custom gamepads / **DualShock 4** via `uinput`.

### 5. SD Card Flash Wear Reduction & Storage Optimization
- Configured filesystems with `noatime` and `commit=120` to reduce disk write cycles and extend SD card flash memory lifespan.
- Continuous Nix store deduplication (`auto-optimise-store = true`) and rolling garbage collection keeping the 3 most recent generations.

---

## Declarative Flake Structure

```nix
{
  description = "toofos - Declarative OS for UNIR DACC Station";

  inputs = {
    nixos-raspberrypi.url = "github:nvmd/nixos-raspberrypi/main";
    nixpkgs.follows = "nixos-raspberrypi/nixpkgs";
  };

  outputs = inputs@{ nixos-raspberrypi, ... }: {
    nixosConfigurations.toofos = nixos-raspberrypi.lib.nixosSystem {
      specialArgs = inputs;
      modules = [
        ./system/configuration.nix
        {
          imports = with nixos-raspberrypi.nixosModules; [
            raspberry-pi-4.base
            raspberry-pi-4.display-vc4
            raspberry-pi-4.bluetooth
          ];
        }
      ];
    };
  };
}
```

---

## Academic Context & Impact

- **Institution:** Federal University of Rondônia (UNIR) — Departamento Acadêmico de Ciência da Computação (DACC).
- **Target Platform:** DACC Station arcade / console unit.
- **Repository:** [github.com/o-thiago/ToofOS](https://github.com/o-thiago/ToofOS)
- **Author:** Thiago Macedo Mendes (`@o-thiago`)
