---
name: css-refactoring
description: Refactor and optimize CSS code for maintainability, performance, and modern standards compliance.
eval_cases:
  - id: 1
    description: "A legacy stylesheet contains 2000+ lines with hardcoded hex colors, px spacing, and multiple !important overrides. Extract design tokens, flatten specificity, and prepare for dark mode."
    expected: "CSS custom properties for all tokens, BEM/utility naming, zero !important, prefers-color-scheme support, no layout breakage."
  - id: 2
    description: "A component library uses float-based layouts, 12-column grid with clearfix hacks, and explicit media queries for each breakpoint. Migrate to modern CSS Grid with container queries."
    expected: "CSS Grid implementation, container queries replacing media queries, logical properties for RTL support, responsive without explicit breakpoints."
  - id: 3
    description: "An animated dashboard has 15 JavaScript-driven animations, complex hover effects, and font loading causing FOIT. Optimize for 60fps, accessibility, and font performance."
    expected: "transform/opacity-only animations, will-change hints, reduced-motion respect, font-display: swap, variable font subsetting."
  - id: 4
    description: "A CSS codebase uses SCSS nesting (5+ levels deep), duplicate selectors, and PurgeCSS-unsafe patterns. Clean nesting, deduplicate, and prepare for native CSS."
    expected: "Native CSS nesting (max 3 levels), zero duplicate rules, PurgeCSS-safe class names, removed SCSS-specific syntax."
---

# CSS Refactoring & Optimization Skill

## Design Tokens

Extract hardcoded values into CSS custom properties:

```css
:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-surface: #ffffff;
  --color-text: #1f2937;
  --color-text-muted: #6b7280;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-8: 2rem;

  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --leading-tight: 1.25;
}
```

Migrate hardcoded values:
- `color: #fff` → `color: var(--color-surface)`
- `padding: 16px` → `padding: var(--space-4)`
- `font-size: 14px` → `font-size: var(--text-sm)`

## Dead CSS Elimination

Detect + remove unused selectors:

1. **Static analysis**: Use PurgeCSS, uncss, or csscss
2. **Coverage tool**: Chrome DevTools Coverage tab
3. **Pattern cleanup**:
   ```css
   /* Remove */
   .legacy-widget { }
   
   /* Refactor to */
   .component { }
   ```

Safe selectors for PurgeCSS:
- Use meaningful class names (`.btn-primary`, not `.b1`)
- Avoid dynamic attributes: `[class*="icon-"]` needs safelist
- Comment-based purge markers: `/* purgecss ignore */`

## Specificity Management

Flatten selector specificity:

```css
/* Bad: high specificity */
#header .nav ul li a.link.active { }
nav ul li a { }

/* Good: low specificity */
.nav__link--active { }
```

Eliminate `!important`:
1. Increase specificity naturally
2. Use CSS custom properties for overrides
3. Cascade w/ later rules

BEM naming:
```
Block:    .card
Element:  .card__title
Modifier: .card--featured
```

Utility class pattern (Tailwind-style):
```css
.flex { display: flex; }
.items-center { align-items: center; }
.gap-4 { gap: var(--space-4); }
```

## Layout Modernization

### Float → Flexbox
```css
/* Old */
.float-left { float: left; }
.clearfix::after { content: ''; clear: both; }

/* Modern */
.flex { display: flex; }
```

### Flexbox → Grid
```css
/* Flexbox column layout */
.flex-col { display: flex; flex-direction: column; }

/* Grid for complex layouts */
.grid-auto-fit {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-4);
}
```

### Grid template areas
```css
.layout {
  display: grid;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  grid-template-columns: 250px 1fr;
}
```

## CSS Performance

### Containment
```css
.widget {
  contain: layout style paint;
  content-visibility: auto;
}
```

### Will-change
```css
.animated-element {
  will-change: transform, opacity;
}
/* Apply only when animation starts, remove after */
```

### Avoid layout thrashing
```css
/* Batch reads and writes */
.foo {
  /* Read */
  const height = element.offsetHeight;
  /* Write */
  element.style.height = height + 10 + 'px';
  /* Read (batched by browser) */
  const width = element.offsetWidth;
}
```

## Responsive Design

### clamp() for fluid sizing
```css
.heading {
  font-size: clamp(1.5rem, 2.5vw, 2.5rem);
}
.spacing {
  padding: clamp(1rem, 3vw, 2rem);
}
```

### Container queries
```css
.card-container {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 1fr 2fr;
  }
}
```

### Logical properties (RTL)
```css
.card {
  margin-inline: auto;
  padding-block: var(--space-4);
  border-inline-start: 4px solid var(--color-primary);
}
```

## Dark Mode

### prefers-color-scheme
```css
:root {
  --color-bg: #ffffff;
  --color-text: #1f2937;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0f172a;
    --color-text: #f1f5f9;
  }
}
```

### data-theme override
```css
[data-theme="dark"] {
  --color-bg: #0f172a;
  --color-text: #f1f5f9;
}

[data-theme="light"] {
  --color-bg: #ffffff;
  --color-text: #1f2937;
}
```

```javascript
document.documentElement.setAttribute('data-theme', 'dark');
```

## Animation Optimization

### Prefer transform/opacity
```css
/* Good */
.slide {
  transform: translateX(100%);
  opacity: 0;
  transition: transform 300ms ease, opacity 300ms ease;
}

/* Avoid */
.move {
  left: 100%;
  background-color: red;
}
```

### Reduced motion
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### GPU acceleration
```css
.gpu {
  transform: translateZ(0);
  backface-visibility: hidden;
}
```

## Typography

### System font stack
```css
.font-sans {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    'Helvetica Neue', Arial, sans-serif;
}

.font-mono {
  font-family: 'SF Mono', 'Fira Code', Consolas, monospace;
}
```

### Font display
```css
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter.woff2') format('woff2');
  font-display: swap;
}
```

### Variable fonts
```css
@font-face {
  font-family: 'InterVariable';
  src: url('/fonts/Inter-Variable.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
}

.text {
  font-variation-settings: 'wght' 400, 'wdth' 100;
}
```

## Native CSS Nesting

### Clean nesting (max 3 levels)
```css
/* SCSS */
.card {
  .card__header {
    .card__title {
      &:hover { }
    }
  }
}

/* Native CSS nesting */
.card {
  &__header {
    &__title {
      &:hover { }
    }
  }
}

/* Flattened (preferred) */
.card { }
.card__header { }
.card__title { }
.card__title:hover { }
```

### Avoid deep nesting patterns
```css
/* Bad: 5+ levels */
.a .b .c .d .e .f { }

/* Good: max 3 levels with BEM */
.a { }
.a__b { }
.a__b__c { }
.a__b__c--d { }
```
