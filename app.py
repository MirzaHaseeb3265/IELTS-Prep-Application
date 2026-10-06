import streamlit as st
from datetime import datetime
from services.reading import get_reading_test, score_reading
from services.storage import init_db, save_attempt, get_history

st.set_page_config(page_title='IELTS Practice Lab', page_icon='📘', layout='wide')
init_db()

st.title('📘 IELTS Academic Practice Lab')
st.caption('Independent IELTS-style practice. Not affiliated with IELTS, Cambridge, British Council, or IDP.')

page = st.sidebar.radio('Go to', ['Dashboard','Reading Mock','Writing','Listening'])

if page == 'Dashboard':
    st.subheader('Your practice dashboard')
    hist = get_history()
    c1,c2,c3 = st.columns(3)
    c1.metric('Tests completed', len(hist))
    c2.metric('Best Reading estimate', max([x['band'] for x in hist], default='—'))
    c3.metric('Latest Reading estimate', hist[-1]['band'] if hist else '—')
    if hist:
        st.dataframe(hist, use_container_width=True)
    st.info('Start with Reading Mock. Writing and Listening are scaffolded for the next build phase.')

elif page == 'Reading Mock':
    st.subheader('IELTS Academic Reading — Practice Mock')
    st.warning('Practice estimate only. Generated/practice material is not an official IELTS test.')
    test = get_reading_test()
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    for pidx, passage in enumerate(test['passages'], 1):
        st.markdown(f"### Passage {pidx}: {passage['title']}")
        st.write(passage['text'])
        st.markdown('#### Questions')
        for q in passage['questions']:
            key = f"q_{q['id']}"
            if q['type'] == 'tfng':
                st.session_state.answers[q['id']] = st.radio(q['prompt'], ['—','TRUE','FALSE','NOT GIVEN'], key=key)
            elif q['type'] == 'mcq':
                st.session_state.answers[q['id']] = st.radio(q['prompt'], ['—'] + q['options'], key=key)
            else:
                st.session_state.answers[q['id']] = st.text_input(q['prompt'], key=key)
    if st.button('Submit Reading Test', type='primary'):
        result = score_reading(test, st.session_state.answers)
        save_attempt(datetime.now().isoformat(timespec='seconds'), result['raw'], result['total'], result['band'])
        st.success(f"Score: {result['raw']}/{result['total']} — Estimated Reading Band: {result['band']}")
        st.progress(result['raw']/result['total'])
        st.markdown('### Review')
        for r in result['review']:
            icon = '✅' if r['correct'] else '❌'
            st.write(f"{icon} Q{r['id']} — Your answer: **{r['user']}** | Correct: **{r['answer']}**")
            if not r['correct']:
                st.caption(r['explanation'])

elif page == 'Writing':
    st.subheader('Writing — next phase')
    st.info('This section is scaffolded. Next we will add Task 1 visuals, Task 2 prompts, timed writing, and criterion-based AI feedback.')

else:
    st.subheader('Listening — next phase')
    st.info('This section is scaffolded. Next we will add validated scripts, TTS audio, 40-question tests, and automatic scoring.')
