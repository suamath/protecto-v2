import streamlit as st
from typing import Optional
from page.scan_page import ScanPage
from page.scan_progress_view import ScanProgressView
from page.Mask import MaskPage
from protectoMethods import ProtectoAPI
from page.masking_configuration_page import MaskConfigPage

VALID_PAGES = {"home", "scan_edit", "scan_progress", "mask", "mask_config"}
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
        self.protecto_api = ProtectoAPI()
        self.scan_page = ScanPage()
        self.scan_progress = ScanProgressView(self.protecto_api)

    def _configure_page(self) -> None:
        st.set_page_config(page_title="Protecto Vault", layout="wide")
        st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

    def _init_session_state(self) -> None:
        if 'page' not in st.session_state:
            st.session_state.page = "home"
        if 'show_scan_submenu' not in st.session_state:
            st.session_state.show_scan_submenu = False
        if 'show_mask_submenu' not in st.session_state:
            st.session_state.show_mask_submenu = False

    def _navigate_to(self, page: str, reset_submenu: bool = True) -> None:
        if page not in VALID_PAGES:
            st.error(f"Invalid page: {page}")
            return
        
        st.session_state.page = page
        st.session_state.current_page = page
        if reset_submenu:
            st.session_state.show_scan_submenu = False
            st.session_state.show_mask_submenu = False

    def show_sidebar(self) -> None:
        with st.sidebar:
            st.title("Protecto")
            
            st.markdown("""
                <style>
                /* Main navigation buttons */
                div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] button[kind="secondary"] {
                    width: 100%;
                    padding: 0.75rem 1rem;
                    margin: 0.1rem 0;
                    border: 1px solid #ffffff30;
                    background-color: transparent;
                    color: white;
                    text-align: left !important;
                    font-size: 1.0em;
                    font-weight: 500;
                    transition: all 0.2s;
                }

                div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] button[kind="secondary"]:hover {
                    border-color: #ffffff80;
                    background-color: #ffffff20;
                }

                /* Submenu container */
                div[data-testid="stSidebar"] .submenu {
                    margin: -0.1rem 0 0.2rem 1.5rem !important;
                    padding: 0.05rem;
                    background: transparent;
                    border-left: 2px solid #ffffff30;
                }

                /* Submenu buttons general style */
                div[data-testid="stSidebar"] .submenu button[kind="secondary"] {
                    background-color: transparent !important;
                    font-size: 0.85rem !important;
                    padding: 0.3rem 0.75rem !important;
                    margin: 0.05rem 0 !important;
                    border: none !important;
                    color: #ffffffcc !important;
                    font-weight: 400 !important;
                    min-height: 20px !important;
                }

                /* Start Scan button specific */
                div[data-testid="stSidebar"] .submenu .start-scan button {
                    color: #4a90e2 !important;
                }

                div[data-testid="stSidebar"] .submenu .start-scan button:hover {
                    color: white !important;
                    background-color: #4a90e280 !important;
                }

                /* Scan Progress button specific */
                div[data-testid="stSidebar"] .submenu .scan-progress button {
                    color: #f0a500 !important;
                }

                div[data-testid="stSidebar"] .submenu .scan-progress button:hover {
                    color: white !important;
                    background-color: #f0a50080 !important;
                }

                /* Active states */
                div[data-testid="stSidebar"] .stButton.active > button {
                    border-left: 4px solid #ff4b4b !important;
                    background-color: #ffffff20 !important;
                    font-weight: 600 !important;
                }

                div[data-testid="stSidebar"] .submenu .start-scan.active button {
                    color: white !important;
                    background-color: #4a90e280 !important;
                }

                div[data-testid="stSidebar"] .submenu .scan-progress.active button {
                    color: white !important;
                    background-color: #f0a50080 !important;
                }

                /* Column spacing */
                div[data-testid="stSidebar"] .submenu [data-testid="column"] {
                    padding: 0 0.05rem !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
            home_active = "active" if st.session_state.page == "home" else ""
            scan_active = "active" if st.session_state.page in ["scan_edit", "scan_progress"] else ""
            mask_active = "active" if st.session_state.page in ["mask", "mask_config"] else ""
            
            self._render_nav_button("Home", home_active, "home")
            self._render_nav_button("Scan", scan_active, None, show_submenu=True, submenu_type="scan")
            
            if st.session_state.show_scan_submenu:
                self._render_scan_submenu()
            
            self._render_nav_button("Mask", mask_active, None, show_submenu=True, submenu_type="mask")
            
            if st.session_state.show_mask_submenu:
                self._render_mask_submenu()

    def _render_nav_button(self, text: str, active_class: str, page: Optional[str], show_submenu: bool = False, submenu_type: Optional[str] = None) -> None:
        st.markdown(f'<div class="stButton {active_class}">', unsafe_allow_html=True)
        if st.button(text, use_container_width=True):
            if show_submenu:
                if submenu_type == "scan":
                    st.session_state.show_scan_submenu = True
                    st.session_state.show_mask_submenu = False
                elif submenu_type == "mask":
                    st.session_state.show_mask_submenu = True
                    st.session_state.show_scan_submenu = False
            elif page:
                self._navigate_to(page)
        st.markdown('</div>', unsafe_allow_html=True)

    def _render_scan_submenu(self) -> None:
        with st.container():
            st.markdown('<div class="submenu">', unsafe_allow_html=True)
            st.markdown(
            """<p style='text-align: center; color: white; font-size: 1.0em; margin-bottom: 65px;'>
            Select the options</p>""", 
            unsafe_allow_html=True
            )
            col1, col2 = st.columns(2)
            
            with col1:
                start_scan_active = "active" if st.session_state.page == "scan_edit" else ""
                st.markdown(f'<div class="stButton start-scan {start_scan_active}">', unsafe_allow_html=True)
                if st.button("Start Scan", use_container_width=True):
                    self._navigate_to("scan_edit", reset_submenu=False)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                scan_progress_active = "active" if st.session_state.page == "scan_progress" else ""
                st.markdown(f'<div class="stButton scan-progress {scan_progress_active}">', unsafe_allow_html=True)
                if st.button("Scan Progress", use_container_width=True):
                    self._navigate_to("scan_progress", reset_submenu=False)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    def _render_mask_submenu(self) -> None:
        with st.container():
            st.markdown('<div class="submenu">', unsafe_allow_html=True)
            mask_config_active = "active" if st.session_state.page == "mask_config" else ""
            self._render_nav_button("Mask Configuration", mask_config_active, "mask_config", False)
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

    def clear_session_state(self, current: str) -> None:
        keys_to_clear = [key for key in st.session_state.keys() if key not in ['page', 'show_scan_submenu', 'show_mask_submenu']]
        for key in keys_to_clear:
            del st.session_state[key]

    def render_page(self) -> None:
        try:
            if st.session_state.page == "home":
                self.home()
            elif st.session_state.page == "scan_edit":
                self.scan_page.show_start_scan()
            elif st.session_state.page == "scan_progress":
                self.clear_session_state("scan_progress")
                st.session_state.page = "scan_progress"
                self.scan_progress.render()
            elif st.session_state.page == "mask":
                MaskPage().show()
            elif st.session_state.page == "mask_config":
                MaskConfigPage().show()
                st.title("Mask Configuration")
                # Add your mask configuration page content here
        except Exception as e:
            st.error(f"Error rendering page: {str(e)}")

    def run(self) -> None:
        self.show_sidebar()
        self.render_page()

if __name__ == "__main__":
    app = ProtectoApp()
    app.run()