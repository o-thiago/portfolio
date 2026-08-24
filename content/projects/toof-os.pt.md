+++
title = "toof-os: NixOS Declarativo para Raspberry Pi 4"
description = "Configuração personalizada e totalmente reproduzível do NixOS para placas Raspberry Pi 4 ARM64 com aceleração gráfica VC4 e módulos modulares."
date = 2025-06-01
weight = 1

[extra]
category = "NixOS / Sistemas"
author = "@o-thiago"
github = "https://github.com/o-thiago/ToofOS"
stack = ["Nix Flakes", "NixOS", "Raspberry Pi 4", "Kernel Linux", "Devicetree"]
+++

## Visão Geral

O **`toof-os`** é uma configuração declarativa de sistema operacional desenvolvida com **NixOS** e **Nix Flakes**, projetada especificamente para placas de desenvolvimento Raspberry Pi 4 (arquitetura ARM64 / AArch64).

Utilizando o modelo puramente funcional do ecossistema Nix, o `toof-os` transforma todo o ambiente operacional — incluindo parâmetros de kernel, drivers gráficos acelerados, rede e perfis de usuário — em uma especificação imutável, versionada e reproduzível.

---

## Destaques do Projeto

- **Arquitetura Baseada em Flakes:** Utiliza os módulos do `nixos-raspberrypi` e `nixpkgs` sem depender de canais legados (`nix-channel`), garantindo builds herméticos.
- **Aceleração Gráfica de Hardware:** Configurado com suporte a drivers VC4 DRM/KMS da Broadcom, stack Bluetooth e firmwares específicos de hardware.
- **Caches Binários Remotos:** Integração com substituters Cachix para eliminar a compilação extensiva de pacotes na própria placa ARM durante a inicialização.
- **Módulos Limpos e Isolados:** Estrutura modular separando configuração de sistema, perfis de usuários, serviços de rede e overlays de hardware.

```nix
{
  description = "toofos - Sistema Operacional Declarativo para Raspberry Pi 4";

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

## Aprendizados Técnicos

O desenvolvimento do `toof-os` proporcionou sólida experiência prática em compilação cruzada (x86_64 -> AArch64), manipulação de Devicetrees do Linux para plataformas ARM e administração avançada do NixOS.
