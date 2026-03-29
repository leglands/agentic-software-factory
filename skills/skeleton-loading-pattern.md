---
name: Skeleton Loading UI Pattern
description: Implement shimmer skeleton loaders that match final layout while data loads asynchronously. Covers CSS animations, accessibility, framework integration, and edge cases.
category: ui-patterns
tags: [loading, skeleton, shimmer, accessibility, ux]
eval_cases:
  - id: css_shimmer_animation
    description: CSS skeleton shimmer animation with keyframes and gradient movement
    test: Verify gradient animates left-to-right with 1.5s duration, infinite loop, ease-in-out timing
  - id: aria_busy_accessibility
    description: aria-busy and aria-live region properly set during loading
    test: Screen reader announces "Loading content" and updates when complete
  - id: skeleton_shape_match
    description: Skeleton placeholder dimensions match final content shape
    test: Before/after layout shift is minimal (<50ms CLS impact)
  - id: sveltekit_await
    description: SvelteKit {#await} block with pending, then, catch branches
    test: Loading skeleton shows for 200ms+, transitions smoothly to content
  - id: nextjs_suspense
    description: Next.js Suspense boundary with loading.tsx fallback
    test: Route transition shows skeleton immediately, content replaces it
  - id: progressive_disclosure
    description: Progressive disclosure - skeleton for container, real content for above-fold
    test: Hero/content area loads first, secondary sections show skeletons
  - id: error_fallback
    description: Error state distinct from loading state with retry action
    test: Network error shows error message with retry button, not spinner
  - id: empty_vs_loading
    description: Empty state vs loading state are visually distinct
    test: Empty list shows "No items" message, loading shows shimmer skeletons
  - id: responsive_skeleton
    description: Skeleton adapts to different viewport sizes
    test: Mobile shows condensed skeleton, desktop shows expanded layout
  - id: staggered_animation
    description: Staggered skeleton animations for multiple items
    test: Each skeleton item animates with 100ms delay offset
  - id: color_customization
    description: Skeleton color scheme respects light/dark mode
    test: Skeleton uses --skeleton-bg and --skeleton-highlight CSS variables
  - id: performance_optimized
    description: Skeleton renders with minimal repaints and GPU compositing
    test: Animation uses transform/opacity only, no layout triggers
---

# Skeleton Loading UI Pattern

## Overview

Skeleton loading is a progressive loading pattern that displays a simplified, animated placeholder matching the shape of upcoming content. Unlike spinners, skeletons reduce perceived wait time by giving users visual confirmation that content is on its way.

## CSS Skeleton Shimmer Animation

```css
/* Base skeleton styles */
.skeleton {
  background: var(--skeleton-bg, #e0e0e0);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.skeleton::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent,
    var(--skeleton-highlight, rgba(255, 255, 255, 0.4)),
    transparent
  );
  transform: translateX(-100%);
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

/* Performance: use transform/opacity only */
@media (prefers-reduced-motion: reduce) {
  .skeleton::after {
    animation: none;
    background: var(--skeleton-highlight, rgba(255, 255, 255, 0.2));
  }
}
```

## Accessibility

```html
<!-- Loading state -->
<div aria-busy="true" aria-live="polite" aria-label="Loading article">
  <div class="skeleton skeleton-text"></div>
  <div class="skeleton skeleton-text skeleton-text-short"></div>
  <div class="skeleton skeleton-avatar"></div>
</div>

<!-- After load: remove aria-busy, announce completion -->
<div aria-busy="false" aria-live="polite" aria-label="Article loaded">
  <!-- actual content -->
</div>
```

**Key accessibility requirements:**
- `aria-busy="true"` during loading prevents assistive tech from announcing partial content
- `aria-live="polite"` announces when content is ready (screen reader users)
- Include `aria-label` describing what loads, not just "Loading..."
- Never use `display: none` to hide skeletons — keep in DOM for layout stability

## Matching Skeleton Shape to Real Content

Skeleton dimensions should mirror the final layout:

```css
.skeleton-text {
  height: 1em;
  width: 100%;
  margin-bottom: 0.5em;
}

.skeleton-text-short {
  width: 60%;
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-card {
  width: 300px;
  height: 200px;
  border-radius: 8px;
}

.skeleton-image {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 8px;
}
```

**Tips:**
- Use CSS variables for consistent spacing matching your design system
- Keep aspect ratios consistent to prevent layout shift (CLS < 0.1)
- Group related skeletons (e.g., avatar + name + date line)

## SvelteKit {#await} Integration

```svelte
<!-- +page.svelte -->
<script>
  import { enhance } from '$app/forms';
</script>

{#await fetchUserProfile(userId)}
  <!-- Pending: show skeleton -->
  <div class="profile-skeleton" aria-busy="true" aria-label="Loading profile">
    <div class="skeleton skeleton-avatar"></div>
    <div class="profile-skeleton__text">
      <div class="skeleton skeleton-text skeleton-text-medium"></div>
      <div class="skeleton skeleton-text skeleton-text-short"></div>
    </div>
  </div>

{:then user}
  <!-- Success: show real content -->
  <div aria-busy="false">
    <img src={user.avatar} alt={user.name} />
    <h1>{user.name}</h1>
    <p>{user.bio}</p>
  </div>

{:catch error}
  <!-- Error state: distinct from loading -->
  <div class="error-state" role="alert">
    <p>Failed to load profile</p>
    <button on:click={() => location.reload()}>Try again</button>
  </div>
{/await}
```

**Important:** The `{#await}` block transitions are not automatic. Use a transition directive or CSS classes to animate between states.

## Next.js Suspense / loading.tsx

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="dashboard-skeleton" aria-busy="true" aria-label="Loading dashboard">
      <div className="skeleton-header">
        <div className="skeleton skeleton-avatar-large"></div>
        <div className="skeleton-header__text">
          <div className="skeleton skeleton-text skeleton-text-large"></div>
          <div className="skeleton skeleton-text skeleton-text-medium"></div>
        </div>
      </div>
      <div className="skeleton-grid">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="skeleton skeleton-card" style={{ animationDelay: `${i * 100}ms` }}></div>
        ))}
      </div>
    </div>
  );
}
```

```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react';

export default function DashboardPage() {
  return (
    <Suspense fallback={<Loading />}>
      <DashboardContent />
    </Suspense>
  );
}
```

## Progressive Disclosure

Load critical content first, skeleton for below-fold:

```tsx
function ArticlePage({ article }) {
  return (
    <article>
      {/* Above-fold: show real content immediately if available */}
      <header>
        <h1>{article.title}</h1>
        <author-info>
          <img src={article.author.avatar} alt="" />
          <span>{article.author.name}</span>
        </author-info>
      </header>

      {/* Below-fold: skeleton while loading related articles */}
      <Suspense fallback={<RelatedArticlesSkeleton />}>
        <RelatedArticles articleId={article.id} />
      </Suspense>
    </article>
  );
}
```

## Error Fallback

Error states must be **visually distinct** from loading:

```css
.error-state {
  background: #fef2f2;
  border: 1px solid #ef4444;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
}

.error-state__icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.error-state__message {
  color: #991b1b;
  font-weight: 500;
}

.loading-skeleton {
  background: linear-gradient(90deg, #e0e0e0, #f0f0f0, #e0e0e0);
}
```

```svelte
{:catch error}
  <div class="error-state" role="alert">
    <span class="error-state__icon">⚠️</span>
    <p class="error-state__message">Could not load profile</p>
    <button on:click={() => refetch()}>Retry</button>
  </div>
{/catch}
```

## Empty State vs Loading State

Never show a skeleton for an empty list — show a clear message:

```svelte
{#await fetchItems()}
  <div class="skeleton-list" aria-busy="true">
    <div class="skeleton skeleton-item"></div>
    <div class="skeleton skeleton-item"></div>
    <div class="skeleton skeleton-item"></div>
  </div>
{:then items}
  {#if items.length === 0}
    <!-- Empty state: NO skeleton, just message -->
    <div class="empty-state" role="status">
      <span class="empty-state__icon">📭</span>
      <p>No items found</p>
    </div>
  {:else}
    <!-- Real content -->
    {#each items as item}
      <ItemCard {item} />
    {/each}
  {/if}
{/await}
```

## Responsive Skeleton

```css
.skeleton-card {
  width: 100%;
  max-width: 300px;
}

@media (min-width: 768px) {
  .skeleton-card {
    max-width: none;
  }
}

/* Mobile: fewer skeleton items */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 768px) {
  .skeleton-list {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }
}
```

## Staggered Animation

```css
.skeleton-item {
  animation: fade-in 0.3s ease-out forwards;
  opacity: 0;
}

@keyframes fade-in {
  to {
    opacity: 1;
  }
}

/* Apply stagger via inline style or nth-child */
.skeleton-item:nth-child(1) { animation-delay: 0ms; }
.skeleton-item:nth-child(2) { animation-delay: 100ms; }
.skeleton-item:nth-child(3) { animation-delay: 200ms; }
.skeleton-item:nth-child(4) { animation-delay: 300ms; }
```

```tsx
{[...Array(4)].map((_, i) => (
  <div
    key={i}
    className="skeleton skeleton-item"
    style={{ animationDelay: `${i * 100}ms` }}
  />
))}
```

## Color Customization with CSS Variables

```css
:root {
  --skeleton-bg: #e0e0e0;
  --skeleton-highlight: rgba(255, 255, 255, 0.4);
}

@media (prefers-color-scheme: dark) {
  :root {
    --skeleton-bg: #2a2a2a;
    --skeleton-highlight: rgba(255, 255, 255, 0.1);
  }
}
```

## Performance Checklist

1. **GPU compositing only**: Use `transform` and `opacity` for animations
2. **Avoid layout triggers**: Never animate `width`, `height`, `margin`, `padding`
3. **Use `will-change` sparingly**: Apply only to actively animating elements, remove after
4. **Minimize repaints**: The shimmer gradient should use a single composited layer
5. **`content-visibility`**: Use for off-screen skeletons if list is long

```css
.skeleton {
  will-change: transform;
  content-visibility: visible; /* default */
}

.skeleton--deferred {
  content-visibility: hidden;
  contain-intrinsic-size: 0 100px; /*预估高度 */
}
```

## Framework Integration Summary

| Framework | Pattern | Key File |
|-----------|---------|----------|
| SvelteKit | `{#await}` block | `+page.svelte` |
| Next.js 13+ | `Suspense` + `loading.tsx` | `app/**/loading.tsx` |
| React | `Suspense` + useTransition | Component level |
| Vue | `v-if` + async setup | `<Suspense>` component |
| Vanilla | Fetch → DOM update | Plain JS |

## Common Pitfalls

- **Skeleton != Spinner**: Skeletons show *shape*, spinners show *activity*
- **Don't over-skeleton**: Too many skeletons look like visual noise; limit to meaningful content
- **Match content size**: Oversized skeletons look broken when content loads
- **Minimum display time**: Show skeleton for at least 200ms to avoid flash
- **Timeout handling**: If skeleton shows >10s, suggest retry or show error
- **Animation jank**: Profile your animation in DevTools, ensure 60fps
