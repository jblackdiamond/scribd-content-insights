"""Run without installing Streamlit: python scripts/test_routing.py"""
from pathlib import Path
import sys,types

m=types.ModuleType('streamlit')
m.set_page_config=lambda **kw:None
m.markdown=lambda *a,**kw:None
m.cache_data=lambda f:f
sys.modules['streamlit']=m
script=Path(__file__).resolve().parent/'app.py'
source=script.read_text().split("st.title('📚 Scribd Content Insights')")[0]
ctx={'__file__':str(script)}
exec(compile(source,str(script),'exec'),ctx)
answer=ctx['answer']
tests={
'How did signups change from Q1 to Q2 2025?':['28','36','+28.6%'],
'Which category is performing best?':['Indie Fiction','359','Ask the Community'],
'How many new subscribers were added in 2025?':['206','232'],
'How many serialized dramas are in the content library?':['Serialized Drama','eligible'],
'How many different authors wrote serialized dramas?':['distinct known creators'],
'How many likes did each category of content get in 2025?':['123 likes'],
'Compare likes, shares, and downloads by category in 2025.':['123 likes','104 shares','142 downloads'],
'How many likes did each category of content get in 2024?':['likes'],
'How many subscriptions are active now?':['444'],
'How many new users registered in 2025?':['new user accounts'],
'Which author was the most popular last year?':['not yet a certified metric'],
'How many likes did each category get?':['Please specify'],
'What is our MRR?':["can’t reliably calculate"],
'How many likes did each category get in 2028?':['No certified'],
}
for question,expectations in tests.items():
    r=answer(question)
    for e in expectations:
        assert e.lower() in r['answer'].lower(),(question,e,r['answer'])
    print('PASS',question,'->',r['answer'][:110])
print('Passed',len(tests),'scenario checks.')
