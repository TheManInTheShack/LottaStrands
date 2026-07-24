# ADR 002 — Godot as the UI layer

## Context
Needed a UI for curation, visualization, and eventually analysis. Options considered: web frontend (React/Vue), Plotly/Dash, native desktop app.

## Decision
Godot 4.x, exported to WebAssembly and served by nginx alongside the FastAPI backend.

## Reasons
- Godot's scene/signal architecture maps well to the graph-centric data model
- WebAssembly export means it runs in the browser without a separate app install
- Touch/mobile support is first-class; the primary use case is phone/tablet interaction
- The graph visualization work (future) is well-suited to Godot's 2D rendering
- Single codebase for all platforms (desktop dev, web deploy, mobile)

## Key UI conventions established
- No right-click context menus — phone users don't have right-click
- No hover-only interactions — touch has no hover state
- InsertStrip pattern: persistent tap target between cards (44px min height)
- `÷` symbol for insert; `×` for remove

## Deployment target
nginx on DigitalOcean: static files serve the Godot WebAssembly export; `/api/*` proxies to the FastAPI backend.
