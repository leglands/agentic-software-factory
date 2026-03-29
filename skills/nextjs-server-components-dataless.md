---
name: nextjs-server-components-dataless
description: Master Next.js App Router server components patterns — data fetching in server components, client components receive props only. Covers server/client boundary, Suspense, streaming, error boundaries, ISR, and metadata.
eval_cases:
  - id: server-client-boundary
    description: User renders a component that fetches data and displays a form. Distinguish which parts must be server vs client components and explain the boundary.
  - id: async-server-components
    description: User writes an async server component that fetches from an external API using await. Verify correct patterns for error handling and parallel fetching.
  - id: suspense-streaming
    description: User creates a page with multiple async components loading at different speeds. Implement Suspense boundaries with loading.tsx and inline Suspense for streaming.
  - id: route-handlers-api
    description: User needs an API endpoint for a client component. Create a route handler (app/api/...) and call it from a client component with fetch.
  - id: isr-revalidation
    description: User wants to cache a page and revalidate it every 60 seconds. Implement revalidate option and explain the difference between ISR and on-demand revalidation.
  - id: parallel-data-fetching
    description: User has a page that fetches user profile and their posts in sequence. Optimize it with Promise.all for parallel fetching.
  - id: error-boundaries
    description: User encounters an error in a server component. Implement error.tsx and not-found.tsx to handle errors gracefully.
  - id: generate-metadata
    description: User wants dynamic metadata per page based on fetched data. Use generateMetadata or export metadata from a server component.
  - id: client-props-only
    description: User tries to pass a function or event handler from a server component to a client component. Explain why this fails and the correct pattern.
  - id: server-components-best-practices
    description: User asks for a comprehensive review of their page.tsx implementation. Evaluate against React Server Components best practices.
  - id: loading-ui-patterns
    description: User wants skeleton loading states. Implement loading.tsx and explain the relationship with Suspense.
  - id: nested-component-boundary
    description: User has deeply nested server/client component tree. Trace the boundary crossing and identify where 'use client' must be placed.
triggers:
  - nextjs app router server components
  - 'use client' directive
  - async server components
  - suspense loading.tsx
  - route handlers api
  - isr revalidate
  - generateMetadata
  - error.tsx not-found.tsx
  - parallel data fetching nextjs
  - streaming server components
version: 1.0.0
tags:
  - nextjs
  - react
  - server-components
  - app-router
  - react-server-components
---

# Next.js App Router Server Components — Dataless Pattern

## Core Principle

Server components fetch data and render. Client components (`'use client'`) receive **props only** — no data fetching, no server-side logic, no direct database access.

---

## 1. Server vs Client Component Boundary

### `'use client'` Directive

```tsx
// app/components/Button.tsx
'use client'

import { useState } from 'react'

interface ButtonProps {
  label: string
  onClick: () => void
}

export function Button({ label, onClick }: ButtonProps) {
  const [pressed, setPressed] = useState(false)
  return (
    <button onClick={() => { setPressed(true); onClick() }}>
      {label} — {pressed ? 'pressed' : 'idle'}
    </button>
  )
}
```

### Server Component (Default)

```tsx
// app/page.tsx — Server Component (no 'use client')
import { Button } from './components/Button'

export default async function Page() {
  // Server-side: direct DB access, file system, external APIs
  const data = await fetchFromDB()
  
  return (
    <div>
      <h1>{data.title}</h1>
      <Button label="Click me" onClick={() => console.log('clicked')} />
    </div>
  )
}
```

### Boundary Rules

| Allowed in Server Components | Allowed in Client Components |
|------------------------------|------------------------------|
| `async/await` functions | `useState`, `useEffect`, `useRef` |
| Direct database queries | Event handlers (`onClick`, `onChange`) |
| File system access | Browser-only APIs |
| Environment variables (server) | `useRouter` from `next/navigation` |
| Rendering React Server Components | Client-side `fetch` |

**Never pass functions from server to client components.** Functions are not serializable.

```tsx
// WRONG — function cannot cross the boundary
export default async function Page() {
  const handleClick = () => console.log('click') // server function
  return <Button onClick={handleClick} /> // ❌ Error
}

// CORRECT — primitive or serializable object only
export default async function Page() {
  return <Button label="Click" onClick={() => console.log('click')} />
}
```

---

## 2. Async Server Components with Await

### Basic Pattern

```tsx
// app/blog/[slug]/page.tsx
interface Post {
  id: string
  title: string
  content: string
  publishedAt: string
}

async function getPost(slug: string): Promise<Post> {
  const res = await fetch(`https://api.example.com/posts/${slug}`, {
    next: { revalidate: 3600 }
  })
  if (!res.ok) throw new Error(`Failed to fetch post: ${slug}`)
  return res.json()
}

export default async function BlogPost({ params }: { params: { slug: string } }) {
  const post = await getPost(params.slug)
  
  return (
    <article>
      <h1>{post.title}</h1>
      <time>{new Date(post.publishedAt).toLocaleDateString()}</time>
      <div>{post.content}</div>
    </article>
  )
}
```

### Error Handling in Async Components

```tsx
// Throw to trigger nearest error.tsx
export default async function BlogPost({ params }: { params: { slug: string } }) {
  let post: Post
  try {
    post = await getPost(params.slug)
  } catch (error) {
    throw new Error(`Could not load post: ${params.slug}`)
  }
  
  if (!post) throw new Error('Post not found')
  
  return <Article post={post} />
}
```

---

## 3. Suspense Boundaries with loading.tsx

### Loading.tsx — Route-Level Streaming

```tsx
// app/blog/loading.tsx
export default function Loading() {
  return (
    <div className="skeleton">
      <div className="skeleton-header" />
      <div className="skeleton-body">
        <div className="skeleton-line" />
        <div className="skeleton-line short" />
        <div className="skeleton-line" />
      </div>
    </div>
  )
}
```

### Inline Suspense for Fine-Grained Streaming

```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react'
import { ActivityFeed } from './components/ActivityFeed'
import { StatsGrid } from './components/StatsGrid'
import { RecentSales } from './components/RecentSales'

function DashboardSkeleton() {
  return <div className="animate-pulse">Loading dashboard...</div>
}

export default async function DashboardPage() {
  return (
    <main>
      <h1>Dashboard</h1>
      <Suspense fallback={<DashboardSkeleton />}>
        <StatsGrid />
      </Suspense>
      <div className="grid grid-cols-2 gap-4">
        <Suspense fallback={<div>Loading activity...</div>}>
          <ActivityFeed />
        </Suspense>
        <Suspense fallback={<div>Loading sales...</div>}>
          <RecentSales />
        </Suspense>
      </div>
    </main>
  )
}
```

---

## 4. Route Handlers as API Layer

### Route Handler Definition

```tsx
// app/api/users/route.ts
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const limit = searchParams.get('limit') ?? '10'
  
  const users = await db.user.findMany({ take: parseInt(limit) })
  
  return NextResponse.json(users)
}

export async function POST(request: Request) {
  const body = await request.json()
  
  if (!body.email) {
    return NextResponse.json({ error: 'email required' }, { status: 400 })
  }
  
  const user = await db.user.create({ data: body })
  
  return NextResponse.json(user, { status: 201 })
}
```

### Calling Route Handler from Client Component

```tsx
// app/components/UserList.tsx
'use client'

import { useState, useEffect } from 'react'

interface User {
  id: string
  name: string
  email: string
}

export function UserList() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/users?limit=5')
      .then(res => res.json())
      .then(data => { setUsers(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div>Loading users...</div>

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name} — {user.email}</li>
      ))}
    </ul>
  )
}
```

---

## 5. Revalidation (ISR)

### Per-Page Revalidation

```tsx
// app/blog/[slug]/page.tsx — Revalidate every hour
export const revalidate = 3600

export default async function BlogPost({ params }: { params: { slug: string } }) {
  const post = await getPost(params.slug)
  return <Article post={post} />
}
```

### Route Segment Config

```tsx
// app/dashboard/page.tsx
export const revalidate = false // Opt out of caching (dynamic)
export const dynamic = 'force-dynamic' // Equivalent
export const dynamic = 'force-static' // Pre-render at build time
```

### On-Demand Revalidation

```tsx
// app/api/revalidate/route.ts
import { NextResponse } from 'next/server'
import { revalidatePath } from 'next/cache'

export async function POST(request: Request) {
  const body = await request.json()
  const secret = request.headers.get('x-revalidate-secret')
  
  if (secret !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ error: 'Invalid secret' }, { status: 401 })
  }
  
  revalidatePath('/blog')
  revalidatePath(`/blog/${body.slug}`)
  
  return NextResponse.json({ revalidated: true })
}
```

### Fetch-Level Cache Config

```tsx
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 60 },     // ISR: revalidate every 60s
  // next: { revalidate: false }  // Dynamic (no cache)
  // next: { revalidate: 0 }      // Always fresh (opt-out)
})
```

---

## 6. Streaming with loading.tsx

### How Streaming Works

1. Server renders page shell immediately
2. Server streams async component output as it resolves
3. `loading.tsx` serves as the fallback for all Suspense boundaries
4. User sees shell instantly, content streams in

### loading.tsx Example

```tsx
// app/feed/loading.tsx
export default function Loading() {
  return (
    <div className="feed-skeleton">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="skeleton-item">
          <div className="skeleton-avatar" />
          <div className="skeleton-content">
            <div className="skeleton-title" />
            <div className="skeleton-text" />
          </div>
        </div>
      ))}
    </div>
  )
}
```

### Page That Streams

```tsx
// app/feed/page.tsx
import { Suspense } from 'react'
import { FeedList } from './components/FeedList'
import { Sidebar } from './components/Sidebar'

export default function FeedPage() {
  return (
    <div className="layout">
      <Suspense fallback={<div>Loading feed...</div>}>
        <FeedList />
      </Suspense>
      <Suspense fallback={<div>Loading sidebar...</div>}>
        <Sidebar />
      </Suspense>
    </div>
  )
}
```

---

## 7. Parallel Data Fetching

### Sequential (Slow)

```tsx
// ❌ Sequential — takes sum of both fetch times
export default async function Page() {
  const user = await getUser(userId)           // 500ms
  const posts = await getUserPosts(userId)     // 500ms
  return <UserProfile user={user} posts={posts} />
}
```

### Parallel (Fast)

```tsx
// ✅ Parallel — takes max of both fetch times (~500ms)
export default async function Page() {
  const [user, posts] = await Promise.all([
    getUser(userId),
    getUserPosts(userId)
  ])
  return <UserProfile user={user} posts={posts} />
}
```

### Structured Parallel Fetching

```tsx
export default async function Page() {
  const userPromise = getUser(userId)
  const statsPromise = getStats(userId)
  const recentActivityPromise = getRecentActivity(userId)
  
  const user = await userPromise
  const [stats, recentActivity] = await Promise.all([
    statsPromise,
    recentActivityPromise
  ])
  
  return (
    <Dashboard 
      user={user} 
      stats={stats} 
      activity={recentActivity} 
    />
  )
}
```

---

## 8. Error Boundaries

### error.tsx — Route-Level

```tsx
// app/blog/error.tsx
'use client'

import { useEffect } from 'react'
import Link from 'next/link'

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    console.error('Blog error:', error)
  }, [error])

  return (
    <div className="error-container">
      <h2>Something went wrong loading this post</h2>
      <p>{error.message}</p>
      <div className="flex gap-4">
        <button onClick={() => reset()}>Try again</button>
        <Link href="/blog">Back to blog</Link>
      </div>
    </div>
  )
}
```

### not-found.tsx — 404 Page

```tsx
// app/blog/[slug]/not-found.tsx
import Link from 'next/link'

export default function NotFound() {
  return (
    <div>
      <h2>Post Not Found</h2>
      <p>Could not find the requested blog post.</p>
      <Link href="/blog">Return to all posts</Link>
    </div>
  )
}
```

### Global Error Boundary

```tsx
// app/global-error.tsx
'use client'

export default function GlobalError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <html>
      <body>
        <h1>Critical Error</h1>
        <button onClick={() => reset()}>Reload</button>
      </body>
    </html>
  )
}
```

---

## 9. generateMetadata

### Static Metadata

```tsx
// app/about/page.tsx
export const metadata = {
  title: 'About Us',
  description: 'Learn about our company',
}

export default function AboutPage() {
  return <div>About content</div>
}
```

### Dynamic Metadata

```tsx
// app/blog/[slug]/page.tsx
interface PageProps {
  params: { slug: string }
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const post = await getPost(params.slug)
  
  if (!post) {
    return { title: 'Post Not Found' }
  }
  
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      images: [{ url: post.imageUrl }],
      publishedTime: post.publishedAt,
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.excerpt,
    },
  }
}

export default async function BlogPost({ params }: PageProps) {
  const post = await getPost(params.slug)
  return <Article post={post} />
}
```

### Metadata Types

```tsx
import type { Metadata } from 'next'

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  return {
    title: {
      absolute: 'Full Title',           // Ignores layout
      default: 'Default Title',         // Fallback
      template: '%s | Brand Name',      // Appends to children
    },
    description: 'Page description',
    keywords: ['keyword1', 'keyword2'],
    authors: [{ name: 'Author Name' }],
    creator: 'Creator Name',
    openGraph: {
      type: 'article',
      url: 'https://example.com/page',
      siteName: 'Site Name',
    },
  }
}
```

---

## 10. React Server Components Best Practices

### Do

- Keep client component surface area small
- Push data fetching to server components
- Use `Promise.all` for parallel fetches
- Place `error.tsx` and `not-found.tsx` at each route segment
- Use `loading.tsx` for streaming skeletons
- Pass serializable props to client components
- Use `generateMetadata` for SEO-critical pages
- Prefer server components for static content

### Don't

- Pass functions, class instances, or non-serializable objects to client components
- Fetch data in client components when it can be done server-side
- Create deep client component trees — keep boundaries high
- Use `useEffect` for initial data fetching — use server components instead
- Mix server-only logic with client-side state management unnecessarily

### Component Composition Pattern

```tsx
// app/dashboard/page.tsx — Server Component
import { DashboardClient } from './DashboardClient'

async function getStats() { /* ... */ }
async function getRecentActivity() { /* ... */ }

export default async function DashboardPage() {
  const [stats, activity] = await Promise.all([
    getStats(),
    getRecentActivity()
  ])
  
  return (
    <DashboardClient 
      initialStats={stats} 
      initialActivity={activity} 
    />
  )
}
```

```tsx
// app/dashboard/DashboardClient.tsx — Client Component
'use client'

interface Props {
  initialStats: Stats
  initialActivity: Activity[]
}

export function DashboardClient({ initialStats, initialActivity }: Props) {
  // Client-side interactions, state, effects
  return (
    <div>
      <StatsDisplay stats={initialStats} />
      <ActivityFeed initialActivity={initialActivity} />
    </div>
  )
}
```

### Mental Model Summary

```
┌─────────────────────────────────────┐
│           Server                   │
│  ┌───────────────────────────────┐  │
│  │  Page (async server component)│  │
│  │  - fetches data               │  │
│  │  - renders server children    │  │
│  │  - passes serializable props  │  │
│  └───────────────┬───────────────┘  │
│                  │ props (serial)   │
│  ┌───────────────▼───────────────┐  │
│  │  Client Component             │  │
│  │  - 'use client'               │  │
│  │  - useState, useEffect         │  │
│  │  - event handlers             │  │
│  │  - NO data fetching           │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Nesting Rule

A client component can render server components **only as children** (via props.children). The server components must be passed as children — they execute on the server before being passed down.

```tsx
// ✅ Valid — server component passed as child
export function ClientWrapper({ children }: { children: React.ReactNode }) {
  'use client'
  return <div className="wrapper">{children}</div>
}

// Used in server component:
<ClientWrapper>
  <ServerChild /> {/* executes on server */}
</ClientWrapper>
```
