import streamlit as st
from pages.Scan import ScanPage
from pages.Mask import MaskPage

# Must be the first Streamlit command
st.set_page_config(
    page_title="Protecto Vault",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .protecto-vault {
        text-align: center;
        font-size: 4em;
        font-weight: bold;
        color: #333;
        margin: 0;
        padding: 0;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Additional styling if needed */
    .stApp {
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)

def home():
    # Add vertical spacing at the top
    st.markdown("""
        <div style="margin-top: 20%;">
        </div>
    """, unsafe_allow_html=True)
    
    # Main content
    st.markdown("""<p style='text-align: center; color: grey; font-size: 1.5em; margin-bottom: 0; '>Make Your Enterprise Data</p>""", unsafe_allow_html=True)
    st.markdown("""<div class="protecto-vault">Protecto Vault</div>""", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: grey; font-size: 2.5em;'>Secure approach to data security and privacy</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: black; font-size: 1.0em;  margin-bottom: 65px;'>Protecto identifies and masks sensitive data while maintaining context and semantic meaning, ensuring accuracy in your LLMs/Gen AI apps.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    home()