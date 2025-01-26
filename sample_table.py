import streamlit as st
import pandas as pd

st.cache_data.clear()

data = {
    'field': ['name', 'email', 'phone', 'address'],
    'to_be_masked': ['Yes', 'No', 'Yes', 'No'],
    'type': ['String', 'String', 'Number', 'String']
}

df = pd.DataFrame(data)

def highlight_mask_status(val):
    if val == 'name' or val == 'phone':
        return 'background-color: #90EE90'
    return 'background-color: #FFB6C6'
        
styled = df.style.applymap(highlight_mask_status, subset=pd.IndexSlice[:, ['field']])

if st.button('Refresh Colors'):
    st.session_state.refresh = True

st.dataframe(
    styled,
    use_container_width=True,
    hide_index=True
)