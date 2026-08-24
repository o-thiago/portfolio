+++
title = "toof-os: Declarative NixOS for Raspberry Pi 4"
description = "A bespoke, fully reproducible NixOS configuration tailored for Raspberry Pi 4 single-board computers with VC4 GPU acceleration and custom modules."
date = 2025-06-01
weight = 1

[extra]
category = "NixOS / Systems"
author = "@o-thiago"
github = "https://github.com/o-thiago/ToofOS"
stack = ["Nix Flakes", "NixOS", "Raspberry Pi 4", "Linux Kernel", "Devicetree"]
+++

## Overview

**`toof-os`** is a bespoke, declarative operating system configuration built with **NixOS** and **Nix Flakes**, engineered specifically for Raspberry Pi 4 ARM64 single-board computers.

By utilizing Nix's purely functional architecture, `toof-os` turns an entire embedded operating system setup—including kernel parameters, graphics acceleration, networking, and userland environments—into a version-controlled, reproducible blueprint.

---

## Key Highlights

- **Pure Flake-Based Architecture:** Uses `nixpkgs` and `nixos-raspberrypi` flake modules to compose system configuration without legacy channel dependencies.
- **Hardware Acceleration:** Configured with Broadcom VC4 DRM display drivers, Bluetooth stack, and hardware-specific firmware blobs.
- **Remote Binary Caches:** Integrated with Cachix substituters to minimize on-device compilation times when bootstrapping new SD cards.
- **Modular Nix Architecture:** Separates system core modules, user profiles, networking daemons, and hardware overlays into cleanly isolated Nix modules.

```nix
{
  description = "toofos - Declarative Raspberry Pi 4 Operating System";

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

## Engineering Takeaways

Building `toof-os` provided in-depth experience with cross-compilation target architectures (AArch64 vs. x86_64), Linux kernel device tree overlays for ARM systems, and declarative system provisioning.
