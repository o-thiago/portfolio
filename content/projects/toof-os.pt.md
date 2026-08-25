+++
title = "toof-os: Sistema Operacional NixOS para o DACC Station da UNIR"
description = "Configuração declarativa em NixOS desenvolvida para ser o sistema operacional do DACC Station, o console arcade da UNIR."
date = 2025-06-01
weight = 1

[extra]
category = "NixOS / Sistemas"
repo = "ToofOS"
stack = ["Nix Flakes", "NixOS", "Raspberry Pi 4", "DACC Station (UNIR)", "nix-ld", "SDL2", "Wayland"]
+++

## O que é o projeto?

O **`toof-os`** é uma configuração personalizada do **NixOS** feita para rodar no **DACC Station** — um projeto de console arcade desenvolvido no **Departamento Acadêmico de Ciência da Computação (DACC)** da **Universidade Federal de Rondônia (UNIR)**.

O objetivo do **DACC Station** é permitir que estudantes da UNIR exibam e joguem projetos desenvolvidos ao longo do curso (jogos feitos em Godot, Unity, SDL2, Java ou binários em C/C++). O `toof-os` foi criado para rodar diretamente nas placas Raspberry Pi 4 do console, cuidando de toda a inicialização, compatibilidade com controles e execução dos jogos.

---

## Como foi construído

### 1. Inicialização e Interface do DACC Station
- O sistema empacota a suíte em C++/SDL2 do console (`dacc-ui`, `process-manager` e `log-server`), que se comunicam através de sockets Unix (`/tmp/dacc-station.sock` e `/tmp/gameman.sock`).
- A inicialização entra direto no ambiente gráfico Wayland via SDDM em modo quiosque, sem precisar abrir desktop tradicional.

### 2. Execução de Jogos com `nix-ld`
Como os alunos criam jogos em ferramentas diversas, empacotar cada jogo individualmente no Nix seria inviável. Por isso, configurei o **`nix-ld`** com uma camada de bibliotecas dinâmicas semelhante ao runtime da Steam:
- Bibliotecas gráficas (Mesa, Vulkan loader, libGL, libdrm, Wayland e X11).
- Áudio e mídia com PipeWire e SDL2 (`SDL2_image`, `SDL2_mixer`, `SDL2_ttf`, `SDL2_gfx`).
- Múltiplas versões do Java JRE pré-instaladas (versões 8, 11, 17, 21 e 25).

### 3. Ajustes de Desempenho e Áudio
- `ananicy-cpp` com regras do CachyOS para priorizar CPU e IO dos jogos em execução.
- PipeWire configurado com `rtkit` para reduzir latência de áudio.
- Governador de CPU fixado em `performance` para evitar engasgos com trocas de frequência no ARM.
- `zramSwap` ativado para gerenciar melhor a memória RAM de 8GB do Raspberry Pi.

### 4. Controles e Armazenamento
- Suporte a controles sem fio de Xbox via `xpadneo` e outros controles/DualShock 4 via `uinput`.
- Sistema de arquivos com `noatime` e `commit=120` para reduzir ciclos de escrita no cartão SD.
- Limpeza automática da Nix Store retendo as 3 últimas gerações do sistema.

---

## Configuração Flake

```nix
{
  description = "toofos - Sistema Operacional para o DACC Station da UNIR";

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

- **Projeto:** [DACC Station](https://github.com/vinytacana/dacc_station_integration) — UNIR
- **Repositório:** {{ github_link(repo="ToofOS") }}
- **Autor:** {{ author_link() }}
