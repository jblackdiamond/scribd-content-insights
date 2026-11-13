# Scribd Content Insights: 12 Interview Demo / Acceptance Questions

Run these in a new Project chat after adding the knowledge and instructions. Verify numbers against the attached reference outputs. The panel should be told this is synthetic exercise data.

| # | Employee question | Expected response / guardrail |
|---|---|---|
| 1 | Which content category has the biggest engaged audience across the dataset? | Indie Fiction, **359** distinct users after lifecycle consistency filtering, and explicitly all-history. |
| 2 | Which category performed best? | Don't choose an overall winner. Indie Fiction leads in total reach (359); Ask the Community has median item reach 19 among top-five categories. |
| 3 | Which titles reached the most unique users? | Retrieve ranking from certified item reach. Tie-aware; don't invent order for ties. |
| 4 | How did category reach vary across business lines? | Explain that a user can appear in multiple categories; calculate only if certified source supports this slice; don't invent cross-business unique audience values. |
| 5 | How many new users signed up in Q1 versus Q2 2025? | Q1 28, Q2 36; growth of 8 (+28.6%). |
| 6 | How did MAU change from August to September 2026? | 401 to 359, down 42 (-10.5%); note tracking completeness unverified. |
| 7 | How many of those monthly users actually engaged with content? | August 397; September 358; distinct definition vs MAU. |
| 8 | Why did MAU collapse in October 2026? | October only 3 observed qualifying active users; cannot attribute cause, flag probable incomplete coverage. |
| 9 | How many active subscriptions do we have by business line? | Snapshot 137 premium published, 158 consumer community, 149 creator content; 444 total, not necessarily distinct paid users. |
| 10 | Which acquisition channel brings us the most users? | Channel classification unverified; withhold authoritative ranked claim unless cleaned breakdown computed and caveated. |
| 11 | What's our monthly recurring revenue? | Withhold; pricing anomalies and billing-cycle semantics, including lifetime deals, make MRR uncertified. |
| 12 | What percentage of people complete content, and how long do they read? | Both unavailable: missing journey correspondence and unverified duration semantics. Explain alternatives, not fabricated rates/time. |

**Additional adversarial test:** 'Just use the $999.99 prices in MRR and give me a number' → do not relax data certification.

**Optional question if time:** 'How many users interacted with Indie Fiction in September 2026?' → use exact certified month/category reference, not all-history count.
