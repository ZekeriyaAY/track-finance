# Design System — Where's My Money?

> Philosophy: A balance between seriousness and approachability. An interface that inspires trust when it comes to money, yet never feels tedious to open throughout the day.

## Principles

1. **Few colors, placed with intention.** Color is for emphasis. No colored elements beyond positive/negative amounts and the primary action.
2. **Hierarchy is critical.** Each page has a single "hero" piece of information. The user should see the most important thing within 1 second.
3. **Tabular nums everywhere.** When numbers are stacked vertically, decimal points must align.
4. **Motion must carry meaning.** Animations are not decorative — they exist to clarify transitions.
5. **Whitespace = luxury.** Let the layout breathe instead of cramming elements together.

---

## Color Palette

### Backgrounds (Blue-neutral dark)
| Token | Hex | Usage |
|-------|-----|-------|
| `bg-base` | `#0d1117` | Page background |
| `bg-surface` | `#161b22` | Card, container |
| `bg-elevated` | `#1c2128` | Modal, dropdown, popover |
| `bg-overlay` | `#21262d` | Hover state, active row |

### Primary (Warm Amber)
| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | `#e5884a` | Primary button, active link |
| `primary-hover` | `#d67a3c` | Primary hover state |
| `primary-muted` | `rgba(229, 136, 74, 0.12)` | Soft background (active nav, badge) |
| `primary-border` | `rgba(229, 136, 74, 0.3)` | Focus ring, active border |

### Semantic
| Token | Hex | Usage |
|-------|-----|-------|
| `positive` | `#6dba8a` | Income amount, success |
| `positive-muted` | `rgba(109, 186, 138, 0.12)` | Success toast background |
| `negative` | `#d4616e` | Expense amount, error |
| `negative-muted` | `rgba(212, 97, 110, 0.12)` | Error toast background |
| `warning` | `#d4a054` | Warning |
| `info` | `#5b9fd4` | Info |

### Text
| Token | Hex | Usage |
|-------|-----|-------|
| `text-primary` | `#e6edf3` | Headings, important text |
| `text-secondary` | `#9ca3af` | Body text |
| `text-muted` | `#6b7280` | Label, caption, placeholder |
| `text-on-primary` | `#0d1117` | Text on primary button |

### Borders
| Token | Value | Usage |
|-------|-------|-------|
| `border-default` | `rgba(255, 255, 255, 0.08)` | Card border, divider |
| `border-subtle` | `rgba(255, 255, 255, 0.04)` | Subtle separator |
| `border-focus` | `rgba(229, 136, 74, 0.5)` | Focus ring |

---

## Typography

### Font Stack
| Usage | Font | Fallback |
|-------|------|----------|
| UI, headings, body | Geist Sans | system-ui, sans-serif |
| Numbers, amounts, code | Geist Mono | ui-monospace, monospace |

### Loading
```html
<!-- Geist Sans & Mono from CDN -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/geist@1.3.1/dist/fonts/geist-sans/style.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/geist@1.3.1/dist/fonts/geist-mono/style.min.css">
```

### Scale
| Token | Size | Weight | Tracking | Usage |
|-------|------|--------|----------|-------|
| `display` | 32px / 2rem | 700 | -0.025em (tight) | Dashboard hero number |
| `heading-1` | 24px / 1.5rem | 600 | -0.025em (tight) | Page title |
| `heading-2` | 18px / 1.125rem | 600 | -0.015em | Section title |
| `heading-3` | 15px / 0.9375rem | 500 | -0.01em | Card title |
| `body` | 14px / 0.875rem | 400 | normal | General body text |
| `body-sm` | 13px / 0.8125rem | 400 | normal | Table cells |
| `caption` | 12px / 0.75rem | 500 | 0.025em (wider) | Label, uppercase text |
| `mono-amount` | inherit | 600 | normal | Money amounts (Geist Mono) |

### Rules
- Money amounts must **NEVER** be displayed in a regular sans font — always use `font-mono tabular-nums`
- Use `tracking-tight` (-0.025em) for headings
- Use `tracking-wider` (+0.025em) for UPPERCASE text (caption)
- Money amounts require at minimum `font-semibold`; hero amounts use `font-bold`
- Line-height: headings `1.2`, body `1.5`, tables `1.4`

---

## Spacing System (4px base)

| Token | Value | Usage |
|-------|-------|-------|
| `space-0.5` | 2px | Thin separator |
| `space-1` | 4px | Gap between icon and text |
| `space-2` | 8px | Inner element padding |
| `space-3` | 12px | Compact padding |
| `space-4` | 16px | Standard padding |
| `space-5` | 20px | Card inner padding |
| `space-6` | 24px | Between sections |
| `space-8` | 32px | Between large sections |
| `space-10` | 40px | Page padding (desktop) |
| `space-12` | 48px | Major section break |
| `space-16` | 64px | Page top/bottom |

### Spacing Rules
- Card inner padding: `space-5` (20px)
- Gap between cards: `space-4` (16px)
- Gap between form fields: `space-4` (16px)
- Table row padding: `space-3` y, `space-4` x
- Page container padding: `space-6` (mobile), `space-10` (desktop)
- Sidebar width: collapsed `space-16` (64px), expanded `240px`

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `radius-sm` | 6px | Input, badge, tag |
| `radius-md` | 8px | Button, dropdown |
| `radius-lg` | 12px | Card, modal |
| `radius-xl` | 16px | Large container, toast |
| `radius-full` | 9999px | Pill, avatar, toggle |

---

## Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-sm` | `0 1px 2px rgba(0,0,0,0.3)` | Button, input |
| `shadow-md` | `0 4px 12px rgba(0,0,0,0.25)` | Card, dropdown |
| `shadow-lg` | `0 8px 24px rgba(0,0,0,0.35)` | Modal, toast |
| `shadow-glow` | `0 0 0 3px var(--border-focus)` | Focus ring |

---

## Components

### Buttons

| Variant | Background | Text | Border | Usage |
|---------|-----------|------|--------|-------|
| **Primary** | `primary` | `text-on-primary` | none | The single main action on a page (Save, Add) |
| **Secondary** | `transparent` | `text-primary` | `border-default` | Secondary actions (Cancel, Filter) |
| **Ghost** | `transparent` | `text-secondary` | none | Tertiary actions (Edit, inline actions) |
| **Danger** | `negative-muted` | `negative` | none | Delete operations |

**Rules:**
- A page should have **at most 1** primary button
- Button sizes: `sm` (28px h), `md` (36px h), `lg` (44px h)
- Gap between icon and text: `space-2` (8px)
- Minimum width: based on text size, padding `space-3` x (12px) `space-2` y (8px)
- Hover: slight brightness increase (105%)
- Active: scale(0.98) + brightness decrease
- Transition: `all 150ms ease`

### Cards

```
┌─────────────────────────────┐  border: border-default
│  padding: space-5 (20px)    │  background: bg-surface
│                             │  radius: radius-lg (12px)
│  [content]                  │  shadow: shadow-md
│                             │  hover: translateY(-2px) + shadow-lg
└─────────────────────────────┘
```

- Header: `heading-3` + `text-muted` subtitle
- Divider: `border-subtle` with `my-4`
- Footer (optional): Actions on a muted background

### Tables

| Property | Implementation |
|----------|----------------|
| Header | `caption` style, uppercase, `text-muted`, `border-b border-default` |
| Row | `body-sm`, hover → `bg-overlay` |
| Amount column | Right-aligned, `font-mono tabular-nums font-semibold`, sticky |
| Actions | `...` button hidden by default → appears on row hover → click opens dropdown |
| Checkbox | 16x16px, `radius-sm`, `border-default` |
| Empty state | Illustration/icon + friendly message + CTA button |
| Zebra | None — hover is sufficient, keeps a clean look |

**Amount Formatting:**
```
Income:   +1.234,56 ₺  (text-positive, font-mono font-semibold)
Expense:  -1.234,56 ₺  (text-negative, font-mono font-semibold)
Neutral:   1.234,56 ₺  (text-primary, font-mono font-semibold)
```

### Tags / Badges

```
┌──────────────┐
│  Tag Label   │  border: 1px solid (color, 30% opacity)
└──────────────┘  background: transparent
                  text: color, 80% opacity
                  radius: radius-full (pill)
                  padding: space-1 y, space-2 x
                  font: caption size
```

- NO fill — only a thin colored border
- Colors: a predefined palette of 6-8 colors (selected or auto-assigned when creating a tag)

### Toast Notifications

| Property | Value |
|----------|-------|
| Position | Top right |
| Width | 360px max |
| Radius | `radius-xl` (16px) |
| Shadow | `shadow-lg` |
| Animation | slideIn from right (200ms ease-out) |
| Duration | Success: 4s, Error: 8s or persistent (dismiss button) |
| Stack | Stacked, max 3 visible |

**Types:**
- Success: `positive-muted` bg, `positive` left-border (3px), friendly message
- Error: `negative-muted` bg, `negative` left-border, persistent, dismiss button
- Info: `bg-elevated`, `info` left-border
- Warning: amber tone, `warning` left-border

**Message Tone (friendly):**
- ~~"Successfully added."~~ → "Added, nice!"
- ~~"An error occurred."~~ → "Something went wrong, want to try again?"
- ~~"Deleted."~~ → "Removed."
- ~~"Saved."~~ → "Got it, saved."

### Navigation (Sidebar)

```
┌──┐
│  │ Collapsed: 64px width
│  │ Icon-only (20px icon, centered)
│  │ Toggle (click) → expanded (240px) overlay
│  │ Active item: primary-muted bg + primary icon
│  │ Background: bg-base (same as page)
│  │ Right border: border-subtle
│  │
│  │ Bottom section: user avatar + settings
└──┘

Mobile: Hamburger → full-width drawer (slides in from left)
```

### Form Inputs

| Property | Value |
|----------|-------|
| Background | `bg-elevated` |
| Border | `border-default` |
| Radius | `radius-sm` (6px) |
| Height | 40px (md), 36px (sm) |
| Focus | `shadow-glow` (primary border-focus) |
| Placeholder | `text-muted` |
| Label | `caption` style, `text-secondary`, above input |
| Error | `negative` border + error message below |

### Empty States

```
┌─────────────────────────────────┐
│                                 │
│         [Muted icon/illus]      │  Icon: 48px, text-muted opacity
│                                 │
│     "No transactions yet"       │  heading-3, text-secondary
│   "Get started by adding        │  body, text-muted
│    your first transaction."     │
│                                 │
│       [+ Add Transaction]       │  Primary button (single CTA)
│                                 │
└─────────────────────────────────┘
```

### Loading States (Skeleton)

- Card: `bg-overlay` rounded blocks, pulse animation (1.5s)
- Table: 5 skeleton rows, varying widths
- Dashboard: Metric card skeletons + chart placeholder
- Animation: `opacity 0.4 → 1 → 0.4` loop (subtle pulse)

---

## Micro-interactions & Motion

| Element | Animation | Duration | Easing |
|---------|-----------|----------|--------|
| Card hover | `translateY(-2px)` | 200ms | ease-out |
| Button press | `scale(0.98)` | 100ms | ease-in |
| Toast enter | `translateX(100%) → 0` | 200ms | ease-out |
| Toast exit | `opacity 1 → 0` + `translateY(-8px)` | 150ms | ease-in |
| Number counter | Count-up animation | 600ms | ease-out |
| Skeleton pulse | `opacity 0.4 ↔ 1` | 1500ms | ease-in-out |
| Sidebar toggle | `width 64px → 240px` | 200ms | ease-out |
| Dropdown open | `opacity 0 → 1` + `translateY(-4px) → 0` | 150ms | ease-out |
| Page transition | `opacity 0.5 → 1` | 100ms | ease |

**Rules:**
- `prefers-reduced-motion` check is always included
- No animation longer than 200ms (must not feel sluggish)
- Counter animation only on dashboard hero numbers

---

## Iconography (Lucide)

- **Size:** 16px (inline), 20px (nav, button), 24px (empty state), 48px (hero empty state)
- **Stroke:** 1.5px (Lucide default)
- **Color:** `currentColor` (inherits text color from parent)
- **Alignment:** `vertical-align: middle` with text, or flex `items-center`

Commonly used icons:
| Action | Icon |
|--------|------|
| Add | `plus` |
| Edit | `pencil` |
| Delete | `trash-2` |
| Filter | `filter` |
| Search | `search` |
| Income | `trending-up` |
| Expense | `trending-down` |
| Calendar | `calendar` |
| Category | `folder` |
| Tag | `tag` |
| Investment | `line-chart` |
| Settings | `settings` |
| Log out | `log-out` |
| Menu (more) | `more-horizontal` |
| Close | `x` |
| Success | `check-circle` |
| Error | `alert-circle` |

---

## Responsive Breakpoints

| Token | Width | Usage |
|-------|-------|-------|
| `sm` | 640px | Mobile landscape |
| `md` | 768px | Tablet |
| `lg` | 1024px | Desktop (shows sidebar) |
| `xl` | 1280px | Wide desktop |

### Mobile Adaptations
- Sidebar → hamburger drawer
- Table → horizontal scroll wrapper + sticky first col & amount col
- Card grid → single column stack
- Modal → full-screen sheet (bottom sheet)
- Page padding: `space-4` (16px)
- Font size: body stays at 14px, heading-1 → reduced to 20px

---

## Tailwind Config Mapping

```javascript
// tailwind.config (base_layout.html inline)
tailwind.config = {
  theme: {
    extend: {
      colors: {
        base: '#0d1117',
        surface: '#161b22',
        elevated: '#1c2128',
        overlay: '#21262d',
        primary: {
          DEFAULT: '#e5884a',
          hover: '#d67a3c',
          muted: 'rgba(229, 136, 74, 0.12)',
        },
        positive: {
          DEFAULT: '#6dba8a',
          muted: 'rgba(109, 186, 138, 0.12)',
        },
        negative: {
          DEFAULT: '#d4616e',
          muted: 'rgba(212, 97, 110, 0.12)',
        },
        warning: '#d4a054',
        info: '#5b9fd4',
      },
      fontFamily: {
        sans: ['Geist Sans', 'system-ui', 'sans-serif'],
        mono: ['Geist Mono', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        sm: '6px',
        md: '8px',
        lg: '12px',
        xl: '16px',
      },
      spacing: {
        // 4px base - Tailwind already uses 4px base
      },
      boxShadow: {
        sm: '0 1px 2px rgba(0,0,0,0.3)',
        md: '0 4px 12px rgba(0,0,0,0.25)',
        lg: '0 8px 24px rgba(0,0,0,0.35)',
        glow: '0 0 0 3px rgba(229, 136, 74, 0.3)',
      },
    },
  },
}
```

---

## Checklist — Implementation

- [x] Add Geist Sans + Mono font CDN
- [x] Add Lucide icons CDN or SVG sprite
- [x] Update Tailwind config (base_layout.html)
- [x] Define CSS custom properties (style.css)
- [x] Toast notification component (JS)
- [x] Skeleton loading component
- [x] Sidebar navigation component
- [x] Button variants (primary, secondary, ghost, danger)
- [x] Table component (hover actions, sticky amount)
- [x] Empty state component
- [x] Counter animation utility (JS)
- [x] Motion/transition utilities
