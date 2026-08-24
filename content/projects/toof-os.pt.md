+++
title = "toof-os: NixOS Declarativo para Raspberry Pi 4"
description = "Configuração personalizada e totalmente reproduzível do NixOS para placas Raspberry Pi 4 ARM64 com aceleração gráfica VC4 e módulos modulares."
date = 2025-06-01
weight = 1

[extra]
category = "NixOS / Sistemas"
github = "https://github.com/o-thiago/toof-os"
stack = ["Nix Flakes", "NixOS", "Raspberry Pi 4", "Kernel Linux", "Devicetree"]
+++

## Visão Geral

O **`toof-os`** é uma configuração personalizada de sistema operacional desenvolvida em **NixOS** e **Nix Flakes**, criada especificamente para computadores de placa única Raspberry Pi 4 (ARM64).

Através da arquitetura puramente funcional do Nix, o `toof-os` transforma toda a configuração do sistema operacional — incluindo parâmetros de kernel, aceleração gráfica, conectividade de rede e ambiente de usuário — em um código versionável e determinístico.

---

## Destaques Técnicos

- **Arquitetura Baseada em Flakes:** Utiliza `nixpkgs` e `nixos-raspberrypi` para compor módulos de sistema sem depender de canais legados.
- **Aceleração de Hardware:** Suporte nativo ao driver de vídeo Broadcom VC4 DRM, pilha Bluetooth e firmware embarcado.
- **Caches Binários Remotos:** Integração com substituters do Cachix para acelerar a inicialização e evitar compilações demoradas diretamente na placa.
- **Módulos Limpos:** Separação estrita entre módulos de hardware, configurações de rede e perfis de usuário.

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
