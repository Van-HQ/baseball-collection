# Baseball Card Collection Dashboard — Style Guide

## Design Philosophy

Dark, data-dense fintech aesthetic. Pure black backgrounds, subtle borders, and a gold accent carry the visual identity. Every element leans on glassmorphism (backdrop-filter blur), tight letter-spacing, and uppercase micro-labels to read as a professional financial dashboard.

---

## Color Palette

| Token | Value | Usage |
|---|---|---|
| `--bg-base` | `#000` | Page background |
| `--bg-card` | `#0d0d0d` | Sidebar, modals, panels |
| `--bg-hover` | `#1a1a1a` | Row hover, chips, inputs |
| `--bg-active` | `#222` | Active states |
| `--border` | `#1e1e1e` | Default dividers |
| `--border-light` | `#2d2d2d` | Lighter dividers, modal borders |
| `--text-primary` | `#fff` | Headings, values |
| `--text-secondary` | `#999` | Supporting text, nav items |
| `--text-muted` | `#555` | Labels, metadata, placeholders |
| `--accent` / `--gold` | `#d4a843` | Primary brand color — gold |
| `--accent-glow` | `rgba(212,168,67,0.12)` | Accent tint backgrounds |
| `--green` | `#22d36a` | Positive P/L, BUY signals |
| `--green-bg` | `rgba(34,211,106,0.1)` | Green tint backgrounds |
| `--red` | `#f25c5c` | Negative P/L, PASS signals |
| `--red-bg` | `rgba(242,92,92,0.1)` | Red tint backgrounds |
| `--yellow` | `#f5c842` | Wax, warnings, stars |
| `--yellow-bg` | `rgba(245,200,66,0.1)` | Yellow tint backgrounds |
| `--purple` | `#7dd3fc` | Ripped card type |
| `--purple-bg` | `rgba(125,211,252,0.1)` | Purple tint backgrounds |
| `--teal` | `#2dd4bf` | Accent variant |

---

## Typography

**Font family:** `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`

| Role | Size | Weight | Letter-spacing | Case |
|---|---|---|---|---|
| Stat card value | 28px | 900 | -1px | — |
| Modal hero value | 21px | 800 | -0.5px | — |
| Panel/modal title | 13–15px | 600–800 | -0.3px | — |
| Body / table rows | 12.5–13px | 400–600 | — | — |
| Micro-label (uppercase) | 9–10px | 700 | +0.6–0.8px | UPPERCASE |
| Badge / chip | 11px | 600–700 | — | — |
| Monospace (card numbers) | 11px | 400 | — | font-family: monospace |

**Key convention:** Labels above data values are always `9–10px`, `font-weight: 700`, `letter-spacing: 0.6–0.8px`, `text-transform: uppercase`, `color: var(--text-muted)`. Values are large, heavy, and tight-tracked.

---

## Layout

### Shell
- **Sidebar:** 220px fixed width, collapsible. `background: var(--bg-card)`, `border-right: 1px solid var(--border)`.
- **Topbar:** 56px, `position: absolute`, `backdrop-filter: blur(18px)`, `background: rgba(0,0,0,0.6)`. Floats above content.
- **Content area:** `padding: 24px`, `padding-top: 80px` to clear topbar, `overflow-y: auto`.

### Grid System
- **Stats row:** `grid-template-columns: repeat(6, 1fr)`, `gap: 14px` — collapses to 3-col at 1200px, 2-col on mobile.
- **2-col grid:** `grid-template-columns: 1fr 1fr`, `gap: 18px`.
- **3-col grid:** `grid-template-columns: 2fr 1fr 1fr`, `gap: 18px`.

---

## Components

### Stat Card
```
background: rgba(13,13,13,0.55)
backdrop-filter: blur(10px)
border-radius: 10px
padding: 18px 20px
box-shadow: 0 0 0 1px var(--border)
```
- 2px colored accent bar at top (36px wide, color matches card variant).
- Hover: lifts `translateY(-1px)`, border brightens to `--border-light`, gold shimmer sweep animation.
- Variants: default, `.green`, `.red`, `.yellow`, `.purple`, `.teal`, `.blue` (gold accent).

### Panel
```
background: rgba(13,13,13,0.5)
backdrop-filter: blur(8px)
border: 1px solid var(--border)
border-radius: 12px
```
- Panel header: `padding: 14px 18px`, `border-left: 2px solid var(--accent)` — the gold left rule is the panel's signature.
- Panel title: `13px`, `font-weight: 600`.

### Chip / Filter Tab
```
background: var(--bg-hover)
border: 1px solid var(--border-light)
border-radius: 20px
padding: 3px 9px
font-size: 11px
```
Active state: `background: var(--accent-glow)`, `border-color: rgba(212,168,67,0.35)`, `color: var(--accent)`.

### Badge
```
background: var(--accent-glow)
color: var(--accent)
border: 1px solid rgba(212,168,67,0.3)
border-radius: 20px
padding: 3px 9px
font-size: 11px
font-weight: 600
```

### Table
- `font-size: 12.5px`, `border-collapse: collapse`.
- `thead th`: `10px`, `font-weight: 700`, `letter-spacing: 0.8px`, `text-transform: uppercase`, `color: var(--text-muted)`, sticky with `background: rgba(0,0,0,0.96)`.
- Row hover: `background: var(--bg-hover)`.
- Sort indicator: `::after` pseudo with `↑`/`↓` in `var(--accent)`.
- P/L cells: `.pl-pos` = `var(--green)`, `.pl-neg` = `var(--red)`, both `font-weight: 600`.

### Search Input
```
background: var(--bg-hover)
border: 1px solid var(--border-light)
border-radius: 8px
padding: 7px 12px 7px 32px
font-size: 13px
```
Focus: `border-color: var(--accent)`. Leading search icon via `::before` pseudo-element.

### Modal
```
background: var(--bg-card)
border: 1px solid var(--border-light)
border-radius: 14px
box-shadow: 0 28px 72px rgba(0,0,0,0.7)
```
- Backdrop: `background: rgba(0,0,0,0.7)`, `backdrop-filter: blur(4px)`.
- Header: `border-left: 3px solid var(--accent)` — the gold left rule, same pattern as panels.
- Enter animation: opacity 0→1, `translateY(6px→0)`, 160ms.

### Toast
```
background: rgba(10,10,10,0.96)
border: 1px solid #2d2d2d
border-radius: 10px
backdrop-filter: blur(16px)
```
Slides in from right (`translateX(16px→0)`), slides out to right. Bottom-right corner, stacks vertically.

---

## Charts (Chart.js 4.x)

### Shared Style Conventions
- **Tooltip:** `background: rgba(5,5,5,0.97)`, `border: 1px solid #282828`, `cornerRadius: 10`, `displayColors: false`. Title white/800, body `#666`.
- **Grid lines:** `color: rgba(255,255,255,0.045)`, `lineWidth: 1`, no ticks.
- **Axis ticks:** `color: #484848`, `font-size: 9.5px`.
- **Crosshair:** Custom plugin draws a `rgba(212,168,67,0.22)` dashed vertical line on hover.
- **Legend pills:** `useBorderRadius: true`, `borderRadius: 4`, `boxWidth: 10`, `boxHeight: 10`.

### Line Charts
- Gradient fill under line: top `rgba(r,g,b,0.38)` → mid `rgba(r,g,b,0.14)` → bottom `rgba(r,g,b,0)`.
- `tension: 0.42`, `pointRadius: 0`, `borderWidth: 2`.

### Horizontal Bar Charts (P/L by Player)
- Solid fill: positive `rgba(34,211,106,0.72)`, negative `rgba(242,92,92,0.72)`.
- Right-edge border only: `borderWidth: { top:0, right:1.5, bottom:0, left:0 }`.
- `borderRadius: 4`, `barThickness: 14`.

### Top Movers (zero-anchored gradient)
- Gradient anchored at the zero pixel on the x-axis, not the chart edge.
- Positive: `rgba(34,211,106,0.08)` at zero → `rgba(34,211,106,0.92)` at bar end.
- Negative: `rgba(242,92,92,0.08)` at zero → `rgba(242,92,92,0.92)` at bar end.

---

## Motion & Animation

| Animation | Details |
|---|---|
| Page transition | `opacity 0→1`, `translateY(6px→0)`, 160ms ease |
| Row enter | Same as page, per-row stagger |
| Stat card hover | `translateY(-1px)`, 200ms |
| Stat card shimmer | Gold diagonal gradient sweeps across on hover, 650ms |
| Progress bar fill | `width` transition, 900ms `cubic-bezier(.25,.46,.45,.94)` |
| Toast in | `translateX(16px→0)`, 280ms |
| Toast out | `translateX(0→16px)`, 220ms |
| Sidebar collapse | `width` transition, 220ms `cubic-bezier(.4,0,.2,1)` |
| Chip/tab | `all` transition, 150ms |

---

## Surface Texture

A subtle SVG fractalNoise grain overlay sits at `z-index: 9998`, `opacity: 0.05`, `pointer-events: none`. It covers the full viewport and gives the dark background a slight tactile texture rather than pure flat black.

---

## Scrollbar
- `width/height: 5px`, transparent track.
- Thumb: `rgba(255,255,255,0.07)`, hover → `rgba(212,168,67,0.5)` (gold).

---

## Spacing Conventions

| Context | Value |
|---|---|
| Panel header padding | `14px 18px` |
| Panel content padding | `16px 18px` |
| Table cell padding | `10px 14px` |
| Stats row gap | `14px` |
| Grid gap | `18px` |
| Sidebar nav item padding | `9px 10px` |
| Border radius — cards/modals | `12–14px` |
| Border radius — chips/badges | `20px` (pill) |
| Border radius — buttons/inputs | `8px` |
| Border radius — tags | `4px` |
