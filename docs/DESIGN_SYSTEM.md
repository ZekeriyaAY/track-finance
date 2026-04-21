# Design System — Where's My Money?

> Felsefe: Ciddiyet ile samimiyet arasında denge. Para konusunda güven veren ama gün içinde açmaktan sıkılmayan bir arayüz.

## Prensipler

1. **Az renk, doğru yerde renk.** Renk vurgu içindir. Pozitif/negatif tutarlar ve primary action dışında renkli element yok.
2. **Hiyerarşi kritiktir.** Her sayfada tek bir "kahraman" bilgi. Kullanıcı 1 saniyede en önemli şeyi görmeli.
3. **Tabular nums her yerde.** Rakamlar alt alta geldiğinde noktalar hizalanmalı.
4. **Hareket anlam taşımalı.** Animasyonlar dekoratif değil, geçişleri anlamlandırmak için.
5. **Boşluk = lüks.** Sıkıştırmak yerine nefes aldırmak.

---

## Color Palette

### Backgrounds (Blue-neutral dark)
| Token | Hex | Kullanım |
|-------|-----|----------|
| `bg-base` | `#0d1117` | Sayfa arkaplani |
| `bg-surface` | `#161b22` | Kart, container |
| `bg-elevated` | `#1c2128` | Modal, dropdown, popover |
| `bg-overlay` | `#21262d` | Hover state, active row |

### Primary (Warm Amber)
| Token | Hex | Kullanım |
|-------|-----|----------|
| `primary` | `#e5884a` | Primary button, active link |
| `primary-hover` | `#d67a3c` | Primary hover state |
| `primary-muted` | `rgba(229, 136, 74, 0.12)` | Soft background (active nav, badge) |
| `primary-border` | `rgba(229, 136, 74, 0.3)` | Focus ring, active border |

### Semantic
| Token | Hex | Kullanım |
|-------|-----|----------|
| `positive` | `#6dba8a` | Gelir tutarı, başarı |
| `positive-muted` | `rgba(109, 186, 138, 0.12)` | Başarı toast background |
| `negative` | `#d4616e` | Gider tutarı, hata |
| `negative-muted` | `rgba(212, 97, 110, 0.12)` | Hata toast background |
| `warning` | `#d4a054` | Uyarı |
| `info` | `#5b9fd4` | Bilgi |

### Text
| Token | Hex | Kullanım |
|-------|-----|----------|
| `text-primary` | `#e6edf3` | Başlıklar, önemli metin |
| `text-secondary` | `#9ca3af` | Gövde metni |
| `text-muted` | `#6b7280` | Label, caption, placeholder |
| `text-on-primary` | `#0d1117` | Primary buton üzerindeki metin |

### Borders
| Token | Value | Kullanım |
|-------|-------|----------|
| `border-default` | `rgba(255, 255, 255, 0.08)` | Kart border, divider |
| `border-subtle` | `rgba(255, 255, 255, 0.04)` | Hafif ayırıcı |
| `border-focus` | `rgba(229, 136, 74, 0.5)` | Focus ring |

---

## Typography

### Font Stack
| Kullanım | Font | Fallback |
|----------|------|----------|
| UI, başlıklar, gövde | Geist Sans | system-ui, sans-serif |
| Rakamlar, tutarlar, kod | Geist Mono | ui-monospace, monospace |

### Loading
```html
<!-- Geist Sans & Mono from CDN -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/geist@1.3.1/dist/fonts/geist-sans/style.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/geist@1.3.1/dist/fonts/geist-mono/style.min.css">
```

### Scale
| Token | Size | Weight | Tracking | Kullanım |
|-------|------|--------|----------|----------|
| `display` | 32px / 2rem | 700 | -0.025em (tight) | Dashboard hero number |
| `heading-1` | 24px / 1.5rem | 600 | -0.025em (tight) | Sayfa başlığı |
| `heading-2` | 18px / 1.125rem | 600 | -0.015em | Section başlığı |
| `heading-3` | 15px / 0.9375rem | 500 | -0.01em | Kart başlığı |
| `body` | 14px / 0.875rem | 400 | normal | Genel gövde metni |
| `body-sm` | 13px / 0.8125rem | 400 | normal | Tablo hücreleri |
| `caption` | 12px / 0.75rem | 500 | 0.025em (wider) | Label, uppercase metin |
| `mono-amount` | inherit | 600 | normal | Para tutarları (Geist Mono) |

### Kurallar
- Para tutarı **ASLA** normal sans font ile gösterilmez → her zaman `font-mono tabular-nums`
- Başlıklarda `tracking-tight` (-0.025em)
- UPPERCASE metinlerde (caption) `tracking-wider` (+0.025em)
- Para tutarında minimum `font-semibold`, hero'da `font-bold`
- Line-height: başlıklar `1.2`, gövde `1.5`, tablo `1.4`

---

## Spacing System (4px base)

| Token | Value | Kullanım |
|-------|-------|----------|
| `space-0.5` | 2px | İnce ayırıcı |
| `space-1` | 4px | İkon ile metin arası |
| `space-2` | 8px | İç element padding |
| `space-3` | 12px | Compact padding |
| `space-4` | 16px | Standart padding |
| `space-5` | 20px | Kart iç padding |
| `space-6` | 24px | Section arası |
| `space-8` | 32px | Büyük section arası |
| `space-10` | 40px | Page padding (desktop) |
| `space-12` | 48px | Major section break |
| `space-16` | 64px | Page top/bottom |

### Spacing Kuralları
- Kart iç padding: `space-5` (20px)
- Kart arası gap: `space-4` (16px)
- Form field arası: `space-4` (16px)
- Tablo satır padding: `space-3` y, `space-4` x
- Page container padding: `space-6` (mobil), `space-10` (desktop)
- Sidebar genişlik: collapsed `space-16` (64px), expanded `240px`

---

## Border Radius

| Token | Value | Kullanım |
|-------|-------|----------|
| `radius-sm` | 6px | Input, badge, tag |
| `radius-md` | 8px | Button, dropdown |
| `radius-lg` | 12px | Card, modal |
| `radius-xl` | 16px | Large container, toast |
| `radius-full` | 9999px | Pill, avatar, toggle |

---

## Shadows

| Token | Value | Kullanım |
|-------|-------|----------|
| `shadow-sm` | `0 1px 2px rgba(0,0,0,0.3)` | Button, input |
| `shadow-md` | `0 4px 12px rgba(0,0,0,0.25)` | Card, dropdown |
| `shadow-lg` | `0 8px 24px rgba(0,0,0,0.35)` | Modal, toast |
| `shadow-glow` | `0 0 0 3px var(--border-focus)` | Focus ring |

---

## Components

### Buttons

| Variant | Background | Text | Border | Kullanım |
|---------|-----------|------|--------|----------|
| **Primary** | `primary` | `text-on-primary` | none | Sayfadaki tek ana aksiyon (Kaydet, Ekle) |
| **Secondary** | `transparent` | `text-primary` | `border-default` | İkincil aksiyonlar (İptal, Filtrele) |
| **Ghost** | `transparent` | `text-secondary` | none | Üçüncül (Düzenle, inline actions) |
| **Danger** | `negative-muted` | `negative` | none | Silme işlemleri |

**Kurallar:**
- Bir sayfada **en fazla 1** primary buton olmalı
- Buton boyutları: `sm` (28px h), `md` (36px h), `lg` (44px h)
- İkon + metin arası: `space-2` (8px)
- Minimum genişlik: metin boyutuna göre, padding `space-3` x (12px) `space-2` y (8px)
- Hover: hafif brightness artışı (105%)
- Active: scale(0.98) + brightness düşüşü
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

- Header: `heading-3` + `text-muted` alt açıklama
- Divider: `border-subtle` ile `my-4`
- Footer (opsiyonel): Muted background ile aksiyonlar

### Tables

| Özellik | Uygulama |
|---------|----------|
| Header | `caption` style, uppercase, `text-muted`, `border-b border-default` |
| Satır | `body-sm`, hover → `bg-overlay` |
| Amount kolonu | Sağa hizalı, `font-mono tabular-nums font-semibold`, sticky |
| Aksiyonlar | `...` butonu varsayılan gizli → satır hover'da belirir → tıklayınca dropdown açılır |
| Checkbox | 16x16px, `radius-sm`, `border-default` |
| Empty state | İllüstrasyon/ikon + samimi mesaj + CTA button |
| Zebra | Yok — hover yeterli, temiz görünüm |

**Amount Formatting:**
```
Gelir:  +1.234,56 ₺  (text-positive, font-mono font-semibold)
Gider:  -1.234,56 ₺  (text-negative, font-mono font-semibold)
Nötr:    1.234,56 ₺  (text-primary, font-mono font-semibold)
```

### Tags / Badges

```
┌──────────────┐
│  Tag Label   │  border: 1px solid (renk, %30 opacity)
└──────────────┘  background: transparent
                  text: renk, %80 opacity
                  radius: radius-full (pill)
                  padding: space-1 y, space-2 x
                  font: caption size
```

- Dolgu (fill) YOK — sadece ince renkli border
- Renkler: önceden tanımlı 6-8 renk paleti (tag oluşturulurken seçilir veya otomatik atanır)

### Toast Notifications

| Özellik | Değer |
|---------|-------|
| Pozisyon | Sağ üst |
| Genişlik | 360px max |
| Radius | `radius-xl` (16px) |
| Shadow | `shadow-lg` |
| Animation | slideIn sağdan (200ms ease-out) |
| Duration | Success: 4s, Error: 8s veya kalıcı (dismiss button) |
| Stack | Üst üste, max 3 görünür |

**Türler:**
- Success: `positive-muted` bg, `positive` left-border (3px), samimi mesaj
- Error: `negative-muted` bg, `negative` left-border, kalıcı, dismiss button
- Info: `bg-elevated`, `info` left-border
- Warning: amber tone, `warning` left-border

**Mesaj Dili (samimi):**
- ~~"Başarıyla eklendi."~~ → "Eklendi, güzel!"
- ~~"Bir hata oluştu."~~ → "Bir şeyler ters gitti, tekrar dener misin?"
- ~~"Silindi."~~ → "Kaldırıldı."
- ~~"Kaydedildi."~~ → "Tamam, kaydettim."

### Navigation (Sidebar)

```
┌──┐
│  │ Collapsed: 64px genişlik
│  │ İkon-only (20px icon, centered)
│  │ Toggle (click) → expanded (240px) overlay
│  │ Active item: primary-muted bg + primary icon
│  │ Background: bg-base (sayfa ile aynı)
│  │ Sağ border: border-subtle
│  │
│  │ Alt kısım: user avatar + settings
└──┘

Mobil: Hamburger → full-width drawer (soldan kayar)
```

### Form Inputs

| Özellik | Değer |
|---------|-------|
| Background | `bg-elevated` |
| Border | `border-default` |
| Radius | `radius-sm` (6px) |
| Height | 40px (md), 36px (sm) |
| Focus | `shadow-glow` (primary border-focus) |
| Placeholder | `text-muted` |
| Label | `caption` style, `text-secondary`, üstte |
| Error | `negative` border + altında error mesajı |

### Empty States

```
┌─────────────────────────────────┐
│                                 │
│         [Muted icon/illus]      │  İkon: 48px, text-muted opacity
│                                 │
│     "Henüz işlem eklenmemiş"    │  heading-3, text-secondary
│   "İlk işlemini ekleyerek       │  body, text-muted
│    başlayabilirsin."            │
│                                 │
│       [+ Yeni İşlem Ekle]      │  Primary button (tek CTA)
│                                 │
└─────────────────────────────────┘
```

### Loading States (Skeleton)

- Kart: `bg-overlay` rounded bloklar, pulse animation (1.5s)
- Tablo: 5 satır skeleton row, farklı genişliklerde
- Dashboard: Metric card'lar skeleton + chart placeholder
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

**Kurallar:**
- `prefers-reduced-motion` kontrolü her zaman eklenir
- 200ms üstü animasyon yok (sluggish hissettirmemeli)
- Counter animation sadece dashboard hero numbers'da

---

## Iconography (Lucide)

- **Size:** 16px (inline), 20px (nav, button), 24px (empty state), 48px (hero empty state)
- **Stroke:** 1.5px (varsayılan Lucide)
- **Color:** `currentColor` (parent'ın text rengini alır)
- **Alignment:** Metin ile `vertical-align: middle` veya flex `items-center`

Sık kullanılan ikonlar:
| Aksiyon | İkon |
|---------|------|
| Ekle | `plus` |
| Düzenle | `pencil` |
| Sil | `trash-2` |
| Filtre | `filter` |
| Arama | `search` |
| Gelir | `trending-up` |
| Gider | `trending-down` |
| Takvim | `calendar` |
| Kategori | `folder` |
| Tag | `tag` |
| Yatırım | `line-chart` |
| Ayarlar | `settings` |
| Çıkış | `log-out` |
| Menu (more) | `more-horizontal` |
| Kapat | `x` |
| Başarı | `check-circle` |
| Hata | `alert-circle` |

---

## Responsive Breakpoints

| Token | Width | Kullanım |
|-------|-------|----------|
| `sm` | 640px | Mobil landscape |
| `md` | 768px | Tablet |
| `lg` | 1024px | Desktop (sidebar gösterir) |
| `xl` | 1280px | Wide desktop |

### Mobil Adaptasyonlar
- Sidebar → hamburger drawer
- Tablo → horizontal scroll wrapper + sticky first col & amount col
- Kart grid → single column stack
- Modal → full-screen sheet (bottom sheet)
- Page padding: `space-4` (16px)
- Font size: body 14px'de kalır, heading-1 → 20px'e düşer

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

## Checklist — Implementasyon

- [x] Geist Sans + Mono font CDN eklenmesi
- [x] Lucide icons CDN veya SVG sprite eklenmesi
- [x] Tailwind config güncellenmesi (base_layout.html)
- [x] CSS custom properties tanımlanması (style.css)
- [x] Toast notification component (JS)
- [x] Skeleton loading component
- [x] Sidebar navigation component
- [x] Button variants (primary, secondary, ghost, danger)
- [x] Table component (hover actions, sticky amount)
- [x] Empty state component
- [x] Counter animation utility (JS)
- [x] Motion/transition utilities
