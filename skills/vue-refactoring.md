---
name: vue-refactoring
version: 1.0.0
description: Refactor Vue.js 3 code from Options API to Composition API, extract composables,
  optimize reactivity and performance, and integrate TypeScript. Use when modernizing Vue
  2/3 codebases, improving component architecture, or optimizing Vue application performance.
metadata:
  category: design
  source: 'community'
  triggers:
  - migrating Vue.js Options API to Composition API
  - extracting reusable logic into Vue composables
  - optimizing Vue reactivity and component performance
  - integrating TypeScript with Vue 3 Composition API
eval_cases:
- id: options-to-composition-migration
  prompt: How do I migrate a Vue 2 Options API component to Vue 3 Composition API with script setup?
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
  prompt: Extract reusable logic from a Vue component into a composable for shared state and behavior
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
  prompt: When should I use ref() vs reactive() and how do I avoid unwanted deep reactivity in Vue 3?
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
  prompt: How do I optimize a Vue component with large lists using v-once, v-memo, and shallowRef?
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
---

# vue-refactoring

# Vue.js 3 Refactoring

Master migration from Options API to Composition API, composable extraction, reactivity patterns, performance optimization, and TypeScript integration for Vue 3.

## Use this skill when

- Migrating Vue 2 Options API code to Vue 3 Composition API
- Extracting reusable logic into composables
- Optimizing Vue component reactivity and render performance
- Integrating TypeScript with Vue 3 defineProps and defineEmits
- Refactoring large Vue components into smaller pieces
- Implementing Pinia stores with composable patterns

## Do not use this skill when

- Writing new Vue code from scratch (use vue-best-practices instead)
- Working with Vue 2 without migration intent
- Fixing trivial CSS/styling issues

## Instructions

1. Assess component complexity and identify migration/refactoring goals.
2. Convert Options API to Composition API using script setup where possible.
3. Extract reusable logic into composables.
4. Apply reactivity best practices (ref vs reactive, shallowRef).
5. Optimize template with v-once, v-memo, and computed properties.
6. Add TypeScript types with defineProps and defineEmits.
7. Validate with type checking and tests.

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

Composables extract and share reusable logic between components.

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

Render once and never update.

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

**Problem:** Store with too many state properties and actions.

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
