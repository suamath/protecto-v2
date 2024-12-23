import streamlit as st
from typing import Optional
from page.Scan import ScanPage
from page.Mask import MaskPage

VALID_PAGES = {"home", "scan_edit", "scan_progress", "mask"}
CSS = """
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
    .stApp {background-color: white;}
    .submenu {display: flex; gap: 10px; padding: 10px 0;}
"""

class ProtectoApp:
    def __init__(self):
        self._configure_page()
        self._init_session_state()

    def _configure_page(self) -> None:
        st.set_page_config(page_title="Protecto Vault", layout="wide")
        st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

    def _init_session_state(self) -> None:
        if 'page' not in st.session_state:
            st.session_state.page = "home"
        if 'show_scan_submenu' not in st.session_state:
            st.session_state.show_scan_submenu = False

    def _navigate_to(self, page: str, reset_submenu: bool = True) -> None:
        if page not in VALID_PAGES:
            st.error(f"Invalid page: {page}")
            return
        
        st.session_state.page = page
        st.session_state.current_page = page  # Add this line
        if reset_submenu:
            st.session_state.show_scan_submenu = False

    def show_sidebar(self) -> None:
        with st.sidebar:
            st.title("Navigation")
            
            if st.button("Home"):
                self._navigate_to("home")
            
            if st.button("Scan"):
                st.session_state.show_scan_submenu = True
            
            if st.session_state.show_scan_submenu:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Start Scan"):
                        self._navigate_to("scan_edit", reset_submenu=False)
                with col2:
                    if st.button("Scan Progress"):
                        self._navigate_to("scan_progress", reset_submenu=False)

            if st.button("Mask"):
                self._navigate_to("mask")

    def home(self) -> None:
        st.markdown("""<div style="margin-top: 20%;"></div>""", unsafe_allow_html=True)
        st.markdown(
            """<p style='text-align: center; color: grey; font-size: 1.5em; margin-bottom: 0;'>
            Make Your Enterprise Data</p>""", 
            unsafe_allow_html=True
        )
        st.markdown("""<div class="protecto-vault">Protecto Vault</div>""", unsafe_allow_html=True)
        st.markdown(
            """<h3 style='text-align: center; color: grey; font-size: 2.5em;'>
            Secure approach to data security and privacy</h3>""", 
            unsafe_allow_html=True
        )
        st.markdown(
            """<p style='text-align: center; color: black; font-size: 1.0em; margin-bottom: 65px;'>
            Protecto identifies and masks sensitive data while maintaining context and semantic meaning, 
            ensuring accuracy in your LLMs/Gen AI apps.</p>""", 
            unsafe_allow_html=True
        )

    def render_page(self) -> None:
        try:
            if st.session_state.page == "home":
                self.home()
            elif st.session_state.page == "scan_edit":
                ScanPage().show_start_scan()
            elif st.session_state.page == "scan_progress":
                ScanPage().show_scan_progress()
            elif st.session_state.page == "mask":
                MaskPage().show()
        except Exception as e:
            st.error(f"Error rendering page: {str(e)}")

    def run(self) -> None:
        self.show_sidebar()
        self.render_page()

if __name__ == "__main__":
    app = ProtectoApp()
    app.run()