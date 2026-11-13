# Scribd Content Insights: Metric Dictionary & Verified Answers v2

**Prototype only.** Synthetic exercise data, not Scribd production metrics. Calculated independently using `scribd_certify_metrics.py`. All time boundaries use the source timestamps as supplied; timezone not known. Treat each month/quarter as a calendar period and state dates explicitly.

## Rules common to all metrics
- Deduplicate 6 exactly duplicated user records on `user_id`, and exclude 40 flagged test users.
- Exclude 8 content rows with `content_type=TEST_TYPE` and their related content events.
- For event-based metrics, exclude events recorded before their associated user's signup date. This removes 29 otherwise eligible content events and leaves **5,163** valid content events, representing 759 users and 292 eligible titles, across the full available event history.
- Qualifying content event types: `content_open`, `content_complete`, `download`, `like`, `share`, `comment_post`. These imply *interaction* not necessarily actual reading/listening.
- For platform MAU, also include `search_query` and `page_view` events, excluding subscription administration and invalid event types. Content events must link to eligible content.
- Count unique people with `COUNT(DISTINCT user_id)` at the requested grain. Users can appear in multiple categories, titles, or months; do not sum distinct audience metrics across them.
- Include titles with **zero** eligible events when computing per-title category distribution metrics.
- Do not claim that any source is independently verified production tracking; confidence is in reproducibility of the exercise calculations, not real-world completeness.

## Approved metrics

### CATEGORY_REACH
Distinct non-test users with >=1 qualifying content event in a category for the selected reporting period. Source `scribd_certified_category_metrics.csv` for all-history, `scribd_certified_category_by_month.csv` for individual source months. **All-history results are not an implicit default for a request about an unspecified recent period.** Caveat: catalog size and content age differ, and engagement is not confirmed consumption.

### ITEM_REACH
Distinct non-test users with >=1 qualifying interaction with a title, from `scribd_certified_item_reach.csv` (full supplied history only). If date filtered by month, calculate independently from the original CSVs with the approved code before answering; do not infer from all-history values.

### MEDIAN_ITEM_REACH
Median of per-item unique reach over *all eligible titles in a category*, including zero-engagement titles; from `scribd_certified_category_metrics.csv` (all history only). This is separate from category reach. No official universal 'best' score.

### PLATFORM_MAU
Distinct non-test users with >=1 qualifying platform event in a calendar month; use `scribd_certified_monthly_metrics.csv`. A search or page view counts, even without a content interaction. Don't sum monthly user counts to get distinct quarterly users.

### MONTHLY_CONTENT_ENGAGED_USERS
Distinct non-test users with >=1 qualifying content event during a calendar month; use `scribd_certified_monthly_metrics.csv`. Not verified readers or listeners. Always <= platform MAU.

### NEW_SIGNUPS
Distinct non-test users grouped by account `signup_date` calendar quarter; use `scribd_certified_quarterly_signups.csv`. A Q1 2025 to Q2 2025 comparison is valid, but not an acquisition causal claim.

### SUBSCRIPTION_STATUS_SNAPSHOT
Count eligible subscription *records* by recorded status, not unique paying subscribers, using `scribd_certified_subscription_status.csv`. Excludes invalid `TEST_STATUS_DO_NOT_USE`, and flagged test users. There are 785 eligible subscription records: 444 active, 212 canceled, 92 paused, 37 trialing.

### ACTIVE_SUBSCRIPTIONS_BY_BUSINESS
Active-status subscription records by business line from `scribd_certified_active_subscriptions_by_business.csv`. No historical inference, no claim these records are all paid.

## Suspended, ambiguous, or not certified
- **MRR**: withhold an authoritative figure because the monthly price interpretation is unclear, anomalous -9.99 and 999.99 records occur, and free/annual/lifetime billing differs. Never silently exclude or correct anomalies, never invent MRR.
- **Completion rate**: completion events vastly outnumber opens; tracked journeys cannot be reliably reconstructed. Do NOT divide `content_complete` count by `content_open` count.
- **Reading/listening time**: `session_duration_sec` may mean app session time, not consumption time; do not aggregate or label as time consumed.
- **Confirmed readers / listeners**: content interactions do not independently prove content was read or played.
- **Historical active subscribers**: subscription table contains current snapshot statuses; historical status cannot be reconstructed reliably.
- **Revenue by title**: no defensible attribution rule exists.
- **Acquisition channel**: labels `influencer_TEST_CAMPAIGN`, `carrier_pigeon`, and missing are unverified; retain these people in overall signup totals, label channels unverified until confirmed.
- **Multi-action engagement rate**: 32 of 5,135 user-content pairs in prior exploratory data had >=2 distinct action types; do not use as depth-performance comparison. This exploratory count predates the lifecycle filter and isn't a certified reference answer.
- **October 2026 activity**: only three qualifying active users are recorded; flag probable coverage problems rather than presenting an unqualified October trend.
- **Best-performing category**: subjective, needs a named performance dimension. Show reach and per-item typical reach separately; do not invent combined weights.

## All-history category results (certified)

| category                            |   category_unique_engaged_users |   eligible_titles |   median_item_reach |   min_item_reach |   max_item_reach |
|:------------------------------------|--------------------------------:|------------------:|--------------------:|-----------------:|-----------------:|
| Indie Fiction                       |                             359 |                29 |                17.0 |               12 |               23 |
| Serialized Drama                    |                             333 |                26 |                16.5 |                9 |               26 |
| Ask the Community                   |                             329 |                22 |                19.0 |               11 |               27 |
| How-To Guides                       |                             296 |                21 |                18.0 |               13 |               24 |
| Fake History of Imaginary Countries |                             285 |                20 |                18.0 |               12 |               24 |
| Self-Help                           |                             280 |                19 |                17.0 |                8 |               27 |
| Fantasy                             |                             264 |                19 |                16.0 |               12 |               26 |
| General Nonsense                    |                             250 |                16 |                18.5 |               14 |               22 |
| Poetry (Bad)                        |                             240 |                16 |                18.0 |               11 |               26 |
| Memes About Reading                 |                             234 |                16 |                18.5 |               10 |               24 |
| Sci-Fi                              |                             218 |                15 |                18.0 |                9 |               22 |
| Book Club Chatter                   |                             218 |                14 |                19.0 |               12 |               25 |
| Definitely Not Fan Fiction          |                             203 |                13 |                17.0 |               13 |               23 |
| Mystery                             |                             199 |                15 |                16.0 |               11 |               21 |
| Fan Theories                        |                             195 |                12 |                18.0 |               13 |               27 |
| Cooking                             |                             146 |                10 |                16.0 |               10 |               22 |
| Romance                             |                             145 |                 9 |                17.0 |               10 |               25 |

## All-history item results (certified, sorted by reach)

| content_id   | title                                            | category                            | business_id   |   item_unique_engaged_users |
|:-------------|:-------------------------------------------------|:------------------------------------|:--------------|----------------------------:|
| CNT_00015    | [MOCK THREAD] Rant: fake topic #15               | Ask the Community                   | BIZ_2         |                          27 |
| CNT_00205    | The Last Prairiefox (Mock Book #205)             | Self-Help                           | BIZ_1         |                          27 |
| CNT_00254    | [MOCK THREAD] Unpopular opinion: fake topic #254 | Fan Theories                        | BIZ_2         |                          27 |
| CNT_00258    | The Imaginary Recipe (Mock Book #258)            | Fantasy                             | BIZ_1         |                          26 |
| CNT_00269    | Episode 91: Totally Original Content (Mock #269) | Serialized Drama                    | BIZ_3         |                          26 |
| CNT_00276    | Episode 10: Totally Original Content (Mock #276) | Poetry (Bad)                        | BIZ_3         |                          26 |
| CNT_00010    | The Great Diary (Mock Book #10)                  | Romance                             | BIZ_1         |                          25 |
| CNT_00090    | [MOCK THREAD] Unpopular opinion: fake topic #90  | Book Club Chatter                   | BIZ_2         |                          25 |
| CNT_00122    | [MOCK THREAD] Unpopular opinion: fake topic #122 | Fan Theories                        | BIZ_2         |                          25 |
| CNT_00124    | [MOCK THREAD] Rant: fake topic #124              | Ask the Community                   | BIZ_2         |                          25 |
| CNT_00194    | [MOCK THREAD] Anyone else fake topic #194        | Book Club Chatter                   | BIZ_2         |                          25 |
| CNT_00024    | [MOCK THREAD] PSA: fake topic #24                | Ask the Community                   | BIZ_2         |                          24 |
| CNT_00037    | Episode 3: Totally Original Content (Mock #37)   | How-To Guides                       | BIZ_3         |                          24 |
| CNT_00042    | [MOCK THREAD] Unpopular opinion: fake topic #42  | Memes About Reading                 | BIZ_2         |                          24 |
| CNT_00052    | Episode 60: Totally Original Content (Mock #52)  | Serialized Drama                    | BIZ_3         |                          24 |
| CNT_00169    | The Last Recipe (Mock Book #169)                 | Fake History of Imaginary Countries | BIZ_1         |                          24 |
| CNT_00017    | The Fake Prairiefox (Mock Book #17)              | Self-Help                           | BIZ_1         |                          23 |
| CNT_00030    | Episode 89: Totally Original Content (Mock #30)  | Indie Fiction                       | BIZ_3         |                          23 |
| CNT_00070    | The Imaginary Algorithm (Mock Book #70)          | Romance                             | BIZ_1         |                          23 |
| CNT_00111    | Episode 3: Totally Original Content (Mock #111)  | Indie Fiction                       | BIZ_3         |                          23 |
| CNT_00150    | The Fake Dragon (Mock Book #150)                 | Fantasy                             | BIZ_1         |                          23 |
| CNT_00180    | Episode 43: Totally Original Content (Mock #180) | Definitely Not Fan Fiction          | BIZ_3         |                          23 |
| CNT_00190    | [MOCK THREAD] PSA: fake topic #190               | Book Club Chatter                   | BIZ_2         |                          23 |
| CNT_00220    | The Secret Diary (Mock Book #220)                | Self-Help                           | BIZ_1         |                          23 |
| CNT_00226    | Episode 53: Totally Original Content (Mock #226) | Indie Fiction                       | BIZ_3         |                          23 |

For full item coverage consult the attached certified item CSV. Do not report a top-25 table as an exhaustive catalog.

## Monthly verified activity

| month   |   platform_mau |   monthly_content_engaged_users |
|:--------|---------------:|--------------------------------:|
| 2021-04 |              1 |                               0 |
| 2021-05 |              1 |                               1 |
| 2021-09 |              3 |                               2 |
| 2021-10 |              1 |                               1 |
| 2021-11 |              1 |                               1 |
| 2022-01 |              3 |                               2 |
| 2022-02 |              1 |                               1 |
| 2022-03 |              3 |                               3 |
| 2022-04 |              2 |                               2 |
| 2022-05 |              1 |                               1 |
| 2022-06 |              4 |                               4 |
| 2022-07 |              9 |                               8 |
| 2022-08 |              6 |                               5 |
| 2022-09 |              5 |                               5 |
| 2022-10 |              7 |                               6 |
| 2022-11 |             14 |                              14 |
| 2022-12 |              8 |                               6 |
| 2023-01 |              8 |                               7 |
| 2023-02 |              4 |                               4 |
| 2023-03 |             12 |                              12 |
| 2023-04 |             12 |                              12 |
| 2023-05 |             16 |                              13 |
| 2023-06 |             13 |                              12 |
| 2023-07 |             25 |                              23 |
| 2023-08 |             22 |                              19 |
| 2023-09 |             20 |                              20 |
| 2023-10 |             22 |                              20 |
| 2023-11 |             30 |                              29 |
| 2023-12 |             24 |                              22 |
| 2024-01 |             30 |                              28 |
| 2024-02 |             27 |                              25 |
| 2024-03 |             35 |                              31 |
| 2024-04 |             30 |                              27 |
| 2024-05 |             35 |                              35 |
| 2024-06 |             41 |                              41 |
| 2024-07 |             32 |                              30 |
| 2024-08 |             44 |                              41 |
| 2024-09 |             34 |                              30 |
| 2024-10 |             50 |                              47 |
| 2024-11 |             54 |                              53 |
| 2024-12 |             55 |                              52 |
| 2025-01 |             65 |                              63 |
| 2025-02 |             65 |                              65 |
| 2025-03 |             74 |                              71 |
| 2025-04 |             74 |                              70 |
| 2025-05 |             92 |                              90 |
| 2025-06 |             94 |                              91 |
| 2025-07 |             90 |                              88 |
| 2025-08 |             85 |                              83 |
| 2025-09 |             96 |                              94 |
| 2025-10 |            124 |                             122 |
| 2025-11 |            136 |                             133 |
| 2025-12 |            153 |                             151 |
| 2026-01 |            147 |                             144 |
| 2026-02 |            160 |                             157 |
| 2026-03 |            214 |                             210 |
| 2026-04 |            220 |                             217 |
| 2026-05 |            249 |                             246 |
| 2026-06 |            290 |                             287 |
| 2026-07 |            352 |                             346 |
| 2026-08 |            401 |                             397 |
| 2026-09 |            359 |                             358 |
| 2026-10 |              3 |                               3 |

## Monthly category reach (complete reference for available months)

| month   | category                            |   category_unique_engaged_users |
|:--------|:------------------------------------|--------------------------------:|
| 2021-05 | Sci-Fi                              |                               1 |
| 2021-09 | Fantasy                             |                               1 |
| 2021-09 | Self-Help                           |                               1 |
| 2021-10 | Cooking                             |                               1 |
| 2021-11 | Self-Help                           |                               1 |
| 2022-01 | Fake History of Imaginary Countries |                               1 |
| 2022-01 | Sci-Fi                              |                               1 |
| 2022-02 | Fantasy                             |                               1 |
| 2022-03 | Book Club Chatter                   |                               1 |
| 2022-03 | Fake History of Imaginary Countries |                               1 |
| 2022-03 | Self-Help                           |                               1 |
| 2022-04 | Fake History of Imaginary Countries |                               1 |
| 2022-04 | General Nonsense                    |                               1 |
| 2022-05 | Fantasy                             |                               1 |
| 2022-06 | Book Club Chatter                   |                               1 |
| 2022-06 | Fake History of Imaginary Countries |                               2 |
| 2022-06 | Romance                             |                               1 |
| 2022-07 | Ask the Community                   |                               1 |
| 2022-07 | Fake History of Imaginary Countries |                               2 |
| 2022-07 | Fantasy                             |                               1 |
| 2022-07 | General Nonsense                    |                               2 |
| 2022-07 | Memes About Reading                 |                               1 |
| 2022-07 | Mystery                             |                               2 |
| 2022-08 | Ask the Community                   |                               2 |
| 2022-08 | Fantasy                             |                               1 |
| 2022-08 | Sci-Fi                              |                               1 |
| 2022-08 | Self-Help                           |                               1 |
| 2022-08 | Serialized Drama                    |                               2 |
| 2022-09 | Fantasy                             |                               1 |
| 2022-09 | Memes About Reading                 |                               1 |
| 2022-09 | Mystery                             |                               1 |
| 2022-09 | Self-Help                           |                               2 |
| 2022-10 | Cooking                             |                               1 |
| 2022-10 | Fan Theories                        |                               1 |
| 2022-10 | How-To Guides                       |                               1 |
| 2022-10 | Indie Fiction                       |                               1 |
| 2022-10 | Memes About Reading                 |                               1 |
| 2022-10 | Mystery                             |                               1 |
| 2022-11 | Ask the Community                   |                               2 |
| 2022-11 | Fake History of Imaginary Countries |                               3 |
| 2022-11 | Fantasy                             |                               1 |
| 2022-11 | How-To Guides                       |                               3 |
| 2022-11 | Memes About Reading                 |                               1 |
| 2022-11 | Mystery                             |                               2 |
| 2022-11 | Self-Help                           |                               2 |
| 2022-12 | Ask the Community                   |                               1 |
| 2022-12 | Book Club Chatter                   |                               1 |
| 2022-12 | Fake History of Imaginary Countries |                               1 |
| 2022-12 | Fantasy                             |                               2 |
| 2022-12 | Serialized Drama                    |                               1 |
| 2023-01 | Ask the Community                   |                               1 |
| 2023-01 | Cooking                             |                               1 |
| 2023-01 | Fake History of Imaginary Countries |                               2 |
| 2023-01 | Fan Theories                        |                               1 |
| 2023-01 | Fantasy                             |                               1 |
| 2023-01 | Sci-Fi                              |                               1 |
| 2023-02 | Fantasy                             |                               2 |
| 2023-02 | Memes About Reading                 |                               1 |
| 2023-02 | Self-Help                           |                               1 |
| 2023-03 | Ask the Community                   |                               1 |
| 2023-03 | Cooking                             |                               1 |
| 2023-03 | Fake History of Imaginary Countries |                               2 |
| 2023-03 | Fan Theories                        |                               1 |
| 2023-03 | Fantasy                             |                               1 |
| 2023-03 | Memes About Reading                 |                               1 |
| 2023-03 | Mystery                             |                               2 |
| 2023-03 | Self-Help                           |                               2 |
| 2023-03 | Serialized Drama                    |                               1 |
| 2023-04 | Ask the Community                   |                               1 |
| 2023-04 | Fake History of Imaginary Countries |                               1 |
| 2023-04 | Fan Theories                        |                               3 |
| 2023-04 | How-To Guides                       |                               1 |
| 2023-04 | Memes About Reading                 |                               2 |
| 2023-04 | Mystery                             |                               1 |
| 2023-04 | Self-Help                           |                               3 |
| 2023-05 | Ask the Community                   |                               2 |
| 2023-05 | Cooking                             |                               1 |
| 2023-05 | Fake History of Imaginary Countries |                               2 |
| 2023-05 | Fantasy                             |                               1 |
| 2023-05 | General Nonsense                    |                               1 |
| 2023-05 | How-To Guides                       |                               2 |
| 2023-05 | Indie Fiction                       |                               1 |
| 2023-05 | Memes About Reading                 |                               1 |
| 2023-05 | Mystery                             |                               1 |
| 2023-05 | Self-Help                           |                               1 |
| 2023-06 | Ask the Community                   |                               1 |
| 2023-06 | Fake History of Imaginary Countries |                               1 |
| 2023-06 | Fan Theories                        |                               3 |
| 2023-06 | Fantasy                             |                               1 |
| 2023-06 | General Nonsense                    |                               2 |
| 2023-06 | How-To Guides                       |                               1 |
| 2023-06 | Memes About Reading                 |                               1 |
| 2023-06 | Self-Help                           |                               1 |
| 2023-06 | Serialized Drama                    |                               2 |
| 2023-07 | Ask the Community                   |                               2 |
| 2023-07 | Book Club Chatter                   |                               1 |
| 2023-07 | Cooking                             |                               2 |
| 2023-07 | Definitely Not Fan Fiction          |                               2 |
| 2023-07 | Fake History of Imaginary Countries |                               1 |
| 2023-07 | Fan Theories                        |                               2 |
| 2023-07 | Fantasy                             |                               4 |
| 2023-07 | General Nonsense                    |                               4 |
| 2023-07 | How-To Guides                       |                               1 |
| 2023-07 | Mystery                             |                               3 |
| 2023-07 | Romance                             |                               1 |
| 2023-08 | Ask the Community                   |                               2 |
| 2023-08 | Book Club Chatter                   |                               1 |
| 2023-08 | Cooking                             |                               1 |
| 2023-08 | Definitely Not Fan Fiction          |                               1 |
| 2023-08 | Fake History of Imaginary Countries |                               1 |
| 2023-08 | Fan Theories                        |                               4 |
| 2023-08 | Fantasy                             |                               2 |
| 2023-08 | General Nonsense                    |                               2 |
| 2023-08 | Indie Fiction                       |                               1 |
| 2023-08 | Memes About Reading                 |                               1 |
| 2023-08 | Sci-Fi                              |                               2 |
| 2023-08 | Self-Help                           |                               2 |
| 2023-09 | Ask the Community                   |                               3 |
| 2023-09 | Book Club Chatter                   |                               1 |
| 2023-09 | Cooking                             |                               1 |
| 2023-09 | Fake History of Imaginary Countries |                               2 |
| 2023-09 | Fan Theories                        |                               1 |
| 2023-09 | Fantasy                             |                               2 |
| 2023-09 | General Nonsense                    |                               1 |
| 2023-09 | Indie Fiction                       |                               1 |
| 2023-09 | Memes About Reading                 |                               2 |
| 2023-09 | Mystery                             |                               1 |
| 2023-09 | Poetry (Bad)                        |                               1 |
| 2023-09 | Romance                             |                               1 |
| 2023-09 | Sci-Fi                              |                               1 |
| 2023-09 | Self-Help                           |                               1 |
| 2023-09 | Serialized Drama                    |                               2 |
| 2023-10 | Ask the Community                   |                               2 |
| 2023-10 | Book Club Chatter                   |                               2 |
| 2023-10 | Cooking                             |                               1 |
| 2023-10 | Fan Theories                        |                               1 |
| 2023-10 | Fantasy                             |                               3 |
| 2023-10 | General Nonsense                    |                               2 |
| 2023-10 | How-To Guides                       |                               2 |
| 2023-10 | Indie Fiction                       |                               1 |
| 2023-10 | Memes About Reading                 |                               1 |
| 2023-10 | Mystery                             |                               1 |
| 2023-10 | Romance                             |                               1 |
| 2023-10 | Self-Help                           |                               2 |
| 2023-10 | Serialized Drama                    |                               1 |
| 2023-11 | Ask the Community                   |                               4 |
| 2023-11 | Book Club Chatter                   |                               2 |
| 2023-11 | Fan Theories                        |                               2 |
| 2023-11 | Fantasy                             |                               3 |
| 2023-11 | General Nonsense                    |                               6 |
| 2023-11 | Indie Fiction                       |                               1 |
| 2023-11 | Memes About Reading                 |                               3 |
| 2023-11 | Mystery                             |                               3 |
| 2023-11 | Romance                             |                               2 |
| 2023-11 | Self-Help                           |                               3 |
| 2023-11 | Serialized Drama                    |                               2 |
| 2023-12 | Ask the Community                   |                               1 |
| 2023-12 | Cooking                             |                               1 |
| 2023-12 | Definitely Not Fan Fiction          |                               1 |
| 2023-12 | Fake History of Imaginary Countries |                               4 |
| 2023-12 | Fan Theories                        |                               1 |
| 2023-12 | Fantasy                             |                               1 |
| 2023-12 | General Nonsense                    |                               3 |
| 2023-12 | Indie Fiction                       |                               3 |
| 2023-12 | Memes About Reading                 |                               3 |
| 2023-12 | Mystery                             |                               1 |
| 2023-12 | Romance                             |                               1 |
| 2023-12 | Self-Help                           |                               1 |
| 2023-12 | Serialized Drama                    |                               1 |
| 2024-01 | Ask the Community                   |                               4 |
| 2024-01 | Book Club Chatter                   |                               3 |
| 2024-01 | Cooking                             |                               1 |
| 2024-01 | Fake History of Imaginary Countries |                               2 |
| 2024-01 | Fan Theories                        |                               2 |
| 2024-01 | Fantasy                             |                               3 |
| 2024-01 | General Nonsense                    |                               2 |
| 2024-01 | Memes About Reading                 |                               5 |
| 2024-01 | Poetry (Bad)                        |                               1 |
| 2024-01 | Romance                             |                               1 |
| 2024-01 | Sci-Fi                              |                               1 |
| 2024-01 | Self-Help                           |                               4 |
| 2024-02 | Ask the Community                   |                               3 |
| 2024-02 | Book Club Chatter                   |                               1 |
| 2024-02 | Cooking                             |                               2 |
| 2024-02 | Definitely Not Fan Fiction          |                               1 |
| 2024-02 | Fake History of Imaginary Countries |                               6 |
| 2024-02 | Fan Theories                        |                               3 |
| 2024-02 | General Nonsense                    |                               1 |
| 2024-02 | How-To Guides                       |                               1 |
| 2024-02 | Mystery                             |                               2 |
| 2024-02 | Romance                             |                               1 |
| 2024-02 | Self-Help                           |                               5 |
| 2024-03 | Book Club Chatter                   |                               8 |
| 2024-03 | Fake History of Imaginary Countries |                               2 |
| 2024-03 | Fan Theories                        |                               3 |
| 2024-03 | General Nonsense                    |                               2 |
| 2024-03 | How-To Guides                       |                               1 |
| 2024-03 | Indie Fiction                       |                               1 |
| 2024-03 | Memes About Reading                 |                               1 |
| 2024-03 | Mystery                             |                               5 |
| 2024-03 | Poetry (Bad)                        |                               2 |
| 2024-03 | Romance                             |                               2 |
| 2024-03 | Sci-Fi                              |                               2 |
| 2024-03 | Self-Help                           |                               3 |
| 2024-04 | Ask the Community                   |                               2 |
| 2024-04 | Book Club Chatter                   |                               2 |
| 2024-04 | Cooking                             |                               2 |
| 2024-04 | Definitely Not Fan Fiction          |                               2 |
| 2024-04 | Fake History of Imaginary Countries |                               3 |
| 2024-04 | Fan Theories                        |                               3 |
| 2024-04 | Fantasy                             |                               2 |
| 2024-04 | General Nonsense                    |                               2 |
| 2024-04 | Memes About Reading                 |                               1 |
| 2024-04 | Mystery                             |                               3 |
| 2024-04 | Poetry (Bad)                        |                               1 |
| 2024-04 | Self-Help                           |                               1 |
| 2024-04 | Serialized Drama                    |                               3 |
| 2024-05 | Ask the Community                   |                               2 |
| 2024-05 | Cooking                             |                               1 |
| 2024-05 | Definitely Not Fan Fiction          |                               3 |
| 2024-05 | Fake History of Imaginary Countries |                               3 |
| 2024-05 | Fan Theories                        |                               2 |
| 2024-05 | Fantasy                             |                               4 |
| 2024-05 | General Nonsense                    |                               3 |
| 2024-05 | How-To Guides                       |                               1 |
| 2024-05 | Indie Fiction                       |                               2 |
| 2024-05 | Memes About Reading                 |                               4 |
| 2024-05 | Mystery                             |                               4 |
| 2024-05 | Poetry (Bad)                        |                               3 |
| 2024-05 | Sci-Fi                              |                               1 |
| 2024-05 | Self-Help                           |                               2 |
| 2024-05 | Serialized Drama                    |                               1 |
| 2024-06 | Ask the Community                   |                               4 |
| 2024-06 | Definitely Not Fan Fiction          |                               1 |
| 2024-06 | Fake History of Imaginary Countries |                               2 |
| 2024-06 | Fan Theories                        |                               5 |
| 2024-06 | Fantasy                             |                               1 |
| 2024-06 | General Nonsense                    |                               6 |
| 2024-06 | How-To Guides                       |                               3 |
| 2024-06 | Indie Fiction                       |                               1 |
| 2024-06 | Memes About Reading                 |                               2 |
| 2024-06 | Mystery                             |                               3 |
| 2024-06 | Poetry (Bad)                        |                               1 |
| 2024-06 | Romance                             |                               2 |
| 2024-06 | Sci-Fi                              |                               5 |
| 2024-06 | Self-Help                           |                               4 |
| 2024-06 | Serialized Drama                    |                               2 |
| 2024-07 | Ask the Community                   |                               2 |
| 2024-07 | Book Club Chatter                   |                               2 |
| 2024-07 | Cooking                             |                               3 |
| 2024-07 | Definitely Not Fan Fiction          |                               1 |
| 2024-07 | Fake History of Imaginary Countries |                               4 |
| 2024-07 | Fan Theories                        |                               3 |
| 2024-07 | Fantasy                             |                               1 |
| 2024-07 | General Nonsense                    |                               1 |
| 2024-07 | How-To Guides                       |                               1 |
| 2024-07 | Indie Fiction                       |                               1 |
| 2024-07 | Mystery                             |                               1 |
| 2024-07 | Poetry (Bad)                        |                               1 |
| 2024-07 | Romance                             |                               2 |
| 2024-07 | Sci-Fi                              |                               1 |
| 2024-07 | Self-Help                           |                               5 |
| 2024-07 | Serialized Drama                    |                               1 |
| 2024-08 | Ask the Community                   |                               4 |
| 2024-08 | Book Club Chatter                   |                               2 |
| 2024-08 | Cooking                             |                               1 |
| 2024-08 | Definitely Not Fan Fiction          |                               2 |
| 2024-08 | Fake History of Imaginary Countries |                               3 |
| 2024-08 | Fan Theories                        |                               3 |
| 2024-08 | Fantasy                             |                               2 |
| 2024-08 | General Nonsense                    |                               4 |
| 2024-08 | Memes About Reading                 |                               6 |
| 2024-08 | Mystery                             |                               4 |
| 2024-08 | Romance                             |                               3 |
| 2024-08 | Sci-Fi                              |                               4 |
| 2024-08 | Self-Help                           |                               3 |
| 2024-08 | Serialized Drama                    |                               1 |
| 2024-09 | Ask the Community                   |                               2 |
| 2024-09 | Book Club Chatter                   |                               2 |
| 2024-09 | Definitely Not Fan Fiction          |                               1 |
| 2024-09 | Fake History of Imaginary Countries |                               3 |
| 2024-09 | Fan Theories                        |                               1 |
| 2024-09 | Fantasy                             |                               2 |
| 2024-09 | General Nonsense                    |                               3 |
| 2024-09 | How-To Guides                       |                               3 |
| 2024-09 | Indie Fiction                       |                               1 |
| 2024-09 | Memes About Reading                 |                               1 |
| 2024-09 | Mystery                             |                               5 |
| 2024-09 | Poetry (Bad)                        |                               1 |
| 2024-09 | Romance                             |                               2 |
| 2024-09 | Self-Help                           |                               3 |
| 2024-09 | Serialized Drama                    |                               1 |
| 2024-10 | Ask the Community                   |                               3 |
| 2024-10 | Book Club Chatter                   |                               4 |
| 2024-10 | Cooking                             |                               4 |
| 2024-10 | Definitely Not Fan Fiction          |                               1 |
| 2024-10 | Fake History of Imaginary Countries |                               4 |
| 2024-10 | Fan Theories                        |                               3 |
| 2024-10 | Fantasy                             |                               2 |
| 2024-10 | General Nonsense                    |                               5 |
| 2024-10 | How-To Guides                       |                               2 |
| 2024-10 | Indie Fiction                       |                               3 |
| 2024-10 | Memes About Reading                 |                               2 |
| 2024-10 | Poetry (Bad)                        |                               1 |
| 2024-10 | Sci-Fi                              |                               1 |
| 2024-10 | Self-Help                           |                               8 |
| 2024-10 | Serialized Drama                    |                               6 |
| 2024-11 | Ask the Community                   |                               2 |
| 2024-11 | Book Club Chatter                   |                               4 |
| 2024-11 | Cooking                             |                               2 |
| 2024-11 | Definitely Not Fan Fiction          |                               3 |
| 2024-11 | Fake History of Imaginary Countries |                               5 |
| 2024-11 | Fan Theories                        |                               5 |
| 2024-11 | Fantasy                             |                               5 |
| 2024-11 | General Nonsense                    |                               1 |
| 2024-11 | How-To Guides                       |                               2 |
| 2024-11 | Indie Fiction                       |                               6 |
| 2024-11 | Memes About Reading                 |                               5 |
| 2024-11 | Mystery                             |                               3 |
| 2024-11 | Romance                             |                               2 |
| 2024-11 | Sci-Fi                              |                               5 |
| 2024-11 | Self-Help                           |                               5 |
| 2024-11 | Serialized Drama                    |                               1 |
| 2024-12 | Ask the Community                   |                               7 |
| 2024-12 | Book Club Chatter                   |                               4 |
| 2024-12 | Definitely Not Fan Fiction          |                               4 |
| 2024-12 | Fake History of Imaginary Countries |                               2 |
| 2024-12 | Fan Theories                        |                               2 |
| 2024-12 | Fantasy                             |                               3 |
| 2024-12 | General Nonsense                    |                               4 |
| 2024-12 | How-To Guides                       |                               2 |
| 2024-12 | Indie Fiction                       |                               8 |
| 2024-12 | Memes About Reading                 |                               5 |
| 2024-12 | Mystery                             |                               2 |
| 2024-12 | Romance                             |                               2 |
| 2024-12 | Sci-Fi                              |                               2 |
| 2024-12 | Self-Help                           |                               4 |
| 2024-12 | Serialized Drama                    |                               3 |
| 2025-01 | Ask the Community                   |                               7 |
| 2025-01 | Book Club Chatter                   |                               4 |
| 2025-01 | Cooking                             |                               1 |
| 2025-01 | Definitely Not Fan Fiction          |                               1 |
| 2025-01 | Fake History of Imaginary Countries |                               6 |
| 2025-01 | Fan Theories                        |                               3 |
| 2025-01 | Fantasy                             |                               4 |
| 2025-01 | General Nonsense                    |                               5 |
| 2025-01 | How-To Guides                       |                               3 |
| 2025-01 | Indie Fiction                       |                              11 |
| 2025-01 | Memes About Reading                 |                               2 |
| 2025-01 | Mystery                             |                               2 |
| 2025-01 | Poetry (Bad)                        |                               3 |
| 2025-01 | Romance                             |                               3 |
| 2025-01 | Sci-Fi                              |                               5 |
| 2025-01 | Self-Help                           |                               6 |
| 2025-01 | Serialized Drama                    |                               2 |
| 2025-02 | Ask the Community                   |                              14 |
| 2025-02 | Book Club Chatter                   |                               1 |
| 2025-02 | Cooking                             |                               1 |
| 2025-02 | Definitely Not Fan Fiction          |                               3 |
| 2025-02 | Fake History of Imaginary Countries |                              11 |
| 2025-02 | Fan Theories                        |                               3 |
| 2025-02 | General Nonsense                    |                               3 |
| 2025-02 | How-To Guides                       |                               1 |
| 2025-02 | Indie Fiction                       |                               2 |
| 2025-02 | Memes About Reading                 |                               7 |
| 2025-02 | Mystery                             |                               6 |
| 2025-02 | Romance                             |                               5 |
| 2025-02 | Sci-Fi                              |                               2 |
| 2025-02 | Self-Help                           |                               6 |
| 2025-02 | Serialized Drama                    |                               2 |
| 2025-03 | Ask the Community                   |                               5 |
| 2025-03 | Book Club Chatter                   |                               4 |
| 2025-03 | Cooking                             |                               3 |
| 2025-03 | Definitely Not Fan Fiction          |                               1 |
| 2025-03 | Fake History of Imaginary Countries |                               5 |
| 2025-03 | Fan Theories                        |                               4 |
| 2025-03 | Fantasy                             |                               9 |
| 2025-03 | General Nonsense                    |                               2 |
| 2025-03 | How-To Guides                       |                               6 |
| 2025-03 | Indie Fiction                       |                               4 |
| 2025-03 | Memes About Reading                 |                               5 |
| 2025-03 | Mystery                             |                               4 |
| 2025-03 | Poetry (Bad)                        |                               1 |
| 2025-03 | Romance                             |                               3 |
| 2025-03 | Sci-Fi                              |                               5 |
| 2025-03 | Self-Help                           |                               8 |
| 2025-03 | Serialized Drama                    |                               3 |
| 2025-04 | Ask the Community                   |                              11 |
| 2025-04 | Book Club Chatter                   |                               6 |
| 2025-04 | Cooking                             |                               3 |
| 2025-04 | Definitely Not Fan Fiction          |                               1 |
| 2025-04 | Fake History of Imaginary Countries |                               5 |
| 2025-04 | Fan Theories                        |                               6 |
| 2025-04 | Fantasy                             |                               4 |
| 2025-04 | General Nonsense                    |                               8 |
| 2025-04 | How-To Guides                       |                               5 |
| 2025-04 | Indie Fiction                       |                               4 |
| 2025-04 | Memes About Reading                 |                               3 |
| 2025-04 | Mystery                             |                               4 |
| 2025-04 | Poetry (Bad)                        |                               1 |
| 2025-04 | Romance                             |                               2 |
| 2025-04 | Sci-Fi                              |                               2 |
| 2025-04 | Self-Help                           |                               4 |
| 2025-04 | Serialized Drama                    |                               7 |
| 2025-05 | Ask the Community                   |                              14 |
| 2025-05 | Book Club Chatter                   |                               2 |
| 2025-05 | Cooking                             |                               4 |
| 2025-05 | Definitely Not Fan Fiction          |                               7 |
| 2025-05 | Fake History of Imaginary Countries |                               9 |
| 2025-05 | Fan Theories                        |                               5 |
| 2025-05 | Fantasy                             |                               8 |
| 2025-05 | General Nonsense                    |                               3 |
| 2025-05 | How-To Guides                       |                               6 |
| 2025-05 | Indie Fiction                       |                               9 |
| 2025-05 | Memes About Reading                 |                               5 |
| 2025-05 | Mystery                             |                               6 |
| 2025-05 | Poetry (Bad)                        |                               5 |
| 2025-05 | Romance                             |                               4 |
| 2025-05 | Sci-Fi                              |                               6 |
| 2025-05 | Self-Help                           |                               5 |
| 2025-05 | Serialized Drama                    |                               6 |
| 2025-06 | Ask the Community                   |                              11 |
| 2025-06 | Book Club Chatter                   |                               1 |
| 2025-06 | Definitely Not Fan Fiction          |                               5 |
| 2025-06 | Fake History of Imaginary Countries |                               2 |
| 2025-06 | Fan Theories                        |                               6 |
| 2025-06 | Fantasy                             |                               3 |
| 2025-06 | General Nonsense                    |                               8 |
| 2025-06 | How-To Guides                       |                               7 |
| 2025-06 | Indie Fiction                       |                              11 |
| 2025-06 | Memes About Reading                 |                               7 |
| 2025-06 | Mystery                             |                              10 |
| 2025-06 | Poetry (Bad)                        |                               2 |
| 2025-06 | Romance                             |                               2 |
| 2025-06 | Sci-Fi                              |                               7 |
| 2025-06 | Self-Help                           |                               5 |
| 2025-06 | Serialized Drama                    |                              13 |
| 2025-07 | Ask the Community                   |                              11 |
| 2025-07 | Book Club Chatter                   |                               3 |
| 2025-07 | Cooking                             |                               3 |
| 2025-07 | Definitely Not Fan Fiction          |                               3 |
| 2025-07 | Fake History of Imaginary Countries |                               7 |
| 2025-07 | Fan Theories                        |                               6 |
| 2025-07 | Fantasy                             |                               5 |
| 2025-07 | General Nonsense                    |                               7 |
| 2025-07 | How-To Guides                       |                               4 |
| 2025-07 | Indie Fiction                       |                               5 |
| 2025-07 | Memes About Reading                 |                               6 |
| 2025-07 | Mystery                             |                               5 |
| 2025-07 | Poetry (Bad)                        |                               2 |
| 2025-07 | Romance                             |                               5 |
| 2025-07 | Sci-Fi                              |                               9 |
| 2025-07 | Self-Help                           |                               8 |
| 2025-07 | Serialized Drama                    |                               5 |
| 2025-08 | Ask the Community                   |                               9 |
| 2025-08 | Book Club Chatter                   |                               3 |
| 2025-08 | Cooking                             |                               4 |
| 2025-08 | Definitely Not Fan Fiction          |                               3 |
| 2025-08 | Fake History of Imaginary Countries |                               4 |
| 2025-08 | Fan Theories                        |                               9 |
| 2025-08 | Fantasy                             |                               7 |
| 2025-08 | General Nonsense                    |                               4 |
| 2025-08 | How-To Guides                       |                               5 |
| 2025-08 | Indie Fiction                       |                               5 |
| 2025-08 | Memes About Reading                 |                               8 |
| 2025-08 | Mystery                             |                               5 |
| 2025-08 | Poetry (Bad)                        |                               1 |
| 2025-08 | Romance                             |                               3 |
| 2025-08 | Sci-Fi                              |                               6 |
| 2025-08 | Self-Help                           |                               9 |
| 2025-08 | Serialized Drama                    |                               6 |
| 2025-09 | Ask the Community                   |                              10 |
| 2025-09 | Book Club Chatter                   |                               5 |
| 2025-09 | Cooking                             |                               3 |
| 2025-09 | Definitely Not Fan Fiction          |                               2 |
| 2025-09 | Fake History of Imaginary Countries |                               5 |
| 2025-09 | Fan Theories                        |                               5 |
| 2025-09 | Fantasy                             |                              12 |
| 2025-09 | General Nonsense                    |                               5 |
| 2025-09 | How-To Guides                       |                               8 |
| 2025-09 | Indie Fiction                       |                              11 |
| 2025-09 | Memes About Reading                 |                               4 |
| 2025-09 | Mystery                             |                               4 |
| 2025-09 | Poetry (Bad)                        |                               1 |
| 2025-09 | Romance                             |                               4 |
| 2025-09 | Sci-Fi                              |                               5 |
| 2025-09 | Self-Help                           |                              20 |
| 2025-09 | Serialized Drama                    |                               5 |
| 2025-10 | Ask the Community                   |                              16 |
| 2025-10 | Book Club Chatter                   |                               2 |
| 2025-10 | Cooking                             |                               7 |
| 2025-10 | Definitely Not Fan Fiction          |                              11 |
| 2025-10 | Fake History of Imaginary Countries |                              12 |
| 2025-10 | Fan Theories                        |                               4 |
| 2025-10 | Fantasy                             |                               8 |
| 2025-10 | General Nonsense                    |                               6 |
| 2025-10 | How-To Guides                       |                              14 |
| 2025-10 | Indie Fiction                       |                               8 |
| 2025-10 | Memes About Reading                 |                               7 |
| 2025-10 | Mystery                             |                               8 |
| 2025-10 | Poetry (Bad)                        |                               4 |
| 2025-10 | Romance                             |                               7 |
| 2025-10 | Sci-Fi                              |                               6 |
| 2025-10 | Self-Help                           |                               6 |
| 2025-10 | Serialized Drama                    |                               8 |
| 2025-11 | Ask the Community                   |                              17 |
| 2025-11 | Book Club Chatter                   |                               8 |
| 2025-11 | Cooking                             |                              10 |
| 2025-11 | Definitely Not Fan Fiction          |                               5 |
| 2025-11 | Fake History of Imaginary Countries |                               8 |
| 2025-11 | Fan Theories                        |                               8 |
| 2025-11 | Fantasy                             |                              12 |
| 2025-11 | General Nonsense                    |                              10 |
| 2025-11 | How-To Guides                       |                              14 |
| 2025-11 | Indie Fiction                       |                              12 |
| 2025-11 | Memes About Reading                 |                               3 |
| 2025-11 | Mystery                             |                               6 |
| 2025-11 | Poetry (Bad)                        |                               2 |
| 2025-11 | Romance                             |                               4 |
| 2025-11 | Sci-Fi                              |                               9 |
| 2025-11 | Self-Help                           |                               7 |
| 2025-11 | Serialized Drama                    |                              10 |
| 2025-12 | Ask the Community                   |                              10 |
| 2025-12 | Book Club Chatter                   |                               9 |
| 2025-12 | Cooking                             |                               5 |
| 2025-12 | Definitely Not Fan Fiction          |                              11 |
| 2025-12 | Fake History of Imaginary Countries |                              10 |
| 2025-12 | Fan Theories                        |                               8 |
| 2025-12 | Fantasy                             |                              14 |
| 2025-12 | General Nonsense                    |                              11 |
| 2025-12 | How-To Guides                       |                               9 |
| 2025-12 | Indie Fiction                       |                              17 |
| 2025-12 | Memes About Reading                 |                               6 |
| 2025-12 | Mystery                             |                              10 |
| 2025-12 | Poetry (Bad)                        |                               7 |
| 2025-12 | Romance                             |                               2 |
| 2025-12 | Sci-Fi                              |                               9 |
| 2025-12 | Self-Help                           |                              18 |
| 2025-12 | Serialized Drama                    |                              14 |
| 2026-01 | Ask the Community                   |                              25 |
| 2026-01 | Book Club Chatter                   |                               5 |
| 2026-01 | Cooking                             |                               4 |
| 2026-01 | Definitely Not Fan Fiction          |                               6 |
| 2026-01 | Fake History of Imaginary Countries |                              13 |
| 2026-01 | Fan Theories                        |                               7 |
| 2026-01 | Fantasy                             |                              14 |
| 2026-01 | General Nonsense                    |                              11 |
| 2026-01 | How-To Guides                       |                              10 |
| 2026-01 | Indie Fiction                       |                              14 |
| 2026-01 | Memes About Reading                 |                              10 |
| 2026-01 | Mystery                             |                               9 |
| 2026-01 | Poetry (Bad)                        |                               6 |
| 2026-01 | Romance                             |                               4 |
| 2026-01 | Sci-Fi                              |                               7 |
| 2026-01 | Self-Help                           |                              10 |
| 2026-01 | Serialized Drama                    |                              13 |
| 2026-02 | Ask the Community                   |                              11 |
| 2026-02 | Book Club Chatter                   |                              11 |
| 2026-02 | Cooking                             |                               5 |
| 2026-02 | Definitely Not Fan Fiction          |                               7 |
| 2026-02 | Fake History of Imaginary Countries |                              20 |
| 2026-02 | Fan Theories                        |                               8 |
| 2026-02 | Fantasy                             |                              15 |
| 2026-02 | General Nonsense                    |                              11 |
| 2026-02 | How-To Guides                       |                              13 |
| 2026-02 | Indie Fiction                       |                              18 |
| 2026-02 | Memes About Reading                 |                               8 |
| 2026-02 | Mystery                             |                               7 |
| 2026-02 | Poetry (Bad)                        |                               5 |
| 2026-02 | Romance                             |                               5 |
| 2026-02 | Sci-Fi                              |                              15 |
| 2026-02 | Self-Help                           |                              11 |
| 2026-02 | Serialized Drama                    |                              15 |
| 2026-03 | Ask the Community                   |                              14 |
| 2026-03 | Book Club Chatter                   |                              22 |
| 2026-03 | Cooking                             |                               5 |
| 2026-03 | Definitely Not Fan Fiction          |                              11 |
| 2026-03 | Fake History of Imaginary Countries |                              10 |
| 2026-03 | Fan Theories                        |                               5 |
| 2026-03 | Fantasy                             |                              23 |
| 2026-03 | General Nonsense                    |                              15 |
| 2026-03 | How-To Guides                       |                              23 |
| 2026-03 | Indie Fiction                       |                              29 |
| 2026-03 | Memes About Reading                 |                              16 |
| 2026-03 | Mystery                             |                               9 |
| 2026-03 | Poetry (Bad)                        |                              12 |
| 2026-03 | Romance                             |                               5 |
| 2026-03 | Sci-Fi                              |                               8 |
| 2026-03 | Self-Help                           |                              18 |
| 2026-03 | Serialized Drama                    |                              25 |
| 2026-04 | Ask the Community                   |                              21 |
| 2026-04 | Book Club Chatter                   |                              19 |
| 2026-04 | Cooking                             |                              12 |
| 2026-04 | Definitely Not Fan Fiction          |                              16 |
| 2026-04 | Fake History of Imaginary Countries |                              13 |
| 2026-04 | Fan Theories                        |                              10 |
| 2026-04 | Fantasy                             |                              12 |
| 2026-04 | General Nonsense                    |                              15 |
| 2026-04 | How-To Guides                       |                              22 |
| 2026-04 | Indie Fiction                       |                              28 |
| 2026-04 | Memes About Reading                 |                              13 |
| 2026-04 | Mystery                             |                               9 |
| 2026-04 | Poetry (Bad)                        |                              15 |
| 2026-04 | Romance                             |                               7 |
| 2026-04 | Sci-Fi                              |                              11 |
| 2026-04 | Self-Help                           |                              15 |
| 2026-04 | Serialized Drama                    |                              23 |
| 2026-05 | Ask the Community                   |                              21 |
| 2026-05 | Book Club Chatter                   |                              25 |
| 2026-05 | Cooking                             |                              14 |
| 2026-05 | Definitely Not Fan Fiction          |                              13 |
| 2026-05 | Fake History of Imaginary Countries |                              15 |
| 2026-05 | Fan Theories                        |                              10 |
| 2026-05 | Fantasy                             |                              17 |
| 2026-05 | General Nonsense                    |                               9 |
| 2026-05 | How-To Guides                       |                              18 |
| 2026-05 | Indie Fiction                       |                              39 |
| 2026-05 | Memes About Reading                 |                              21 |
| 2026-05 | Mystery                             |                               5 |
| 2026-05 | Poetry (Bad)                        |                              20 |
| 2026-05 | Romance                             |                              11 |
| 2026-05 | Sci-Fi                              |                              18 |
| 2026-05 | Self-Help                           |                              12 |
| 2026-05 | Serialized Drama                    |                              43 |
| 2026-06 | Ask the Community                   |                              26 |
| 2026-06 | Book Club Chatter                   |                              21 |
| 2026-06 | Cooking                             |                              12 |
| 2026-06 | Definitely Not Fan Fiction          |                              17 |
| 2026-06 | Fake History of Imaginary Countries |                              29 |
| 2026-06 | Fan Theories                        |                              14 |
| 2026-06 | Fantasy                             |                              17 |
| 2026-06 | General Nonsense                    |                              23 |
| 2026-06 | How-To Guides                       |                              20 |
| 2026-06 | Indie Fiction                       |                              42 |
| 2026-06 | Memes About Reading                 |                              23 |
| 2026-06 | Mystery                             |                              13 |
| 2026-06 | Poetry (Bad)                        |                              24 |
| 2026-06 | Romance                             |                              12 |
| 2026-06 | Sci-Fi                              |                              13 |
| 2026-06 | Self-Help                           |                              18 |
| 2026-06 | Serialized Drama                    |                              27 |
| 2026-07 | Ask the Community                   |                              40 |
| 2026-07 | Book Club Chatter                   |                              17 |
| 2026-07 | Cooking                             |                              13 |
| 2026-07 | Definitely Not Fan Fiction          |                              21 |
| 2026-07 | Fake History of Imaginary Countries |                              33 |
| 2026-07 | Fan Theories                        |                              17 |
| 2026-07 | Fantasy                             |                              29 |
| 2026-07 | General Nonsense                    |                              16 |
| 2026-07 | How-To Guides                       |                              40 |
| 2026-07 | Indie Fiction                       |                              61 |
| 2026-07 | Memes About Reading                 |                              28 |
| 2026-07 | Mystery                             |                              17 |
| 2026-07 | Poetry (Bad)                        |                              39 |
| 2026-07 | Romance                             |                              17 |
| 2026-07 | Sci-Fi                              |                              20 |
| 2026-07 | Self-Help                           |                              22 |
| 2026-07 | Serialized Drama                    |                              36 |
| 2026-08 | Ask the Community                   |                              34 |
| 2026-08 | Book Club Chatter                   |                              27 |
| 2026-08 | Cooking                             |                              13 |
| 2026-08 | Definitely Not Fan Fiction          |                              37 |
| 2026-08 | Fake History of Imaginary Countries |                              47 |
| 2026-08 | Fan Theories                        |                              23 |
| 2026-08 | Fantasy                             |                              26 |
| 2026-08 | General Nonsense                    |                              25 |
| 2026-08 | How-To Guides                       |                              46 |
| 2026-08 | Indie Fiction                       |                              72 |
| 2026-08 | Memes About Reading                 |                              29 |
| 2026-08 | Mystery                             |                              19 |
| 2026-08 | Poetry (Bad)                        |                              46 |
| 2026-08 | Romance                             |                              24 |
| 2026-08 | Sci-Fi                              |                              21 |
| 2026-08 | Self-Help                           |                              30 |
| 2026-08 | Serialized Drama                    |                              63 |
| 2026-09 | Ask the Community                   |                              28 |
| 2026-09 | Book Club Chatter                   |                              24 |
| 2026-09 | Cooking                             |                              11 |
| 2026-09 | Definitely Not Fan Fiction          |                              23 |
| 2026-09 | Fake History of Imaginary Countries |                              26 |
| 2026-09 | Fan Theories                        |                               5 |
| 2026-09 | Fantasy                             |                              21 |
| 2026-09 | General Nonsense                    |                              21 |
| 2026-09 | How-To Guides                       |                              55 |
| 2026-09 | Indie Fiction                       |                              53 |
| 2026-09 | Memes About Reading                 |                              20 |
| 2026-09 | Mystery                             |                              21 |
| 2026-09 | Poetry (Bad)                        |                              79 |
| 2026-09 | Romance                             |                               9 |
| 2026-09 | Sci-Fi                              |                              37 |
| 2026-09 | Self-Help                           |                              23 |
| 2026-09 | Serialized Drama                    |                              77 |
| 2026-10 | Cooking                             |                               1 |
| 2026-10 | Fantasy                             |                               1 |
| 2026-10 | Sci-Fi                              |                               1 |

## Quarterly signup counts (complete)

| quarter   |   new_users |
|:----------|------------:|
| 2021Q1    |          34 |
| 2021Q2    |          29 |
| 2021Q3    |          26 |
| 2021Q4    |          28 |
| 2022Q1    |          36 |
| 2022Q2    |          36 |
| 2022Q3    |          34 |
| 2022Q4    |          29 |
| 2023Q1    |          30 |
| 2023Q2    |          36 |
| 2023Q3    |          29 |
| 2023Q4    |          38 |
| 2024Q1    |          32 |
| 2024Q2    |          43 |
| 2024Q3    |          37 |
| 2024Q4    |          34 |
| 2025Q1    |          28 |
| 2025Q2    |          36 |
| 2025Q3    |          30 |
| 2025Q4    |          34 |
| 2026Q1    |          32 |
| 2026Q2    |          41 |
| 2026Q3    |          28 |

## Subscription status snapshot

| status   |   subscription_records |
|:---------|-----------------------:|
| active   |                    444 |
| canceled |                    212 |
| paused   |                     92 |
| trialing |                     37 |

## Active-status subscription records by business

| business_id   |   active_subscription_records | business_line             |
|:--------------|------------------------------:|:--------------------------|
| BIZ_1         |                           137 | premium_published_content |
| BIZ_2         |                           158 | consumer_community        |
| BIZ_3         |                           149 | creator_content           |

## Validation checklist
- Check population and time window before giving each numeric answer.
- If a user asks for arbitrary dates or groupings not available in this document, do not interpolate or invent. Execute the reproducible script against original source CSVs with appropriate filters if executable file-analysis tools and original files are available; otherwise say the exact cut is not precomputed.
- Compare all answers with these certified reference tables; state if data missing or metric unsupported.
- Apply exact date logic: Q1=Jan 1 through Mar 31 inclusive; computationally use [Jan 1, Apr 1). Previous calendar month is not rolling 30 days.
- For ambiguous questions, don't silently choose performance weights or proxy metrics.
