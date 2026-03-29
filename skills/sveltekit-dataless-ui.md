---
name: sveltekit-dataless-ui
description: SvelteKit dataless component pattern — components receive data via props, never fetch internally. Server load functions handle all data fetching.
version: '1.0.0'
metadata:
  category: frontend
eval_cases:
  - id: dataless-component
    prompt: 'Refactor this SvelteKit component to be dataless. Remove all fetch calls and data loading logic from the component.'
    checks:
      - 'regex:export let|\$props\(\)'
      - 'not_regex:fetch\(|onMount.*fetch|\.*fetch'
      - 'length_min:100'
    expectations:
      - 'Component receives all data via props, no internal fetch calls'

  - id: server-load-function
    prompt: 'Create a +page.server.ts load function for a user dashboard page that fetches user data, notifications, and recent activity.'
    checks:
      - 'regex:export.*load.*PageServer'
      - 'regex:return \{'
      - 'not_regex:export let data'
    expectations:
      - 'Load function returns all page data, no client-side fetching'

  - id: skeleton-loading-states
    prompt: 'Add skeleton loading states to a SvelteKit component that displays a list of items while data is being fetched.'
    checks:
      - 'regex:\{#await|\{:else\}'
      - 'regex:skeleton|loading|placeholder'
      - 'not_regex:fetch\('
    expectations:
      - 'Uses await block for loading states, skeleton components shown during load'

  - id: error-boundary
    prompt: 'Add error handling to a SvelteKit page using the error boundary pattern for failed data fetches.'
    checks:
      - 'regex:\+error\.svelte|throw error'
      - 'not_regex:try \{.*fetch'
    expectations:
      - 'Uses SvelteKit error boundary, not try/catch for data fetching errors'

  - id: typescript-props-interfaces
    prompt: 'Define TypeScript interfaces for a user card component that receives user data, settings, and callbacks as props.'
    checks:
      - 'regex:interface.*Props|type.*Props'
      - 'regex:export let|data:.*Props'
      - 'not_regex:fetch\('
    expectations:
      - 'Component uses typed props interface, no data fetching in component'

  - id: slot-patterns
    prompt: 'Implement a dataless card component with header, body, and footer slots that receives content via props/slots.'
    checks:
      - 'regex:slot|^\s*<slot'
      - 'regex:export let'
      - 'not_regex:fetch\('
    expectations:
      - 'Component uses slots for composition, receives data via props only'

  - id: derived-stores-from-props
    prompt: 'Create a computed/derived store in a SvelteKit component that derives UI state from passed props without fetching.'
    checks:
      - 'regex:\$derived|\$effect|derived\('
      - 'regex:export let'
      - 'not_regex:fetch\('
    expectations:
      - 'Component derives state from props using Svelte 5 $derived or $effect'

  - id: ssr-data-flow
    prompt: 'Demonstrate proper SSR data flow in SvelteKit: data fetched in +page.server.ts, passed to component, rendered server-side.'
    checks:
      - 'regex:\+page\.server\.ts'
      - 'regex:export let data|let \{ data \}'
      - 'not_regex:onMount.*fetch'
    expectations:
      - 'Data flows from server load to component props, SSR-compatible'

  - id: form-actions
    prompt: 'Implement a form action in +page.server.ts that handles form submission for creating/updating a resource.'
    checks:
      - 'regex:actions.*=|export.*actions'
      - 'regex:form.*fail|redirect'
      - 'not_regex:fetch\(.*form'
    expectations:
      - 'Form action handles submission server-side, uses SvelteKit form actions'

  - id: progressive-enhancement
    prompt: 'Add progressive enhancement to a form in SvelteKit using use:enhance for seamless client-side navigation without full page reload.'
    checks:
      - 'regex:use:enhance'
      - 'regex:export.*actions'
      - 'not_regex:fetch\(.*POST'
    expectations:
      - 'Form uses use:enhance for progressive enhancement, actions handle POST'

  - id: streaming-data
    prompt: 'Implement streaming data in SvelteKit using the streaming pattern with Promise-based data that loads progressively.'
    checks:
      - 'regex:export.*load|return.*Promise'
      - 'regex:\{#await.*data'
      - 'not_regex:client.*fetch'
    expectations:
      - 'Uses SvelteKit streaming pattern with await blocks for progressive loading'

  - id: dataless-table
    prompt: 'Create a dataless table component that receives row data, column definitions, and sort callbacks via props.'
    checks:
      - 'regex:export let.*rows|export let.*columns'
      - 'not_regex:fetch\(|await.*fetch'
      - 'length_min:150'
    expectations:
      - 'Table component is purely presentational, receives all data via props'
---

# SvelteKit Dataless UI Pattern

## Principle
Components are PURE renderers. They receive data via props and emit events. ALL data fetching happens in:
- +page.server.ts (server load functions)  
- +layout.server.ts (shared data)
- form actions (+page.server.ts actions)

## Rules
1. NEVER fetch() inside a component or +page.ts (client load)
2. ALL data comes from +page.server.ts via export let data (SvelteKit 1.x) or $props() (Svelte 5)
3. Loading states: use {#await} or skeleton components while server data loads
4. Error states: use +error.svelte, never try/catch in components
5. Type safety: define interfaces in $lib/types/ matching proto definitions

## Patterns

### Dataless Component
```svelte
<script lang="ts">
  import type { User } from '$lib/types';
  
  interface Props {
    user: User;
    onEdit?: (id: string) => void;
  }
  
  let { user, onEdit }: Props = $props();
</script>

<div class="user-card">
  <h3>{user.name}</h3>
  <p>{user.email}</p>
  {#if onEdit}
    <button onclick={() => onEdit(user.id)}>Edit</button>
  {/if}
</div>
```

### Server Load Function
```typescript
// +page.server.ts
import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params }) => {
  const response = await fetch(`/api/users/${params.id}`);
  
  if (!response.ok) {
    throw error(404, 'User not found');
  }
  
  const user = await response.json();
  
  return {
    user
  };
};
```

### Skeleton Loading
```svelte
<script lang="ts">
  import type { PageData } from './$types';
  
  let { data }: { data: PageData } = $props();
</script>

{#await data.users}
  <div class="skeleton-list">
    {#each Array(5) as _}
      <div class="skeleton-item">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-text"></div>
      </div>
    {/each}
  </div>
{:then users}
  {#each users as user}
    <UserCard {user} />
  {/each}
{:catch error}
  <p>Failed to load users: {error.message}</p>
{/await}
```

### Error Boundary
```svelte
<!-- +error.svelte -->
<script>
  import { page } from '$app/stores';
</script>

<div class="error-container">
  <h1>{$page.status}</h1>
  <p>{$page.error?.message}</p>
  <a href="/">Return home</a>
</div>
```

### TypeScript Props Interface
```typescript
// $lib/types/user.ts
export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  createdAt: Date;
}

export interface UserCardProps {
  user: User;
  variant?: 'compact' | 'full';
  onEdit?: (id: string) => void;
  onDelete?: (id: string) => void;
}
```

### Slot Composition
```svelte
<!-- Card.svelte -->
<script lang="ts">
  interface Props {
    title: string;
    children?: import('svelte').Snippet;
    footer?: import('svelte').Snippet;
  }
  
  let { title, children, footer }: Props = $props();
</script>

<div class="card">
  <header class="card-header">
    <h2>{title}</h2>
  </header>
  <main class="card-body">
    {#if children}
      {@render children()}
    {/if}
  </main>
  {#if footer}
    <footer class="card-footer">
      {@render footer()}
    </footer>
  {/if}
</div>
```

### Derived Store from Props
```svelte
<script lang="ts">
  interface Props {
    items: Array<{ name: string; completed: boolean }>;
  }
  
  let { items }: Props = $props();
  
  let completedCount = $derived(items.filter(i => i.completed).length);
  let progress = $derived(items.length > 0 ? (completedCount / items.length) * 100 : 0);
</script>

<div class="progress">
  <div class="progress-bar" style="width: {progress}%"></div>
  <span>{completedCount}/{items.length} completed</span>
</div>
```

### Form Actions
```typescript
// +page.server.ts
import type { Actions } from './$types';
import { fail, redirect } from '@sveltejs/kit';

export const actions: Actions = {
  create: async ({ request }) => {
    const data = await request.formData();
    const name = data.get('name');
    
    if (!name || typeof name !== 'string') {
      return fail(400, { name, missing: true });
    }
    
    const response = await fetch('/api/items', {
      method: 'POST',
      body: JSON.stringify({ name })
    });
    
    if (!response.ok) {
      return fail(500, { name, error: 'Failed to create item' });
    }
    
    redirect(303, '/items');
  }
};
```

### Progressive Enhancement
```svelte
<script>
  import { enhance } from '$app/forms';
  import type { ActionData } from './$types';
  
  let { form }: { form: ActionData } = $props();
</script>

<form method="POST" action="?/create" use:enhance>
  <input name="name" value={form?.name ?? ''} />
  {#if form?.missing}
    <span class="error">Name is required</span>
  {/if}
  <button type="submit">Create</button>
</form>
```

### Streaming Data
```typescript
// +page.server.ts
export const load: PageServerLoad = async () => {
  return {
    users: fetch('/api/users').then(r => r.json()),
    stats: fetch('/api/stats').then(r => r.json())
  };
};
```

```svelte
{#await data.users}
  <UsersSkeleton />
{:then users}
  <UserList {users} />
{/await}
```

### Dataless Table
```svelte
<script lang="ts">
  interface Column {
    key: string;
    label: string;
    render?: (value: unknown, row: Record<string, unknown>) => unknown;
  }
  
  interface Props {
    rows: Record<string, unknown>[];
    columns: Column[];
    onSort?: (key: string, direction: 'asc' | 'desc') => void;
    sortKey?: string;
    sortDirection?: 'asc' | 'desc';
  }
  
  let { rows, columns, onSort, sortKey, sortDirection }: Props = $props();
</script>

<table class="data-table">
  <thead>
    <tr>
      {#each columns as col}
        <th 
          class:sorted={sortKey === col.key}
          onclick={() => onSort?.(col.key, sortDirection === 'asc' ? 'desc' : 'asc')}
        >
          {col.label}
        </th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each rows as row}
      <tr>
        {#each columns as col}
          <td>
            {col.render ? col.render(row[col.key], row) : row[col.key]}
          </td>
        {/each}
      </tr>
    {/each}
  </tbody>
</table>
```
