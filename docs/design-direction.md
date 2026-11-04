# Visual direction - ChildHealth Explorer

Research date: 2 November 2026. Approved by the project author and applied to the prototype in the 3 November revision. The final application is a separate implementation stage.

## Applied revision

- Source Sans 3 for interface text; Source Serif 4 for the main heading and wordmark. The prototype loads them through Google Fonts with fallback fonts.
- Open layouts, simple dividers between metrics and 6 px control corners. The decorative plus symbol and tagline were removed.
- Color feedback lasts 110 ms; section changes and source explanations use 150 ms. Charts interpolate over 240 ms only for the same measure, years and missing-value pattern. Other selections update directly.
- `prefers-reduced-motion` disables motion. Colors follow the host theme. There is no entrance animation, counting effect or artificial delay.
- Fonts, colors, radii, spacing and feedback durations are grouped at the start of the stylesheet. Optional customization controls expose corner radius, density, serif headings and motion.
- The initial version is retained in `docs/prototype/childhealth-ui-initial.html`; screenshots of the revised layout use the `prototype-refined-` prefix.

The sections below record the reasoning and sources behind the original recommendation.

## Goal and criteria

The interface should feel deliberately designed for this subject and be easy for the author to customize. Fonts and effects do not establish who made a site. The working criteria are suitability for data analysis, legibility, consistency and useful details.

The chosen direction is an analytical application with restrained editorial typography: specific public-health content, a clear text hierarchy, fewer enclosing panels and functional motion. This is a project design choice, not an experimental finding about detecting AI-generated sites.

## Typography

- **Source Sans 3** for navigation, forms, body text, tables and charts. Adobe describes it as a family designed for user interfaces.
- **Source Serif 4** for the main heading and, optionally, short introductions. Adobe presents it as a companion to Source Sans, with optical sizes.
- Both are open-source under the OFL. Keep license files when distributing fonts; webfonts can be served locally. Check diacritics and numerical glyphs during implementation.

**IBM Plex Sans** is an alternative for a more technical research-tool direction. Two sans-serif families are not needed simultaneously.

Initial sizes for visual review:

| Element | Size / usage |
|---|---|
| Body text | 16 px; approximately 1.5 line height |
| Filters and controls | 14-16 px, depending on density |
| Main heading | 28-32 px; medium weight |
| Charts and secondary data | 12-14 px; keep labels legible |
| Table numbers | Right-aligned; tabular figures where available |

These are prototype choices, not sizes mandated by the sources.

## Composition

1. Reduce nested rounded panels. Charts and tables can use simple dividers.
2. Test 4-8 px corner radii against the original 14 px. Radius alone is not evidence of AI use.
3. Keep the green accent and readable contrast in both themes. Use data colors to distinguish series or states.
4. Remove the decorative "Global health / Country insights" label. A section title and country-year-source context provide the useful information.
5. Use precise indicator names and explanations tied to the current selection.
6. Build identity around the project name; the original plus symbol is not a final logo.
7. Keep sources, units, years and data availability visible.

## Transitions and animation

NN/g recommends subtle animation for feedback and state changes. Carbon distinguishes productive motion for tasks and data visualization from expressive motion for special moments.

| Interaction | Initial proposal |
|---|---|
| Hover / focus / active state | 110 ms, mainly color; show focus immediately |
| Small panel opening | 150 ms with gentle deceleration |
| Section change | At most 150 ms, without large movement or delayed access |
| Updating the same chart indicator | About 240 ms, only where it helps track a change |
| Changing the indicator or unit | Direct update; do not interpolate incompatible measures |
| Numeric updates | Show final values directly, without counting from zero |
| Loading | Show an indicator only for a real wait; no artificial delays or progress |

The initial easing curve is Carbon productive standard: `cubic-bezier(0.2, 0, 0.38, 0.9)`. Refine it through testing; durations do not guarantee a perceived "human" result.

Bounce, parallax, continuously animated backgrounds, glow and staggered card entrances do not support the current analysis tasks.

Respect `prefers-reduced-motion` while keeping the interface functional. W3C technique C39 supports this approach in connection with WCAG 2.3.3 (AAA); the prototype has not been certified for accessibility.

## Author customization

Group fonts, colors, spacing, radii and durations in clear style variables. The author can change wording, density, accents, labels and annotations without changing data logic. Compare the revised version visually before adopting further changes.

## Primary sources consulted

- [Adobe Source Sans 3 - official repository](https://github.com/adobe-fonts/source-sans)
- [Adobe Source Serif 4 - official specimen](https://adobe-fonts.github.io/source-serif/)
- [Adobe Source Serif - repository and license](https://github.com/adobe-fonts/source-serif)
- [IBM Design Language - IBM Plex](https://www.ibm.com/design/language/typography/typeface/)
- [Carbon - motion, easing and durations](https://www.carbondesignsystem.com/building-blocks/foundations/motion/overview)
- [Nielsen Norman Group - the role of animation in UX](https://www.nngroup.com/articles/animation-purpose-ux/)
- [W3C - reduced-motion technique C39](https://www.w3.org/WAI/WCAG22/Techniques/css/C39.html)
