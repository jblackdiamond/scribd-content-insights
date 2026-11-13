"""Scribd Content Insights: grounded conversational prototype using synthetic certified aggregates."""
from pathlib import Path
import re
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
st.set_page_config(page_title='Scribd Content Insights',page_icon='📚',layout='centered')
st.markdown('''<style>
.block-container{max-width:900px;padding-top:2rem}
[data-testid="stChatMessage"] {border:1px solid rgba(128,128,128,.16);border-radius:15px;padding:1rem}
</style>''',unsafe_allow_html=True)

@st.cache_data
def load():
    names=['monthly_metrics','category_metrics','category_by_month','item_reach','quarterly_signups',
           'subscription_status','active_subscriptions_by_business','catalog_creators']
    names += [f'subscription_starts_{g}' for g in ('year','quarter','month')]
    names += [f'subscription_starts_by_plan_{g}' for g in ('year','quarter','month')]
    names += [f'interactions_{g}' for g in ('year','quarter','month')]
    return {n:pd.read_csv(DATA/f'scribd_certified_{n}.csv') for n in names}
D=load()
MONTHS={m.lower():i for i,m in enumerate('January February March April May June July August September October November December'.split(),1)}
ACTIONS={'like':'likes','share':'shares','download':'downloads'}
QUALIFYING='content_open, content_complete, download, like, share, comment_post'

def period(q):
    """Returns an unambiguous supported time grain and a set of ordered keys."""
    x=q.lower()
    years=re.findall(r'\b20\d{2}\b',x)
    common_year=years[0] if len(set(years))==1 else None
    qs=[]
    for m in re.finditer(r'\b(20\d{2})\s*q([1-4])\b|\bq([1-4])\s*(20\d{2})?\b',x):
        year=m.group(1) or m.group(4) or common_year
        if year:
            key=f'{year}Q{m.group(2) or m.group(3)}'
            if key not in qs: qs.append(key)
    if qs:return 'quarter',qs
    ms=[]
    for m in re.finditer(r'\b20\d{2}[-/](?:0?[1-9]|1[0-2])\b',x):
        key=m.group().replace('/','-')
        y,mo=key.split('-');key=f'{y}-{int(mo):02d}'
        if key not in ms:ms.append(key)
    for name,num in MONTHS.items():
        for m in re.finditer(r'\b'+name+r'\b',x):
            local=re.search(r'\b20\d{2}\b',x[m.end():m.end()+14]);year=local.group() if local else common_year
            if year:
                key=f'{year}-{num:02d}'
                if key not in ms:ms.append(key)
    if ms:return 'month',ms
    if re.search(r'\blast year\b',x):return 'year',['2025']  # Demonstration current date: Nov 2026
    if len(years)==1:return 'year',[years[0]]
    if len(set(years))>1:return 'year',list(dict.fromkeys(years))
    return None,[]

def category_filter(q,options):
    x=q.lower()
    matches=[c for c in options if c.lower() in x or (c.lower().endswith('s') and c.lower()[:-1] in x)]
    return max(matches,key=len) if matches else None

def result(answer,explanation,detail,important=None,chart=None,table=None):
    return dict(answer=answer,explanation=explanation,detail=detail,important=important,chart=chart,table=table)

def refuse(reason,important=None,detail='Request not matched to a validated metric, dimension and period. No numerical result returned.'):
    return result(reason,'The assistant only returns numbers when the requested measure, breakdown, and time period match a certified reference.',detail,important)

def describe_period(grain,keys):
    return ', '.join(str(k) for k in keys)

def answer(q):
    x=q.lower().strip()
    grain,keys=period(q)
    dfc=D['catalog_creators'];cats=dfc.category.tolist()
    cat=category_filter(q,cats)
    if re.search(r'\bmrr\b|monthly recurring revenue|\barr\b|\brevenue\b',x):
        return refuse('I can’t certify recurring revenue from these data.','Anomalous prices and uncertain annual/lifetime billing semantics prevent a trustworthy MRR calculation.','MRR: WITHHELD. Prices include -$9.99 and $999.99; billing cycles and recognized revenue are not certified.')
    if 'completion rate' in x or 'finish rate' in x:
        return refuse('I can’t verify a completion rate.','Content-open tracking is inconsistent with completion events; the denominator is not reliable.','COMPLETION_RATE: WITHHELD. Source: engagement event audit.')
    if 'duration' in x or 'time spent' in x or ('how much time' in x and ('read' in x or 'listen' in x)):
        return refuse('Reading or listening time is not reliably measurable.','The session-duration field has not been validated as actual content-consumption time.','READING_TIME: WITHHELD. Do not sum session_duration_sec as consumption.')
    if 'acquisition channel' in x or 'marketing channel' in x:
        return refuse('An authoritative acquisition-channel ranking is not available.','Source channel values include unverified or test-like values.','ACQUISITION_CHANNEL: UNVERIFIED DIMENSION.')

    # INTERACTIONS: must resolve action, category dimension, and historical period before retrieving counts.
    asked_actions=[a for a in ACTIONS if re.search(r'\b'+a+r's?\b',x)]
    if asked_actions:
        if not grain or len(keys)!=1:
            return refuse('Please specify one calendar year, quarter, or month for likes, shares, or downloads.','For example: “How many likes did each category get in 2025?”')
        data=D[f'interactions_{grain}'];p=keys[0]
        if p not in data[grain].astype(str).values:
            return refuse(f'No certified interaction results are available for {p}.')
        subset=data.loc[(data[grain].astype(str)==p)&data.event_type.isin(asked_actions)].copy()
        if cat:subset=subset[subset.category.eq(cat)]
        if subset.empty:return refuse('No certified interaction rows matched that exact request.')
        # Populate zero-count categories for an all-category breakdown.
        if not cat:
            idx=pd.MultiIndex.from_product([cats,asked_actions],names=['category','event_type'])
            subset=subset.set_index(['category','event_type']).reindex(idx,fill_value=0).reset_index()
        wide=subset.pivot_table(index='category',columns='event_type',values='event_count',aggfunc='sum',fill_value=0).reindex(columns=asked_actions,fill_value=0)
        wide=wide.rename(columns=ACTIONS).astype(int)
        wide=wide.sort_values(list(wide.columns),ascending=False)
        totals=wide.sum()
        summary=', '.join(f'**{int(totals[ACTIONS[a]]):,} {ACTIONS[a]}**' for a in asked_actions)
        if cat:
            msg=f'For **{cat}** in **{p}**, there were {summary}.'
        else:
            msg=f'Across eligible content categories in **{p}**, there were {summary}. The breakdown by category is below.'
        return result(msg,'These are counts of recorded actions, not counts of unique people. An individual can generate more than one action. The requested period uses the event date.',f'Metrics: {", ".join(a.upper()+"_EVENTS" for a in asked_actions)}. Grain: {grain} × category × action type. Period: {p}. Source: scribd_certified_interactions_{grain}.csv. Filters: non-test users, non-test content, valid user/content joins, events on/after user signup. Event IDs counted distinctly; category is drawn from eligible content.', 'Action counts do not prove that someone read or listened to the content. Zero rows are filled from the eligible category catalog; event tracking completeness is not independently verified.',chart=wide,table=wide)

    # Subscription acquisition must precede snapshot routing: never answer historical starts with snapshot counts.
    if re.search(r'\bsubscription(s)?\b|\bsubscriber(s)?\b',x):
        new_requested=bool(re.search(r'\bnew\b|\bstart(?:ed|s|ing)?\b|\badded\b|\bacqui(?:red|sition)\b|\bjoin(?:ed)?\b',x))
        if new_requested or (grain is not None):
            if not grain or len(keys)!=1:
                return refuse('Which single year, quarter, or month should I use for new subscription starts?')
            p=keys[0]
            by_plan=bool(re.search(r'\bplan\b|\btier\b|\btype\b|\bbreakdown\b',x))
            d=D[f'subscription_starts_by_plan_{grain}' if by_plan else f'subscription_starts_{grain}']
            selected=d[d[grain].astype(str)==p]
            if selected.empty:return refuse(f'No certified subscription-start results are available for {p}.')
            if by_plan:
                display=selected[['plan_tier','subscription_starts','users_starting_subscriptions']].set_index('plan_tier').sort_values('subscription_starts',ascending=False)
                msg=f'**{p}** subscription starts by plan type are shown below. Across plans, distinct-user counts should not be summed to estimate unique subscribers.'
                chart=display[['subscription_starts']]
            else:
                starts=int(selected.iloc[0].subscription_starts);users=int(selected.iloc[0].users_starting_subscriptions)
                msg=f'In **{p}**, **{users:,} distinct users** started **{starts:,} subscription records**.'
                display=None;chart=None
            return result(msg,'A subscription start is identified using the subscription start date. A user starting multiple eligible subscriptions within the period counts once in the unique-user total.',f'Metrics: SUBSCRIPTION_STARTS and USERS_STARTING_SUBSCRIPTIONS. Grain: {grain}'+(' × plan tier.' if by_plan else '.')+f' Source: scribd_certified_subscription_starts{"_by_plan" if by_plan else ""}_{grain}.csv. Filters: remove test-user and TEST_STATUS_DO_NOT_USE records; count distinct subscription IDs and distinct user IDs. Date: start_date, period {p}.','These are starts, not necessarily first-ever subscribers, new paying customers, or subscriptions still active today. Free plans and trialing subscriptions are not silently removed.',chart=chart,table=display)
        if 'business' in x:
            d=D['active_subscriptions_by_business'].set_index('business_line')
            return result('Current active subscription **records** by business are shown below.','Counts represent the latest recorded status, not historical unique subscribers.','ACTIVE_SUBSCRIPTIONS_BY_BUSINESS; source: scribd_certified_active_subscriptions_by_business.csv; grain: subscription record × business line.','May include Free plans; active records are not synonymous with paying people.',chart=d[['active_subscription_records']],table=d[['active_subscription_records']])
        d=D['subscription_status'].set_index('status');active=int(d.loc['active','subscription_records'])
        return result(f'The latest snapshot contains **{active:,} active subscription records**.','A snapshot tells us what status is recorded at extraction time.','SUBSCRIPTION_STATUS_SNAPSHOT; grain: subscription record; source: scribd_certified_subscription_status.csv; excludes test users and TEST_STATUS_DO_NOT_USE.','Active subscription records are not necessarily unique paying subscribers; no historical status can be inferred.',chart=d[['subscription_records']],table=d[['subscription_records']])

    # CATALOG COUNTS and linked creator counts (snapshot only).
    if re.search(r'\bauthors?\b|\bcreators?\b',x) and (re.search(r'\bhow many\b|\bnumber of\b|\bdifferent\b',x)):
        if not cat:return refuse('Which catalog category would you like to count authors or creators for?')
        if grain:return refuse('Historical author counts are not certified. I can count linked creators in the current supplied catalog snapshot instead.')
        r=dfc.set_index('category').loc[cat]
        n=int(r.distinct_linked_creators);missing=int(r.missing_creator_links)
        return result(f'**{n:,} distinct known creators** are linked to eligible **{cat}** titles in the supplied catalog.','This counts distinct creator IDs associated with titles in the requested category. It does not count titles or assume every title has a known creator.',f'DISTINCT_LINKED_CREATORS; grain: category × creator_id. Source: scribd_certified_catalog_creators.csv, derived from eligible content. Excludes content_type=TEST_TYPE. Missing creator links: {missing:,} of {int(r.eligible_titles):,} eligible titles.','Some titles lack creator IDs. The source does not establish contributor roles, so “known creators” is more precise than “all authors”.')
    if re.search(r'\bhow many\b|\bnumber of\b|\bcount\b',x) and (re.search(r'\b(?:content|titles|items|books|dramas|library|catalog)\b',x)) and not re.search(r'\busers?\b|\bpeople\b|\bengaged\b',x):
        if grain:return refuse('This catalog metric reflects the supplied catalog snapshot, not a historical count as of a past date.')
        if cat:
            r=dfc.set_index('category').loc[cat];n=int(r.eligible_titles)
            return result(f'The supplied catalog contains **{n:,} eligible {cat} titles**.','Each eligible content ID is counted once in the category, including titles with no observed interactions.',f'CONTENT_CATALOG_COUNT; grain: distinct content_id within category. Source: scribd_certified_catalog_creators.csv. Filter: content_type != TEST_TYPE. Category: {cat}.','This is a supplied catalog snapshot, not necessarily a count of titles currently available to customers.')
        counts=dfc[['category','eligible_titles']].set_index('category').sort_values('eligible_titles',ascending=False)
        return result(f'The supplied catalog includes **{int(dfc.eligible_titles.sum()):,} eligible titles** across **{len(dfc)} categories**.','Each content ID is counted once, including titles with no measured engagement.','CONTENT_CATALOG_COUNT; distinct eligible content IDs, excluding TEST_TYPE; source scribd_certified_catalog_creators.csv.','Availability and publishing-state semantics are not established.',chart=counts,table=counts)

    # Account signups, distinct from subscription starts.
    if re.search(r'\bsign[ -]?ups?\b|\bnew (?:user|account)s?\b|\bregistrations?\b',x):
        qs=[]
        if grain=='quarter':qs=keys
        elif grain=='year':
            d=D['quarterly_signups'];qs=[str(q) for q in d.quarter if str(q)[:4] in keys]
        else:return refuse('Account signups are currently certified by calendar quarter or full year, not individual month.')
        if not qs:return refuse('No matching certified signup quarter exists.')
        d=D['quarterly_signups'].set_index('quarter');missing=[p for p in qs if p not in d.index]
        if missing:return refuse('One or more requested signup periods have no certified reference rows.')
        if grain=='year':
            total=sum(int(d.loc[v,'new_users']) for v in qs)
            return result(f'**{total:,} new user accounts** were registered in **{keys[0]}**.','Account registrations are counted from signup dates, not subscription start dates.','NEW_SIGNUPS; distinct non-test user IDs by signup quarter, summed for a complete year. Source: scribd_certified_quarterly_signups.csv.','A new user account is not necessarily a new paid subscriber.')
        vals=[int(d.loc[v,'new_users']) for v in qs]
        msg=', '.join(f'**{k}: {v:,} signups**' for k,v in zip(qs,vals))
        if len(qs)==2:
            delta=vals[1]-vals[0]
            msg+=f'. Change: **{delta:+,}** (**{delta/vals[0]*100:+.1f}%**).' if vals[0] else f'. Change: {delta:+,}; percentage undefined from zero.'
        return result(msg,'New non-test user accounts are grouped by calendar quarter based on signup date.','NEW_SIGNUPS; grain: signup quarter; source scribd_certified_quarterly_signups.csv; distinct user_id and test-user filter.','Account registrations do not imply paid subscription acquisition.')

    # Monthly activity: period must be months.
    if re.search(r'\bmau\b|monthly active|content.engaged users?|platform activ',x):
        if grain!='month':return refuse('Monthly activity is certified by calendar month. Please name the month and year.')
        d=D['monthly_metrics'].set_index('month')
        if any(k not in d.index for k in keys):return refuse('One or more requested months have no certified monthly activity data.')
        selected=d.loc[keys,['platform_mau','monthly_content_engaged_users']]
        if isinstance(selected,pd.Series): selected=selected.to_frame().T
        msg='; '.join(f'**{k}**: platform active **{int(d.loc[k,"platform_mau"]):,}**, content-engaged **{int(d.loc[k,"monthly_content_engaged_users"]):,}**' for k in keys)
        if len(keys)==2:
            old=int(d.loc[keys[0],'platform_mau']);new=int(d.loc[keys[1],'platform_mau'])
            if old:msg+=f'. Platform activity changed **{(new-old)/old*100:+.1f}%**.'
        return result(msg,'Platform activity includes approved platform actions; content-engaged users require qualifying interactions with eligible titles. Neither directly proves content was read or heard.','PLATFORM_MAU, MONTHLY_CONTENT_ENGAGED_USERS; grain: calendar month; sources: scribd_certified_monthly_metrics.csv; non-test users; eligible event definitions and lifecycle filtering.','October 2026 is unusually sparse and may reflect incomplete instrumentation or data coverage.',chart=selected)

    # Reach, not interchangeable with individual action counts.
    if re.search(r'\bcategory\b|\bcategories\b|\breach\b|\bperform\b|\bpopular\b',x):
        if re.search(r'\bauthors?\b|\bcreators?\b',x):return refuse('Author popularity is not yet a certified metric.','The source has incomplete creator associations, and “popular” needs a definition, such as unique audience reach. No author ranking is currently certified.')
        if grain=='year' or grain=='quarter':
            return refuse('Category reach for this period is not yet certified.','An all-history category figure must not be substituted for a year or quarter.','CATEGORY_REACH: available for all history or an individual certified calendar month, not this aggregation.')
        if grain=='month':
            if len(keys)!=1:return refuse('Please request one calendar month for category reach.')
            d=D['category_by_month'];sub=d[d.month.eq(keys[0])].sort_values('category_unique_engaged_users',ascending=False)
            if sub.empty:return refuse('No certified category reach results for that month.')
            if cat:
                selected=sub[sub.category.eq(cat)];val=int(selected.iloc[0].category_unique_engaged_users) if not selected.empty else 0
                msg=f'**{cat}** reached **{val:,} distinct engaged users** in **{keys[0]}**.'
            else:
                top=sub.iloc[0];msg=f'In **{keys[0]}**, **{top.category}** had the largest measured category audience: **{int(top.category_unique_engaged_users):,}** distinct engaged users.'
            display=sub[['category','category_unique_engaged_users']].set_index('category').head(15)
            return result(msg,'A person counts once per category in the selected month, even if they perform multiple qualifying actions.','CATEGORY_REACH; grain: category × month; source scribd_certified_category_by_month.csv; qualifying events: '+QUALIFYING+'; test/lifecycle filters applied.','Engagement is not confirmed consumption; category audiences overlap. October 2026 has suspiciously thin coverage.',chart=display,table=display)
        if grain:return refuse('That category-reach time interval is not available in the certified references.')
        d=D['category_metrics'].sort_values('category_unique_engaged_users',ascending=False)
        top=d.iloc[0];median=d.head(5).sort_values('median_item_reach',ascending=False).iloc[0]
        best=bool(re.search(r'\bbest\b|\bperform\b|\bpopular\b',x))
        if cat:
            r=d[d.category.eq(cat)].iloc[0];msg=f'Across all eligible history, **{cat}** reached **{int(r.category_unique_engaged_users):,} distinct engaged users**.'
        elif best:
            msg=f'It depends on how we define performance. **{top.category}** reached the most people (**{int(top.category_unique_engaged_users):,}**). Among the five largest categories by audience reach, **{median.category}** has the highest typical audience per title (median **{median.median_item_reach:g}** users).'
        else:
            msg=f'Across all eligible history, **{top.category}** reached the most people (**{int(top.category_unique_engaged_users):,}** distinct engaged users).'
        display=d[['category','category_unique_engaged_users']].set_index('category').head(12)
        return result(msg,'Category audience reach counts each person once per category. A title’s median audience is the middle value when titles are ordered by audience size; unlike a simple average, one runaway hit does not pull it upward. Titles with zero observed engagement are included.','CATEGORY_REACH and MEDIAN_ITEM_REACH; all-history source scribd_certified_category_metrics.csv; grains: category × unique user, then title × unique user before median within category. Qualifying events: '+QUALIFYING+'. Exclude test users and TEST_TYPE content, and events before signup.','This is not a universal ranking; larger catalogs have different opportunities to accumulate reach. Interactions are not verified reads or listens.',chart=display,table=display)

    if re.search(r'\bitem\b|\btitle\b|\bbook\b',x) and re.search(r'\btop\b|\bbest\b|\breach\b',x):
        if grain:return refuse('Time-bounded title reach is not certified in the available reference tables.')
        d=D['item_reach'].sort_values('item_unique_engaged_users',ascending=False);top=d.iloc[0]
        show=d[['title','item_unique_engaged_users']].head(10).set_index('title')
        return result(f'The title with highest all-history reach is **{top.title}** at **{int(top.item_unique_engaged_users):,} distinct engaged users**.','Each eligible user counts once per title, regardless of the number of recorded interactions.','ITEM_REACH; grain: unique users per title; source scribd_certified_item_reach.csv; all-history eligible event population.','All-history reach does not equal most read or most completed.',chart=show,table=show)

    return refuse('I can’t verify that exact question from the currently certified metrics.','I can explain what additional source fields or calculation would be needed, but I won’t substitute a different metric or time period.','No matching certified metric × dimension × period. No numeric result returned.')

def render(r):
    st.markdown(r['answer'])
    if r.get('chart') is not None:
        st.bar_chart(r['chart'],use_container_width=True)
    if r.get('table') is not None and len(r['table'])>1:
        with st.expander('View data table'):
            st.dataframe(r['table'],use_container_width=True)
    st.markdown('**What this means / How this is calculated**')
    st.write(r['explanation'])
    if r.get('important'):
        st.info('**Important to know**\n\n'+r['important'],icon='ℹ️')
    with st.expander('View technical details'):
        parts = [part.strip() for part in re.split(r';\s*|(?<=\.)\s+(?=[A-Z])', r['detail']) if part.strip()]
        for part in parts:
            st.markdown(f'- {part}')

st.title('📚 Scribd Content Insights')
st.caption('Conversational analytics prototype · synthetic exercise data · certified metric calculations')
with st.expander('About this prototype'):
    st.write('A deliberately constrained reference-backed analytics application. It interprets supported questions using validated rules and retrieves certified aggregates. It does **not** query a live warehouse or use a deployed LLM for interpretation. An LLM intent parser can be added later behind the same strict metric/period validation layer. No figures describe actual Scribd performance.')
examples=['Which category is performing best?','How did signups change from Q1 to Q2 2025?','How many new subscribers were added in 2025?','How many serialized dramas are in the content library?','How many different authors wrote serialized dramas?','How many likes did each category get in 2025?','Compare likes, shares, and downloads by category in 2025.','What is our monthly recurring revenue?']
with st.sidebar:
    st.header('Example questions')
    for i,example in enumerate(examples):
        if st.button(example,key=f'ex{i}',use_container_width=True):st.session_state.next_query=example
    st.divider();st.caption('Only synthetic, certified aggregates. No raw user records in this app.')
if 'messages' not in st.session_state:st.session_state.messages=[]
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        if msg['role']=='user':st.markdown(msg['question'])
        else:render(msg['result'])
q=st.chat_input('Ask a question about the data...') or st.session_state.pop('next_query',None)
if q:
    st.session_state.messages.append({'role':'user','question':q})
    st.session_state.messages.append({'role':'assistant','result':answer(q)})
    st.rerun()
