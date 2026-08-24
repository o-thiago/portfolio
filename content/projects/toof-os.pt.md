+++
title = "toof-os: Sistema Operacional NixOS para a DACC Station da UNIR"
description = "Sistema operacional declarativo desenvolvido em NixOS sob medida para alimentar a console arcade DACC Station do Departamento Acadêmico de Ciência da Computação da UNIR."
date = 2025-06-01
weight = 1

[extra]
category = "NixOS / Sistemas"
author = "@o-thiago"
github = "https://github.com/o-thiago/ToofOS"
stack = ["Nix Flakes", "NixOS", "Raspberry Pi 4", "DACC Station (UNIR)", "nix-ld", "SDL2", "Wayland", "Kernel Linux"]
+++

## Visão Geral

O **`toof-os`** é um sistema operacional personalizado, imutável e declarativo desenvolvido com **NixOS** e **Nix Flakes** projetado especificamente para ser o sistema operacional que alimenta a **DACC Station** — projeto de console / estação arcade do **Departamento Acadêmico de Ciência da Computação (DACC)** da **Universidade Federal de Rondônia (UNIR)**.

A **DACC Station** foi concebida como uma estação interativa de hardware para demonstração e execução de jogos desenvolvidos pelos próprios alunos do curso de Ciência da Computação da UNIR (utilizando engines como Godot, SDL2, Unity, Java, além de executáveis em C/C++). O `toof-os` opera nas placas Raspberry Pi 4 da estação, inicializando diretamente na interface da DACC Station com foco em alta performance e baixa latência.

---

## Decisões Técnicas & Arquitetura do Sistema

### 1. Integração Direta com a Interface da DACC Station
- Integração e empacotamento em Nix da suíte em C++/SDL2 da estação (`dacc-ui`, `process-manager` e `log-server`), orquestrados por sockets Unix de IPC (`/tmp/dacc-station.sock` e `/tmp/gameman.sock`).
- Inicialização direta no ambiente gráfico Wayland via SDDM em modo quiosque (kiosk console mode).

### 2. Runtime Universal para Jogos dos Alunos via `nix-ld`
Para que os estudantes possam rodar jogos compilados dinamicamente em diversas engines sem a necessidade de empacotar cada jogo individualmente no Nix, o `toof-os` fornece um ambiente de runtime universal baseado no padrão do **Steam Runtime**:
- **Gráficos e GPU:** Drivers Mesa, Vulkan loader, libGL, libdrm, Wayland e bibliotecas de compatibilidade X11.
- **Áudio & Multimídia:** PipeWire de baixa latência, ALSA com suporte a 32-bit, PulseAudio e suíte completa SDL2 (`SDL2_image`, `SDL2_mixer`, `SDL2_ttf`, `SDL2_gfx`).
- **Múltiplos Ambientes Java:** Conjunto de runtimes Eclipse Temurin pré-instalados (JRE 8, 11, 17, 21 e 25).

### 3. Otimizações de Desempenho e Áudio em Tempo Real
- **Agendamento de Processos:** Integração do daemon `ananicy-cpp` com conjunto de regras do CachyOS para ajuste dinâmico de prioridade de CPU e IO (nice/ionice), mitigando engasgos (stuttering) em tempo de jogo.
- **Prioridade de Áudio:** Configuração do `rtkit` para escalonamento em tempo real do PipeWire.
- **Frequência da CPU:** Fixação de `cpuFreqGovernor = "performance"` para manter clocks estáveis.
- **Gerenciamento de RAM:** Configuração de `zramSwap` (50% da memória física) para otimizar os 8GB de RAM do Raspberry Pi.

### 4. Suporte a Controles e Periféricos
- Suporte nativo a controles sem fio do Xbox via módulo `xpadneo`.
- Suporte a gamepads não convencionais e **DualShock 4** via camada `uinput`.

### 5. Preservação do Cartão SD & Otimização do Armazenamento
- Montagem com parâmetros `noatime` e `commit=120` para reduzir ciclos desnecessários de escrita na memória flash do cartão SD.
- Deduplicação automática de arquivos na Nix Store (`auto-optimise-store = true`) e coleta de lixo periódica retendo as 3 gerações mais recentes do sistema.

---

## Estrutura Flake do Sistema

```nix
{
  description = "toofos - Sistema Operacional Declarativo para a DACC Station da UNIR";

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

## Contexto Acadêmico & Repositório

- **Instituição:** Universidade Federal de Rondônia (UNIR) — Departamento Acadêmico de Ciência da Computação (DACC).
- **Finalidade:** Sistema Operacional dedicado da console arcade **DACC Station**.
- **Repositório:** [github.com/o-thiago/ToofOS](https://github.com/o-thiago/ToofOS)
- **Autor:** Thiago Macedo Mendes (`@o-thiago`)
