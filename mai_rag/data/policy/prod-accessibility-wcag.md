---
title: Accessibility Standard (WCAG 2.1 AA)
doc_id: prod-accessibility-wcag
owner: Design Leadership
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Accessibility Standard (WCAG 2.1 AA)

## 1. Purpose & Compliance Level

Northwind is committed to digital accessibility for all users, regardless of ability. All customer-facing products must meet **Web Content Accessibility Guidelines (WCAG) 2.1 Level AA** as the minimum standard.

**Legal Basis**: Supports compliance with ADA (Americans with Disabilities Act), Section 508 of the Rehabilitation Act, and EU Accessibility Directive (EAA).

**Non-Negotiable**: Accessibility is not a feature or nice-to-have; it's a core product requirement baked into every design and development cycle.

## 2. WCAG 2.1 AA Checklist

### 2.1 Perceivable: Users can perceive content

| Criterion | Requirement | How to Test |
|-----------|-------------|-----------|
| **1.1.1 Non-text Content** | All images have descriptive alt text (e.g., "Product dashboard showing revenue by region" not "screenshot.png") | Use axe DevTools; scan for missing alt tags |
| **1.3.1 Info & Relationships** | Content structure uses proper semantic HTML (`<h1>`, `<h2>`, `<label>`, `<button>`, not `<div>`) | Use WAVE browser extension; check heading hierarchy |
| **1.4.3 Contrast (Minimum)** | Text has ≥4.5:1 contrast ratio; large text (18pt+) has ≥3:1 | Use Color Contrast Analyzer tool; test on dark background |
| **1.4.5 Images of Text** | Avoid text in images; use styled text instead | Design review: Replace image-based text with CSS/fonts |

### 2.2 Operable: Users can navigate and interact with content

| Criterion | Requirement | How to Test |
|-----------|-------------|-----------|
| **2.1.1 Keyboard** | All functionality available via keyboard (no mouse-only interactions) | Tab through page; verify all buttons/links activatable via Enter/Space |
| **2.1.2 No Keyboard Trap** | Keyboard focus never trapped (user can always tab out) | Tab through page; confirm Tab always moves focus forward |
| **2.4.3 Focus Order** | Logical tab order matches visual flow (left-to-right, top-to-bottom) | Tab through form; check focus order makes sense |
| **2.4.7 Focus Visible** | Keyboard focus is always visible (e.g., highlight border around button) | Tab through page; verify visible focus indicator on each element |

### 2.3 Understandable: Users can comprehend content

| Criterion | Requirement | How to Test |
|-----------|-------------|-----------|
| **3.1.1 Language of Page** | Primary language declared in HTML (`<html lang="en">`) | Check page source; inspect `<html>` tag |
| **3.2.4 Consistent Navigation** | Navigation menus appear in same location and order on every page | Spot check 5 pages; verify header/footer consistent |
| **3.3.1 Error Identification** | Form errors clearly identified (text + color + icon, never color alone) | Fill invalid form; check error message identifies field and problem |
| **3.3.2 Labels or Instructions** | Form fields have visible labels or instructions (e.g., `<label for="email">Email Address</label>`) | Inspect form; verify every input has associated label |

### 2.4 Robust: Content works with assistive technologies

| Criterion | Requirement | How to Test |
|-----------|-------------|-----------|
| **4.1.2 Name, Role, Value** | Components have accessible name, role, and value (ARIA where needed) | Use axe DevTools; check that buttons have accessible name, inputs have labels |
| **4.1.3 Status Messages** | Live updates announced to screen readers (e.g., toast notifications using `aria-live="polite"`) | Use NVDA screen reader (Windows) or VoiceOver (Mac); confirm notifications read aloud |

## 3. Common Issues & Fixes

### 3.1 Missing Alt Text

**Issue**: Image has no `alt` attribute; screen reader users see "image.png"

**Fix**:
```jsx
// ❌ Bad
<img src="/dashboard.png" />

// ✅ Good
<img src="/dashboard.png" alt="Dashboard showing Q2 revenue trending upward 15%" />
```

**Alt Text Rules**:
- Describe the image's purpose, not just "image" or "screenshot"
- For purely decorative images, use `alt=""` (empty)
- For complex images (charts, diagrams), provide text alternative in page body or linked description

### 3.2 Missing Form Labels

**Issue**: Input field has no label; screen reader users don't know what field is for

**Fix**:
```jsx
// ❌ Bad
<input type="email" placeholder="Email address" />

// ✅ Good
<label htmlFor="email">Email address</label>
<input id="email" type="email" placeholder="name@example.com" />
```

### 3.3 Insufficient Color Contrast

**Issue**: Light gray text (#A0A0A0) on white background fails contrast requirement

**Fix**: Use `Design System Guidelines` color palette; all colors pre-verified for 4.5:1 contrast on dark backgrounds.

**Test with**: Contrast Ratio tool (https://webaim.org/resources/contrastchecker/) or axe DevTools.

### 3.4 No Keyboard Navigation

**Issue**: Modal dialog requires mouse click to close; no keyboard shortcut

**Fix**:
```jsx
// ❌ Bad
<Dialog>
  <button onClick={close}>Close</button> {/* Only mouse accessible */}
</Dialog>

// ✅ Good
<Dialog onEscape={close}>  {/* Escape key closes */}
  <button onClick={close}>Close</button>
</Dialog>
```

### 3.5 Missing Live Region Announcements

**Issue**: Toast notification appears on screen but screen reader users don't hear it

**Fix**:
```jsx
// ❌ Bad
<div>{notificationMessage}</div>

// ✅ Good
<div aria-live="polite" aria-atomic="true">
  {notificationMessage}
</div>
```

## 4. Testing Process

### 4.1 Automated Testing

Use tools to catch common issues:

| Tool | What It Finds | How to Use |
|------|---------------|-----------|
| **axe DevTools** (browser extension) | Missing alt text, color contrast, ARIA violations | Run scan on staging page; fix critical issues |
| **WAVE** (browser extension) | Missing labels, empty buttons, redundant form controls | Scan page; review warnings and errors |
| **Lighthouse** (Chrome DevTools) | Accessibility score, audit suggestions | Run audit in DevTools; review suggestions |
| **WebAIM Color Contrast Checker** | Foreground/background contrast ratio | Paste colors; verify ≥4.5:1 for body text |

**Workflow**:
1. Developer implements feature
2. Run axe DevTools on staging page
3. Fix all **Errors** (critical accessibility failures)
4. Review **Warnings** (likely issues, often false positives)

### 4.2 Manual Testing

Automated tools catch ~40% of issues; manual testing is essential:

| Test | How | Who |
|------|-----|-----|
| **Keyboard Navigation** | Tab through page; verify all buttons/links reachable and activatable | Developer or QA |
| **Screen Reader** | Use NVDA (Windows) or VoiceOver (Mac) to navigate; listen for clear labels and instructions | Accessibility specialist or designer |
| **Zoom to 200%** | Resize browser to 200% zoom; verify layout doesn't break and text is readable | Developer or QA |
| **Mobile Accessibility** | Test on mobile with screen reader enabled (TalkBack on Android, VoiceOver on iOS) | Designer or QA |

**Tools**:
- **NVDA** (free, open-source screen reader for Windows): https://www.nvaccess.org/
- **VoiceOver** (built-in macOS screen reader): `Cmd+F5` to enable
- **JAWS** (commercial, premium): Often used by enterprise customers (optional for internal testing)

### 4.3 Acceptance Criteria for Accessibility

Every feature must meet:

- ✅ **Zero critical axe errors** on staging page
- ✅ **4.5:1 contrast** on all text (verified with color contrast checker)
- ✅ **Keyboard navigable**: All interactive elements reachable and usable via Tab + Enter/Space
- ✅ **Screen reader tested**: 2+ interactive states tested with NVDA or VoiceOver; labels are clear
- ✅ **No zoom breakage**: Layout stable at 200% zoom; text remains readable
- ✅ **ARIA correct**: If using ARIA attributes, roles/properties used correctly (avoid `<div role="button">` anti-patterns)

## 5. Development Workflow

### 5.1 Design Phase

- Verify color palette meets 4.5:1 contrast (see `Design System Guidelines`)
- Use semantic HTML (`<h1>`, `<label>`, `<button>`) in mockups, not `<div>` divs with `role` attributes
- Include all interactive states (focus, hover, active, disabled) in designs

### 5.2 Development Phase

1. **Use Semantic HTML**: `<button>`, `<label>`, `<fieldset>`, `<a>`, not role-based divs
2. **Alt Text**: Every image gets descriptive alt text
3. **Form Labels**: Every input has visible `<label>` and `id` matching
4. **Focus Styles**: Ensure visible focus indicator (e.g., 2px blue outline)
5. **ARIA Only When Needed**: Don't over-use ARIA; semantic HTML is better
6. **Keyboard Handlers**: Add `onKeyDown` handlers for interactive components (e.g., Escape to close modal)
7. **Live Regions**: Use `aria-live="polite"` for notifications and dynamic updates

### 5.3 QA & Testing Phase

- Run axe DevTools on staging; fix all errors
- Keyboard navigation test: Tab through entire page
- Screen reader test: NVDA/VoiceOver on 3+ key user flows
- Zoom test: 200% zoom on desktop; 200% zoom on mobile
- Document any known limitations (e.g., "3D visualization not keyboard accessible; roadmap item for next quarter")

## 6. Accessibility Review Checklist

Before shipping any feature:

- [ ] No critical axe errors
- [ ] 4.5:1 contrast verified on all text
- [ ] All form inputs have visible labels
- [ ] All images have alt text (or empty `alt=""` if decorative)
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Focus styles visible on all interactive elements
- [ ] No color-only information (e.g., red box needs label or icon too)
- [ ] Screen reader tested with NVDA or VoiceOver
- [ ] Zoom 200% tested; layout stable
- [ ] Mobile screen reader tested (VoiceOver or TalkBack)

## 7. Accessibility Specialists

**Who to contact** for accessibility questions:

| Question | Contact | How |
|----------|---------|-----|
| Is my design accessible? | @a11y-design on Slack | Post Figma link or screenshot |
| How do I test with a screen reader? | @a11y-qa on Slack | Ask for guidance or live session |
| Is this ARIA attribute correct? | @a11y-eng on Slack | Post code snippet or ask specific question |
| Can we defer accessibility to v2? | VP Engineering | Answer: No. Accessibility is a core requirement. |

## 8. Accessibility Metrics

Track quarterly:

- **New Features Meeting WCAG 2.1 AA**: % of shipped features with zero critical axe errors (target: 100%)
- **Automated Test Coverage**: % of pages with axe scanning enabled in CI/CD (target: 100%)
- **Manual Testing**: % of features with screen reader testing before release (target: 100%)
- **Customer Feedback**: Accessibility-related support tickets / month (target: <1% of total)

## 9. Resources

- **WCAG 2.1 Specification**: https://www.w3.org/WAI/WCAG21/quickref/
- **WebAIM Guides**: https://webaim.org/ (articles on accessibility topics)
- **A11y Project**: https://www.a11yproject.com/ (checklist and resources)
- **Inclusive Components**: https://inclusive-components.design/ (pattern library for accessible UIs)
- **Deque Accessibility Training**: Internal training available; ask VP Design to schedule

