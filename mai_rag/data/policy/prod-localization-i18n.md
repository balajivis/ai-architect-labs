---
title: Localization & Internationalization Standard
doc_id: prod-localization-i18n
owner: Product & Engineering
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Localization & Internationalization Standard

## 1. Purpose

Localization (L10n) and Internationalization (i18n) ensure Northwind Cloud works for customers worldwide. Internationalization is the technical architecture (RTL support, unicode, date formats); localization is translating content into local languages.

**Scope**: Currently supporting English (US). French, German, Spanish (ES), and Japanese in roadmap for 2026–2027.

## 2. Supported Languages & Regions

### Current (2026)

| Language | Region | Status | Notes |
|----------|--------|--------|-------|
| **English** | US | ✅ Supported | Primary language; all content in English |
| **English** | UK/AU/CA | ✅ Partial | Same as US English; no region-specific variants |

### Planned (2026–2027 Roadmap)

| Language | Region | Status | Target Date |
|----------|--------|--------|-------------|
| **Spanish** | ES (Spain) | 🔄 Planned | Q3 2026 |
| **French** | FR (France) | 🔄 Planned | Q3 2026 |
| **German** | DE (Germany) | 🔄 Planned | Q4 2026 |
| **Japanese** | JP (Japan) | 🔄 Planned | Q4 2026 |

## 3. Internationalization (i18n) Infrastructure

### 3.1 Technology Stack

| Component | Tool | Notes |
|-----------|------|-------|
| **Translation Framework** | next-intl (Next.js) | Handles locale routing, message catalogs |
| **Date Formatting** | date-fns with locale support | Consistent date/time formatting per region |
| **Number Formatting** | Built-in Intl.NumberFormat API | Currency, percentages, thousands separators |
| **Text Direction** | CSS `dir` attribute + Tailwind RTL classes | RTL for Arabic/Hebrew (future support) |
| **String Extraction** | i18n Scanner (custom) | Identifies translatable strings in code |

### 3.2 i18n Setup Checklist

For every new feature, ensure:

- ✅ **No hardcoded strings**: All user-facing text extracted to message catalogs
- ✅ **Placeholder support**: Messages support interpolation (e.g., "Hello, {name}!")
- ✅ **Date/time localization**: Use `format()` from date-fns with locale, not hardcoded formats
- ✅ **Number localization**: Use `Intl.NumberFormat` for currency, percentages
- ✅ **Pluralization**: Handle singular/plural forms (e.g., "1 file" vs. "5 files")
- ✅ **RTL-safe**: No hardcoded `left`/`right` CSS; use `start`/`end` or CSS logical properties
- ✅ **Icon review**: Icons meaningful in target cultures (no culture-specific symbols)

### 3.3 Code Example: English

```typescript
// messages/en.json
{
  "greeting": "Welcome, {name}!",
  "file_count": {
    "one": "You have 1 file",
    "other": "You have {count} files"
  },
  "price": "Price: {price, number, currency}"
}

// components/Dashboard.tsx
import { useTranslations } from 'next-intl';
import { format } from 'date-fns';
import { enUS } from 'date-fns/locale';

export function Dashboard({ user, fileCount, subscription }) {
  const t = useTranslations();
  
  return (
    <div>
      <h1>{t('greeting', { name: user.firstName })}</h1>
      <p>{t('file_count', { count: fileCount })}</p>
      <p>{t('price', { price: subscription.monthlyPrice })}</p>
      <p>Updated: {format(new Date(), 'PPP', { locale: enUS })}</p>
    </div>
  );
}
```

## 4. String Extraction & Translation Workflow

### 4.1 Developer Workflow

1. **Write Feature**: Extract all user-facing strings to i18n catalog:

```typescript
// ❌ Bad: Hardcoded string
<button>Export Report</button>

// ✅ Good: Extracted to translation catalog
<button>{t('button_export_report')}</button>
```

2. **Message Catalog Entry**:

```json
// messages/en.json
{
  "button_export_report": "Export Report",
  "dialog_export_title": "Choose Export Format",
  "dialog_export_format_pdf": "PDF",
  "dialog_export_format_csv": "CSV"
}
```

3. **Validation**: Use script to detect untranslated strings:

```bash
npm run i18n:extract  # Scan for hardcoded strings (should find none)
npm run i18n:validate # Confirm all required messages exist
```

### 4.2 Translation Vendor Workflow

**When new language planned** (e.g., Spanish 2026-Q3):

1. **Extract English Catalog**: Export all strings from `messages/en.json`
2. **Send to Translation Vendor**: Share English catalog + context (screenshots, URLs)
3. **Vendor Reviews**: Translators review English strings; may request clarifications (e.g., "Is 'Cloud' a product name or generic?")
4. **Translation Delivery**: Vendor provides translated file (e.g., `messages/es.json`)
5. **QA Review**: Product team review translations for accuracy, tone, cultural fit
6. **Integration**: Merge `messages/es.json` into codebase; test with Spanish locale

**Timeline**: 4–6 weeks for new language translation (depends on content volume).

## 5. Localization Guidelines

### 5.1 Date & Time Formatting

| Region | Date Format | Time Format | Example |
|--------|-------------|-------------|---------|
| **US (en-US)** | MM/DD/YYYY | 12-hour (AM/PM) | 06/09/2026, 2:23 PM |
| **UK (en-GB)** | DD/MM/YYYY | 24-hour | 09/06/2026, 14:23 |
| **ES (es-ES)** | DD/MM/YYYY | 24-hour | 09/06/2026, 14:23 |
| **DE (de-DE)** | DD.MM.YYYY | 24-hour | 09.06.2026, 14:23 |
| **JP (ja-JP)** | YYYY/MM/DD | 24-hour | 2026/06/09, 14:23 |

**Code**:

```typescript
import { format } from 'date-fns';
import { enUS, es, de, ja } from 'date-fns/locale';

const locale = getUserLocale(); // 'en-US', 'es-ES', etc.
const localeMap = { 'en-US': enUS, 'es-ES': es, 'de-DE': de, 'ja-JP': ja };

const formatted = format(new Date(), 'PPP p', { locale: localeMap[locale] });
// Output: "June 9, 2026, 2:23 PM" (en-US)
// Output: "9 de junio de 2026, 14:23" (es-ES)
```

### 5.2 Currency Formatting

| Region | Currency | Format | Example |
|--------|----------|--------|---------|
| **US** | USD | $X,XXX.XX | $1,234.56 |
| **Spain** | EUR | X.XXX,XX € | 1.234,56 € |
| **Germany** | EUR | X.XXX,XX € | 1.234,56 € |
| **Japan** | JPY | ¥X,XXX | ¥123,456 |

**Code**:

```typescript
const formatter = new Intl.NumberFormat(locale, {
  style: 'currency',
  currency: currencyCode, // 'USD', 'EUR', 'JPY'
});

console.log(formatter.format(1234.56));
// en-US: "$1,234.56"
// es-ES: "1.234,56 €"
```

### 5.3 Number Formatting

- **Thousands separator**: US = 1,234.5; Europe = 1.234,5; Japan = 1,234.5
- **Decimal separator**: US = . (period); Europe = , (comma)
- **Percentages**: Format using locale-aware `Intl.NumberFormat` with `style: 'percent'`

### 5.4 Text Direction (RTL)

For future Arabic/Hebrew support:

**CSS Logical Properties** (preferred):

```css
/* ❌ Avoid absolute directions */
.sidebar { margin-left: 20px; }

/* ✅ Use logical directions */
.sidebar { margin-inline-start: 20px; } /* Respects RTL */
```

**HTML Markup**:

```html
<!-- Set dir="rtl" on root for RTL languages -->
<html dir="ltr" lang="en-US">
<html dir="rtl" lang="ar-SA">

<!-- Inline text direction (rare) -->
<p dir="auto">English text عربي text</p>
```

**Flex & Grid**:

```css
/* Flex direction auto-flips in RTL */
.container {
  display: flex;
  flex-direction: row; /* → ← in RTL */
}
```

### 5.5 Icons & Cultural Sensitivity

**Review icons before translation**:
- ❌ Thumbs up (offensive in some cultures)
- ❌ Mailbox shape (varies by region)
- ❌ Currency symbols (use text "USD" instead of "$" for clarity)
- ✅ Abstract symbols or text labels

**Testing**: Request feedback from native speakers on icon appropriateness.

## 6. Product Localization Checklist

Before shipping a new feature in a new language:

- [ ] All UI text translated (no English fallthrough)
- [ ] Dates formatted per region
- [ ] Currency formatted per region
- [ ] All number formats use locale awareness
- [ ] No hardcoded left/right (use start/end or logical CSS)
- [ ] Text direction set correctly (RTL if applicable)
- [ ] Icons reviewed for cultural sensitivity
- [ ] Help text and tooltips translated
- [ ] Error messages translated
- [ ] Email templates translated
- [ ] Date picker supports target language months/day names
- [ ] Form validation messages translated
- [ ] Native speakers (from target region, not just language) reviewed UI

## 7. Adding a New Language

**Process** (estimated 8 weeks):

**Week 1**: Approval & Planning
- Product + VP Engineering approve new language
- Assign translation vendor
- Extract current English message catalog

**Weeks 2–5**: Translation & QA
- Vendor translates all strings
- Product team reviews for accuracy and tone
- Request revisions if needed (1–2 rounds)

**Weeks 6–7**: Integration & Testing
- Engineer integrates translated messages into codebase
- QA tests: all pages, forms, error messages in new language
- Bug fixes for formatting, text overflow, RTL (if applicable)

**Week 8**: Launch
- Deploy with new language enabled for opt-in (or specific region)
- Monitor for issues
- Collect user feedback

## 8. String Guidelines for Translators

### 8.1 Context for Translators

Provide for each message:

```json
{
  "button_export_report": {
    "message": "Export Report",
    "context": "Button label for exporting a report as PDF or CSV",
    "maxLength": 30,
    "notes": "Keep concise; appears in sidebar export menu"
  }
}
```

### 8.2 Avoid Ambiguity

- ❌ "Save" (ambiguous: Save in editor? Save as file?)
- ✅ "Save Draft" or "Download File"

- ❌ "Settings" (ambiguous: Global settings? Feature settings?)
- ✅ "Dashboard Settings" or "Account Preferences"

### 8.3 Placeholders & Interpolation

```json
{
  "welcome_message": "Welcome, {firstName}! You have {documentCount} documents.",
  "file_count_singular": "You have 1 file",
  "file_count_plural": "You have {count} files"
}
```

Explain to translators: `{firstName}` and `{count}` are placeholders; translate around them, not replacing them.

## 9. Performance: Lazy Loading Translations

For performance, load translations on-demand:

```typescript
// ✅ Good: Lazy load Spanish messages only if user selects Spanish
const messages = {
  'en': () => import('./messages/en.json'),
  'es': () => import('./messages/es.json'),
};

async function loadLocale(locale: string) {
  return messages[locale]?.();
}
```

## 10. Localization Metrics

Track quarterly:

| Metric | Target |
|--------|--------|
| **Translation Completeness** | 100% of UI strings translated in active languages |
| **Native Speaker Review** | ≥1 native speaker review per language (before launch) |
| **User Reports (L10n)** | <5 localization bugs per quarter per language |
| **Date/Number Formats** | 100% of dates/numbers use locale formatting (no hardcoded) |

