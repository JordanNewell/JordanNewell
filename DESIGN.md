# JordanNewell (profile/masthead) — Visual Design Guide

GitHub profile register of public work. Identity: NEWELL Brand System verbatim — this
surface represents Jordan himself in fleet-consistent brand. Recorded from the shipped
masthead SVG assets.

## Palette (NEWELL Brand System — verbatim)

| Token | Hex | Role |
|---|---|---|
| background | `#0A0A0A` | Masthead canvas |
| surface | `#0F0F0F` | Cards, badges |
| text | `#FFFFFF` | Primary type |
| muted | `#A0A0A0` | Secondary type, rules |
| border | `#1F1F1F` | Edge definition (no shadows for depth) |
| primary | `#00FF41` | The green — masthead accents, dividers |
| accent | `#1AFF72` | Accent lift — discrete highlights, never blended |

Constraints: no pure `#000000`, no pure `#00FF00`, no indigo/violet defaults, no Inter
display, no gradients. Source of truth: `10_PROJECTS/brand-system/` in the vault.

## Rules

- Green is accent, not field: masthead stays black/white/gray with green wayfinding.
- Green on dark only (≈12:1 on `#0A0A0A`); never green type on GitHub's light default
  mode (fails at ~1.4:1).
- Keep asset palettes locked to these seven tokens — profile art is brand surface.
