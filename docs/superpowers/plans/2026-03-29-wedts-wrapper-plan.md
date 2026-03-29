# WEDTS Wrapper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a new npm package named `wedts` that wraps the existing Rust/WASM crypto output and provides stronger TypeScript support, including generic JSON decryption types.

**Architecture:** Keep the Rust `crypto-wasm` crate as the source of cryptographic behavior, but stop exposing its raw package as the public npm surface. Instead, add a JavaScript/TypeScript wrapper package under `packages/wedts` that vendors the generated wasm-pack output and exports typed helpers for runtime and TS consumers.

**Tech Stack:** Rust, wasm-pack, Node.js, npm, ES modules, TypeScript declaration files

---

### Task 1: Add failing tests for the new wrapper package

**Files:**
- Create: `packages/wedts/package.json`
- Create: `packages/wedts/tests/runtime.mjs`
- Create: `packages/wedts/tests/types.ts`
- Create: `packages/wedts/tsconfig.json`

- [ ] **Step 1: Write failing runtime and type tests**

Add tests that expect:
- `wedts` exports `encryptText` and `decryptText`
- `wedts` exports `encryptJson` and `decryptJson<T>`
- `decryptJson<{message: string}>` is type-usable

- [ ] **Step 2: Run tests to verify they fail**

Run:
- `npm test --prefix packages/wedts`
- `npx tsc -p packages/wedts/tsconfig.json --noEmit`

Expected: FAIL because the wrapper package implementation does not exist yet

- [ ] **Step 3: Write minimal package scaffolding**

Create the package and test harness, but do not implement the runtime exports until after the failing run is observed.

- [ ] **Step 4: Run tests to confirm the intended red state**

Run the same commands and confirm the failure is because exports are missing, not because the tests are malformed.

- [ ] **Step 5: Commit**

```bash
git add packages/wedts
git commit -m "test: add wedts wrapper test harness"
```

### Task 2: Implement the wedts wrapper package

**Files:**
- Create: `packages/wedts/index.js`
- Create: `packages/wedts/index.d.ts`
- Create: `packages/wedts/scripts/build-wasm.mjs`
- Modify: `packages/wedts/package.json`

- [ ] **Step 1: Write the wrapper implementation**

Implement:
- runtime re-exports for `encryptText` and `decryptText`
- a JSON wrapper layer for `encryptJson` and `decryptJson<T>`
- a build step that runs `wasm-pack` and copies generated output into the package

- [ ] **Step 2: Run runtime tests**

Run: `npm test --prefix packages/wedts`
Expected: PASS

- [ ] **Step 3: Run type tests**

Run: `npx tsc -p packages/wedts/tsconfig.json --noEmit`
Expected: PASS

- [ ] **Step 4: Refine package metadata**

Set npm package name to `wedts`, and add description, repository, and publish metadata needed for release.

- [ ] **Step 5: Commit**

```bash
git add packages/wedts crates/crypto-wasm/Cargo.toml
git commit -m "feat: add typed wedts npm wrapper"
```

### Task 3: Update example consumption

**Files:**
- Modify: `examples/react/package.json`
- Modify: `examples/react/test.mjs`
- Modify: `examples/react/README.md`
- Modify: `README.md`

- [ ] **Step 1: Change the React example to consume `wedts`**

Point the local example to the new wrapper package instead of the published `@ohxxx/wed` package.

- [ ] **Step 2: Run the example test to verify the integration fails first if needed**

Run: `npm test --prefix examples/react`
Expected: FAIL until the dependency and import path match the new wrapper package correctly

- [ ] **Step 3: Finish the example wiring**

Use either a local file dependency or npm workspace-style linkage so the example resolves the local `wedts` package.

- [ ] **Step 4: Run the example test to verify it passes**

Run: `npm test --prefix examples/react`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add examples/react README.md
git commit -m "docs: switch react example to wedts"
```

### Task 4: Run full verification

**Files:**
- Modify: `.gitignore` if build artifacts need ignore coverage

- [ ] **Step 1: Run full wrapper verification**

Run:
- `npm test --prefix packages/wedts`
- `npx tsc -p packages/wedts/tsconfig.json --noEmit`
- `npm test --prefix examples/react`
- `cargo test -p crypto-wasm`

- [ ] **Step 2: Fix any integration gaps**

Add only the minimal changes required to get all verification commands green.

- [ ] **Step 3: Re-run full verification**

Run the same commands again and confirm all pass.

- [ ] **Step 4: Commit**

```bash
git add .gitignore packages/wedts examples/react README.md
git commit -m "test: verify wedts wrapper integration"
```
