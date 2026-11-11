"""Scribd Content Insights: reference-driven demo, synthetic interview data."""
import os
import re
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
DATA = ROOT / "data"
st.set_page_config(page_title="Scribd Content Insights", page_icon="📚", layout="centered")

@st.cache_data
def load():
    names = ["monthly_metrics", "category_metrics", "category_by_month", "item_reach", "quarterly_signups", "subscription_status", "active_subscriptions_by_business"]
    return {n: pd.read_csv(DATA / f"scribd_certified_{n}.csv") for n in names}

D = load()

# The language model is never asked to calculate numerical answers. It may only
# select a limited, explicitly allowed intent, which is independently validated.
INTENTS = ["category_best", "category_reach", "category_month", "signups_quarter", "monthly_activity", "subscription_status", "business_subscriptions", "item_reach", "mrr", "completion", "duration", "acquisition", "unknown"]

def classify(q):
    """Optional LLM classification; deterministic fallback on missing credentials/errors."""
    api_key = None
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        pass
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI
            out = OpenAI(api_key=api_key, timeout=10).responses.create(
                model="gpt-4.1-mini",
                instructions=("Select exactly one intent for this analytics question. Do not answer or calculate. "
                              f"Allowed intents: {', '.join(INTENTS)}. "
                              "Prefer unknown if out of scope; output only the intent ID."),
                input=q,
                max_output_tokens=32,
            )
            choice = out.output_text.strip().lower()
            if choice in INTENTS:
                return choice, "LLM-classified"
        except Exception:
            pass
    x=q.lower()
    if re.search(r'\bmrr\b|monthly recurring revenue|revenue|arr\b', x): return "mrr", "rules"
    if 'completion' in x or 'finish rate' in x: return "completion", "rules"
    if 'time' in x and ('read' in x or 'listen' in x or 'spend' in x) or 'duration' in x: return "duration", "rules"
    if 'acquisition' in x or 'marketing channel' in x: return "acquisition", "rules"
    if 'signup' in x or 'sign-up' in x or 'new user' in x: return "signups_quarter", "rules"
    if 'mau' in x or 'monthly active' in x or 'engaged user' in x and ('month' in x or 'august' in x or 'september' in x): return "monthly_activity", "rules"
    if 'subscription' in x or 'subscriber' in x: return "business_subscriptions" if 'business' in x else "subscription_status", "rules"
    if 'title' in x or 'item' in x or 'book' in x: return "item_reach", "rules"
    if 'category' in x or 'categories' in x:
        if 'month' in x or any(m in x for m in ['january','february','march','april','may','june','july','august','september','october','november','december']) or re.search(r'20\d\d[-/]\d\d',x): return "category_month", "rules"
        return ("category_best" if 'best' in x or 'perform' in x or 'top' in x else "category_reach"), "rules"
    return "unknown", "rules"

MONTHS = {m.lower():i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
def months_in_question(q):
    q=q.lower()
    months=re.findall(r'20\d{2}[-/](?:0[1-9]|1[0-2])',q)
    for name,i in MONTHS.items():
        for m in re.finditer(r'\b'+name+r'\b', q):
            y=re.search(r'\b20\d\d\b',q[m.end():m.end()+12])
            if y: months.append(f'{y.group()}-{i:02d}')
    return list(dict.fromkeys(m.replace('/','-') for m in months))

def quarters_in_question(q):
    return list(dict.fromkeys(re.findall(r'\b(?:20\d{2}Q[1-4]|Q[1-4]\s*20\d{2})\b',q.upper())))

def answer(q, intent):
    x=q.lower()
    if intent == 'mrr':
        return dict(answer="I can't certify monthly recurring revenue from these records.", explanation="Prices include anomalous values (-$9.99 and $999.99), and annual/lifetime billing semantics are unresolved. Repairing them silently would manufacture a financial metric.", detail="Metric: MRR; certification status: withheld; source: audit and metric contract.")
    if intent == 'completion':
        return dict(answer="A trustworthy completion rate isn't available.", explanation="The content-open coverage is inconsistent with completion events, so a completion-rate denominator cannot be defended.", detail="Completion rate: not certified. Requires instrumentation audit.")
    if intent == 'duration':
        return dict(answer="These data don't reliably measure time spent reading or listening.", explanation="The session-duration field is not validated as content-consumption time.", detail="Consumption duration: unsupported. Do not sum raw session durations.")
    if intent == 'acquisition':
        return dict(answer="I wouldn't rank acquisition channels from these data yet.", explanation="Channel values are unverified. Users remain in overall population counts, but attribution claims are not certified.", detail="Acquisition channel: unverified dimension.")
    if intent in ['category_best','category_reach']:
        df=D['category_metrics'].sort_values('category_unique_engaged_users',ascending=False)
        top=df.iloc[0]
        leaders=df.head(5).sort_values('median_item_reach',ascending=False)
        median=leaders.iloc[0]
        if intent=='category_best':
            msg=f"It depends on the definition of performance. **{top.category}** leads total category reach (**{int(top.category_unique_engaged_users):,}** distinct engaged users). Among the five highest-reach categories, **{median.category}** has the highest median reach per title (**{median.median_item_reach:g}** users)."
        else:
            msg=f"Across the certified all-history window, **{top.category}** has the highest category reach: **{int(top.category_unique_engaged_users):,}** distinct engaged users."
        return dict(answer=msg, explanation="Category reach counts distinct eligible users who engaged with content in a category. Median item reach measures the typical title within a category. These are different measures; no universal 'best' score is defined.", detail="CATEGORY_REACH and MEDIAN_ITEM_REACH; all-history certified category_metrics.csv; eligible content events and titles only.", chart=df.head(10)[['category','category_unique_engaged_users']].set_index('category'))
    if intent=='category_month':
        months=months_in_question(q)
        if len(months)!=1: return dict(answer="Please specify a single calendar month and year, for example September 2026.", explanation="Only certified month-by-category results are available for monthly category reach.",detail="CATEGORY_REACH; grain: month × category.")
        df=D['category_by_month']; frame=df[df.month==months[0]].sort_values('category_unique_engaged_users',ascending=False)
        if frame.empty: return dict(answer=f"No certified category data available for {months[0]}.",explanation="I won't infer a value outside the reference rows.",detail="Certified month × category reference.")
        best=frame.iloc[0]
        return dict(answer=f"In **{months[0]}**, **{best.category}** leads monthly category reach with **{int(best.category_unique_engaged_users):,}** engaged users.",explanation="Distinct eligible engaged users within that category and calendar month. Monthly categories may overlap across users.", detail=f"CATEGORY_REACH; source category_by_month.csv; month={months[0]}; October 2026 coverage should be treated with caution.",chart=frame.head(10)[['category','category_unique_engaged_users']].set_index('category'))
    if intent=='signups_quarter':
        qs=quarters_in_question(q)
        if not qs and 'q1' in x and 'q2' in x:
            years=re.findall(r'20\d{2}',x)
            if len(years)==1: qs=[years[0]+'Q1',years[0]+'Q2']
        qs=[re.sub(r'^(Q[1-4])\s*(20\d{2})$',lambda m:m.group(2)+m.group(1),v) for v in qs]
        if not qs: return dict(answer="Which quarter(s) and year should I compare? For example, Q1 vs Q2 2025.",explanation="Signups are certified by calendar quarter.",detail="NEW_SIGNUPS; quarterly_signups.csv.")
        df=D['quarterly_signups'].set_index('quarter')
        if len(qs)==1: qs=qs[:1]
        if any(v not in df.index for v in qs): return dict(answer="At least one requested quarter has no certified result.",explanation="I won't extrapolate beyond the reporting window.",detail="NEW_SIGNUPS; quarterly_signups.csv.")
        vals=[int(df.loc[v,'new_users']) for v in qs]
        msg=', '.join(f"**{v}: {n:,}**" for v,n in zip(qs,vals))
        if len(qs)==2:
            delta=vals[1]-vals[0]; pct=100*delta/vals[0] if vals[0] else None
            msg+=f". Change: **{delta:+,}** signups (**{pct:+.1f}%**)." if pct is not None else f". Change: {delta:+,}; percentage undefined (zero baseline)."
        return dict(answer=msg,explanation="New user records by calendar quarter, under the certified eligibility rules.",detail="NEW_SIGNUPS; grain: calendar quarter; source quarterly_signups.csv.")
    if intent=='monthly_activity':
        ms=months_in_question(q)
        if not ms and 'august' in x and 'september' in x and '2026' in x: ms=['2026-08','2026-09']
        if not ms: return dict(answer="Which month(s) would you like? Try August and September 2026.",explanation="Only certified calendar-month results are supported.",detail="PLATFORM_MAU, MONTHLY_CONTENT_ENGAGED_USERS; monthly_metrics.csv.")
        df=D['monthly_metrics'].set_index('month')
        if any(m not in df.index for m in ms): return dict(answer="No certified data for one or more requested months.",explanation="I won't invent missing month values.",detail="monthly_metrics.csv")
        lines=[f"**{m}**: platform MAU **{int(df.loc[m,'platform_mau']):,}**; content-engaged users **{int(df.loc[m,'monthly_content_engaged_users']):,}**." for m in ms]
        if len(ms)==2:
            old=int(df.loc[ms[0],'platform_mau']); new=int(df.loc[ms[1],'platform_mau'])
            lines.append(f"Platform MAU changed **{(new-old)/old*100:+.1f}%**." if old else "MAU percentage change is undefined from zero.")
        return dict(answer='  \n'.join(lines),explanation="MAU counts users active on the platform; content-engaged users require eligible content interactions. These groups are not identical. October 2026 has coverage caveats.",detail="PLATFORM_MAU and MONTHLY_CONTENT_ENGAGED_USERS; month-grain; source monthly_metrics.csv.",chart=df.loc[ms,['platform_mau','monthly_content_engaged_users']])
    if intent=='subscription_status':
        df=D['subscription_status'].set_index('status')
        active=int(df.loc['active','subscription_records'])
        return dict(answer=f"The snapshot has **{active:,} active subscription records**. This is not necessarily the count of distinct paying subscribers.",explanation="Snapshot status describes records at extraction time, not historical status or recognized recurring revenue.",detail="SUBSCRIPTION_STATUS_SNAPSHOT; source subscription_status.csv; grain: subscription record.",chart=df)
    if intent=='business_subscriptions':
        df=D['active_subscriptions_by_business'].set_index('business_line')
        return dict(answer="Active subscription *records* by business line: "+', '.join(f"**{i}** {int(v):,}" for i,v in df.active_subscription_records.items())+'.',explanation="Current snapshot, not historical unique paid users.",detail="ACTIVE_SUBSCRIPTIONS_BY_BUSINESS; source active_subscriptions_by_business.csv.",chart=df[['active_subscription_records']])
    if intent=='item_reach':
        df=D['item_reach'].sort_values('item_unique_engaged_users',ascending=False)
        top=df.iloc[0]
        return dict(answer=f"Highest certified all-history item reach is **{int(top.item_unique_engaged_users)}** users for **{top.title}** (ID: {top.content_id}).",explanation="Distinct eligible users engaging with an eligible title. This is not completion or reading time.",detail="ITEM_REACH; source item_reach.csv; all-history certified population.",chart=df.head(10)[['title','item_unique_engaged_users']].set_index('title'))
    return dict(answer="I can't verify that question from the currently certified reference tables.",explanation="Try a category-reach, quarterly-signups, monthly-activity, item-reach or subscription-snapshot question. Unsupported filters require a new certified calculation.",detail="No certified metric/source row matched the request. No numerical result generated.")

st.title("📚 Scribd Content Insights")
st.caption("Conversational analytics prototype · synthetic exercise data · verified reference tables")
with st.expander("What this prototype does (and doesn't do)"):
    st.write("Questions map to approved metrics; numbers come from certified CSV lookups and deterministic arithmetic. Optional LLM use is limited to intent selection. This is not a live warehouse, an enforced semantic API, or a claim about Scribd's real business performance.")
examples=["Which category is performing best?","How did signups change from Q1 to Q2 2025?","How did platform MAU compare with content-engaged users in August and September 2026?","What's our monthly recurring revenue?","How many people engaged with each category in September 2026?"]
with st.sidebar:
    st.header("Try a question")
    for ex in examples:
        if st.button(ex,use_container_width=True): st.session_state.next_query=ex
    st.divider()
    st.caption("Every figure comes from synthetic certified exercise data. Do not use for real business decisions.")
if 'messages' not in st.session_state: st.session_state.messages=[]
for m in st.session_state.messages:
    with st.chat_message(m['role']):
        st.markdown(m['text'])
        if 'result' in m:
            res=m['result']
            st.markdown('**What this means / How this is calculated**')
            st.write(res['explanation'])
            if 'chart' in res: st.bar_chart(res['chart'])
            with st.expander("Technical details"):
                st.write(res['detail'])
            st.caption(f"Routing: {m['routing']} · Synthetic certified references")
entered=st.chat_input("Ask a question about the data...")
q=entered or st.session_state.pop('next_query',None)
if q:
    st.session_state.messages.append({'role':'user','text':q})
    intent,route=classify(q)
    res=answer(q,intent)
    st.session_state.messages.append({'role':'assistant','text':res['answer'],'result':res,'routing':f'{route} → {intent}'})
    st.rerun()
