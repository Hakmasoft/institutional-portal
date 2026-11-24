# Design system

The portal uses Tailwind CSS v4 (via `django-tailwind-cli`) and
`django-cotton` for component abstraction. No CSS framework beyond
Tailwind; no component library like Bootstrap or DaisyUI.

## Decisions log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| CSS framework | Tailwind CSS v4 | Purged bundle ~10KB; battle-tested; solves 80% of layout/spacing/color |
| Token config | Tailwind `@theme` in `assets/css/source.css` | v4 CSS-first config; tokens are real CSS custom properties |
| Component abstraction | django-cotton | HTML-like syntax (`<c-button>`); named slots; no class soup in templates |
| Build tool | `django-tailwind-cli` standalone binary | No Node.js, no npm; one management command |
| Visual direction | Modern academic (blue primary, 6px radii, subtle shadows) | Trust + approachability |
| Dark mode | Light only in v1; tokens structured for later | Doubles visual QA; not a top user ask |
| Icons | Inline SVG only, sparingly | Icon fonts are 100KB+; SVG earns weight only where it pays |
| Wordmark | Text-only for now | Branding decision deferred until logo exists |
| Fonts | System stack (Tailwind default `font-sans`) | No webfont cost; native on every device |
| Utility classes in templates | Allowed only for layout wrappers | Component styling belongs inside Cotton components |

## Tokens

Defined in `@theme { ... }` in `assets/css/source.css`. Tailwind v4
generates utilities from them automatically:

- `--color-primary` → `bg-primary`, `text-primary`, `border-primary`
- `--color-danger` → `bg-danger`, `text-danger`, etc.
- `--color-present` → `bg-present`, `text-present`, etc.
- `--container-page` → `max-w-(--container-page)` for page width

Never hardcode a color value in a template or component.

## Cotton components

All components are in `templates/cotton/`.

| File | Tag | Usage |
|------|-----|-------|
| `button.html` | `<c-button>` | Primary, secondary, danger, ghost variants |
| `badge.html` | `<c-badge>` | Present, absent, late, excused, neutral variants |
| `card.html` | `<c-card>` | `padded` attribute for larger padding |
| `flash.html` | `<c-flash>` | Success, error, warning, and info variants |
| `field.html` | `<c-field>` | Label, name, help, and error attributes |
| `empty_state.html` | `<c-empty-state>` | Title attribute with descriptive slot |
| `nav.html` | `<c-nav>` | No attributes; role-aware |

## Accessibility commitments

- All interactive elements reachable via keyboard
- `:focus-visible` shows a 2px outline (`outline-primary`)
- Skip-to-content link in `base.html`
- `<main id="main-content" tabindex="-1">`
- `<nav aria-label="Main navigation">`
- `role="status"` on flash messages
- Form fields always have `<label for>`
- Touch targets at least 44px
- `prefers-reduced-motion: reduce` is respected
- Color is never the only signal

## What NOT to add

- No CSS framework beyond Tailwind
- No component library that wraps Tailwind
- No CSS-in-JS or additional PostCSS plugins
- No web fonts
- No icon font libraries
- No dark mode until explicitly revisited

## Development workflow

- Dev: `python manage.py tailwind runserver`
- Separate: `python manage.py tailwind watch` + `runserver`
- Production: `python manage.py tailwind build` then `collectstatic`
- Rebuild manually: `python manage.py tailwind build`
