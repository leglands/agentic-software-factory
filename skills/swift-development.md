---
name: swift-development
version: 1.0.0
description: Swift/SwiftUI development skill. Covers Swift 6 concurrency (async/await, actors), SwiftUI views (declarative, state, @Observable), UIKit interop, XCTest, SPM, Combine, error handling (Result, throws), performance (Instruments).
metadata:
  category: development
  source: software-factory
  triggers:
  - swift development
  - swiftui development
  - ios development swift
eval_cases:
- id: swift-async-await
  prompt: How do I implement async/await in Swift 6 for a network call?
  should_trigger: true
  checks:
  - length_min:80
  - no_placeholder
  expectations:
  - Shows async function declaration, await usage, Task wrapper
  tags:
  - swift
  - concurrency
- id: swiftui-state-management
  prompt: Explain @State vs @Binding vs @ObservedObject in SwiftUI.
  should_trigger: true
  checks:
  - length_min:100
  - no_placeholder
  expectations:
  - Contrasts all three property wrappers with use cases
  tags:
  - swiftui
  - state-management
- id: swift-actor-isolation
  prompt: How do actors prevent data races in Swift 6?
  should_trigger: true
  checks:
  - length_min:80
  - no_placeholder
  expectations:
  - Explains actor isolation, Sendable, @MainActor
  tags:
  - swift
  - actors
- id: swiftui-observable
  prompt: Implement @Observable macro for a SwiftUI model.
  should_trigger: true
  checks:
  - length_min:60
  - no_placeholder
  expectations:
  - Shows @Observable class, observed properties
  tags:
  - swiftui
  - observable
- id: uikit-swiftui-interop
  prompt: Wrap a UIViewController in SwiftUI using UIViewControllerRepresentable.
  should_trigger: true
  checks:
  - length_min:80
  - no_placeholder
  expectations:
  - Shows UIViewControllerRepresentable implementation
  tags:
  - uiKit
  - swiftui
- id: xctest-unit-test
  prompt: Write a unit test for a Swift async function using XCTest.
  should_trigger: true
  checks:
  - length_min:80
  - no_placeholder
  expectations:
  - Uses XCTest expectation, async test method
  tags:
  - testing
  - xctest
- id: xctest-ui-test
  prompt: Create a UI test that taps a button and verifies a label changes.
  should_trigger: true
  checks:
  - length_min:60
  - no_placeholder
  expectations:
  - Uses XCUITest, XCTAssertEqual, app.buttons[]
  tags:
  - testing
  - ui-testing
- id: spm-package-dependency
  prompt: Add a Swift Package Manager dependency to an Xcode project via Package.swift.
  should_trigger: true
  checks:
  - length_min:60
  - no_placeholder
  expectations:
  - Shows package manifest, dependencies array, target
  tags:
  - spm
  - package-manager
- id: combine-publisher
  prompt: Create a Combine publisher that debounces text input.
  should_trigger: true
  checks:
  - length_min:80
  - no_placeholder
  expectations:
  - Shows PassthroughSubject, debounce, sink
  tags:
  - combine
  - reactive
- id: swift-error-result
  prompt: Handle errors with Result type in Swift.
  should_trigger: true
  checks:
  - length_min:60
  - no_placeholder
  expectations:
  - Shows Result<Success, Failure>, .success, .failure, flatMap
  tags:
  - error-handling
  - result
- id: swift-throws-prop
  prompt: Propagate errors with throws and do-catch in Swift.
  should_trigger: true
  checks:
  - length_min:60
  - no_placeholder
  expectations:
  - Shows throws keyword, do-catch, try usage
  tags:
  - error-handling
  - throws
- id: instruments-performance
  prompt: Profile memory leaks using Instruments in Xcode.
  should_trigger: true
  checks:
  - length_min:80
  - no_placeholder
  expectations:
  - Mentions Instruments, Leaks, Allocations, timeline analysis
  tags:
  - performance
  - instruments
- id: swiftui-list-performance
  prompt: Optimize a slow SwiftUI List with large datasets.
  should_trigger: true
  checks:
  - length_min:80
  - no_placeholder
  expectations:
  - Mentions lazy loading, Equatable, diffable data
  tags:
  - swiftui
  - performance
---

# swift-development

## Use this skill when

- Swift/SwiftUI app development tasks
- iOS/macOS/watchOS/tvOS platform work
- Swift concurrency, actors, async/await
- SwiftUI state management, @Observable
- UIKit-SwiftUI interoperability
- XCTest unit/UI testing
- Swift Package Manager
- Combine reactive programming
- Swift error handling (Result, throws)
- Performance profiling with Instruments

## Do not use this skill when

- Non-Apple platform development
- Backend-only work (use appropriate backend skill)
- Android/Kotlin work

## Instructions

- Provide concise, production-ready Swift code
- Follow Swift 6 concurrency rules
- Prefer @Observable over @StateObject for SwiftUI 5+
- Use actors for shared mutable state
- Include error handling in all async code
- Write testable code with dependency injection

---

# Swift 6 Concurrency

## async/await

```swift
func fetchUser(id: String) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

Task {
    do {
        let user = try await fetchUser(id: "123")
        print(user)
    } catch {
        print("Failed: \(error)")
    }
}
```

## Actors

```swift
actor UserCache {
    private var cache: [String: User] = [:]
    
    func user(for id: String) -> User? {
        cache[id]
    }
    
    func setUser(_ user: User, for id: String) {
        cache[id] = user
    }
}

let cache = UserCache()
Task {
    await cache.setUser(User(id: "1", name: "Alice"), for: "1")
}
```

## Sendable

```swift
struct User: Sendable {
    let id: String
    let name: String
}

@MainActor
class ViewModel: @unchecked Sendable {
    var name: String = ""
}
```

## Task cancellation

```swift
Task {
    for try await line in URLSession.shared.bytes(from: url) {
        // Check cancellation periodically
        try Task.checkCancellation()
    }
}
```

## Structured concurrency

```swift
async let user = fetchUser(id: "1")
async let posts = fetchPosts(userId: "1")
let (u, p) = try await (user, posts)
```

---

# SwiftUI Views

## @Observable (Swift 5.9+, iOS 17+)

```swift
@Observable
class UserProfile {
    var name: String = ""
    var email: String = ""
}

struct ProfileView: View {
    let profile: UserProfile
    
    var body: some View {
        Text(profile.name)
        TextField("Name", text: $profile.name)
    }
}
```

## @State, @Binding

```swift
struct CounterView: View {
    @State private var count = 0
    
    var body: some View {
        VStack {
            Text("\(count)")
            Button("Increment") { count += 1 }
            ChildView(count: $count)
        }
    }
}

struct ChildView: View {
    @Binding var count: Int
}
```

## @ObservedObject, @StateObject

```swift
class CounterModel: ObservableObject {
    @Published var count = 0
}

struct ObservedView: View {
    @ObservedObject var model: CounterModel
}

struct StateObjectView: View {
    @StateObject var model = CounterModel()
}
```

## View modifiers

```swift
Text("Hello")
    .font(.headline)
    .foregroundColor(.primary)
    .padding()
    .background(Color.secondary)
    .cornerRadius(8)
```

## Navigation

```swift
NavigationStack {
    List(items) { item in
        NavigationLink(value: item) {
            Text(item.name)
        }
    }
    .navigationDestination(for: Item.self) { item in
        DetailView(item: item)
    }
}
```

---

# UIKit Interop

## UIViewControllerRepresentable

```swift
struct MyViewControllerRepresentable: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> MyViewController {
        MyViewController()
    }
    
    func updateUIViewController(_ controller: MyViewController, context: Context) {
        controller.update(with: context.coordinator.data)
    }
}
```

## UIViewRepresentable

```swift
struct MyUIViewRepresentable: UIViewRepresentable {
    func makeUIView(context: Context) -> UIView {
        let view = UIView()
        view.backgroundColor = .systemBlue
        return view
    }
    
    func updateUIView(_ view: UIView, context: Context) {}
}
```

## Hosting SwiftUI in UIKit

```swift
let swiftUIView = MySwiftUIView()
let hostingController = UIHostingController(rootView: swiftUIView)
present(hostingController, animated: true)
```

---

# Combine

## Publishers

```swift
let subject = PassthroughSubject<String, Never>()

subject
    .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
    .removeDuplicates()
    .sink { value in
        print(value)
    }
```

## URLSession publisher

```swift
extension URLSession {
    func dataTaskPublisher(for url: URL) -> AnyPublisher<Data, URLError>
}

URLSession.shared.dataTaskPublisher(for: url)
    .map(\.data)
    .decode(type: User.self, decoder: JSONDecoder())
    .receive(on: DispatchQueue.main)
    .sink(receiveCompletion: { _ in }, receiveValue: { print($0) })
```

---

# Error Handling

## Result type

```swift
func fetchUser(id: String) -> Result<User, Error> {
    .success(User(id: "1", name: "Alice"))
}

let result = fetchUser(id: "1")
switch result {
case .success(let user): print(user)
case .failure(let error): print(error)
}
```

## Throws

```swift
func validate(_ input: String) throws {
    guard !input.isEmpty else {
        throw ValidationError.empty
    }
}

do {
    try validate("")
} catch let error as ValidationError {
    print(error)
} catch {
    print("Unknown error")
}
```

## Typed throws (Swift 6)

```swift
enum NetworkError: Error {
    case invalidURL
    case requestFailed(underlying: Error)
}

func fetch() throws(NetworkError) -> Data {
    throw .invalidURL
}
```

---

# XCTest

## Unit tests

```swift
import XCTest

final class UserTests: XCTestCase {
    func testFetchUser() async throws {
        let user = try await fetchUser(id: "1")
        XCTAssertEqual(user.id, "1")
    }
    
    func testPerformance() {
        measure {
            // code to measure
        }
    }
}
```

## Async testing with expectation

```swift
func testAsyncFetch() {
    let expectation = expectation(description: "fetch completes")
    
    Task {
        _ = try? await fetchUser(id: "1")
        expectation.fulfill()
    }
    
    wait(for: [expectation], timeout: 5)
}
```

## UI tests

```swift
import XCTest

final class LoginUITests: XCTestCase {
    func testLogin() {
        let app = XCUIApplication()
        app.launch()
        
        app.textFields["username"].tap()
        app.typeText("alice")
        
        app.secureTextFields["password"].tap()
        app.typeText("secret")
        
        app.buttons["login"].tap()
        
        XCTAssertTrue(app.staticTexts["welcome"].waitForExistence(timeout: 3))
    }
}
```

---

# Swift Package Manager

## Package.swift

```swift
import PackageDescription

let package = Package(
    name: "MyLibrary",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [
        .library(name: "MyLibrary", targets: ["MyLibrary"])
    ],
    dependencies: [
        .package(url: "https://github.com/apple/swift-collections", from: "1.0.0")
    ],
    targets: [
        .target(name: "MyLibrary", dependencies: [
            .product(name: "Collections", package: "swift-collections")
        ])
    ]
)
```

## Xcode integration

- Add via File > Add Package Dependencies
- Or: .package(url:) in Package.swift
- Resolve with swift package resolve
- Build with swift build

---

# Performance (Instruments)

## Time Profiler

- Select Time Profiler template
- Record app usage
- Analyze stack traces
- Identify hot functions

## Allocations

- Track memory allocations
- Check for retain cycles
- Use Generations to detect leaks

## Leaks

- Detect autorelease pool issues
- Find circular references
- Verify dealloc calls

## Core Animation

- FPS monitoring
- Offscreen rendering
- Layer compositing

## SwiftUI optimization

```swift
LazyVStack {  // vs VStack for large lists
    ForEach(items) { item in
        ItemRow(item: item)
            .equatable() // prevent re-renders
    }
}
```

---

# Best Practices

- Swift 6: Enable strict concurrency
- Prefer struct over class unless reference semantics needed
- Use protocols for dependency injection
- @Observable for view models (iOS 17+)
- Actor for shared mutable state
- Never @MainActor on stored properties
- Test async code with XCTest expectations
- Profile before optimizing
- Use lazy stacks for large lists
- Equatable for SwiftUI view identity
