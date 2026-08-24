+++
title = "fifine-rgb: Utilitário Linux para Controle de Hardware USB"
description = "Utilitário CLI leve para Linux para controlar os modos e cores de iluminação RGB em microfones USB Fifine via relatórios HID diretos."
date = 2025-02-15
weight = 5

[extra]
category = "Sistemas / Hardware"
github = "https://github.com/o-thiago/fifine-rgb"
stack = ["C / Rust", "Linux HID", "libusb", "Protocolos USB", "Nix Flakes"]
+++

## Visão Geral

Diversos periféricos USB modernos não possuem software oficial de configuração para distribuições Linux, exigindo ambientes Windows até para tarefas simples como ajustar a cor da iluminação ou desligar anéis de LED.

O **`fifine-rgb`** é uma ferramenta de linha de comando para Linux que realiza engenharia reversa do protocolo de relatórios USB HID de microfones Fifine.

```bash
# Exemplos de uso:
fifine-rgb --mode static --color 00E5FF
fifine-rgb --mode breathe --speed slow
fifine-rgb --off
```
