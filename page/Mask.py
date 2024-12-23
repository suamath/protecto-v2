import streamlit as st

class MaskPage:
    def __init__(self):
        self.mask_options = ["Option 1", "Option 2", "Option 3"]
    
    def apply_mask(self):
        st.info("Applying mask...")
        st.success("Mask applied successfully!")
    
    def show(self):
        st.title("Mask Operation")
        selected_mask = st.selectbox("Select Mask Type", self.mask_options)
        if st.button("Apply Mask", use_container_width=True):
            self.apply_mask()

if __name__ == "__main__":
    mask_page = MaskPage()
    mask_page.show()