import pandas as pd
import streamlit as st
def select_col(x):
    cbg = 'background-color: blue; color:blue'
    c2 = ''
    #compare columns
    maskbg = x['YN'] == "Yes"
    df1 =  pd.DataFrame(c2, index=x.index, columns=x.columns)
    #modify values of df1 column by boolean mask
    df1.loc[maskbg, 'command'] = cbg
    return df1
def change():
    for index, updates in st.session_state.data_edited['edited_rows'].items():
        for column, new_value in updates.items():
            st.session_state.df.at[index, column] = new_value
    for  row in  st.session_state.df.iterrows():
        print(row)
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        [
            {"command": "st.selectbox", "rating": 7, "is_widget": True, "YN": "Yes"},
            {"command": "st.balloons", "rating": 5, "is_widget": False, "YN": "Yes"},
            {"command": "st.time_input", "rating": 3, "is_widget": True, "YN": "No"},
        ]
    )
st.session_state.styled_df = st.session_state.df.style.apply(select_col, axis=None)
edited_df = st.data_editor(
    st.session_state.styled_df,
    column_config={
        "command": "Streamlit Command",
        "rating": st.column_config.NumberColumn(
            "Your rating",
            help="How much do you like this command (1-5)?",
            min_value=1,
            max_value=15,
            step=1,
            format="%d ⭐"
        ),
        "is_widget": "Widget ?",
        "YN":st.column_config.SelectboxColumn(
            "Status",
            help="The category of the app",
            width="medium",
            options=[
                        "Yes",
                        "No"
            ],
            required=True,
        )
    },
    disabled=["command"],
    hide_index=True,
    on_change=change,
    key="data_edited"
)
