# 14 - UI / Frontend Design Overview

## 1. Purpose

This document defines the final frontend UI structure, responsive behavior, and implementation direction for the **CoTrip** collaborative travel planning app.

It is intended to guide Claude Code when implementing the React frontend.

This document reflects the finalized Pencil UI design direction for:

- Desktop pages
- Mobile reference screens
- Workspace navigation
- Design system behavior
- Traditional Chinese interface copy policy
- The simplified MVP scope without reminder or notification UI

The attached Pencil design file should be treated as the **primary visual reference**, while this document defines the **implementation rules and screen responsibilities**.

---

# 2. Product Name and Language Policy

## 2.1 Final Product Name

The official app name is:

```text
CoTrip
```

The name should remain in English across the UI.

Examples:

- Header wordmark: `CoTrip`
- Landing page branding: `CoTrip`
- Mock invite URL if displayed: `cotrip.app/join/...`

---

## 2.2 Interface Language

The frontend UI language should primarily use:

```text
Traditional Chinese
```

This applies to:

- Page titles
- Buttons
- Navigation labels
- Form labels
- Empty states
- Status messages
- Explanatory text
- Modal copy
- Invite-related copy
- Settings copy

The product name `CoTrip` remains in English.

---

### 2.3 Traditional Chinese Copy Direction

Exact wording may be refined during implementation, but the app should default to:

- Natural Traditional Chinese product copy
- Concise, warm, and polished microcopy
- Avoid direct word-for-word machine translation
- Preserve the calm, editorial product tone established in the Pencil design

---

### 2.4 Example UI Copy Mapping

| English design placeholder | Preferred Traditional Chinese implementation direction |
|---|---|
| My Trip Dashboard | 我的旅程 |
| Create Trip | 建立旅程 |
| Candidate Places | 想去的地點 |
| Group Voting | 群組投票 |
| Your Itinerary | 行程表 |
| Invite Friends | 邀請朋友 |
| Join this trip | 加入這趟旅程 |
| Settings | 設定 |
| Add Place | 新增地點 |
| Generate Itinerary | 產生行程表 |
| Save changes | 儲存變更 |
| Discard | 放棄變更 |

---

# 3. UI Source of Truth

## 3.1 Visual Source of Truth

Use the finalized Pencil UI design as the visual reference for:

- Layout proportions
- Card structure
- Page spacing
- Typography hierarchy
- CTA styling
- Workspace shell
- Mobile adaptation
- Navigation behavior
- Final CoTrip wordmark placement
- Final removal of reminder-related UI from the Settings flow

Claude Code should not invent an unrelated UI style.

---

## 3.2 Documentation Source of Truth

Use this document together with:

- `01-system-architecture-overview.md`
- `02-api-specification-overview.md`
- `03-api-trip-and-member.md`
- `04-api-invite.md`
- `05-api-candidate-and-vote.md`
- `06-api-itinerary.md`

This document governs **frontend layout and UI behavior**, while the API documents govern **data integration**.

---

# 4. Final Design Direction

## 4.1 Core Visual Identity

CoTrip should feel like:

> A warm, editorial, collaborative travel planning workspace.

The UI should be:

- calm
- friendly
- organized
- lightly premium
- collaborative
- travel-inspired, but not a travel marketplace

It should **not** look like:

- a hotel booking platform
- a social media travel feed
- a dense enterprise admin dashboard
- a playful cartoon-style mobile app

---

## 4.2 Visual Characteristics

The finalized Pencil design establishes:

- warm parchment-like page backgrounds
- near-white cards and panels
- soft borders
- subtle elevation
- dark pill-shaped primary CTA buttons
- outlined secondary pill buttons
- muted status badges
- serif-style major headings
- clean sans-serif UI/body copy
- generous whitespace
- structured information hierarchy

---

# 5. Design System Summary

## 5.1 Surfaces

| Surface | Usage |
|---|---|
| Warm page background | Main app background |
| Near-white cards | Forms, trip cards, ranking rows, itinerary blocks |
| Slightly softer inner surfaces | Secondary panels, nested blocks, small content containers |

---

## 5.2 Buttons

### Primary CTA

Use for the most important action on a screen.

Examples:

- 建立旅程
- 加入這趟旅程
- 產生行程表
- 儲存變更

Visual direction:

- dark filled pill
- high contrast
- visually dominant, but not oversized

---

### Secondary CTA

Use for secondary but still meaningful actions.

Examples:

- 稍後再說
- 返回
- 查看運作方式
- 重新產生
- 取消

Visual direction:

- outlined pill
- lower emphasis than primary CTA

---

### Tertiary / Ghost Actions

Use for subtle actions such as:

- edit icon
- delete icon
- copy link
- see all
- navigation helper actions
- minor inline adjustments

---

## 5.3 Cards

Cards are a central UI primitive.

Use near-white cards for:

- trip cards
- invitation cards
- candidate place cards
- ranking rows
- itinerary day groups
- settings forms
- dashboard statistics
- invite panels

Cards should feel:

- lightweight
- calm
- editorial
- not heavily boxed or visually noisy

---

## 5.4 Badges

Use muted rounded badges for:

- 地點類型
  - 景點
  - 餐廳
- 規劃狀態
  - 規劃中
  - 投票中
  - 行程已完成
- 身分狀態
  - 擁有者
  - 成員
- Current interaction states where appropriate
  - 已投票
  - 尚未加入

Badges should remain visually restrained.

---

# 6. Final Desktop Page Inventory

The desktop frontend should include the following pages.

| Page | Suggested Route |
|---|---|
| Landing Page | `/` |
| My Trip Dashboard | `/trips` |
| Create Trip Page | `/trips/new` |
| Join Trip Invite | `/join/:inviteToken` |
| Trip Workspace: Overview | `/trips/:tripId` or `/trips/:tripId/overview` |
| Trip Workspace: Places | `/trips/:tripId/places` |
| Trip Workspace: Voting | `/trips/:tripId/voting` |
| Trip Workspace: Itinerary | `/trips/:tripId/itinerary` |
| Trip Workspace: Members | `/trips/:tripId/members` |
| Trip Workspace: Settings | `/trips/:tripId/settings` |

---

# 7. Desktop Page Specifications

---

## 7.1 Landing Page

### Purpose

Introduce CoTrip and communicate the product flow:

```text
建立旅程 → 一起提出想去的地點 → 投票 → 產生共享行程
```

### Main Sections

1. Top navigation
   - CoTrip wordmark
   - Sign-in action
   - Primary CTA

2. Hero section
   - Small introductory badge
   - Main headline
   - Supporting paragraph
   - Primary and secondary CTA buttons

3. Product preview card
   - Visual mockup of the trip workspace
   - Should communicate:
     - collaborative planning
     - candidate places
     - voting
     - group avatars

4. “How it works” section
   - Three cards:
     1. 建立旅遊群組
     2. 蒐集地點並一起投票
     3. 產生共享行程表

### Implementation Notes

- Keep the page centered and spacious.
- Do not replace the product preview with large travel photography.
- Hero copy should be rewritten in natural Traditional Chinese during implementation.
- The landing page should remain product-led, not tourism-marketplace-led.

---

## 7.2 My Trip Dashboard

### Purpose

Serve as the logged-in user’s home page for trip entry and quick status scanning.

### Main Sections

1. App header
   - CoTrip wordmark
   - User name or profile indicator
   - Avatar

2. Greeting block
   - Personalized welcome message
   - Lightweight trip summary

3. Primary action
   - 建立旅程

4. Upcoming trip card list / grid
   - Each trip card shows:
     - trip title
     - destination
     - date range
     - planning status
     - small member avatar cluster
     - member count / role
     - enter/open trip action

### Desktop Layout

- Desktop uses a horizontal multi-card arrangement.
- The layout should feel spacious and readable.
- Trip cards should feel like collaborative trip workspaces, not travel product listings.

---

## 7.3 Create Trip Page

### Purpose

Allow the user to create a new travel group.

### Main Content

Single focused form card with:

- 旅程名稱
- 目的地
- 開始日期
- 結束日期
- 描述

### Actions

- Primary: 建立旅程
- Secondary: 取消 / 返回旅程列表

### Visual Pattern

Use a centered, focused form layout similar in calmness to the Join Invite page.

---

## 7.4 Join Trip Invite Page

### Purpose

Allow a user to preview an invitation and join a trip.

### Main Content

Centered invitation card containing:

- 邀請標籤
- 旅程名稱
- 目的地
- 旅遊日期
- 群組人數
- 邀請者資訊

### Actions

- Primary: 加入這趟旅程
- Secondary: 稍後再說

### Supporting Text

Explain that joining allows the user to:

- 新增想去的地點
- 參與投票
- 一起調整行程表

### Implementation Notes

- This page should remain focused and ceremonial.
- It should work well for users arriving from a shared invite link.
- Copy should be concise and warm.

---

# 8. Desktop Trip Workspace

The trip workspace is the central product experience.

## 8.1 Shared Desktop Workspace Shell

All desktop workspace pages use:

1. Left sidebar navigation
2. Top trip header
3. Main content area

---

## 8.2 Top Trip Header

Should display:

- Trip title
- Destination
- Date range
- Member avatar cluster
- 邀請朋友 action

This structure should remain consistent across:

- Overview
- Places
- Voting
- Itinerary
- Members
- Settings

---

## 8.3 Left Sidebar Navigation

Desktop workspace sidebar contains:

- 總覽
- 想去的地點
- 群組投票
- 行程表
- 成員
- 設定

The active page must be clearly indicated through:

- subtle rounded active background
- stronger text/icon color
- consistent visual treatment across all workspace screens

---

# 9. Desktop Workspace Page Specifications

---

## 9.1 Trip Workspace: Overview

### Purpose

Summarize the current trip planning state.

### Main Content

1. Summary metric cards
   - 提案地點數
   - 總投票數
   - 參與成員數
   - 已規劃天數

2. Top voted places preview
   - Ranked short list
   - Category badges
   - Vote counts

3. Quick actions
   - 新增地點
   - 前往投票
   - 產生行程表

### Implementation Notes

This page should remain a calm planning dashboard, not an analytics dashboard.

---

## 9.2 Trip Workspace: Places

### Purpose

Show candidate attractions and restaurants proposed by members.

### Main Content

1. Header block
   - 想去的地點
   - Number of proposed places
   - Number of contributing members

2. Filter chips
   - 全部
   - 景點
   - 餐廳

3. Primary action
   - 新增地點

4. Candidate place cards
   - Category badge
   - Place title
   - Short description / note
   - Proposed-by metadata
   - Vote count
   - Vote / voted state
   - Edit / delete secondary controls where applicable

### Implementation Notes

- Keep single-column proposal card layout on desktop.
- Cards should feel collaborative and editorial, not like marketplace listing tiles.

---

## 9.3 Trip Workspace: Voting

### Purpose

Act as the group decision-making center.

### Main Content

1. Page title
   - 群組投票

2. Summary line
   - Number of places
   - Sorted by votes

3. Filter chips
   - 全部
   - 景點
   - 餐廳

4. Ranked list
   - Rank number
   - Place title
   - Category badge
   - Proposed-by metadata
   - Vote count
   - Vote / voted button

### Implementation Notes

- Top-ranked items may receive very subtle visual emphasis.
- Avoid making it look overly gamified.
- The page should visually feel like the decision-making bridge between Places and Itinerary.

---

## 9.4 Trip Workspace: Itinerary

### Purpose

Display the generated shared itinerary and act as the “payoff” screen of the product.

### Main Content

1. Page title
   - 行程表

2. Summary
   - 旅遊天數
   - 已排入地點數
   - 由群組投票結果產生

3. Actions
   - 重新產生
   - 分享行程表

4. Day sections
   - Day label
   - Date
   - Optional city or trip segment
   - Number of places

5. Itinerary item rows
   - 時段
     - 上午
     - 午餐
     - 下午
     - 晚餐
   - Place title
   - Supporting note
   - Category badge
   - Edit / delete secondary actions

### Implementation Notes

- Use full-width day sections on desktop.
- This page should feel structured and rewarding, not fragmented.
- The visual hierarchy should clearly show that this is the product outcome after place collection and voting.

---

## 9.5 Trip Workspace: Members

### Purpose

Show trip members and manage invitations.

### Main Content

#### A. Member list

Each member row shows:

- avatar
- display name
- email or supporting metadata if used
- role badge:
  - 擁有者
  - 成員

#### B. Invite friends panel

Should include:

- 邀請朋友 title
- explanation text
- CTA to create invite link
- generated invite link preview if available
- copy-link action
- expiration note if applicable

### Implementation Notes

- Keep the page clean and collaborative.
- Do not overbuild advanced role management in the MVP.
- The invite panel should align with the system’s invite-link functionality.

---

## 9.6 Trip Workspace: Settings

### Purpose

Allow editing core trip metadata.

### Main Content

Single primary settings form card containing:

- 旅程名稱
- 目的地
- 開始日期
- 結束日期
- 描述

### Actions

- Secondary: 放棄變更
- Primary: 儲存變更

### Implementation Notes

- This page should match the final Pencil design after removal of the previous reminder panel.
- The settings form should be visually balanced as the only primary content block.
- The MVP does **not** include reminder or notification settings.
- Do not create a substitute side card or filler content to replace the removed reminder panel.

---

# 10. Final Mobile Design Direction

The mobile design should be treated as a **purposeful mobile adaptation**, not a compressed desktop layout.

The finalized mobile references include:

1. Mobile — Landing Page
2. Mobile — My Trip Dashboard
3. Mobile — Join Trip Invite
4. Mobile — Trip Workspace: Places
5. Mobile — Trip Workspace: Itinerary
6. Mobile — Trip Workspace: More Menu

---

# 11. Mobile Navigation Pattern

## 11.1 Bottom Navigation

Mobile trip workspace uses bottom navigation:

```text
總覽 | 地點 | 投票 | 行程 | 更多
```

Recommended conceptual mapping:

| UI Label | Destination |
|---|---|
| 總覽 | Overview |
| 地點 | Places |
| 投票 | Voting |
| 行程 | Itinerary |
| 更多 | More menu |

---

## 11.2 More Menu

The `更多` item opens a bottom sheet or compact overlay.

Menu items include:

- 成員
- 設定
- 邀請朋友, if included according to final implementation structure

This menu should preserve the calm visual system and feel touch-friendly.

The MVP does **not** include any reminder or notification entry in this menu.

---

# 12. Mobile Screen Specifications

---

## 12.1 Mobile Landing Page

### Main Differences from Desktop

- Vertical hero flow
- CTA buttons may stack vertically
- Product preview becomes a compact mobile-friendly preview card
- “How it works” cards stack vertically

---

## 12.2 Mobile My Trip Dashboard

### Main Differences from Desktop

- Trip cards appear in a single-column vertical list
- Create Trip CTA remains prominent
- Greeting summary remains compact
- Header uses compact mobile branding and avatar layout

---

## 12.3 Mobile Join Trip Invite

### Main Differences from Desktop

- Single centered card remains the focus
- Layout becomes narrower and vertically compact
- Actions remain large enough for touch interaction

---

## 12.4 Mobile Trip Workspace: Places

### Main Differences from Desktop

- Compact trip header
- Filter chips fit the narrow layout; horizontal scrolling is acceptable if needed
- Candidate place cards stack vertically
- Vote / voted state remains readable
- Bottom navigation visible

---

## 12.5 Mobile Trip Workspace: Itinerary

### Main Differences from Desktop

- Day sections remain vertical
- Itinerary items stack naturally for reading
- Avoid desktop-style wide table behavior
- Bottom navigation visible

---

# 13. Responsive Guidance for Screens Without Dedicated Mobile Frames

The following desktop pages do not currently require dedicated Pencil mobile frames, but should be adapted following the established mobile patterns:

- Create Trip Page
- Trip Workspace: Overview
- Trip Workspace: Voting
- Trip Workspace: Members
- Trip Workspace: Settings

---

## 13.1 Expected Adaptation Strategy

| Desktop Screen | Mobile Strategy |
|---|---|
| Create Trip | Single-column centered form |
| Overview | Metric cards stack; quick actions become vertical cards |
| Voting | Ranking rows become vertical mobile list cards |
| Members | Member list and invite panel stack vertically |
| Settings | Settings form becomes a single-column mobile form |

---

# 14. Suggested Frontend Component Structure

```text
src/
├── pages/
│   ├── LandingPage.tsx
│   ├── TripsDashboardPage.tsx
│   ├── CreateTripPage.tsx
│   ├── JoinInvitePage.tsx
│   └── workspace/
│       ├── TripOverviewPage.tsx
│       ├── TripPlacesPage.tsx
│       ├── TripVotingPage.tsx
│       ├── TripItineraryPage.tsx
│       ├── TripMembersPage.tsx
│       └── TripSettingsPage.tsx
│
├── components/
│   ├── layout/
│   │   ├── PublicHeader.tsx
│   │   ├── AppHeader.tsx
│   │   ├── WorkspaceSidebar.tsx
│   │   ├── MobileWorkspaceHeader.tsx
│   │   ├── MobileBottomNav.tsx
│   │   └── MobileMoreSheet.tsx
│   │
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Badge.tsx
│   │   ├── Card.tsx
│   │   ├── AvatarGroup.tsx
│   │   └── EmptyState.tsx
│   │
│   ├── trip/
│   │   ├── TripCard.tsx
│   │   ├── TripSummaryCards.tsx
│   │   └── TripHeader.tsx
│   │
│   ├── places/
│   │   ├── CandidatePlaceCard.tsx
│   │   └── PlaceFilterChips.tsx
│   │
│   ├── voting/
│   │   └── RankingRow.tsx
│   │
│   ├── itinerary/
│   │   ├── ItineraryDaySection.tsx
│   │   └── ItineraryItemRow.tsx
│   │
│   ├── members/
│   │   ├── MemberList.tsx
│   │   └── InvitePanel.tsx
│   │
│   └── settings/
│       └── TripSettingsForm.tsx
│
├── api/
│   ├── httpClient.ts
│   ├── tripApi.ts
│   ├── inviteApi.ts
│   ├── candidateApi.ts
│   ├── voteApi.ts
│   └── itineraryApi.ts
│
├── auth/
│   ├── authClient.ts
│   └── useAuth.ts
│
├── types/
│   ├── trip.ts
│   ├── candidate.ts
│   ├── itinerary.ts
│   └── member.ts
│
└── router/
    └── index.tsx
```

---

# 15. Frontend Implementation Principles

Claude Code should follow these principles during implementation:

1. Use the Pencil designs as the visual reference.
2. Use this document as the UI behavior and screen responsibility reference.
3. Keep all user-facing copy primarily in Traditional Chinese.
4. Keep the product name `CoTrip` in English.
5. Do not invent new major pages outside the documented MVP.
6. Do not redesign the workspace navigation model.
7. Preserve:
   - desktop sidebar navigation
   - mobile bottom navigation
   - mobile More menu behavior
8. Build reusable components for:
   - cards
   - buttons
   - badges
   - avatar groups
   - trip summaries
9. Keep responsive behavior intentional rather than relying only on automatic shrinking.
10. Match the finalized warm editorial product tone as closely as practical.
11. Do not reintroduce reminder or notification UI.
12. Settings-related UI should only cover core trip metadata in the MVP.

---

# 16. MVP Frontend Completion Criteria

The frontend MVP implementation is considered complete when:

1. Public landing page matches the approved CoTrip direction.
2. Authentication entry points are visually supported.
3. User can view trip dashboard.
4. User can create a trip.
5. User can open an invite page.
6. User can join a trip.
7. User can access a trip workspace.
8. Workspace overview is implemented.
9. Places page is implemented.
10. Voting page is implemented.
11. Itinerary page is implemented.
12. Members page is implemented.
13. Settings page is implemented.
14. Desktop workspace uses the correct left sidebar structure.
15. Mobile workspace uses the correct bottom navigation structure.
16. Mobile More menu provides access to Members and Settings.
17. Interface language is primarily Traditional Chinese.
18. The visual system remains consistent with the Pencil design reference.
19. No reminder or notification UI is implemented in the MVP.