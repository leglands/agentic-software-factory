---
name: vue-refactoring
version: 1.0.0
description: Refactor Vue.js 3 code from Options API to Composition API, extract composables,
  optimize reactivity and performance, and integrate TypeScript. Use when modernizing
  Vue 2/3 codebases, improving component architecture, or optimizing Vue application
  performance.
metadata:
  category: design
  source: community
  triggers:
  - migrating Vue.js Options API to Composition API
  - extracting reusable logic into Vue composables
  - optimizing Vue reactivity and component performance
  - integrating TypeScript with Vue 3 Composition API
eval_cases:
- id: options-to-composition-migration
  prompt: How do I migrate a Vue 2 Options API component to Vue 3 Composition API
    with script setup?
  should_trigger: true
  checks:
  - length_min:200
  - no_placeholder
  expectations:
  - Converts Options API lifecycle hooks to Composition API equivalents
  - Demonstrates script setup syntax
  - Maps data to ref/reactive
  - Maps methods to plain functions
  - Maps computed properties to computed()
  - Maps watch/watchEffect appropriately
  tags:
  - vue
  - composition-api
  - migration
- id: composable-extraction-pattern
  prompt: Extract reusable logic from a Vue component into a composable for shared
    state and behavior
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Identifies reusable stateful logic
  - Creates composable with reactive state
  - Returns tuple or object with refs
  - Shows usage in component via destructuring
  - Handles cleanup in onUnmounted or returned teardown
  tags:
  - vue
  - composables
  - code-organization
- id: reactivity-patterns-choice
  prompt: When should I use ref() vs reactive() and how do I avoid unwanted deep reactivity
    in Vue 3?
  should_trigger: true
  checks:
  - length_min:120
  - no_placeholder
  expectations:
  - Explains ref() for primitives and reactive() for objects
  - Demonstrates toRefs for destructuring props
  - Explains shallowRef for performance with large objects
  - Warns against replacing reactive objects entirely
  - Shows proper reactive destructuring patterns
  tags:
  - vue
  - reactivity
  - performance
- id: vue-performance-optimization
  prompt: How do I optimize a Vue component with large lists using v-once, v-memo,
    and shallowRef?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Demonstrates v-once for static content
  - Shows v-memo with dependency tracking for list items
  - Explains shallowRef for large data structures
  - Reduces unnecessary re-renders
  - Provides complete realistic example
  tags:
  - vue
  - performance
  - v-once
  - v-memo
- id: pinia-composable-store
  prompt: Convert a Vue Pinia store from Options API style to Composition API setup
    function style with proper typing
  checks:
  - regex: defineStore.*setup|Composition API
  - length_min: 150
  - has_keyword: ref|reactive
  expectations:
  - Uses setup function syntax instead of options object
  - Defines state with ref/reactive
  - Converts actions to plain functions
  - Returns reactive state and methods
  - Demonstrates TypeScript typing
- id: typescript-defineprops-emits
  prompt: Add proper TypeScript types to a Vue 3 component using defineProps and defineEmits
    with runtime validation
  checks:
  - regex: defineProps|defineEmits
  - length_min: 120
  - has_keyword: interface|type
  expectations:
  - Defines props interface with types
  - Uses defineProps with generic syntax
  - Typed emits with event payloads
  - withDefaults for optional props
  - Proper null handling
- id: async-component-suspense
  prompt: Implement async component loading with Vue Suspense and defineAsyncComponent
    for code splitting
  checks:
  - regex: defineAsyncComponent|Suspense
  - length_min: 130
  - has_keyword: loadingComponent|errorComponent
  expectations:
  - Uses defineAsyncComponent with loader
  - Implements Suspense with fallback
  - Handles loading and error states
  - Configures delay and timeout
  - Demonstrates proper async setup
- id: template-v-if-to-computed
  prompt: Refactor complex v-if chains in a Vue template to use computed properties
    for better readability
  checks:
  - regex: computed|v-if
  - length_min: 100
  - has_keyword: v-else-if|v-show
  expectations:
  - Identifies complex conditional logic
  - Extracts to computed property
  - Replaces v-if chain with single condition
  - Improves template readability
  - Maintains reactivity
- id: component-splitting-large
  prompt: Split a large Vue component over 400 lines into smaller subcomponents and
    composables
  checks:
  - regex: import.*vue|<script setup
  - length_min: 140
  - has_keyword: extract|职责
  expectations:
  - Identifies logical sections
  - Extracts child components
  - Moves reusable logic to composables
  - Keeps main component under 200 lines
  - Maintains component communication
- id: shallowref-performance
  prompt: When should I use shallowRef instead of ref in Vue 3 and how to avoid deep
    reactivity overhead
  checks:
  - regex: shallowRef|triggerUpdate
  - length_min: 110
  - has_keyword: .value|markRaw|toRaw
  expectations:
  - Explains shallowRef behavior
  - Shows when shallowRef is preferable
  - Demonstrates manual triggerUpdate pattern
  - Compares with markRaw and toRaw
  - Provides performance guidance
- id: lifecycle-hooks-migration
  prompt: Map Vue 2 lifecycle hooks (beforeCreate, created, mounted, updated) to Vue
    3 Composition API equivalents
  checks:
  - regex: onMounted|onUpdated|onUnmounted
  - length_min: 100
  - has_keyword: setup|beforeCreate
  expectations:
  - Maps beforeCreate to setup()
  - Maps mounted to onMounted()
  - Maps updated to onUpdated()
  - Maps unmounted to onUnmounted()
  - Handles errorCaptured hook
- id: generic-components-ts
  prompt: Create a generic Vue 3 component with TypeScript that accepts a typed item
    list and render function
  checks:
  - regex: generic|<script setup lang="ts"
  - length_min: 100
  - has_keyword: extends|interface
  expectations:
  - Uses generic type parameter
  - Defines item interface constraint
  - Generic render item pattern
  - Props typing with generics
  - Template type safety
- id: composable-async-fetch
  prompt: Create an async composable for data fetching with loading, error, and data
    states
  checks:
  - regex: shallowRef|async.*function
  - length_min: 130
  - has_keyword: loading|error|data
  expectations:
  - Creates reactive state for data/error/loading
  - Implements async fetch function
  - Proper try-catch error handling
  - Returns tuple with destructuring
  - Handles cleanup appropriately
- id: vite-manual-chunks
  prompt: Configure Vite to split vendor chunks for Vue, Vue Router, and Pinia in
    production builds
  checks:
  - regex: manualChunks|vite\.config
  - length_min: 90
  - has_keyword: vendor|build
  expectations:
  - Configures manualChunks in rollupOptions
  - Separates Vue core vendor chunk
  - Separates router and state management
  - Optimizes bundle size
  - Improves caching strategy
- id: reactive-destructuring-toref
  prompt: How to properly destructure reactive objects and props while maintaining
    reactivity in Vue 3
  checks:
  - regex: toRefs|toRaw|reactive
  - length_min: 100
  - has_keyword: destructure|spread
  expectations:
  - Uses toRefs for props destructuring
  - Maintains reactivity on destructured refs
  - Explains toRaw for raw access
  - Avoids destructuring reactive directly
  - Shows proper usage patterns
---

# vue-refactoring

# Vue.js 3 Refactoring

Master migration from Options API to Composition API, composable extraction, reactivity patterns, performance optimization, + TypeScript integration for Vue 3.

## Use this skill when

- Migrating Vue 2 Options API code to Vue 3 Composition API
- Extracting reusable logic into composables
- Optimizing Vue component reactivity + render performance
- Integrating TypeScript with Vue 3 defineProps + defineEmits
- Refactoring large Vue components into smaller pieces
- Implementing Pinia stores with composable patterns

## Do not use this skill when

- Writing new Vue code from scratch (use vue-best-practices instead)
- Working with Vue 2 without migration intent
- Fixing trivial CSS/styling issues

## Instructions

1. Assess component complexity + identify migration/refactoring goals.
2. Convert Options API to Composition API using script setup where possible.
3. Extract reusable logic into composables.
4. Apply reactivity best practices (ref vs reactive, shallowRef).
5. Optimize template with v-once, v-memo, + computed properties.
6. Add TypeScript types with defineProps + defineEmits.
7. Validate with type checking + tests.

---

## 1. Options API to Composition API Migration

### Lifecycle Hook Mapping

| Options API | Composition API |
|-------------|-----------------|
| `created` | Direct in setup() |
| `mounted` | `onMounted()` |
| `updated` | `onUpdated()` |
| `unmounted` | `onUnmounted()` |
| `beforeCreate` | First line of setup() |
| `beforeMount` | `onBeforeMount()` |
| `beforeUpdate` | `onBeforeUpdate()` |
| `beforeUnmount` | `onBeforeUnmount()` |
| `errorCaptured` | `onErrorCaptured()` |

### Script Setup Conversion

```vue
<!-- Options API (Vue 2 style) -->
<template>
  <div>{{ greeting }} {{ name }}</div>
</template>

<script>
export default {
  name: 'GreetingComponent',
  data() {
    return {
      name: 'World',
      count: 0
    }
  },
  computed: {
    greeting() {
      return `Hello, ${this.name}!`
    }
  },
  methods: {
    increment() {
      this.count++
    }
  },
  mounted() {
    console.log('Component mounted')
  }
}
</script>
```

```vue
<!-- Composition API with script setup -->
<template>
  <div>{{ greeting }} {{ name }}</div>
  <button @click="increment">Count: {{ count }}</button>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const name = ref('World')
const count = ref(0)

const greeting = computed(() => `Hello, ${name.value}!`)

function increment() {
  count.value++
}

onMounted(() => {
  console.log('Component mounted')
})
</script>
```

### Key Conversion Patterns

**Data → ref or reactive:**
```javascript
// Options API
data() {
  return {
    user: { name: 'John', age: 30 },
    items: []
  }
}

// Composition API
const user = reactive({ name: 'John', age: 30 })
const items = ref([])
```

**This → Direct refs:**
```javascript
// Options API - accessing via this
this.username
this.fetchUser()

// Composition API - direct access
username.value
fetchUser()
```

**Props → defineProps:**
```javascript
// Options API
props: {
  title: String,
  count: { type: Number, default: 0 }
}

// Composition API with script setup
const props = defineProps<{
  title?: string
  count?: number
}>()
```

**Emits → defineEmits:**
```javascript
// Options API
emits: ['update', 'delete']

// Composition API with script setup
const emit = defineEmits<{
  update: [value: string]
  delete: [id: number]
}>()
```

---

## 2. Composables: Extract Reusable Logic

Composables extract + share reusable logic between components.

### Composable Structure

```javascript
// composables/useCounter.ts
import { ref, computed } from 'vue'

export function useCounter(initialValue = 0) {
  const count = ref(initialValue)
  
  const doubled = computed(() => count.value * 2)
  
  function increment() {
    count.value++
  }
  
  function decrement() {
    count.value--
  }
  
  function reset() {
    count.value = initialValue
  }
  
  return {
    count,
    doubled,
    increment,
    decrement,
    reset
  }
}
```

### Using Composables

```vue
<script setup>
import { useCounter } from '@/composables/useCounter'
import { useLocalStorage } from '@/composables/useLocalStorage'

const { count, increment, reset } = useCounter(10)
const { value: username, setValue } = useLocalStorage('username', '')
</script>
```

### Stateful vs Stateless Composables

**Stateful (shared state):**
```javascript
// Creates single reactive state shared across all callers
const todos = ref([])
export function useTodos() {
  return { todos }
}
```

**Stateless (instance per call):**
```javascript
// Each caller gets independent state
export function useCounter(initial = 0) {
  const count = ref(initial)
  return { count }
}
```

### Async Composables

```javascript
// composables/useFetch.ts
import { ref, shallowRef } from 'vue'

export function useFetch<T>(url: string) {
  const data = shallowRef<T | null>(null)
  const error = ref<Error | null>(null)
  const loading = ref(false)
  
  async function fetchData() {
    loading.value = true
    try {
      const response = await fetch(url)
      data.value = await response.json()
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }
  
  return { data, error, loading, fetchData }
}
```

---

## 3. Reactivity: ref vs reactive

### When to Use ref()

- Primitive values (string, number, boolean)
- Values that may be reassigned entirely
- Template refs

```javascript
const count = ref(0)
const message = ref('')
const user = ref(null)

// Access value with .value
count.value++

// In templates, .value is auto-unwrapped
// <span>{{ count }}</span> renders 1
```

### When to Use reactive()

- Complex objects with multiple properties
- Objects you want to maintain reactivity on properties
- Arrays

```javascript
const state = reactive({
  user: null,
  items: [],
  filter: 'all'
})

// No .value needed
state.user = { name: 'John' }
state.items.push({ id: 1 })
```

### Avoiding Unwanted Deep Reactivity

**Problem:** Deep reactivity overhead for large objects.

**Solution 1: shallowRef**
```javascript
import { shallowRef } from 'vue'

// Only triggers update on .value assignment, not nested changes
const largeData = shallowRef({ rows: [] })

// To trigger update after mutation:
largeData.value.rows.push(newRow)
largeData.value = { ...largeData.value }
```

**Solution 2: toRaw**
```javascript
import { toRaw, reactive } from 'vue'

const state = reactive({ items: [] })
const plain = toRaw(state) // Get raw object, no reactivity tracking
```

**Solution 3: markRaw**
```javascript
import { markRaw } from 'vue'

const config = markRaw({
  apiUrl: 'https://api.example.com',
  maxRetries: 3
})
// config will never be made reactive
```

### toRefs for Props Destructuring

```javascript
import { toRefs } from 'vue'

const props = defineProps<{
  title: string
  count: number
  user?: { name: string }
}>()

// toRefs maintains reactivity when destructuring
const { title, count, user } = toRefs(props)

// Access as regular refs
console.log(title.value)
```

---

## 4. Performance: v-once, v-memo, shallowRef

### v-once for Static Content

Render once + never update.

```vue
<template>
  <!-- Static content - rendered once, never re-evaluated -->
  <div v-once>
    <HeavyComponent :static-data="constantData" />
  </div>
  
  <!-- Dynamic content -->
  <UserProfile :user="currentUser" />
</template>
```

### v-memo for List Performance

Memoize subtrees based on specific dependencies.

```vue
<template>
  <!-- Only re-renders when item.status or item.selected changes -->
  <div v-for="item in items" :key="item.id" v-memo="[item.status, item.selected]">
    <StatusBadge :status="item.status" />
    <checkbox :checked="item.selected" />
    <ComplexContent :data="item.data" />
  </div>
</template>
```

### shallowRef for Large Data

```vue
<script setup>
import { shallowRef } from 'vue'

// Triggers update only on .value replacement, not nested mutations
const tableData = shallowRef([])

async function loadData() {
  const rows = await fetchLargeDataset()
  tableData.value = rows // Triggers update
}

function updateRow(id, changes) {
  // This does NOT trigger update - for performance
  const idx = tableData.value.findIndex(r => r.id === id)
  if (idx !== -1) {
    tableData.value[idx] = { ...tableData.value[idx], ...changes }
    // Force update if needed:
    tableData.value = [...tableData.value]
  }
}
</script>
```

### Computed for Complex Conditions

Replace complex v-if chains with computed properties.

```vue
<template>
  <!-- Before: complex v-if chain -->
  <div v-if="user && user.isActive && !user.isBanned && hasPermission('view')">
    Content
  </div>
  
  <!-- After: computed property -->
  <div v-if="canViewContent">
    Content
  </div>
</template>

<script setup>
const canViewContent = computed(() => {
  return user.value?.isActive 
    && !user.value?.isBanned 
    && hasPermission('view')
})
</script>
```

---

## 5. Component Size: Split Large Components

Target: Components under 200 lines of script code.

### Splitting Strategy

**1. Extract Template Fragments:**
```vue
<!-- Before: UserDashboard.vue - 400 lines -->
<script setup>
// ... all logic
</script>
<template>
  <div class="dashboard">
    <UserStats />
    <RecentActivity />
    <NotificationPanel />
    <QuickActions />
    <Analytics />
    <Settings />
  </div>
</template>

<!-- After: UserDashboard.vue - 80 lines -->
<script setup>
import UserStats from './UserStats.vue'
import RecentActivity from './RecentActivity.vue'
import NotificationPanel from './NotificationPanel.vue'
import QuickActions from './QuickActions.vue'
import Analytics from './Analytics.vue'
import Settings from './Settings.vue'
</script>
<template>
  <div class="dashboard">
    <UserStats />
    <RecentActivity />
    <NotificationPanel />
    <QuickActions />
    <Analytics />
    <Settings />
  </div>
</template>
```

**2. Extract Composable Logic:**
```vue
<!-- Before: useFetch in component -->
<script setup>
const data = ref(null)
const loading = ref(false)
const error = ref(null)

async function fetchUser() {
  loading.value = true
  try {
    data.value = await api.getUser()
  } catch (e) {
    error.value = e
  }
  loading.value = false
}
</script>

<!-- After: useUser composable -->
<script setup>
import { useUser } from '@/composables/useUser'
const { user, loading, error, fetchUser } = useUser()
</script>
```

**3. Extract Sub-Components:**
```vue
<!-- Before: Complex row in template -->
<tr v-for="item in items" :key="item.id">
  <td>{{ formatDate(item.created) }}</td>
  <td>
    <span :class="getStatusClass(item.status)">
      {{ getStatusLabel(item.status) }}
    </span>
  </td>
  <td>
    <button @click="edit(item)" :disabled="!canEdit(item)">Edit</button>
    <button @click="delete(item)" :disabled="!canDelete(item)">Delete</button>
  </td>
</tr>

<!-- After: ItemRow component -->
<tr v-for="item in items" :key="item.id">
  <ItemRow :item="item" @edit="edit" @delete="delete" />
</tr>
```

---

## 6. Pinia Store Patterns

### Composable Store Pattern

Prefer composable-style stores over option-style stores.

```javascript
// stores/useAuthStore.ts
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  
  const isAuthenticated = computed(() => !!user.value)
  const userName = computed(() => user.value?.name ?? '')
  
  async function login(credentials) {
    const response = await api.login(credentials)
    user.value = response.user
    token.value = response.token
  }
  
  function logout() {
    user.value = null
    token.value = null
  }
  
  return {
    user,
    token,
    isAuthenticated,
    userName,
    login,
    logout
  }
})
```

### Avoiding Store Bloat

**Problem:** Store with too many state properties + actions.

**Solution: Split into Domain Stores**

```javascript
// stores/useUserProfile.ts - Only user profile data
export const useUserProfileStore = defineStore('userProfile', () => {
  const profile = ref(null)
  const loading = ref(false)
  
  async function fetchProfile(id) { /* ... */ }
  async function updateProfile(data) { /* ... */ }
  
  return { profile, loading, fetchProfile, updateProfile }
})

// stores/useUserPreferences.ts - Only preferences
export const useUserPreferencesStore = defineStore('userPreferences', () => {
  const preferences = ref({})
  
  async function updatePreference(key, value) { /* ... */ }
  async function resetPreferences() { /* ... */ }
  
  return { preferences, updatePreference, resetPreferences }
})
```

---

## 7. Async Components and Suspense

### Async Component Definition

```javascript
// components/UserProfile.vue
const UserProfile = defineAsyncComponent({
  loader: () => import('./UserProfile.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorBoundary,
  delay: 200,
  timeout: 3000
})
```

### Suspense with Async Setup

```vue
<template>
  <Suspense>
    <template #default>
      <UserProfile :user-id="id" />
    </template>
    <template #fallback>
      <div class="loading">Loading profile...</div>
    </template>
  </Suspense>
</template>

<script setup>
import { ref } from 'vue'
import UserProfile from './UserProfile.vue'

const id = ref(1)
</script>
```

### Async Setup with Promises

```vue
<script setup>
import { defineAsyncComponent, ref } from 'vue'

const UserSettings = defineAsyncComponent(() =>
  import('./UserSettings.vue')
)

const settings = ref(null)

async function loadSettings() {
  // Setup can be async
  settings.value = await fetchSettings()
}
</script>
```

---

## 8. Template Cleanup

### Replace v-if Chains with Computed

```vue
<!-- Before -->
<template>
  <div v-if="isAdmin && !isSuspended && hasPermission('dashboard')">
    Admin Dashboard
  </div>
  <div v-else-if="isManager && !isSuspended && hasPermission('dashboard')">
    Manager Dashboard
  </div>
  <div v-else-if="isUser && !isSuspended && hasPermission('dashboard')">
    User Dashboard
  </div>
  <div v-else>
    Access Denied
  </div>
</template>

<!-- After -->
<script setup>
const dashboardType = computed(() => {
  if (isSuspended.value) return 'suspended'
  if (isAdmin.value && hasPermission('dashboard')) return 'admin'
  if (isManager.value && hasPermission('dashboard')) return 'manager'
  if (isUser.value && hasPermission('dashboard')) return 'user'
  return 'denied'
})
</script>

<template>
  <AdminDashboard v-if="dashboardType === 'admin'" />
  <ManagerDashboard v-else-if="dashboardType === 'manager'" />
  <UserDashboard v-else-if="dashboardType === 'user'" />
  <SuspendedMessage v-else-if="dashboardType === 'suspended'" />
  <AccessDenied v-else />
</template>
```

### Use v-show for Frequent Toggle

```vue
<!-- v-if destroys/recreates - use for rare condition changes -->
<div v-if="showModal">
  <Modal />
</div>

<!-- v-show toggles display - use for frequent visibility changes -->
<div v-show="isExpanded">
  <CollapsibleContent />
</div>
```

---

## 9. TypeScript Integration

### defineProps with Type

```typescript
// Basic type
const props = defineProps<{
  title: string
  count: number
}>()

// With defaults using withDefaults
interface Props {
  title?: string
  count?: number
  items: string[]
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Default Title',
  count: 0
})
```

### defineEmits with Type

```typescript
// Typed emits
const emit = defineEmits<{
  update: [value: string]
  delete: [id: number]
  'custom-event': [payload: { data: string; meta: object }]
}>()

// Usage
emit('update', 'new value')
emit('delete', 42)
emit('custom-event', { data: 'test', meta: {} })
```

### Template Refs

```typescript
import { ref, onMounted } from 'vue'

const inputRef = ref<HTMLInputElement | null>(null)

onMounted(() => {
  inputRef.value?.focus()
})
</script>

<template>
  <input ref="inputRef" type="text" />
</template>
```

### Generic Components

```typescript
// GenericList.vue
<script setup lang="ts" generic="T extends { id: string | number }">
defineProps<{
  items: T[]
  renderItem: (item: T) => any
}>()
</script>
```

---

## 10. Vite Optimization

### Manual Chunks

```javascript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-charts': ['chart.js', 'vue-chartjs'],
          'vendor-ui': ['@headlessui/vue', '@heroicons/vue']
        }
      }
    }
  }
})
```

### Dependency Pre-bundling

```javascript
// vite.config.ts
export default defineConfig({
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'axios',
      'lodash-es'
    ],
    exclude: [
      'my-local-package'
    ]
  }
})
```

### Build Analysis

```javascript
// vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    vue(),
    visualizer({
      filename: 'stats.html',
      open: true,
      gzipSize: true
    })
  ]
})
```

---

## Safety

- Always test reactivity after migration (props, emits, lifecycle).
- Use TypeScript strict mode to catch type errors.
- Run Vue DevTools to verify component structure post-migration.
- Profile before/after with Vue Performance DevTools.
- Keep backward compatibility during incremental migration.
