---
title: Template Structure Pattern
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - CLAUDE.md
  - templates/
---

# Template Structure Pattern

Jinja2 template conventions for all pages.

## Template Hierarchy

```
base_layout.html  — HTML skeleton, CSS/JS CDN imports, sidebar nav
  └─ base.html    — Content area, flash messages, page blocks
       └─ page.html  — Actual page content
  └─ base_minimal.html — Login page only (no sidebar)
```

## Page Template Convention

```html
{% extends "base.html" %}
{% block content %}
  <!-- Page content -->
{% endblock %}
```

## Rules

1. **CSRF token** required in ALL POST forms: `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`
2. **No external JS files** — all JavaScript inline in `<script>` tags
3. **Icons:** Lucide via `<i data-lucide="icon-name"></i>` (Font Awesome only for legacy investment type icons)
4. **Responsive:** Use Tailwind responsive prefixes (`md:`, `lg:`)
5. **Dark theme only** — use design system color tokens
6. **Template directory:** `templates/{blueprint_name}/` matches blueprint
7. **Amounts:** Use `.amount` CSS class and Geist Mono font for money values

## Related

- [[design-system]]
- [[2026-01-15-no-spa]]
- [[route-handler]]
