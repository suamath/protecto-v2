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
    section[data-testid="stSidebar"] {
        background-color: #1e3d59 !important;
        padding: 2rem 1rem;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
        padding-bottom: 1rem;
        border-bottom: 1px solid #ffffff40;
        margin-bottom: 1rem;
        color: white;
    }
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
            st.title("Protecto")
            
            st.markdown("""
                <style>
                /* Main buttons styling */
                section[data-testid="stSidebar"] .stButton button {
                    width: 100%;
                    padding: 0.75rem 1rem;
                    margin: 0.25rem 0;
                    border: 1px solid #ffffff30;
                    background-color: transparent;
                    color: white;
                    text-align: left !important;
                    font-size: 1.1em;
                    transition: all 0.2s;
                }
                section[data-testid="stSidebar"] .stButton button:hover {
                    border-color: #ffffff80;
                    background-color: #ffffff20;
                }
                section[data-testid="stSidebar"] .stButton.active button {
                    background-color: #ffffff30;
                    border-left: 4px solid #ff4b4b;
                }
                
                /* Submenu container styling */
                section[data-testid="stSidebar"] .submenu {
                    margin: 0;
                    padding: 0.1rem 0 0.1rem 1.5rem;
                    border-left: 2px solid #ffffff30;
                    margin-left: 1rem;
                }
                
                /* Submenu buttons styling */
                section[data-testid="stSidebar"] .submenu .stButton button {
                    background-color: #ffffff10;
                    font-size: 0.85em;
                    padding: 0.35rem 0.75rem;
                    margin: 0.1rem 0;
                    min-height: 32px;
                    border-radius: 4px;
                    border: 1px solid #ffffff20;
                }
                
                section[data-testid="stSidebar"] .submenu .stButton.active button {
                    background-color: #ffffff25;
                    border-left: 2px solid #ff4b4b;
                    color: #ff4b4b;
                }
                
                /* Column container for submenu */
                section[data-testid="stSidebar"] .submenu [data-testid="column"] {
                    padding: 0 0.2rem;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Main navigation buttons with active state
            home_active = "active" if st.session_state.page == "home" else ""
            scan_active = "active" if st.session_state.page in ["scan_edit", "scan_progress"] else ""
            mask_active = "active" if st.session_state.page == "mask" else ""
            
            st.markdown(f'<div class="stButton {home_active}">', unsafe_allow_html=True)
            if st.button("Home", use_container_width=True):
                self._navigate_to("home")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="stButton {scan_active}">', unsafe_allow_html=True)
            if st.button("Scan", use_container_width=True):
                st.session_state.show_scan_submenu = True
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Scan submenu
            if st.session_state.show_scan_submenu:
                with st.container():
                    st.markdown('<div class="submenu">', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        start_scan_active = "active" if st.session_state.page == "scan_edit" else ""
                        st.markdown(f'<div class="stButton {start_scan_active}">', unsafe_allow_html=True)
                        if st.button("Start Scan", use_container_width=True):
                            self._navigate_to("scan_edit", reset_submenu=False)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        scan_progress_active = "active" if st.session_state.page == "scan_progress" else ""
                        st.markdown(f'<div class="stButton {scan_progress_active}">', unsafe_allow_html=True)
                        if st.button("Scan Progress", use_container_width=True):
                            self._navigate_to("scan_progress", reset_submenu=False)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="stButton {mask_active}">', unsafe_allow_html=True)
            if st.button("Mask", use_container_width=True):
                self._navigate_to("mask")
            st.markdown('</div>', unsafe_allow_html=True)

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