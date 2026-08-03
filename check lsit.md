# Anatomy Explorer — Full Project Guide

A complete, self-contained brief. Paste this into any AI tool or read it yourself to continue the project from any point.

---

## 1. Project Concept

A web (later mobile) app where anyone — students and curious learners alike — can explore an interactive 3D model of the human body to learn every bone and muscle: name, location, and quick facts.

- **Type:** Personal side project (not tied to coursework/FYP — full freedom to move fast and scrappy)
- **Audience:** Everyone — med/nursing/physio students, school/college biology students, and general public curiosity learners
- **Platform:** Web first (React), mobile app later
- **Core experience:** Interactive, clickable 3D body model (skeleton first, muscles next)

---

## 2. The Wedge — Why This, Not Just Another Anatomy Site

Established players (BioDigital Human, Visible Body, Complete Anatomy) are polished but paywalled, English-only, and generic. To stand out, lean into at least one of these as the headline:

- **Free/open access** — no subscription wall, unlike every major competitor
- **Bilingual labeling** (English + Nepali/Devanagari) — a genuinely underserved niche; none of the big players do this
- **Exam-mode** tied to real curricula (MBBS, BSc Nursing, physiotherapy syllabi) instead of generic reference content

Pick one (or more) early — it shapes what content and features matter most.

---

## 3. Competitive Landscape (Existing Free/Freemium Options)

The space is more crowded than it looks at first glance — worth studying these before building.

**Genuinely free, no paywall**
- **Zygote Body** (zygotebody.com) — free online 3D anatomy atlas; view/isolate structures, quiz mode (picking a part shows a multiple-choice quiz)
- **3D Bones and Muscles (Anatomy)** app — fully free; skeleton + 145+ muscles, virtual dissection (peel muscle layers), audio pronunciations, quizzes, Latin names, supports French/Spanish/German (no Nepali)
- **Humio** — free 3D atlas; all 206 bones + 600+ muscles with attachment points, aimed at students and physicians

**Free-with-premium-tiers**
- **Humanatomy** (web/iOS/Android) — all bones + skeletal muscles, detailed data (Latin name, function, origin, insertion, antagonists, nerve, artery), built-in quiz mode
- **Visible Body**, **Complete Anatomy**, **TeachMeAnatomy** — mostly free-to-try, paid for full access

**What this means for the wedge:** "free 3D skeleton with clickable parts and a quiz" already exists in multiple solid forms. The remaining genuine openings:
- **No competitor does Nepali/Devanagari labeling** — still untapped
- **None are tied to local exam curricula** (MBBS/nursing/physio syllabi in Nepal specifically)
- Most require a download or a heavier platform — a fast, no-signup, purely web-based tool could still win on convenience

**Action item:** spend an afternoon actually using Zygote Body and 3D Bones and Muscles before building, so Phase 1 isn't accidentally rebuilding something that already exists — make sure the Nepali/curriculum angle is baked into the MVP, not bolted on later.

---

## 4. Everything Required for This Project

### 3.1 Skills / Knowledge
| What | Status | Notes |
|---|---|---|
| React fundamentals | Already have | From Summit Route experience |
| Three.js / `react-three-fiber` | New — needs learning | Cameras, meshes, raycasting (click detection on 3D objects), lighting. Budget a few days. |
| Basic 3D file handling | New — needs learning | Loading `.glb`/`.gltf` files (standard web 3D format); inspecting mesh names in Blender so you know what to attach click events to |
| FastAPI + PostgreSQL | Already have | Reused from other projects |

### 3.2 Software / Tools (all free)
- **Node.js** + code editor — already set up
- **Blender** (free) — not for modeling from scratch, but to open downloaded 3D models, inspect/rename bone meshes, and re-export as optimized `.glb`
- **Git/GitHub** — already familiar

### 3.3 The 3D Model — the hardest requirement
This is the actual bottleneck of the whole project. You need a model that is:
- **Separated into individual named meshes per bone** — this is what makes "click a bone" possible (a single fused mesh won't work)
- **Reasonably low polygon count** so it loads fast in-browser (raw medical scan data is often too heavy)
- **Properly licensed** for your use — Creative Commons or similar is fine for a free personal project

**Sources to check:**
- Z-Anatomy (open-source Blender anatomy project)
- BodyParts3D (free, Creative Commons anatomy dataset)
- Sketchfab (filter by Creative Commons license)

### 3.4 Content / Data
- A master list of all bones: English name, Latin name, optional Nepali name, short description/fact
- Can be manually compiled from public-domain anatomy references (e.g. Gray's Anatomy) or simple med-student reference lists — tedious but not technically hard
- Later: muscle data (name, origin, insertion, function) — more complex than bone data

### 3.5 Backend & Hosting (mostly free tier)
- FastAPI + PostgreSQL for bone/muscle data, quiz questions, user progress
- Free hosting: Vercel or Netlify (frontend), Railway or Render free tier (backend + database)

### 3.6 Time Estimate
- Phase 1 demo (rotating skeleton + a handful of clickable bones): **1–2 weekends**, assuming the 3D asset search doesn't drag on

---

## 5. Tech Stack Summary

| Layer | Choice | Why |
|---|---|---|
| 3D rendering | `react-three-fiber` + `three.js` | React-native way to do 3D, no separate engine to learn |
| Frontend framework | React + Tailwind | Familiar stack |
| Backend | FastAPI | Familiar stack |
| Database | PostgreSQL | Familiar stack |
| Auth (later) | JWT | For save-progress/leaderboards |
| Optional AI layer | LLM + small RAG knowledge base | For an "ask about this bone" chat feature |

---

## 6. Build Order — Step by Step

### Phase 1 — Prove the Core Loop (1–2 weekends)
1. Source ONE free 3D skeleton model (see 4.3 above) — do not model bones from scratch
2. Open it in Blender first to confirm bones are separated into individual named meshes; re-export as `.glb` if needed
3. Set up a React project with `react-three-fiber` + `three.js`
4. Load the `.glb` model and get it rotating/zooming in-browser
5. Hardcode 10–15 major bones (skull, femur, humerus, spine, ribs, pelvis, etc.) with clickable hotspots using raycasting
6. Clicking a bone shows a popup: name, Latin name, 1–2 quick facts
7. **Goal:** a working "click a bone, see info" demo — this is your proof of concept

### Phase 2 — Fill It Out
1. Expand coverage to all ~206 bones
2. Move bone data out of hardcoded JS into JSON or a PostgreSQL table (fields: `name`, `latin_name`, `nepali_name`, `system`, `description`, `fun_fact`)
3. Add a search bar (typing "femur" flies the camera to it / highlights it)
4. Add bilingual names (English + Devanagari) if pursuing the Nepal-angle differentiator
5. Build a basic quiz mode: "Click the mandible" style prompts, timed or untimed, with score tracking

### Phase 3 — Polish & Differentiate
1. Add a muscular layer toggle (harder — muscle meshes are messier and often not cleanly separated in free models)
2. Add bookmarks/notes per bone for revision
3. Add progress tracking (which bones/systems the user has mastered)
4. Optional: LLM-powered "ask about this bone" chat panel, grounded in a small curated anatomy knowledge base (reuse RAG + hallucination-guard patterns if you've built similar systems before)

---

## 7. Feature Checklist (v1 "Definition of Done")
- [ ] 3D skeleton loads and is rotatable/zoomable
- [ ] All major bones clickable with an info popup
- [ ] Search-to-locate works
- [ ] Basic quiz mode functional
- [ ] Deployed and viewable online (Vercel/Netlify + Railway/Render)

---

## 8. Open Questions for Next Session
- Final project name?
- Which specific 3D model/dataset to commit to?
- Nepali localization: full commitment, or English-first with bilingual as a stretch goal?
- Monetization (if any), or purely free/portfolio?
