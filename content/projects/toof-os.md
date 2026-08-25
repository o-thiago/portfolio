+++
title = "toof-os: NixOS Operating System for UNIR's DACC Station"
description = "Declarative NixOS configuration built to power the DACC Station, an arcade console project at UNIR running on Raspberry Pi 4."
date = 2025-06-01
weight = 1

[extra]
category = "NixOS / Systems"
repo = "ToofOS"
stack = ["Nix Flakes", "NixOS", "Raspberry Pi 4", "DACC Station (UNIR)", "nix-ld", "SDL2", "Wayland"]
+++

## What is the project?

**`toof-os`** is a custom **NixOS** configuration created to run on the **DACC Station**—a gaming arcade console project built at the **Department of Computer Science (DACC)** of the **Federal University of Rondônia (UNIR)**.

The purpose of the **DACC Station** is to showcase and play games developed by UNIR students (using Godot, Unity, SDL2, Java, or custom C/C++ builds). `toof-os` runs on the station's Raspberry Pi 4 boards, handling the system startup, controller support, and game execution.

---

## How it works

### 1. DACC Station Launcher & Kiosk Boot
- Packages the station's C++/SDL2 interface (`dacc-ui`, `process-manager`, `log-server`), communicating via Unix sockets (`/tmp/dacc-station.sock` and `/tmp/gameman.sock`).
- Automatically boots straight into the Wayland session via SDDM in kiosk mode on startup.

### 2. Universal Game Compatibility via `nix-ld`
Because students build games with different engines, packaging each game as a separate Nix derivation isn't practical. To solve this, I configured **`nix-ld`** with common dynamic libraries (similar to Valve's Steam Runtime):
- Graphics libraries (Mesa, Vulkan loader, libGL, libdrm, Wayland, and X11).
- Low-latency audio and media through PipeWire and SDL2 (`SDL2_image`, `SDL2_mixer`, `SDL2_ttf`, `SDL2_gfx`).
- Pre-installed Java runtimes (JRE 8, 11, 17, 21, and 25).

### 3. Performance & Audio Tweaks
- `ananicy-cpp` with CachyOS rulesets to prioritize CPU and I/O for active games.
- PipeWire real-time scheduling via `rtkit` to reduce audio latency.
- CPU governor locked to `performance` on ARM to avoid stuttering from dynamic scaling.
- `zramSwap` configured at 50% RAM to help with memory usage on the 8GB Pi.

### 4. Gamepad & Storage Optimizations
- Wireless Xbox controller support via `xpadneo` and generic/DualShock 4 gamepads through `uinput`.
- Filesystem mounted with `noatime` and `commit=120` to reduce write wear on the SD card.
- Automatic Nix store deduplication keeping the 3 most recent generations.

---

## Flake Configuration

```nix
{
  description = "toofos - Operating System for UNIR DACC Station";

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

## Links

- **Project:** [DACC Station](https://github.com/vinytacana/dacc_station_integration) — UNIR
- **Repository:** {{ github_link(repo="ToofOS") }}
- **Author:** {{ author_link() }}
