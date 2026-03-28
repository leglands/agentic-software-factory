---
name: react-state-management
version: 1.0.0
description: Master modern React state management with Redux Toolkit, Zustand, Jotai,
  and React Query. Use when setting up global state, managing server state, or choosing
  between state management solutions.
metadata:
  category: design
  source: 'antigravity-awesome-skills (MIT) — source: community'
  triggers:
  - setting up global state, managing server state, or choosing between state manage
eval_cases:
- id: react-state-management-approach
  prompt: How should I approach react state management for a production system?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Provides concrete guidance on react state management
  tags:
  - react
- id: react-state-management-best-practices
  prompt: What are the key best practices and pitfalls for react state management?
  should_trigger: true
  checks:
  - length_min:100
  - no_placeholder
  expectations:
  - Lists concrete best practices for react state management
  tags:
  - react
  - best-practices
- id: react-state-management-antipatterns
  prompt: What are the most common mistakes to avoid with react state management?
  should_trigger: true
  checks:
  - length_min:80
  - no_placeholder
  expectations:
  - Identifies anti-patterns or mistakes to avoid
  tags:
  - react
  - antipatterns
- id: react-zustand-setup
  prompt: How do I set up a Zustand store with devtools and persistence middleware?
  checks:
  - regex: create.*devtools.*persist|persist.*devtools
  - length_min: 80
  - has_keyword: zustand
  expectations:
  - Shows Zustand store creation with middleware setup
  - Includes devtools and persist configuration
- id: react-redux-toolkit-slice
  prompt: Create a Redux Toolkit slice for managing user authentication state with
    async thunk
  checks:
  - regex: createSlice|createAsyncThunk
  - length_min: 100
  - has_keyword: redux
  expectations:
  - Defines slice with reducers and async thunk
  - Includes proper TypeScript types for user state
- id: react-jotai-atoms
  prompt: How do I create derived atoms in Jotai that compute values from other atoms?
  checks:
  - regex: atom.*get.*atom|derived
  - length_min: 60
  - has_keyword: jotai
  expectations:
  - Demonstrates atom composition
  - Shows computed/derived state pattern
- id: react-query-optimistic-update
  prompt: Implement optimistic updates with React Query for a mutation
  checks:
  - regex: onMutate|queryClient.setQueryData|rollback
  - length_min: 80
  - has_keyword: react-query
  expectations:
  - Shows onMutate for optimistic update
  - Includes rollback logic in onError
- id: react-state-selection
  prompt: What is the best way to select specific state slices to prevent unnecessary
    re-renders?
  checks:
  - regex: selector|useStore.*=>|subscribe
  - length_min: 50
  - has_keyword: zustand
  expectations:
  - Explains selective subscription pattern
  - Mentions avoiding full store subscription
- id: react-query-vs-redux
  prompt: When should I use React Query vs Redux for state management?
  checks:
  - regex: server.*state|client.*state|caching
  - length_min: 80
  - has_keyword: react-query
  expectations:
  - Differentiates server vs client state
  - Recommends appropriate tool per use case
- id: react-migration-redux
  prompt: Migrate legacy Redux to Redux Toolkit - show the before and after pattern
  checks:
  - regex: createSlice|Immer|reducers
  - length_min: 70
  - has_keyword: redux
  expectations:
  - Shows legacy Redux pattern
  - Demonstrates RTK modern equivalent
- id: react-form-state
  prompt: Which library should I use for form state management in React?
  checks:
  - regex: React Hook Form|Formik|validation
  - length_min: 40
  - has_keyword: form
  expectations:
  - Recommends form state solution
  - Mentions validation approach
- id: react-url-state
  prompt: How do I manage URL state like query parameters and route state?
  checks:
  - regex: nuqs|React Router|searchParams
  - length_min: 40
  - has_keyword: url
  expectations:
  - Addresses URL state management
  - Mentions routing integration
- id: react-combining-states
  prompt: How do I combine Zustand for UI state with React Query for server state?
  checks:
  - regex: useQuery|useStore|client.*state
  - length_min: 60
  - has_keyword: zustand
  expectations:
  - Shows hybrid approach
  - Separates client and server state concerns
- id: react-normalize-state
  prompt: Why should I normalize nested data structures in my state?
  checks:
  - regex: normalize|flatten|update.*easy
  - length_min: 50
  - has_keyword: state
  expectations:
  - Explains normalization benefits
  - Mentions easier state updates
- id: react-atomic-vs-global
  prompt: When is Jotai better than Redux Toolkit for atomic updates?
  checks:
  - regex: atomic|granular|re-render
  - length_min: 60
  - has_keyword: jotai
  expectations:
  - Contrasts atomic vs global state
  - Highlights Jotai's granular updates
- id: react-state-immutable-updates
  prompt: How do I ensure immutable state updates work correctly in React?
  checks:
  - regex: immer|immutable|spread.*operator|Object.assign
  - length_min: 60
  - has_keyword: state
  expectations:
  - Explains immutable update patterns
  - Mentions Immer or spread operators
- id: react-swr-vs-react-query
  prompt: What are the differences between SWR and React Query for data fetching?
  checks:
  - regex: swr|react-query|cache|stale
  - length_min: 70
  - has_keyword: react-query
  expectations:
  - Compares SWR and React Query features
  - Discusses caching strategies
- id: react-redux-selector-pattern
  prompt: How do I create optimized Redux selectors with reselect to prevent re-renders?
  checks:
  - regex: createSelector|selector|memoize
  - length_min: 60
  - has_keyword: redux
  expectations:
  - Shows memoized selector creation
  - Demonstrates selector composition
- id: react-zustand-middleware
  prompt: How do I add custom middleware to a Zustand store for logging or auth?
  checks:
  - regex: middleware|zustand.*middleware|console.log
  - length_min: 50
  - has_keyword: zustand
  expectations:
  - Demonstrates custom middleware pattern
  - Shows store middleware chain
- id: react-context-vs-global-state
  prompt: When should I use React Context instead of Zustand or Redux?
  checks:
  - regex: context|Provider|global.*state|re-render
  - length_min: 60
  - has_keyword: context
  expectations:
  - Contrasts Context with global stores
  - Explains when Context is appropriate
- id: react-query-cache-invalidation
  prompt: How do I properly invalidate React Query cache after a mutation?
  checks:
  - regex: invalidateQueries|queryClient|queryKey
  - length_min: 50
  - has_keyword: react-query
  expectations:
  - Shows cache invalidation pattern
  - Demonstrates queryKey usage
- id: react-state-testing
  prompt: What is the best approach for testing React state management logic?
  checks:
  - regex: test|jest|vitest|renderHook|store.*test
  - length_min: 50
  - has_keyword: test
  expectations:
  - Recommends testing strategies
  - Mentions testing libraries for state
- id: react-jotai-provider
  prompt: Do I need a Provider wrapper when using Jotai in my React app?
  checks:
  - regex: Provider|jotai|atom
  - length_min: 40
  - has_keyword: jotai
  expectations:
  - Clarifies Jotai provider requirements
  - Explains store-less architecture
- id: react-redux-toolkit-rtk-query
  prompt: How do I set up RTK Query for automatic API caching and synchronization?
  checks:
  - regex: createApi|fetchBaseQuery|endpoint
  - length_min: 70
  - has_keyword: redux
  expectations:
  - Shows RTK Query API slice setup
  - Demonstrates automatic caching
- id: react-zustand-persistence
  prompt: How do I persist Zustand state to localStorage and rehydrate on reload?
  checks:
  - regex: persist|localStorage|storage|rehydrate
  - length_min: 50
  - has_keyword: zustand
  expectations:
  - Demonstrates persistence middleware
  - Shows storage configuration
- id: react-server-state-caching
  prompt: How does React Query handle stale-while-revalidate caching?
  checks:
  - regex: staleTime|gcTime|revalidate|cache
  - length_min: 50
  - has_keyword: react-query
  expectations:
  - Explains stale-while-revalidate pattern
  - Discusses cache timing configuration
- id: react-atomic-design-state
  prompt: How should I structure state atoms in Jotai for a scalable application?
  checks:
  - regex: atom|primitive|derived|split
  - length_min: 50
  - has_keyword: jotai
  expectations:
  - Shows atom composition strategies
  - Demonstrates scalable atom organization
---
# react-state-management

# React State Management

Comprehensive guide to modern React state management patterns, from local component state to global stores and server state synchronization.

## Do not use this skill when

- The task is unrelated to react state management
- You need a different domain or tool outside this scope

## Instructions

- Clarify goals, constraints, and required inputs.
- Apply relevant best practices and validate outcomes.
- Provide actionable steps and verification.
- If detailed examples are required, open `resources/implementation-playbook.md`.

## Use this skill when

- Setting up global state management in a React app
- Choosing between Redux Toolkit, Zustand, or Jotai
- Managing server state with React Query or SWR
- Implementing optimistic updates
- Debugging state-related issues
- Migrating from legacy Redux to modern patterns

## Core Concepts

### 1. State Categories

| Type | Description | Solutions |
|------|-------------|-----------|
| **Local State** | Component-specific, UI state | useState, useReducer |
| **Global State** | Shared across components | Redux Toolkit, Zustand, Jotai |
| **Server State** | Remote data, caching | React Query, SWR, RTK Query |
| **URL State** | Route parameters, search | React Router, nuqs |
| **Form State** | Input values, validation | React Hook Form, Formik |

### 2. Selection Criteria

```
Small app, simple state → Zustand or Jotai
Large app, complex state → Redux Toolkit
Heavy server interaction → React Query + light client state
Atomic/granular updates → Jotai
```

## Quick Start

### Zustand (Simplest)

```typescript
// store/useStore.ts
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

interface AppState {
  user: User | null
  theme: 'light' | 'dark'
  setUser: (user: User | null) => void
  toggleTheme: () => void
}

export const useStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        theme: 'light',
        setUser: (user) => set({ user }),
        toggleTheme: () => set((state) => ({
          theme: state.theme === 'light' ? 'dark' : 'light'
        })),
      }),
      { name: 'app-storage' }
    )
  )
)

// Usage in component
function Header() {
  const { user, theme, toggleTheme } = useStore()
  return (
    <header className={theme}>
      {user?.name}
      <button onClick={toggleTheme}>Toggle Theme</button>
    </header>
  )
}
```

## Patterns

### Pattern 1: Redux Toolkit with TypeScript

```typescript
// store/index.ts
import { configureStore } from '@reduxjs/toolkit'
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux'
import userReducer from './slices/userSlice'
import cartReducer from './slices/cartSlice'

export const store = configureStore({
  reducer: {
    user: userReducer,
    cart: cartReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

// Typed hooks
export const useAppDispatch: () => AppDispatch = useDispatch
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector
```

```typescript
// store/slices/userSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'

interface User {
  id: string
  email: string
  name: string
}

interface UserState {
  current: User | null
  status: 'idle' | 'loading' | 'succeeded' | 'failed'
  error: string | null
}

const initialState: UserState = {
  current: null,
  status: 'idle',
  error: null,
}

export const fetchUser = createAsyncThunk(
  'user/fetchUser',
  async (userId: string, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/users/${userId}`)
      if (!response.ok) throw new Error('Failed to fetch user')
      return await response.json()
    } catch (error) {
      return rejectWithValue((error as Error).message)
    }
  }
)

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User>) => {
      state.current = action.payload
      state.status = 'succeeded'
    },
    clearUser: (state) => {
      state.current = null
      state.status = 'idle'
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUser.pending, (state) => {
        state.status = 'loading'
        state.error = null
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.status = 'succeeded'
        state.current = action.payload
      })
      .addCase(fetchUser.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.payload as string
      })
  },
})

export const { setUser, clearUser } = userSlice.actions
export default userSlice.reducer
```

### Pattern 2: Zustand with Slices (Scalable)

```typescript
// store/slices/createUserSlice.ts
import { StateCreator } from 'zustand'

export interface UserSlice {
  user: User | null
  isAuthenticated: boolean
  login: (credentials: Credentials) => Promise<void>
  logout: () => void
}

export const createUserSlice: StateCreator<
  UserSlice & CartSlice, // Combined store type
  [],
  [],
  UserSlice
> = (set, get) => ({
  user: null,
  isAuthenticated: false,
  login: async (credentials) => {
    const user = await authApi.login(credentials)
    set({ user, isAuthenticated: true })
  },
  logout: () => {
    set({ user: null, isAuthenticated: false })
    // Can access other slices
    // get().clearCart()
  },
})

// store/index.ts
import { create } from 'zustand'
import { createUserSlice, UserSlice } from './slices/createUserSlice'
import { createCartSlice, CartSlice } from './slices/createCartSlice'

type StoreState = UserSlice & CartSlice

export const useStore = create<StoreState>()((...args) => ({
  ...createUserSlice(...args),
  ...createCartSlice(...args),
}))

// Selective subscriptions (prevents unnecessary re-renders)
export const useUser = () => useStore((state) => state.user)
export const useCart = () => useStore((state) => state.cart)
```

### Pattern 3: Jotai for Atomic State

```typescript
// atoms/userAtoms.ts
import { atom } from 'jotai'
import { atomWithStorage } from 'jotai/utils'

// Basic atom
export const userAtom = atom<User | null>(null)

// Derived atom (computed)
export const isAuthenticatedAtom = atom((get) => get(userAtom) !== null)

// Atom with localStorage persistence
export const themeAtom = atomWithStorage<'light' | 'dark'>('theme', 'light')

// Async atom
export const userProfileAtom = atom(async (get) => {
  const user = get(userAtom)
  if (!user) return null
  const response = await fetch(`/api/users/${user.id}/profile`)
  return response.json()
})

// Write-only atom (action)
export const logoutAtom = atom(null, (get, set) => {
  set(userAtom, null)
  set(cartAtom, [])
  localStorage.removeItem('token')
})

// Usage
function Profile() {
  const [user] = useAtom(userAtom)
  const [, logout] = useAtom(logoutAtom)
  const [profile] = useAtom(userProfileAtom) // Suspense-enabled

  return (
    <Suspense fallback={<Skeleton />}>
      <ProfileContent profile={profile} onLogout={logout} />
    </Suspense>
  )
}
```

### Pattern 4: React Query for Server State

```typescript
// hooks/useUsers.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

// Query keys factory
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters: UserFilters) => [...userKeys.lists(), filters] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
}

// Fetch hook
export function useUsers(filters: UserFilters) {
  return useQuery({
    queryKey: userKeys.list(filters),
    queryFn: () => fetchUsers(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes (formerly cacheTime)
  })
}

// Single user hook
export function useUser(id: string) {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => fetchUser(id),
    enabled: !!id, // Don't fetch if no id
  })
}

// Mutation with optimistic update
export function useUpdateUser() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateUser,
    onMutate: async (newUser) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: userKeys.detail(newUser.id) })

      // Snapshot previous value
      const previousUser = queryClient.getQueryData(userKeys.detail(newUser.id))

      // Optimistically update
      queryClient.setQueryData(userKeys.detail(newUser.id), newUser)

      return { previousUser }
    },
    onError: (err, newUser, context) => {
      // Rollback on error
      queryClient.setQueryData(
        userKeys.detail(newUser.id),
        context?.previousUser
      )
    },
    onSettled: (data, error, variables) => {
      // Refetch after mutation
      queryClient.invalidateQueries({ queryKey: userKeys.detail(variables.id) })
    },
  })
}
```

### Pattern 5: Combining Client + Server State

```typescript
// Zustand for client state
const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  modal: null,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  openModal: (modal) => set({ modal }),
  closeModal: () => set({ modal: null }),
}))

// React Query for server state
function Dashboard() {
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const { data: users, isLoading } = useUsers({ active: true })
  const { data: stats } = useStats()

  if (isLoading) return <DashboardSkeleton />

  return (
    <div className={sidebarOpen ? 'with-sidebar' : ''}>
      <Sidebar open={sidebarOpen} onToggle={toggleSidebar} />
      <main>
        <StatsCards stats={stats} />
        <UserTable users={users} />
      </main>
    </div>
  )
}
```

## Best Practices

### Do's
- **Colocate state** - Keep state as close to where it's used as possible
- **Use selectors** - Prevent unnecessary re-renders with selective subscriptions
- **Normalize data** - Flatten nested structures for easier updates
- **Type everything** - Full TypeScript coverage prevents runtime errors
- **Separate concerns** - Server state (React Query) vs client state (Zustand)

### Don'ts
- **Don't over-globalize** - Not everything needs to be in global state
- **Don't duplicate server state** - Let React Query manage it
- **Don't mutate directly** - Always use immutable updates
- **Don't store derived data** - Compute it instead
- **Don't mix paradigms** - Pick one primary solution per category

## Migration Guides

### From Legacy Redux to RTK

```typescript
// Before (legacy Redux)
const ADD_TODO = 'ADD_TODO'
const addTodo = (text) => ({ type: ADD_TODO, payload: text })
function todosReducer(state = [], action) {
  switch (action.type) {
    case ADD_TODO:
      return [...state, { text: action.payload, completed: false }]
    default:
      return state
  }
}

// After (Redux Toolkit)
const todosSlice = createSlice({
  name: 'todos',
  initialState: [],
  reducers: {
    addTodo: (state, action: PayloadAction<string>) => {
      // Immer allows "mutations"
      state.push({ text: action.payload, completed: false })
    },
  },
})
```

## Resources

- [Redux Toolkit Documentation](https://redux-toolkit.js.org/)
- [Zustand GitHub](https://github.com/pmndrs/zustand)
- [Jotai Documentation](https://jotai.org/)
- [TanStack Query](https://tanstack.com/query)

---

## Live Documentation

When working on tasks covered by this skill, use fetch_url to get current docs:
- fetch_url(https://redux-toolkit.js.org/)
- fetch_url(https://github.com/pmndrs/zustand)
- fetch_url(https://jotai.org/)
- fetch_url(https://tanstack.com/query)
- Always verify SDK versions against live docs
