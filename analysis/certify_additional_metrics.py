"""Rebuild additional certified aggregate CSVs from the six original synthetic exercise tables.
Run: python scripts/certify_additional_metrics.py /path/to/original/csv/directory
No user-level raw data is included in the public Streamlit app repository.
"""
from pathlib import Path
import sys
import pandas as pd

INPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
OUT = Path(__file__).resolve().parents[1] / 'data'
OUT.mkdir(parents=True, exist_ok=True)
def read(prefix):
    matches = list(INPUT.glob(prefix+'*.csv'))
    if len(matches)!=1: raise RuntimeError(f'Expected one source table for {prefix}, got {len(matches)}')
    return pd.read_csv(matches[0])
u=read('Exesrcise_users').copy()
c=read('Exercise_content_items').copy()
e=read('Exercise_engagement_events').copy()
s=read('Exercise_subscriptions').copy()
creators=read('Exercise_creators').copy()
assert not u.groupby('user_id')['is_test_account_flag'].nunique().gt(1).any()
assert not c.content_id.duplicated().any()
assert not s.subscription_id.duplicated().any()
assert not e.event_id.duplicated().any()
u=u.drop_duplicates('user_id')
u['signup_date']=pd.to_datetime(u.signup_date,errors='raise')
e['event_timestamp']=pd.to_datetime(e.event_timestamp,errors='raise')
s['start_date']=pd.to_datetime(s.start_date,errors='raise')
users=u.loc[~u.is_test_account_flag]
content=c.loc[c.content_type.ne('TEST_TYPE')].copy()
assert len(content)==292
assert not content.creator_id.dropna().isin(creators.creator_id).eq(False).any()

catalog=content.groupby('category',as_index=False).agg(eligible_titles=('content_id','nunique'),known_creator_links=('creator_id',lambda x:x.notna().sum()),distinct_linked_creators=('creator_id','nunique'))
catalog['missing_creator_links']=catalog['eligible_titles']-catalog['known_creator_links']
catalog=catalog.sort_values('category')
catalog.to_csv(OUT/'scribd_certified_catalog_creators.csv',index=False)

subs=s.merge(u[['user_id','is_test_account_flag']],on='user_id',how='left',validate='many_to_one')
assert subs.is_test_account_flag.notna().all()
subs=subs.loc[(~subs.is_test_account_flag)&(subs.status!='TEST_STATUS_DO_NOT_USE')].copy()
subs['year']=subs.start_date.dt.year
subs['month']=subs.start_date.dt.strftime('%Y-%m')
subs['quarter']=subs.start_date.dt.to_period('Q').astype(str)
# "New subscriber" is defined here as distinct users who started at least one eligible subscription in period.
# No inference about first-ever status or paid-only conversions.
for grain in ('year','quarter','month'):
    d=subs.groupby(grain,as_index=False).agg(subscription_starts=('subscription_id','nunique'),users_starting_subscriptions=('user_id','nunique'))
    d.to_csv(OUT/f'scribd_certified_subscription_starts_{grain}.csv',index=False)
    d2=subs.groupby([grain,'plan_tier'],as_index=False).agg(subscription_starts=('subscription_id','nunique'),users_starting_subscriptions=('user_id','nunique'))
    d2.to_csv(OUT/f'scribd_certified_subscription_starts_by_plan_{grain}.csv',index=False)

events=e.loc[e.event_type.isin(['like','share','download'])].merge(users[['user_id','signup_date']],on='user_id',how='inner',validate='many_to_one').merge(content[['content_id','category']],on='content_id',how='inner',validate='many_to_one')
events=events.loc[events.event_timestamp.dt.normalize().ge(events.signup_date.dt.normalize())].copy()
events['year']=events.event_timestamp.dt.year
events['month']=events.event_timestamp.dt.strftime('%Y-%m')
events['quarter']=events.event_timestamp.dt.to_period('Q').astype(str)
for grain in ('year','quarter','month'):
    out=events.groupby([grain,'category','event_type'],as_index=False).agg(event_count=('event_id','nunique'))
    out.to_csv(OUT/f'scribd_certified_interactions_{grain}.csv',index=False)

# Cross-check original certified lifecycle population on all six event types.
all_events=e.loc[e.event_type.isin(['content_open','content_complete','download','share','comment_post','like'])].merge(users[['user_id','signup_date']],on='user_id',how='inner',validate='many_to_one').merge(content[['content_id']],on='content_id',how='inner',validate='many_to_one')
all_events=all_events.loc[all_events.event_timestamp.dt.normalize().ge(all_events.signup_date.dt.normalize())]
assert len(all_events)==5163, f'Expected 5,163 certified eligible content events, got {len(all_events)}'
assert int(pd.read_csv(OUT/'scribd_certified_category_metrics.csv').category_unique_engaged_users.max())==359
print('Verified clean events:',len(all_events))
print('Catalog entries:',len(content),'linked creator titles:',content.creator_id.notna().sum())
print('2025 subscription starts:',subs.loc[subs.year.eq(2025)].subscription_id.nunique(), 'users starting:',subs.loc[subs.year.eq(2025)].user_id.nunique())
print('2025 interactions:',events.loc[events.year.eq(2025)].event_type.value_counts().to_dict())
