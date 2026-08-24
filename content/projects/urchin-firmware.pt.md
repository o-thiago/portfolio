+++
title = "Firmware ZMK para Teclado Dividido Urchin de 34 Teclas"
description = "Arquitetura de firmware de alta performance para teclados mecânicos ergonômicos divididos com ZMK e Zephyr RTOS."
date = 2025-05-15
weight = 2

[extra]
category = "Firmware / Embarcados"
github = "https://github.com/o-thiago/urchin-zmk-firmware"
stack = ["ZMK Firmware", "Zephyr RTOS", "C", "Devicetree", "BLE Sem Fio"]
+++

## Visão Geral

O **Urchin** é um teclado mecânico ergonômico dividido ultracompacto de 34 teclas com disposição colunar e 2 teclas de polegar em cada metade.

Este projeto implementa uma arquitetura completa de firmware baseada no framework **ZMK Firmware** (construído sobre o Zephyr RTOS), com configurações em C e Devicetree.

---

## Arquitetura e Engenharia de Camadas

- **Home-Row Modifiers (HRMs):** Teclas modificadoras (`Shift`, `Ctrl`, `Alt`, `Super`) posicionadas na linha base das mãos com temporização bilateral para evitar acionamentos acidentais durante a digitação rápida.
- **Combos de Teclas:** O pressionamento simultâneo de teclas adjacentes dispara símbolos essenciais (ex.: `Q + W` = `Esc`, `O + P` = `Backspace`), reduzindo o movimento dos polegares e dos dedos em mais de 60%.
- **Camadas Funcionais:** Camadas dedicadas para números, navegação, mídia e símbolos ativadas com toques momentâneos no polegar.
- **Eficiência Energética no Bluetooth (BLE):** Otimização de perfis de energia no microcontrolador Nordic nRF52840, permitindo meses de autonomia em baterias LiPo compactas.

```
/* Disposição da Matriz de 34 Teclas */
      Mão Esquerda                Mão Direita
[ Q  W  E  R  T ]          [ Y  U  I  O  P ]
[ A  S  D  F  G ]          [ H  J  K  L  ; ]  <-- Home-row Mods
[ Z  X  C  V  B ]          [ N  M  ,  .  / ]
      [ NAV SYM ]          [ SPC NUM ]
```
