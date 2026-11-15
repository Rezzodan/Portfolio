# Client Mini App (two messenger platforms)

![Cover](./assets/cover.png)
## Screenshots

![Client menu](./assets/ui-menu.png)

Mobile client menu with deal status chip (demo/fixture data — no real client PII).

**Role:** Frontend / product delivery  
**Status:** Production  
**Stack:** React · TypeScript · Vite · MUI · React Query · Telegram WebApp + second-platform bridge

## Overview

Client cabinet inside messengers: onboarding without a separate native app store release.

## What I built

- Full client journey: registration → certificate → e-signature → bureau report upload → deal status
- One codebase for a **Telegram Mini App** and a mini app on **a second messenger platform**
- Platform adapter / bridge layer for launch params and user identity
- Production deploys via Docker images (with version boot-markers)

## Results

- Self-serve onboarding for end clients
- Dual-platform delivery without maintaining two products

## Hard problem

**The second platform's webview broke when the Telegram SDK was injected** — infinite loaders / “failed to get profile”.  
**Fix:** platform-specific bridge, never load Telegram scripts on the other platform, boot markers, and mandatory image rebuilds (hotfixes via `docker cp` disappeared after recreate).

## Confidentiality

No source code or secrets. UI of authenticated client cabinets is not shown (PII risk).
