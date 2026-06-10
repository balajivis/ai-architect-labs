---
title: Design System Guidelines
doc_id: prod-design-system-guidelines
owner: Design Leadership
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Design System Guidelines

## 1. Purpose

The Northwind Design System is the single source of truth for all visual, interactive, and accessibility standards across Northwind Cloud products. All product teams must use this system to ensure brand consistency, fast development, and accessible user experiences.

**Design System Location**: Figma workspace: `northwind-design-system` (read-only for all employees; edit access for Design team).

## 2. Core Principles

1. **Accessibility First**: All components meet WCAG 2.1 AA (see *Accessibility Standard*)
2. **Consistency Over Innovation**: Reuse existing components before creating new ones
3. **Performance**: Components optimized for web performance; minimal CSS bloat
4. **Dark Mode Native**: All components designed for dark theme (light mode is legacy)
5. **Mobile Responsive**: Components work at 320px (mobile) to 2560px (ultra-wide)
6. **Developer Friendly**: Clear documentation, copy-paste code examples, TypeScript types

## 3. Component Hierarchy

| Level | Scope | Examples |
|-------|-------|----------|
| **Primitives** | Atomic UI elements | Button, Input, Icon, Badge, Divider |
| **Components** | Reusable patterns | Form, Dialog, Toast, Dropdown, SearchField |
| **Layouts** | Page-level structures | SidebarLayout, DashboardLayout, SettingsLayout |
| **Patterns** | Domain-specific templates | DataTable with sorting/filtering, InvoiceList, UserProfile |

**Rule**: Always use Primitives from the design system. Create new Components only if no existing component fits. Create Layouts or Patterns only with Design Lead approval.

## 4. Color Palette

### 4.1 Semantic Colors

| Use | Color | Hex | WCAG 2.1 AA Contrast |
|-----|-------|-----|----------------------|
| **Primary Action** | Indigo 600 | #4F46E5 | 7.2:1 on #000 |
| **Success** | Green 500 | #10B981 | 5.8:1 on #000 |
| **Warning** | Amber 500 | #F59E0B | 3.1:1 on #000 |
| **Error** | Red 500 | #EF4444 | 4.5:1 on #000 |
| **Neutral** | Zinc 400 | #A1A5AB | 6.4:1 on #000 |

### 4.2 Accessibility Requirements

- **Color Contrast**: All text must meet **4.5:1 ratio minimum** for body text (WCAG AA)
- **Color Alone**: Never convey information using color alone (e.g., red box without label). Pair with icon, text, or pattern
- **Dark Mode**: All colors tested on zinc-950 (#09090B) background
- **Light Mode**: (Legacy) All colors tested on white (#FFFFFF) background; no new light mode work

## 5. Typography

### 5.1 Font Scale

| Role | Font Size | Line Height | Weight | Examples |
|------|-----------|-----------|--------|----------|
| **Display** | 48px–56px | 1.2 | 700 (Bold) | Page headlines, marketing |
| **H1** | 36px | 1.25 | 700 (Bold) | Section headers |
| **H2** | 28px | 1.3 | 600 (Semi) | Subsection headers |
| **H3** | 20px | 1.4 | 600 (Semi) | Card titles, sidebar headers |
| **Body** | 16px | 1.5 | 400 (Regular) | Paragraph text, table cells |
| **Small** | 14px | 1.5 | 400 (Regular) | Labels, captions, help text |
| **Tiny** | 12px | 1.4 | 400 (Regular) | Badges, timestamps |

### 5.2 Font Families

- **Sans-Serif**: Inter (primary; open-source; excellent readability at all sizes)
- **Monospace**: IBM Plex Mono (code blocks, API responses)
- **Fallback**: System font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`

## 6. Spacing & Layout Grid

### 6.1 Spacing Scale

All spacing uses 4px base unit:

| Token | Value | Usage |
|-------|-------|-------|
| **xs** | 4px | Minimal gap (icon spacing within button) |
| **sm** | 8px | Small margin (form field spacing) |
| **md** | 16px | Default padding (card padding, section spacing) |
| **lg** | 24px | Large section gap |
| **xl** | 32px | Major section separation |
| **2xl** | 48px | Page-level gap |

### 6.2 Layout Grid

- **12-column grid** on desktop (each column = (viewport width - 48px) / 12)
- **4-column grid** on tablet
- **1-column** on mobile (full width – 16px padding)
- **Gutters**: 16px (8px left + right padding)

## 7. Component Checklist

Before using any component, verify:

- ✅ **Accessibility**: Component includes ARIA labels, keyboard navigation, color contrast
- ✅ **States**: Component shows all states (default, hover, active, disabled, error, loading)
- ✅ **Responsive**: Component works at 320px, 768px, 1024px, 1440px viewports
- ✅ **Dark Mode**: Component tested on zinc-950 background
- ✅ **TypeScript**: Component is fully typed; no `any` types
- ✅ **Documentation**: Component has Storybook story with all props documented

**Storybook URL**: `storybook.northwind.local:6006` (internal only)

## 8. Creating New Components

**ONLY** create new components if:

1. ✅ No existing component solves the problem
2. ✅ Design Lead has approved the design (prevents duplication)
3. ✅ Component will be used in ≥2 features (reusable, not one-off)

**Process**:

1. **Design**: Create Figma component in `northwind-design-system` workspace; include all states
2. **Review**: Get Design Lead + 1 engineer to review; ensure accessibility and alignment with design system
3. **Implement**: Create React component in `components/primitives/` or `components/components/` folder
4. **Test**: ≥90% code coverage; Storybook story; manual accessibility testing
5. **Document**: Write JSDoc comment explaining props, usage, and accessibility notes
6. **Register**: Add to component registry in `components/index.ts`

## 9. Dark Mode Specifications

All Northwind products use a **dark theme** with this palette:

| Token | Color | Hex | Usage |
|-------|-------|-----|-------|
| **bg-base** | Zinc 950 | #09090B | Page background |
| **bg-secondary** | Zinc 900 | #18181B | Card background, sidebar |
| **bg-tertiary** | Zinc 800 | #27272A | Hover state, input field |
| **text-primary** | Zinc 50 | #FAFAFA | Body text |
| **text-secondary** | Zinc 400 | #A1A5AB | Secondary text, captions |
| **border** | Zinc 700 | #3F3F46 | Component borders |

**Verification**: Test all components on `#09090B` background in Figma.

## 10. Responsive Design Breakpoints

| Breakpoint | Width | Devices | Grid |
|-----------|-------|---------|------|
| **mobile** | 320–767px | Phone | 1 column |
| **tablet** | 768–1023px | Tablet (portrait) | 4 column |
| **desktop** | 1024–1439px | Laptop | 12 column |
| **wide** | 1440px+ | Desktop, ultra-wide monitors | 12 column (centered, max-width 1440px) |

**CSS**: Use Tailwind breakpoints: `sm:`, `md:`, `lg:`, `xl:` (matches above ranges exactly).

## 11. Animation & Motion

### 11.1 Easing Functions

| Animation | Duration | Easing | Usage |
|-----------|----------|--------|-------|
| **Micro** (icon change) | 150ms | ease-out | Icon swap, button state |
| **Standard** (entrance) | 250ms | ease-out | Modal open, sidebar slide |
| **Emphasis** (attention) | 300ms | ease-in-out | Bounce, pulse (use sparingly) |
| **Slow** (departure) | 400ms | ease-in | Modal close, fade out |

### 11.2 Accessibility

- Respect `prefers-reduced-motion` media query; set `animation: none` if user has motion-reducing accessibility setting enabled
- Never auto-play animations; require user interaction
- Avoid flashing or strobing (≤3 flashes/second)

## 12. Internationalization & Localization

Components must support:

- **RTL Languages**: Arabic, Hebrew, Farsi (see *Localization & Internationalization Standard*)
- **Long Text**: German and Russian text 30–50% longer than English; design for text expansion
- **Icon Semantics**: Icons work in RTL context (e.g., no arrow-right that becomes arrow-left in RTL; use directional icons with caution)

## 13. Design System Maintenance

- **Version Control**: Design System components tracked in `components/` folder, version bumped in `package.json`
- **Breaking Changes**: Major version bump (e.g., 2.0.0 → 3.0.0) for prop changes; teams notified 4 weeks in advance
- **Deprecation**: Old components marked `deprecated` in Storybook; full removal after 8 weeks
- **Migration Guide**: When component changes, provide before/after examples and code migrations

## 14. When to Deviate

**Rarely**, designs may need to deviate from the system (e.g., specialized visualization, brand landmark page). Approval required from:

- Design Lead (aesthetic fit)
- VP Engineering (implementation feasibility)
- Accessibility specialist (WCAG 2.1 AA compliance must still be met)

Document deviation in a comment on the Figma file and the code (JSDoc).

