# QField Assistance Page - Bootstrap 5 & Hugo Best Practices

## Overview

The assistance page has been completely refactored to follow Hugo best practices and use Bootstrap 5 components properly.

## Key Improvements

### 1. Data-Driven Content
- **Data File**: `data/assistance.yaml` - Centralizes all content for easy maintenance
- **Separation of Concerns**: Content is separated from presentation logic
- **Internationalization Ready**: Data structure supports easy translation

### 2. Reusable Partials
- **Service Card Partial**: `layouts/partials/assistance/service-card.html`
- **Customize Section Partial**: `layouts/partials/assistance/customize-section.html`
- **Modular Design**: Components can be reused across different pages

### 3. Bootstrap 5 Compliance
- **Modern Classes**: Uses Bootstrap 5.3+ classes (`g-4`, `visually-hidden`, etc.)
- **Flexbox Layout**: Proper flexbox implementation for equal height cards
- **Responsive Design**: Mobile-first approach with proper breakpoints
- **Accessibility**: ARIA labels, semantic HTML, screen reader support

### 4. Performance Optimizations
- **Asset Pipeline**: Uses Hugo's asset pipeline for CSS processing
- **SCSS Organization**: Structured SCSS with proper nesting and variables
- **Lazy Loading**: Images use `loading="lazy"` attribute
- **Fingerprinting**: CSS fingerprinting for cache busting

### 5. SEO & Accessibility
- **Structured Data**: Ready for schema.org implementation
- **Meta Tags**: Comprehensive meta tags and Open Graph support
- **Semantic HTML**: Proper HTML5 semantic elements
- **Keyboard Navigation**: Full keyboard accessibility support

## File Structure

```
├── content/
│   └── assistance.md                           # Page content and frontmatter
├── data/
│   └── assistance.yaml                         # All page data
├── layouts/
│   ├── assistance.html                         # Main page layout
│   └── partials/assistance/
│       ├── service-card.html                   # Reusable service card
│       └── customize-section.html              # Customize section
└── themes/qfield-theme-v3/assets/sass/
    └── styles.scss                             # Page-specific styles
```

## Data Structure

The `data/assistance.yaml` file contains:

- **Hero Section**: Title and optional subtitle
- **Services Array**: List of all assistance services with:
  - Title, description, icon
  - Call-to-action text and URL
  - External link flag
  - Optional inline links
- **Customize Section**: Special section for customization services

## Bootstrap 5 Features Used

- **Grid System**: Responsive grid with gutters (`g-4`)
- **Card Components**: Modern card layout with proper flexbox
- **Utility Classes**: Spacing, text, and display utilities
- **Accessibility**: Screen reader classes and ARIA attributes
- **Hover Effects**: CSS transitions and transforms

## Development Best Practices

1. **Content Management**: Use data files for content that changes frequently
2. **Component Reusability**: Create partials for reusable UI components
3. **CSS Organization**: Use SCSS with proper nesting and BEM methodology
4. **Performance**: Optimize images and use Hugo's asset pipeline
5. **Accessibility**: Always include proper ARIA labels and semantic HTML

## Future Enhancements

- Add JSON-LD structured data for better SEO
- Implement dark mode support
- Add animation library integration
- Create A/B testing capabilities for CTAs
- Add analytics tracking for service card interactions

## Testing

The page has been tested for:
- Responsive design (mobile, tablet, desktop)
- Keyboard navigation
- Screen reader compatibility
- Cross-browser compatibility
- Performance metrics