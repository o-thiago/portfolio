+++
title = "GPMecatrônica Cards & Research Platform"
description = "Full-stack web application and member card generation platform for the Mechatronics Research Group at IFRO."
date = 2025-04-10
weight = 3

[extra]
category = "Web / Full-Stack"
github = "https://github.com/o-thiago/gpm-cards"
stack = ["Next.js 14", "TypeScript", "PostgreSQL", "Tailwind CSS", "Nix / process-compose", "Docker"]
+++

## Overview

Developed for the **GPMecatrônica** research group at the Federal Institute of Rondônia (IFRO), this platform serves as an interactive showcase, member credential system, and dynamic card generator for scientific events and member profiles.

---

## Technical Stack & Architectural Decisions

- **Full-Stack Architecture:** Built on **Next.js** App Router with **TypeScript**, implementing server actions, dynamic image rendering, and strictly typed ORM schemas.
- **Nix-Powered Dev Environment:** Configured a local multi-service orchestration pipeline via `flake.nix` and `process-compose-flake`, provisioning local PostgreSQL instances, prefetching dependencies, and standardizing runtimes across the entire research team with zero manual environment configuration.
- **Containerization & CI/CD:** Layered multi-stage Docker container builds via Nix (`dockerTools.buildLayeredImage`), producing deterministic, minimal-footprint deployment images.

```nix
/* Declarative process composition with process-compose */
services.postgres."gpm-cards-db" = {
  enable = true;
  initialDatabases = [ { name = "gpm-cards"; } ];
  initialScript.after = ''
    CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'postgres';
  '';
};
```

---

## Impact

Standardized member profile generation, event participation credentials, and streamlined onboarding for new research students joining the lab.
