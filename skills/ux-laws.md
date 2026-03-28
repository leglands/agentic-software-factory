---
name: ux-laws
version: "2.0.0"
description: >
  Applies the 30 Laws of UX (Jon Yablonski — https://lawsofux.com) to user story
  writing, UX audit, design critique, and mobile/offline resilience patterns.
  Full origins, real product examples, cross-law relationships, and 4 application contexts.
metadata:
  category: design
  source: "https://lawsofux.com — Jon Yablonski (MIT)"
  integrated_by: "macaron-software/software-factory"
  integration_rationale: >
    Evidence-based cognitive laws reduce the subjective gap in UX review.
    Applied in 4 contexts: (1) US acceptance criteria — measurable cognitive constraints;
    (2) UX audit — 30-law checklist; (3) design critique — explain WHY not just THAT;
    (4) mobile/offline UX — network resilience with empathic messaging.
  triggers:
    - "when writing user stories or acceptance criteria"
    - "when reviewing or auditing a UI/UX"
    - "when critiquing a design proposal"
    - "when doing a UX heuristic evaluation"
    - "when discussing cognitive load or user mental models"
    - "when agent must evaluate if a UI is too complex"
    - "when defining performance SLAs for user-facing interactions"
    - "when designing mobile or offline-capable features"
    - "when handling network errors, retries, or disconnection states"
---

# UX Laws v2 — Agent Guide

Source: https://lawsofux.com (Jon Yablonski, MIT License)
30 laws w/ origins, examples, cross-law relations, 4 application contexts.

---

## THE 30 LAWS

### 1. Aesthetic-Usability Effect
*Beautiful design → perceived as more usable.*
**Origin**: Kurosu & Kashimura, Hitachi, 1995. 26 ATM UIs, 252 participants — stronger correlation b/w aesthetic appeal + perceived ease vs actual ease.
**Insight**: Beautiful design masks usability problems — can hide issues during testing.
**Takeaways**:
1. Aesthetically pleasing design → positive brain response → users believe it works better.
2. Users tolerate minor usability issues more in beautiful designs.
3. ⚠️ Visually pleasing design can hide usability problems in usability testing.
**AC**: "Visual design score (SUS aesthetic subscale) ≥70"

### 2. Choice Overload
*Too many options → overwhelm.*
**Origin**: Alvin Toffler coined "overchoice" in *Future Shock* (1970). Related → **Hick's Law**.
**Takeaways**:
1. Too many options hurt decision-making quality + experience perception.
2. Enable side-by-side comparison when necessary (e.g. pricing tiers).
3. Prioritize content at any moment (featured product); provide narrowing tools (search, filter).
**AC**: "Primary selection ≤7 options; all others behind filter/search"

### 3. Chunking
*Info broken down + grouped into meaningful wholes.*
**Origin**: George A. Miller, 1956 "Magical Number Seven, Plus or Minus Two". Related → **Miller's Law**.
**Takeaways**:
1. Chunking enables scanning — users find goal-relevant info faster.
2. Visually distinct groups w/ clear hierarchy align w/ how people evaluate digital content.
3. Use modules, separators, hierarchy to show relationships.
**AC**: "Content organized into ≤7 named groups per screen level"

### 4. Cognitive Bias
*Systematic thinking errors that influence perception + decision-making.*
**Origin**: Amos Tversky & Daniel Kahneman, 1972. Human judgment deviates from rational choice via heuristics — mental shortcuts that introduce systematic errors.
**Takeaways**:
1. Mental shortcuts (heuristics) increase efficiency but introduce biases w/out awareness.
2. Understanding biases (confirmation, anchoring, availability) helps design against dark patterns.
3. ⚠️ Never exploit cognitive biases for conversion — design ethically. Related → **Peak-End Rule**.
**Alert**: Identify dark patterns (false scarcity, misleading defaults, roach motel) — refuse to implement.

### 5. Cognitive Load
*Mental resources needed to understand + interact w/ an interface.*
**Origin**: John Sweller, late 1980s, expanding on Miller's info processing theories. "Cognitive Load Theory, Learning Difficulty, and Instructional Design" (1988). Related → **Miller's Law**, **Working Memory**.
**Types**:
- **Intrinsic**: effort for info relevant to goal (unavoidable)
- **Extraneous**: mental processing from distracting/unnecessary design (reducible)
**Takeaways**:
1. When info exceeds working space → tasks harder, details missed, user overwhelmed.
2. Remove extraneous cognitive load: unnecessary elements, ambiguous labels, redundant choices.
3. Design each screen to do ONE thing.
**AC**: "Each screen has exactly one primary action; secondary actions collapsed"

### 6. Doherty Threshold
*Productivity soars when computer + user interact at pace (<400ms) where neither waits.*
**Origin**: Walter J. Doherty & Ahrvind J. Thadani, IBM Systems Journal, 1982. Previous standard was 2000ms; they established 400ms as threshold for "addicting" interaction.
**Takeaways**:
1. System feedback within **400ms** keeps user attention + increases productivity.
2. Use *perceived* performance: skeleton screens, optimistic updates, instant visual response.
3. Animations engage visually while loading happens in background.
4. Progress bars make waits tolerable — even if inaccurate.
5. ⚠️ Intentional artificial delay can *increase* perceived value + trust (e.g. "Calculating..." for 800ms).
**SLA**: 0–100ms=instant | 100–400ms=fast | 400ms–1s=acceptable+indicator | >1s=loading state | >10s=background task+notification

### 7. Fitts's Law
*Target acquisition time = f(distance to + size of target).*
**Origin**: Paul Fitts, 1954. MT = a + b × log₂(2D/W). Fast movements + small targets = higher error rate.
**Takeaways**:
1. Touch targets must be large enough for accurate selection.
2. Adequate spacing between touch targets (min 8px; 16px preferred).
3. Place targets near user's natural task area (e.g. Submit near last field, not top-right).
**Minimums**: ≥44×44px (Apple HIG) | ≥48×48dp (Material) | ≥24×24px (WCAG 2.5.5 AAA)
**AC**: "All interactive targets have minimum touch area 44×44px"

### 8. Flow
*Mental state of full immersion — energized focus, control, enjoyment.*
**Origin**: Mihály Csíkszentmihályi, 1975. Balance point between challenge + skill.
**Takeaways**:
1. Flow = balance between task difficulty + user skill level.
2. Too hard → frustration; too easy → boredom. Match challenge to skill.
3. Provide feedback so users know what was done + what was accomplished.
4. Remove friction: optimize efficiency, make content discoverable.
**Anti-patterns**: Interrupt-driven confirmations, mode errors, unexpected navigation, modal dialogs mid-task.
**AC**: "Primary user flow contains 0 forced interruptions (modals, required redirects)"

### 9. Goal-Gradient Effect
*Tendency to approach goal increases w/ proximity to goal.*
**Origin**: Clark Hull, 1932 (behaviorist). Rats ran faster as they approached food. Implications for human reward programs understudied until Kivetz et al. (2006). Related → **Zeigarnik Effect**.
**Takeaways**:
1. Closer to completing task → faster work toward it.
2. Artificial progress toward goal increases motivation to complete.
3. Always show how close users are to completion.
**AC**: "Multi-step flows display progress indicator showing current step / total steps"
**Tactic**: Pre-fill loyalty cards (2/10 perceived as more motivating than 0/8 even w/ more stamps needed)

### 10. Hick's Law
*Decision time increases w/ number + complexity of choices.*
**Origin**: William Edmund Hick & Ray Hyman, 1952. RT = b × log₂(n + 1).
**Examples**: Google homepage (1 action), Apple TV remote (transfers complexity to TV interface), Slack progressive onboarding (hide all features except messaging input initially).
**Takeaways**:
1. Minimize choices when response time is critical.
2. Break complex tasks into smaller steps.
3. Highlight recommended options (reduce perceived complexity).
4. Progressive onboarding for new users.
5. ⚠️ Don't oversimplify to abstraction — removing too much removes capability.
**AC**: "Primary navigation ≤7 items; recommended option visually highlighted"

### 11. Jakob's Law
*Users spend most time on other sites — they prefer your site works same way.*
**Origin**: Jakob Nielsen, Nielsen Norman Group.
**Example**: YouTube 2017 redesign — allowed users to preview new Material Design UI, revert to old, submit feedback. Managed mental model transition w/out friction.
**Takeaways**:
1. Users transfer expectations from familiar products to new ones that appear similar.
2. Leverage existing mental models → users focus on tasks, not on learning new models.
3. When redesigning: give users time w/ old version before forcing new one.
**Related**: → **Mental Model**
**AC**: "All standard patterns (form save, navigation breadcrumbs, back button) follow established web conventions"

### 12. Law of Common Region
*Elements perceived as groups if they share an area w/ clearly defined boundary.*
**Origin**: Gestalt psychology (Prägnanz). One of 5 grouping categories.
**Takeaways**:
1. Common region creates clear structure for quickly understanding element relationships.
2. Border around elements = easy way to create common region.
3. Background color behind group = alternative way to create common region.
**Related**: → **Law of Proximity**, **Law of Prägnanz**

### 13. Law of Proximity
*Objects near each other tend to be grouped together.*
**Origin**: Gestalt psychology.
**Example**: Google search results — spacing between results groups each result as a related cluster.
**Takeaways**:
1. Proximity establishes relationship between nearby objects.
2. Elements in close proximity perceived to share similar functionality or traits.
3. Proximity helps users organize information faster.
**Rule**: Form labels must be closer to their input than to adjacent inputs.

### 14. Law of Prägnanz
*People perceive ambiguous/complex images as simplest form possible.*
**Origin**: Max Wertheimer, 1910. Observation at railroad crossing — lights appearing as single moving light (phi phenomenon). Foundation of Gestalt psychology.
**Takeaways**:
1. Human eye finds simplicity + order in complex shapes — prevents info overload.
2. Simple figures processed + remembered better than complex ones.
3. Eye simplifies complex shapes into unified forms.
**Rule**: Icons must be reducible to simplest geometric form + still recognizable.

### 15. Law of Similarity
*Human eye perceives similar elements as a group, even if separated.*
**Origin**: Gestalt psychology. Similarity via color, shape, size, orientation, movement.
**Takeaways**:
1. Visually similar elements perceived as related.
2. Color, shape, size, orientation, movement signal group membership + shared meaning.
3. Links + navigation must be visually differentiated from regular text.
**AC**: "All clickable elements use same visual treatment (color + underline/hover state)"

### 16. Law of Uniform Connectedness
*Visually connected elements perceived as more related than unconnected ones.*
**Origin**: Gestalt psychology.
**Example**: Google search results — borders around featured snippets/videos create visual connection + priority.
**Takeaways**:
1. Group similar functions w/ shared visual connection: colors, lines, frames, shapes.
2. Tangible connecting references (lines, arrows) create visual connection between sequential elements.
3. Use uniform connectedness to show context or emphasize relationships.

### 17. Mental Model
*Compressed model of what we think we know about a system + how it works.*
**Origin**: Kenneth Craik, *The Nature of Explanation* (1943). Related → **Jakob's Law**.
**Takeaways**:
1. We form working models about systems + apply them to similar new situations.
2. Match designs to users' mental models → they focus on tasks, not on learning.
3. E-commerce conventions (product cards, carts, checkout) exist b/c they match mental models.
4. Shrinking gap between designer mental models + user mental models = UX's biggest challenge.
**Methods**: user interviews, personas, journey maps, empathy maps, card sorting.

### 18. Miller's Law
*Average person can only keep 7 (±2) items in working memory.*
**Origin**: George Miller, 1956, "Magical Number Seven, Plus or Minus Two". Applied to short-term memory + channel capacity.
**Example**: Phone numbers chunked as (XXX) XXX-XXXX — 10 digits in 3 chunks.
**Takeaways**:
1. ⚠️ Don't use "7" to justify artificial design limitations — use chunking instead.
2. Organize content into smaller chunks.
3. Short-term memory capacity varies per individual + context.
**Related**: → **Chunking**, **Cognitive Load**, **Working Memory**

### 19. Occam's Razor
*Among equally good solutions, prefer one w/ fewest assumptions.*
**Origin**: William of Ockham (c.1287–1347), "lex parsimoniae" — law of parsimony.
**Takeaways**:
1. Best way to reduce complexity = not create it in first place.
2. Analyze each element — remove as many as possible w/out compromising function.
3. "Done" = when nothing more can be removed, not when nothing more can be added.
**Test**: "Can this feature/field/step be removed? What breaks?"

### 20. Paradox of Active User
*Users never read manuals — they start using software immediately.*
**Origin**: Mary Beth Rosson & John Carroll, 1987. New users skipped manuals, hit roadblocks, but still refused to read documentation.
**Takeaways**:
1. Users motivated to complete *immediate* tasks — won't invest in upfront learning.
2. They'd save time long-term by learning the system, but they don't — this is the paradox.
3. Make guidance *contextual + inline* — tooltips, coach marks, empty states — not separate docs.
**AC**: "Primary action discoverable within 10 seconds w/out documentation"

### 21. Pareto Principle (80/20 Rule)
*Roughly 80% of effects come from 20% of causes.*
**Origin**: Vilfredo Pareto observed 80% of Italy's land owned by 20% of population.
**Takeaways**:
1. Inputs + outputs are not evenly distributed.
2. Large group may have only a few meaningful contributors.
3. Focus majority of effort on areas that bring largest benefits to most users.
**Application**: Identify 20% of features used 80% of time → make those prominent. Deprioritize rest.

### 22. Parkinson's Law
*Any task inflates to fill all available time.*
**Origin**: Cyril Northcote Parkinson, *The Economist*, 1955.
**Takeaways**:
1. Limit task time to what users expect it'll take.
2. Reducing actual duration below expected improves UX.
3. Autofill, saved info, smart defaults prevent task inflation (checkout, booking forms).
**AC**: "Checkout form pre-fills all available data from user profile; only unknowns require input"

### 23. Peak-End Rule
*People judge experiences based on peak + end, not on average.*
**Origin**: Kahneman, Fredrickson, Schreiber & Redelmeier, 1993 "When More Pain Is Preferred to Less: Adding a Better End." Cold water experiment — 14°C for 60s vs 14°C for 60s + 15°C for 30s: participants preferred longer trial. Related → **Cognitive Bias**.
**Examples**:
- Mailchimp's high-five illustration after sending campaign (peak delight)
- Uber showing driver location immediately after request to reduce perceived wait (avoiding negative peak)
**Takeaways**:
1. Pay close attention to most intense points AND final moments of user journey.
2. Design to delight at most helpful/entertaining moment.
3. ⚠️ People recall negative experiences more vividly than positive ones.
**AC**: "On task completion, user receives clear confirmation w/ positive reinforcement + explicit next step"

### 24. Postel's Law (Robustness Principle)
*Be liberal in what you accept, conservative in what you send.*
**Origin**: Jon Postel, TCP spec. "Be conservative in what you do, be liberal in what you accept from others."
**Takeaways**:
1. Be empathetic, flexible, tolerant of various user inputs.
2. Anticipate any input format, access method, or capability.
3. More anticipation = more resilient design.
4. Accept variable input (e.g. phone: accept +33 6 12, 0612, 06-12-34, 06 12 34 56) → normalize internally → output consistently.
**AC**: "Phone/date/postal code fields accept all common format variants + normalize on blur"

### 25. Selective Attention
*We focus attention only on subset of stimuli related to our goals.*
**Origin**: Multiple theories from 1950s–1970s: Broadbent Filter Theory (1958), Cherry's Cocktail Party Effect (1953), Treisman's Attenuation Model (1960). Related → **Von Restorff Effect**.
**Key phenomena**:
- **Banner Blindness**: users ignore ad-like content even when it contains important info
- **Change Blindness**: significant interface changes go unnoticed w/out strong cues
**Takeaways**:
1. Users filter out irrelevant info — designers must guide attention, prevent overwhelm.
2. Never style important content to look like ads; never place content where ads typically appear.
3. Signal important changes w/ strong visual cues (animation, color change, toast notifications).
**AC**: "No critical action or status message placed in location typically used for ads"

### 26. Serial Position Effect
*Users best remember first + last items in a series.*
**Origin**: Herman Ebbinghaus. Primacy effect (beginning recalled via long-term memory) + Recency effect (end recalled via working memory).
**Takeaways**:
1. Place least important items in middle of lists.
2. Place key actions at far left/right within navigation elements.
3. Most critical CTA in primary (first) or final (last) position in a group.
**AC**: "Primary CTA positioned first or last in its action group; destructive actions in middle"

### 27. Tesler's Law (Law of Conservation of Complexity)
*For any system, there is a certain amount of complexity that cannot be reduced.*
**Origin**: Larry Tesler, Xerox PARC, mid-1980s. "An engineer should spend an extra week reducing complexity vs making millions of users spend an extra minute."
**Takeaways**:
1. All processes have irreducible complexity — it must be assumed by system OR user.
2. Always move complexity to system (defaults, validation, automation), not user.
3. ⚠️ Tognazzini's caveat: when you simplify, users attempt more complex tasks — new complexity appears.
4. Design for real users, not idealized rational ones.
**AC**: "Every required input field has a smart default or can be pre-filled from available context"

### 28. Von Restorff Effect (Isolation Effect)
*When multiple similar objects present, the one that differs is most likely remembered.*
**Origin**: Hedwig von Restorff (1906–1962), 1933 study on categorically similar item lists w/ one isolated item.
**Takeaways**:
1. Make important info + key actions visually distinctive.
2. ⚠️ Use restraint — too many "distinctive" elements compete + none stand out (crying wolf).
3. ⚠️ Don't rely exclusively on color for contrast (color blindness).
4. ⚠️ Consider motion sensitivity when using animation for contrast.
**AC**: "Exactly one primary CTA per screen; all others visually secondary"

### 29. Working Memory
*Cognitive system that temporarily holds + manipulates info needed for tasks.*
**Origin**: Term coined by Miller, Galanter & Pribram; formalized by Atkinson & Shiffrin (1968). Capacity: 4–7 chunks, fades after 20–30 seconds.
**Key insight**: Brains excel at *recognition* (seen before?) but struggle at *recall* (what was on previous screen?). Related → **Cognitive Load**.
**Takeaways**:
1. Design w/ working memory limit in mind — show only necessary + relevant info.
2. Support recognition over recall: differentiate visited links, show breadcrumbs, display what was selected.
3. Carry critical info across screens (comparison tables, persistent summary bars in checkout).
**AC**: "Users never need to remember info from one screen to complete action on another"

### 30. Zeigarnik Effect
*People remember uncompleted or interrupted tasks better than completed ones.*
**Origin**: Bluma Zeigarnik (1900–1988), Soviet psychologist, Berlin School. Memory study in 1920s comparing incomplete vs complete tasks. Related → **Goal-Gradient Effect**.
**Takeaways**:
1. Provide clear signifiers of additional/available content (invite discovery).
2. Artificial progress toward goal increases motivation to complete.
3. Show clear progress indicators.
**Tactic**: Multi-step forms: save progress, show "Continue where you left off" on return. Unfinished task stays on user's mind.
**AC**: "If user abandons multi-step flow, progress is saved + highlighted on next visit"

---

## CROSS-LAW RELATIONSHIP MAP

| Law | Closely Related To |
|-----|--------------------|
| Choice Overload | Hick's Law |
| Chunking | Miller's Law |
| Cognitive Load | Miller's Law, Working Memory |
| Cognitive Bias | Peak-End Rule |
| Goal-Gradient Effect | Zeigarnik Effect |
| Jakob's Law | Mental Model |
| Law of Common Region | Law of Proximity, Law of Prägnanz |
| Mental Model | Jakob's Law |
| Miller's Law | Chunking, Cognitive Load, Working Memory |
| Peak-End Rule | Cognitive Bias |
| Selective Attention | Von Restorff Effect |
| Working Memory | Cognitive Load |
| Zeigarnik Effect | Goal-Gradient Effect |

---

## CONTEXT A — Writing User Stories + Acceptance Criteria

Use these laws to make acceptance criteria **measurable + cognitive-science-backed**.

### Hick's Law
- **AC**: "Given N choices presented, user reaches decision in under X seconds"
- **Rule**: max 5–7 primary actions per screen; progressively disclose rest
- **Violation**: "User can configure 15 settings on first screen" → violates Hick's

### Miller's Law
- **AC**: "No single view presents more than 7 items w/out pagination or grouping"
- **Rule**: chunk related items; use progressive disclosure beyond 7

### Cognitive Load
- **AC**: "Feature does not add a new required input field to an existing flow"
- **Question**: "What decision or memory burden does this remove from user?"

### Doherty Threshold
- **AC**: "Page responds to user action within 400ms (visual feedback or result)"
- **Rule**: if backend takes >400ms, show immediate optimistic feedback or skeleton screen

### Goal-Gradient Effect
- **AC**: "Progress indicator shows user's position in X-step flow"

### Peak-End Rule
- **AC**: "On form submission, user sees clear success confirmation w/ next step"
- **Violation**: 8-step form ending w/ "Your request was submitted" (flat, emotionless ending)

### Pareto Principle (80/20)
- **Use as scoping filter**: identify 20% of features delivering 80% of user value → build those first

### Tesler's Law
- **Question**: "Which side — user or system — is better equipped to handle this complexity?"
- **Rule**: move complexity to system; expose simple surface to user

### Occam's Razor
- **AC**: "Feature can be used w/out reading documentation"
- **Test**: "Can any element be removed w/out breaking the feature?"

### Parkinson's Law
- **Rule**: constrain story scope explicitly. Add explicit exclusion lines: "OUT OF SCOPE: X, Y, Z"

### Zeigarnik Effect
- **AC**: "If user leaves multi-step flow, their progress is saved + a reminder is shown on return"

### Postel's Law
- **AC**: "Phone/date/postal fields accept all common formats; normalized on blur/submit"

---

## CONTEXT B — UX Audit Checklist (30 Laws)

Report format per law: **Law | Status (✅/❌/⚠️/N/A) | Evidence | Recommendation**

### PERCEPTION & GROUPING (Gestalt)
| Law | What to check |
|-----|--------------|
| Law of Proximity | Related items visually close; unrelated items have whitespace separation |
| Law of Common Region | Related items share a container/border/background |
| Law of Similarity | Items w/ similar function look similar (color, shape, size) |
| Law of Uniform Connectedness | Connected items (lines, borders) imply relationship |
| Law of Prägnanz | Complex graphics reduce to most readable, simplest form |

### ATTENTION & MEMORY
| Law | What to check |
|-----|--------------|
| Miller's Law | No list/menu/set exceeds 7 (±2) ungrouped items |
| Von Restorff Effect | Primary CTA visually distinct from secondary actions (exactly 1 standout) |
| Serial Position Effect | Most important items are first or last in lists/navs |
| Selective Attention | Non-critical content doesn't compete w/ main task; nothing looks like an ad |
| Working Memory | Users never need to remember info from screen A to act on screen B |
| Mental Model | UI matches what users know from other apps (Jakob's Law conventions) |

### DECISION & INTERACTION
| Law | What to check |
|-----|--------------|
| Hick's Law | Primary options ≤7; secondary options hidden until needed; recommended option highlighted |
| Fitts's Law | Click/touch targets ≥44×44px, close to natural cursor/thumb path, adequate spacing |
| Cognitive Load | Each page asks user to do exactly one thing |
| Choice Overload | Dropdowns/filters have sensible defaults; visible options ≤10; comparison available |
| Flow | Interaction sequence uninterrupted; 0 forced modals mid-task; no dead-ends |

### TIME & PERFORMANCE
| Law | What to check |
|-----|--------------|
| Doherty Threshold | Every user action gets visual feedback in <400ms |
| Goal-Gradient Effect | Progress indicator in multi-step flows; current step shown |
| Peak-End Rule | Key moment (peak) + closing confirmation (end) well-designed |
| Zeigarnik Effect | Long/async tasks show saved state on return |
| Parkinson's Law | Form pre-fills available data; autofill leveraged for completion |

### COGNITIVE PRINCIPLES
| Law | What to check |
|-----|--------------|
| Aesthetic-Usability Effect | UI visually clean + consistent (users perceive prettier = more usable) |
| Chunking | Info grouped into meaningful units (≤7 per group) |
| Cognitive Bias | No dark patterns exploiting anchoring, scarcity, urgency, or social proof |
| Paradox of Active User | Core actions discoverable <10 seconds w/out documentation |
| Postel's Law | Input: liberal (multiple formats accepted); Output: consistent + normalized |
| Tesler's Law | Complexity absorbed by system (defaults, validation, automation), not user |

### STRATEGY & STRUCTURE
| Law | What to check |
|-----|--------------|
| Jakob's Law | Conventions from other apps respected (save, back, nav patterns) |
| Occam's Razor | No feature/field exists w/out a clear user need |
| Pareto Principle | 20% of features used most are most prominent + optimized |

---

## CONTEXT C — Design Critique Template

```
## UX Laws Critique — [Feature Name]

### Violations (must fix before ship)
- **[Law Name]**: [What is violated] → [Recommended fix]

### Warnings (should fix in next iteration)
- **[Law Name]**: [Potential issue] → [Suggested improvement]

### Compliant (notable strengths)
- **[Law Name]**: [What the design does right]

### Net Assessment
Cognitive load: [Low/Medium/High]
Decision complexity: [Low/Medium/High — Hick's score: N options at primary level]
Memory demand: [Low/Medium/High — Miller's score: N ungrouped items max]
Peak moment: [Identified / Not designed]
End moment: [Designed / Generic]
```

---

## CONTEXT D — Mobile & Network Resilience UX

*Apply when designing web async, native mobile apps, or any feature w/ network dependency.*

### Doherty Threshold → Network States
Map response time to UX treatment:

| Latency | Treatment |
|---------|-----------|
| 0–100ms | No indicator needed — instant |
| 100–400ms | Subtle spinner (don't interrupt flow) |
| 400ms–1s | Progress indicator + context label |
| 1s–3s | Skeleton screen (content shape placeholder) |
| 3s–10s | Progress bar + estimated time + cancel option |
| >10s | Background task + "We'll notify you" + dismissable |

### Offline / Network Loss States
**Empathic messaging patterns** (not technical error messages):

```
❌ BAD:  "ERR_NETWORK_CHANGED"
❌ BAD:  "Request failed with status 0"
❌ BAD:  "No internet connection."

✅ GOOD (empathic): 
- "You're offline — don't worry, your work is saved."
- "Lost connection. We'll keep trying + sync when you're back online."
- "Slow connection — this might take a moment. Your data is safe."
- "Back online! Syncing your changes now..."
```

**Required states to design**:
1. **Offline detected**: empathic message, show cached data if available, queue pending actions
2. **Partial connectivity** (high latency): degraded mode indicator, disable non-critical features
3. **Reconnected**: auto-retry pending actions, sync notification, success confirmation
4. **Conflict** (offline edit + server edit): clear merge UI, never silently overwrite

### Retry UX (Zeigarnik + Goal-Gradient)
```
- Show retry attempt count: "Retrying... (attempt 2/3)"
- Exponential backoff indicator: "Next retry in 10s"
- Manual override: "Retry now" button always visible
- Clear failure state: "Failed after 3 attempts — save locally or try later"
- Never loop silently — user must know something is happening
```

### Optimistic Updates (Doherty + Peak-End Rule)
```
- Apply state change instantly in UI (optimistic)
- Queue action for when network available
- On failure: roll back gracefully w/ clear explanation
- Pattern: Action → Instant feedback → Background confirm → (if fail) Friendly rollback message
```

### Progressive Loading (Chunking + Working Memory)
```
- Load critical content first (above fold)
- Lazy load below-fold content
- Skeleton screens: match actual content shape (not generic spinner)
- Preserve user position on reload (scroll restoration)
```

### Mobile-Specific Fitts's Law Targets

| Context | Minimum size |
|---------|-------------|
| Primary CTA | 48×48dp / 44×44pt |
| Navigation item | 44×44dp |
| Close/Back button | 44×44dp, positioned reachably (bottom sheet) |
| Form input height | 48dp / 44pt |
| Touch target spacing | 8dp minimum between adjacent targets |
| Thumb zone (phone) | Bottom 60% of screen — put primary actions there |

### Offline-First AC Pattern
```
Given the user is offline
When they perform [action]
Then the UI responds within 100ms (local state update)
And shows "Saved offline — will sync when connected"
And the action is queued and retried automatically when connection resumes
And on successful sync, user receives a subtle confirmation toast
```

---

## QUICK REFERENCE — Law to Category

| Category | Laws |
|----------|------|
| **Scope / Prioritization** | Pareto, Occam's Razor, Parkinson's Law, Tesler's |
| **Decision UX** | Hick's, Choice Overload, Cognitive Load |
| **Memory** | Miller's, Working Memory, Chunking, Zeigarnik |
| **Perception (Gestalt)** | Proximity, Common Region, Similarity, Uniform Connectedness, Prägnanz |
| **Interaction** | Fitts's, Doherty Threshold, Flow |
| **Emotional / Narrative** | Peak-End Rule, Aesthetic-Usability Effect, Goal-Gradient, Von Restorff |
| **Mental Models** | Jakob's Law, Mental Model, Paradox of Active User |
| **System Design** | Postel's Law, Tesler's Law |
| **Attention** | Selective Attention, Cognitive Bias |
| **Mobile / Network** | Doherty, Fitts's, Postel's, Zeigarnik, Goal-Gradient |
