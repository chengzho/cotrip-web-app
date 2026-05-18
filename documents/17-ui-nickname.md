# 17 - UI Specification: Nickname / Display Name Editing

## 1. Purpose

This document defines the frontend UX design for the **CoTrip nickname / display name editing feature**.

It covers:

- Where users access the nickname editing flow
- Recommended UI pattern
- Traditional Chinese copy
- Integration with the `GET /me` and `PATCH /me` API endpoints
- Future testing implications

This document does not cover avatar upload, first-login onboarding, or any profile feature beyond display name editing.

---

# 2. Feature Goal

After a user logs in, their CoTrip display name should be visible and editable.

The display name appears in:

- Authenticated header (already rendered as a user initial chip)
- Candidate proposer labels ("由 小周 提案")
- Trip member list
- Invite preview inviter label

The nickname editing flow gives users a simple, low-friction way to set or change the name that their collaborators see.

---

# 3. Recommended Entry Point

## 3.1 Current Header State

The workspace top bar (`TripWorkspaceTopBar.tsx`) currently renders:

```text
[initial chip]  登出
```

The initial chip shows a one-character abbreviation of the current display name.

## 3.2 Proposed Change

Replace the plain "登出" text-button area with a small user menu.

Clicking the user chip or a chevron next to it opens a dropdown menu with two actions:

```text
設定顯示名稱
登出
```

This pattern is:

- Minimal — no new page, no separate settings route
- Consistent with the existing compact header design
- Familiar to users accustomed to account menus

The menu should close on outside click or Escape key press.

---

# 4. Nickname Edit Modal

## 4.1 Trigger

Clicking "設定顯示名稱" from the header menu opens a compact modal.

## 4.2 Recommended UI Pattern

**Use a modal**, not a new page or side panel.

Rationale:

- The CoTrip workspace UI is dense with navigation panels; a modal avoids competing with existing layout.
- The edit operation is a single field with a single action — it does not warrant a dedicated page.
- A modal is consistent with the overall MVP scope of keeping settings lightweight.

## 4.3 Modal Layout

```text
┌─────────────────────────────────┐
│  設定顯示名稱               ✕   │
│                                 │
│  這個名稱會顯示在旅程成員、      │
│  提案與邀請資訊中。              │
│                                 │
│  顯示名稱                       │
│  ┌───────────────────────────┐  │
│  │ 小周                      │  │
│  └───────────────────────────┘  │
│                                 │
│              [取消]  [儲存]      │
└─────────────────────────────────┘
```

## 4.4 Pre-fill Behavior

When the modal opens, the input field should be pre-filled with the user's current `display_name` value retrieved from `GET /me` or from the existing auth context if already loaded.

---

# 5. Traditional Chinese Copy

| Element | Copy |
|---|---|
| Header menu item | 設定顯示名稱 |
| Modal title | 設定顯示名稱 |
| Modal description | 這個名稱會顯示在旅程成員、提案與邀請資訊中。 |
| Field label | 顯示名稱 |
| Confirm button | 儲存 |
| Cancel button | 取消 |
| Validation error — empty | 顯示名稱不能為空白 |
| Validation error — too long | 顯示名稱不能超過 50 個字元 |
| Success — toast or inline confirmation | 顯示名稱已更新 |

---

# 6. API Integration

## 6.1 On Modal Open

If the current display name is not yet loaded in the auth context, call `GET /me` to pre-fill the field.

If the display name is already available from the auth context (e.g., stored after login), use that value directly without an additional network call.

## 6.2 On Submit

1. Trim the input value client-side.
2. If empty after trim, show inline validation error: `顯示名稱不能為空白`.
3. If longer than 50 characters after trim, show inline validation error: `顯示名稱不能超過 50 個字元`.
4. Call `PATCH /me` with `{ "display_name": trimmedValue }`.
5. On success (HTTP 200):
   - Update the auth context with the new display name.
   - Refresh the header initial chip display.
   - Close the modal.
   - Show a brief confirmation — either a toast notification or an inline "顯示名稱已更新" message that auto-dismisses.
6. On API error:
   - Show a brief error message inside the modal.
   - Do not close the modal.
   - Allow the user to retry.

---

# 7. Surfaces That Automatically Reflect the Change

After a successful `PATCH /me` call, the following surfaces will show the new display name without requiring a full page reload:

| Surface | Update mechanism |
|---|---|
| Header user chip initial | Re-derived from new display name in auth context |
| Candidate proposer label | Reflected on next `GET /trips/{tripId}/candidates` fetch |
| Member list | Reflected on next `GET /trips/{tripId}/members` fetch |
| Invite preview | Reflected on next `GET /invites/{token}` fetch |

The candidate and member list surfaces refresh naturally when the user navigates between pages, so no explicit invalidation is required in the MVP.

---

# 8. Header Scope

The user menu entry point should appear in:

- Desktop workspace top bar (`TripWorkspaceTopBar.tsx`)

It should also appear in the mobile header if one exists (`MobileWorkspaceHeader.tsx`).

The entry page / dashboard header should similarly offer a user menu if a user chip or name is rendered there in the future.

Do not implement the nickname editing flow on the entry/dashboard page in the MVP unless explicitly requested. The workspace context is the primary target.

---

# 9. Files Expected to Be Modified

When this feature is implemented:

| File | Expected change |
|---|---|
| `webui/src/components/layout/TripWorkspaceTopBar.tsx` | Add user dropdown menu with "設定顯示名稱" and "登出" |
| `webui/src/context/AuthContext.tsx` | Store and expose current display name; refresh after PATCH /me |
| `webui/src/api/index.ts` or similar | Add `getMe()` and `updateDisplayName()` API client functions |
| New modal component | e.g., `webui/src/components/user/NicknameModal.tsx` |

---

# 10. Future Testing Implications

When this feature is implemented, verify:

| Scenario | Expected result |
|---|---|
| Open modal | Input pre-filled with current display name |
| Submit empty input | Inline validation error shown, request not sent |
| Submit valid name | Modal closes, header reflects new name |
| Submit name exceeding 50 chars | Inline validation error shown |
| API returns 400 | Error message shown inside modal, modal stays open |
| Cancel | Modal closes, no change persisted |

---

# 11. MVP Scope Boundaries

This document covers the minimum viable nickname editing UX.

Out of scope:

| Feature | Status |
|---|---|
| Avatar upload | Deferred |
| First-login mandatory nickname onboarding | Deferred |
| Separate `/profile` or `/settings` page | Deferred |
| Profile visibility settings | Not applicable in MVP |
