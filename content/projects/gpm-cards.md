+++
title = "GPMecatrônica Cards Platform"
description = "Web application built with Next.js and PostgreSQL for member profiles and card generation at GPMecatrônica (IFRO)."
date = 2025-04-10
weight = 2

[extra]
category = "Web / Full-Stack"
repo = "gpm-cards"
stack = ["Next.js", "TypeScript", "PostgreSQL", "Tailwind CSS", "Nix", "Docker"]
+++

## What is the project?

A web application developed for the **GPMecatrônica** research group at IFRO (Porto Velho Calama Campus). The system manages lab member registrations, showcases member profiles, and generates digital ID cards for academic events.

---

## Technical Details

- **Frontend & Backend:** Built using **Next.js** (App Router) and **TypeScript**, with typed database schemas and Tailwind CSS.
- **Local Services via Nix:** Used `process-compose` in Nix Flakes to automate spinning up local PostgreSQL instances during development. This allows other lab members to get the project running with a single command without having to manually install and configure PostgreSQL on their machines.
- **Docker:** Configured multi-stage Docker builds to keep production deployments lightweight and consistent.

```nix
/* Local PostgreSQL service setup using process-compose */
services.postgres."gpm-cards-db" = {
  enable = true;
  initialDatabases = [ { name = "gpm-cards"; } ];
  initialScript.after = ''
    CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'postgres';
  '';
};
```

---

## Links

- **Repository:** {{ github_link(repo="gpm-cards") }}
- **Author:** {{ author_link() }}
