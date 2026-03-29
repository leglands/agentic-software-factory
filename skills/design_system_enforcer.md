# Design System Enforcer

## PURPOSE
Validate design system adherence. Block violations. Ensure consistent UI across codebase.

---

## RULES

### TOKEN CONSISTENCY

- **COLORS**: use design tokens ONLY. NO hardcoded hex values. token format: `var(--color-name)` or `theme.colors.name`
- **SPACING**: use spacing scale ONLY: `4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px`. NO arbitrary values
- **TYPOGRAPHY**: use type scale tokens ONLY. NO inline font-size, font-weight, line-height declarations

### COMPONENT API COMPLIANCE

- prop naming: camelCase, prefixed compound names (e.g., `hasError`, `isLoading`)
- boolean props: prefer `is*`, `has*`, `should*` prefix
- size prop: strict enum `sm | md | lg`
- variant prop: strict enum per component (see component inventory)
- pass all event handlers via `on*` callback props, NO inline `onClick={}`

### A11Y WCAG AA MINIMUM

- color contrast: 4.5:1 text, 3:1 UI components
- focus visible: ALWAYS present on interactive elements
- aria-label: required when icon-only button or text insufficient
- role: required for non-semantic elements
- tabIndex: 0 for interactive, -1 for non-interactive
- alt text: required for all img elements
- form labels: explicit `htmlFor` association

### RESPONSIVE BREAKPOINTS

- breakpoints: `sm=640px, md=768px, lg=1024px, xl=1280px`
- use mobile-first. default styles = mobile. `min-width` for larger
- NO `max-width` breakpoints
- use CSS Grid/Flexbox for layout. NO fixed pixel widths for responsive

### DARK MODE SUPPORT

- all color usages: MUST reference semantic token (e.g., `var(--color-bg-primary)`)
- NOT reference raw color variable directly in component
- use `prefers-color-scheme: dark` media query or `data-theme` attribute
- test BOTH light and dark mode rendering

### ICON CONSISTENCY

- icons: Feather SVG ONLY (24x24 stroke-width=2)
- NO inline SVG unless documented exception
- import via icon component: `<Icon name="check" size={16} />`
- stroke color: inherit from text color via `currentColor`

### NO INLINE STYLES

- ZERO `style={}` props on DOM elements
- ZERO `style={}` props on components
- use CSS classes or design system components ONLY
- exception: dynamic values from theme calc only with code review

### NO HARDCODED HEX

- ZERO hex color literals in code
- ZERO hex color literals in CSS
- use design token references ONLY
- exception: CSS variables in theme files (reviewed)

### SKELETON LOADING VARIANTS

- SkeletonComponent variants: `text | circular | rectangular | card`
- SkeletonAnimation: `pulse | wave | shimmer`
- skeleton color: `var(--skeleton-base)` + `var(--skeleton-highlight)`
- usage: explicit `aria-busy="true"` on container, `aria-hidden="true"` on skeleton

---

## EVAL_CASES

### 1. HARDCODED HEX
```tsx
// ❌ BLOCKED
<div style={{ color: '#FF5733' }}>Text</div>

// ✅ PASS
<div className="text-primary">Text</div>
```

### 2. INLINE STYLE
```tsx
// ❌ BLOCKED
<button style={{ marginTop: '10px' }}>Click</button>

// ✅ PASS
<Button className="mt-2">Click</Button>
```

### 3. TOKEN VIOLATION
```tsx
// ❌ BLOCKED
padding: 13px

// ✅ PASS
padding: var(--spacing-3) // 12px
```

### 4. ICON VIOLATION
```tsx
// ❌ BLOCKED
<svg width="20" height="20"><circle.../></svg>

// ✅ PASS
<Icon name="circle" size={20} />
```

### 5. CONTRAST VIOLATION
```tsx
// ❌ BLOCKED
<span style={{ color: '#999' }}>Small text</span>

// ✅ PASS
<span className="text-muted">Small text</span>
// Must verify --color-muted >= 4.5:1 against bg
```

### 6. MISSING ARIA LABEL
```tsx
// ❌ BLOCKED
<button><Icon name="close" /></button>

// ✅ PASS
<button aria-label="Close"><Icon name="close" /></button>
```

### 7. WRONG BREAKPOINT
```tsx
// ❌ BLOCKED
@media (max-width: 768px) { ... }

// ✅ PASS
@media (min-width: 768px) { ... }
```

### 8. MISSING FOCUS
```tsx
// ❌ BLOCKED
<a href="#" onClick={...}>Link</a>

// ✅ PASS
<a href="#" onClick={...} tabIndex={0}>Link</a>
// Or use <Link> component with focus styles
```

### 9. MISSING FORM LABEL
```tsx
// ❌ BLOCKED
<input id="email" placeholder="Email" />

// ✅ PASS
<label htmlFor="email">Email</label>
<input id="email" />
```

### 10. DARK MODE TOKEN
```tsx
// ❌ BLOCKED
background: #FFFFFF

// ✅ PASS
background: var(--color-bg-primary)
// Supports dark: var(--color-bg-primary-dark) via theme
```

### 11. SKELETON MISSING ARIA
```tsx
// ❌ BLOCKED
<div>
  <Skeleton />
</div>

// ✅ PASS
<div aria-busy="true">
  <Skeleton aria-hidden="true" />
</div>
```

### 12. SKELETON WRONG VARIANT
```tsx
// ❌ BLOCKED
<Skeleton variant="custom" />

// ✅ PASS
<Skeleton variant="text" />
// Allowed: text | circular | rectangular | card
```

---

## ENFORCEMENT

- BLOCK merge if any rule violated
- CI must run design-system-lint before merge
- if design token missing: request addition to design-tokens.json
- if component API mismatch: consult component inventory docs

---

## EXCEPTIONS

- approved via design-system-review comment on PR
- documented in DESIGN_EXCEPTIONS.md with expiry date
- emergency hotfix with two-reviewer approval

---

## REFERENCES

- Feather Icons: https://feathericons.com
- WCAG 2.1 AA: https://www.w3.org/WAI/WCAG21/quickref/
- Design Tokens Format: https://design-tokens.github.io/community-group/format/
