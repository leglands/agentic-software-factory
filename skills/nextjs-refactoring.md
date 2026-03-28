---
name: nextjs-refactoring
description: Refactor and optimize Next.js applications using the App Router paradigm. Evaluates Server Components vs Client Components boundaries, data fetching patterns, route handlers, metadata API, streaming, Server Actions, bundle analysis, and runtime selection.
framework: nextjs
version: "14+"
eval_cases:
  - id: server-client-boundary
    description: Analyze a Next.js page component and determine the optimal Server/Client Component boundary. Given a component file, identify which parts require 'use client' and which can remain server-side, explaining the tradeoffs and performance implications.
  - id: data-fetching-migration
    description: Convert a page using useEffect + useState for data fetching to native fetch with caching. Transform client-side data fetching patterns to server-side async/await with appropriate cache/revalidate options.
  - id: bundle-optimization
    description: Audit a Next.js app for bundle bloat using @next/bundle-analyzer. Identify large dependencies, suggest dynamic imports, and implement code splitting strategies to reduce initial load size.
  - id: seo-metadata-refactor
    description: Migrate legacy next/head usage to the new Metadata API. Replace Head exports with generateMetadata functions, ensuring proper OG tags, canonical URLs, and viewport configuration.
---

## Server vs Client Components

Minimize `'use client'`. Default to Server Components; add `'use client'` only when:
- Using browser APIs (window, localStorage)
- Using React state/-effects (useState, useEffect)
- Using event handlers needing interactivity
- Using client-only hooks

```tsx
// Server Component (default) - data fetching, no interactivity
async function ProductList() {
  const data = await fetch('https://api.example.com/products', { 
    next: { revalidate: 3600 } 
  }).then(r => r.json());
  return <ul>{data.map(p => <li key={p.id}>{p.name}</li>)}</ul>;
}

// Client Component - only when needed
'use client';
import { useState } from 'react';
export function AddToCart({ productId }: { productId: string }) {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>Add ({count})</button>;
}
```

## Data Fetching

Use server-side fetch w/ cache/revalidate. Avoid useEffect for data fetching.

```tsx
// Good: Server-side fetch with ISR
async function getProducts() {
  const res = await fetch('https://api.example.com/products', {
    next: { revalidate: 3600 } // Revalidate every hour
  });
  return res.json();
}

// Good: Dynamic data with on-demand revalidation
async function getProduct(slug: string) {
  const res = await fetch(`https://api.example.com/products/${slug}`, {
    next: { tags: ['product', slug] } // For revalidateTag()
  });
  return res.json();
}

// Bad: Avoid this pattern
'use client';
function Products() {
  const [data, setData] = useState([]);
  useEffect(() => {
    fetch('/api/products').then(r => r.json()).then(setData);
  }, []);
  // ...
}
```

## Route Handlers (app router)

Migrate from `pages/api/` to `app/` route handlers.

```typescript
// app/api/products/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const data = await fetch('https://api.example.com/products').then(r => r.json());
  return NextResponse.json(data);
}

export async function POST(request: Request) {
  const body = await request.json();
  // Handle creation
  return NextResponse.json({ created: true }, { status: 201 });
}
```

## Image Optimization

Use `next/image` w/ proper sizing + blur placeholders.

```tsx
import Image from 'next/image';

export async function ProductImage({ src, alt }: { src: string; alt: string }) {
  return (
    <Image
      src={src}
      alt={alt}
      width={400}
      height={300}
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,..." // Generate with: 'blurDataURL' = await getPlaiceholder(src).then(p => p.base64)
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      priority={false} // Set true for above-the-fold images
    />
  );
}
```

## Bundle Analysis

Analyze + optimize client bundle size.

```bash
npm install @next/bundle-analyzer --save-dev
```

```javascript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({
  // other config
});
```

```bash
ANALYZE=true npm run build
```

Use dynamic imports for heavy components:

```tsx
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  loading: () => <p>Loading...</p>,
  ssr: false, // Disable SSR if component doesn't need it
});
```

## Metadata API for SEO

Replace `next/head` with Metadata API.

```tsx
// app/products/[id]/page.tsx
import { Metadata } from 'next';
import { getProduct } from '@/lib/api';

type Props = { params: { id: string } };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const product = await getProduct(params.id);
  return {
    title: product.name,
    description: product.description,
    openGraph: {
      title: product.name,
      description: product.description,
      images: [{ url: product.image, width: 400, height: 300 }],
    },
    alternates: {
      canonical: `/products/${params.id}`,
    },
  };
}

export default async function ProductPage({ params }: Props) {
  const product = await getProduct(params.id);
  return <h1>{product.name}</h1>;
}
```

## Streaming with Suspense

Use Suspense boundaries + loading.tsx for streaming.

```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react';
import { getUser, getStats } from '@/lib/api';

function StatsSkeleton() {
  return <div className="animate-pulse bg-gray-200 h-32" />;
}

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<StatsSkeleton />}>
        <Stats />
      </Suspense>
    </div>
  );
}

async function Stats() {
  const stats = await getStats(); // Slow query
  return <div>Stats: {JSON.stringify(stats)}</div>;
}
```

```tsx
// app/dashboard/loading.tsx - Automatic Suspense boundary
export default function Loading() {
  return <div className="animate-pulse">Loading dashboard...</div>;
}
```

## Server Actions for Mutations

Replace API routes w/ Server Actions for form mutations.

```tsx
// app/actions.ts
'use server';

export async function submitOrder(formData: FormData) {
  const productId = formData.get('productId');
  // Validate and process
  await db.order.create({ data: { productId } });
  revalidatePath('/orders');
  return { success: true };
}
```

```tsx
// app/orders/new/page.tsx
import { submitOrder } from '@/app/actions';

export default function NewOrderPage() {
  return (
    <form action={submitOrder}>
      <input name="productId" type="text" />
      <button type="submit">Submit Order</button>
    </form>
  );
}
```

## Parallel and Intercepting Routes

```tsx
// Parallel routes - @folder syntax
// app/@analytics/page.tsx and app/@realtime/page.tsx
export default function DashboardLayout({
  analytics,
  realtime,
}: {
  analytics: React.ReactNode;
  realtime: React.ReactNode;
}) {
  return (
    <div>
      <main>Main content</main>
      <aside>{analytics}</aside>
      <aside>{realtime}</aside>
    </div>
  );
}

// Intercepting routes - modal patterns
// app/feed/@modal/(.)photos/[id]/page.tsx
// Intercepts /photos/[id] when accessed from /feed
```

## ISR Patterns

```tsx
// Revalidate on a schedule
export const revalidate = 3600; // Revalidate every hour

// Per-page revalidation
async function getProduct(id: string) {
  const res = await fetch(`https://api.example.com/products/${id}`, {
    next: { revalidate: 3600 },
  });
  return res.json();
}

// On-demand revalidation with tags
export async function generateStaticParams() {
  const products = await fetch('https://api.example.com/products').then(r => r.json());
  return products.map((p: { id: string }) => ({ id: p.id }));
}
```

## Edge Runtime vs Node Runtime

```typescript
// app/api/edge/route.ts - Edge Runtime
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function middleware(request: NextRequest) {
  const country = request.geo.country;
  return NextResponse.json({ country });
}
```

```typescript
// app/api/node/route.ts - Node Runtime (default)
import { NextResponse } from 'next/server';

export const runtime = 'nodejs'; // Explicit

export async function GET() {
  const data = await fetch('https://api.example.com/data'); // Node fetch with longer timeout
  return NextResponse.json({ data });
}
```

Choose Edge for: geo-based routing, low-latency responses, streaming.  
Choose Node for: filesystem access, long-running tasks, Node.js APIs, SQL databases.
