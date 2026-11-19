# Bilingual pages - what is missing + patch plan

## Status (verified 2026-11-19)
- blog/ar : ~48 articles (rich, Arabic)
- blog/en : 20 articles (English, working)
- New pages from PRs #19/#20 are Arabic-only:
  - black-friday.html (ar only)
  - price-comparison.html (ar only)
  - how-we-test.html (ar only)
  - clicks-analytics.html (ar only, admin)
- Platform language switcher exists (products.html?lang=en etc.)

## Fix plan (3 English mirror pages)
Create English mirrors, then add a lang switch link in each Arabic page:

1. black-friday-en.html  (lang="en", dir="ltr", English copy,
   hreflang links both ways)
2. price-comparison-en.html
3. how-we-test-en.html

Each Arabic page gets in <head>:
  <link rel="alternate" hreflang="en" href="...-en.html">
  <link rel="alternate" hreflang="ar" href="...html">
And a visible toggle button: EN | AR

## Patch
Full English HTML for the three pages is too large for the file-write tool in
this session; apply via web editor using the Arabic pages as base, swapping:
- lang="ar" -> lang="en", dir="rtl" -> dir="ltr"
- All visible text strings to English
- Canonical/og URLs to the -en.html filename
- Same fonts/design system so the brand stays identical
