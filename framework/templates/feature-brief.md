# <NN> — <Feature name>

Status: draft | reviewed | designed | built
Mock-ups: <path or link, once designed>

## Intent

- **For**: <who, in what situation>
- **Problem**: <what it solves>
- **Success**: <how we will know it works>
- **Out of scope**: <what it does not do>
- **Target**: <mobile app / website / CLI / API… and on what: phone sizes, browsers, terminals>

## Flows

1. **[N.1] <Screen>** — <what the user does, where it leads>
2. **[N.2] <Screen>** — …

Entry points: <…> · Exits: <…, back navigation, cancel>

## States

| Screen | Case | What the user sees | Copy | Way out |
|---|---|---|---|---|
| [N.1] | Empty, first use | <empty state with illustration?> | « … » | <primary action> |
| [N.1] | Offline | <banner, rest of the app usable> | « … » | Retry |
| [N.1] | Service down | <distinct from offline> | « … » | Retry |
| … | | | | |

## Motion

| Element | Animation | Why | Duration / easing | Reduce motion |
|---|---|---|---|---|
| <…> | <…> | feedback / continuity / attention | <token> | <replacement or none> |

## UX decisions

| Question | Options | Choice | Reason |
|---|---|---|---|
| <…> | A / B | A | <…> |

Voice: <formal / informal address, tone of errors>

## Accessibility

- <the checks that fit the target: labels, contrast, text scaling, colour-independent cues, touch targets / keyboard navigation / `NO_COLOR` / error bodies…>

## Design prompt

> <Self-contained prompt for Claude Design: the feature in two sentences, the design system to use, then every screen [N.M] with each of its states from the table above, the motion to show, and the variants the target needs (themes, screen sizes).>

## Acceptance checklist

- [ ] [N.1] <state> — <expected result>
- [ ] …
