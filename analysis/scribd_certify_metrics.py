"""Rebuild self-service reference answers from original Scribd synthetic CSVs.
Run in directory alongside original source files: python scribd_certify_metrics.py
No LLM is used for calculating any reported metrics.
"""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent
read=lambda pat: pd.read_csv(next(ROOT.glob(pat)))
users=read('Exesrcise_users*csv'); content=read('Exercise_content_items*csv'); events=read('Exercise_engagement_events*csv'); subs=read('Exercise_subscriptions*csv'); biz=read('Exercise_Businesses*csv')
assert not users.loc[users.duplicated('user_id',keep=False)].groupby('user_id').apply(lambda a:len(a.drop_duplicates())==1,include_groups=False).eq(False).any()
users=users.drop_duplicates('user_id').copy(); users['signup_date']=pd.to_datetime(users.signup_date)
users=users.loc[users.is_test_account_flag.eq(False)].copy()
assert content.content_id.is_unique and events.event_id.is_unique
eligible_content=content.loc[content.content_type.ne('TEST_TYPE')].copy()
events['event_timestamp']=pd.to_datetime(events.event_timestamp)
content_actions=['content_open','content_complete','download','like','share','comment_post']
base=events.merge(users[['user_id','signup_date']],how='inner',on='user_id',validate='many_to_one')
base=base.loc[base.event_timestamp>=base.signup_date].copy()
content_events=base.loc[base.event_type.isin(content_actions)].merge(eligible_content[['content_id','category','title','business_id']],on='content_id',how='inner',validate='many_to_one')
all_content=content_events.content_id.nunique()
monthly_content=content_events.assign(month=content_events.event_timestamp.dt.to_period('M').astype(str)).groupby('month').user_id.nunique().rename('monthly_content_engaged_users')
platform=base.loc[base.event_type.isin(content_actions+['search_query','page_view'])].copy()
platform=platform.loc[~platform.event_type.isin(content_actions)|platform.content_id.isin(eligible_content.content_id)].copy()
monthly_platform=platform.assign(month=platform.event_timestamp.dt.to_period('M').astype(str)).groupby('month').user_id.nunique().rename('platform_mau')
monthly=pd.concat([monthly_platform,monthly_content],axis=1).fillna(0).astype(int).reset_index()
assert (monthly.monthly_content_engaged_users<=monthly.platform_mau).all()
monthly.to_csv(ROOT/'scribd_certified_monthly_metrics.csv',index=False)
by_category=content_events.groupby('category').user_id.nunique().rename('category_unique_engaged_users').reset_index()
by_item=content_events.groupby('content_id').user_id.nunique().rename('item_unique_engaged_users').reset_index()
items=eligible_content[['content_id','title','category','business_id']].merge(by_item,on='content_id',how='left',validate='one_to_one')
items.item_unique_engaged_users=items.item_unique_engaged_users.fillna(0).astype(int)
items.sort_values(['item_unique_engaged_users','content_id'],ascending=[False,True]).to_csv(ROOT/'scribd_certified_item_reach.csv',index=False)
category_stats=items.groupby('category').agg(eligible_titles=('content_id','size'),median_item_reach=('item_unique_engaged_users','median'),min_item_reach=('item_unique_engaged_users','min'),max_item_reach=('item_unique_engaged_users','max')).reset_index()
cat=by_category.merge(category_stats,on='category',how='right',validate='one_to_one').fillna({'category_unique_engaged_users':0})
cat.category_unique_engaged_users=cat.category_unique_engaged_users.astype(int)
cat=cat.sort_values('category_unique_engaged_users',ascending=False)
cat.to_csv(ROOT/'scribd_certified_category_metrics.csv',index=False)
# Date-bounded content category metrics, for a limited library of precomputed reference answers.
content_events['month']=content_events.event_timestamp.dt.to_period('M').astype(str)
cat_month=content_events.groupby(['month','category']).user_id.nunique().rename('category_unique_engaged_users').reset_index()
cat_month.to_csv(ROOT/'scribd_certified_category_by_month.csv',index=False)
# User signups and snapshot statuses.
users['quarter']=users.signup_date.dt.to_period('Q').astype(str)
signups=users.groupby('quarter').user_id.nunique().rename('new_users').reset_index()
signups.to_csv(ROOT/'scribd_certified_quarterly_signups.csv',index=False)
subscriptions=subs.merge(users[['user_id']],on='user_id',how='inner',validate='many_to_one')
subscriptions=subscriptions.loc[subscriptions.status.ne('TEST_STATUS_DO_NOT_USE')]
statuses=subscriptions.groupby('status').size().rename('subscription_records').reset_index()
statuses.to_csv(ROOT/'scribd_certified_subscription_status.csv',index=False)
activebiz=subscriptions.loc[subscriptions.status.eq('active')].groupby('business_id').size().rename('active_subscription_records').reset_index().merge(biz[['business_id','business_line']],on='business_id',validate='one_to_one')
activebiz.to_csv(ROOT/'scribd_certified_active_subscriptions_by_business.csv',index=False)
assert len(users)==760 and len(eligible_content)==292 and len(subscriptions)==785
assert monthly.set_index('month').loc['2026-08','platform_mau']==401
assert monthly.set_index('month').loc['2026-09','platform_mau']==359
assert statuses.set_index('status').loc['active','subscription_records']==444
print('Harmonized eligible content events:',len(content_events),'unique content-engaged users:',content_events.user_id.nunique())
print('Category rankings:\n',cat.head(6).to_string(index=False))
print('Monthly samples:\n',monthly.loc[monthly.month.isin(['2026-07','2026-08','2026-09','2026-10'])].to_string(index=False))
print('2025 quarters:\n',signups.loc[signups.quarter.str.startswith('2025')].to_string(index=False))
print('Top item reach:\n',items.sort_values('item_unique_engaged_users',ascending=False).head(3).to_string(index=False))
print('Subscription active counts:\n',activebiz.to_string(index=False))
