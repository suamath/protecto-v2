import streamlit as st
import pandas as pd
from protectoMethods import ProtectoAPI

class MaskProgressPage:
    def __init__(self):
        self.protecto_api = ProtectoAPI()
        
    def create_progress_table(self):
        # Get mask progress data from API
        progress_data = self.protecto_api.get_mask_progress()
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(progress_data)
        
        # Rename columns to match requirements
        df = df.rename(columns={
            'object_name': 'Object',
            'criteria': 'Criteria',
            'status': 'Status',
            'total_no_of_rows_approved_for_masking': 'Total no.of rows to be masked',
            'total_masked_value': 'masked',
            'last_updated_time': 'Last Approved Time'  # Changed to match the actual data field
        })
        
        # Select and reorder columns
        df = df[['Object', 'Criteria', 'Status', 'Total no.of rows to be masked', 'masked', 'Last Approved Time']]
        
        # Convert last_updated_time to datetime
        df['Last Approved Time'] = pd.to_datetime(df['Last Approved Time'])
        
        # Custom styling for the Status column
        def style_status(status):
            if status == 'Success':
                return 'background-color: #90EE90'  # Light green
            elif status == 'Failed':
                return 'background-color: #FFB6C1'  # Light red
            return 'background-color: #87CEEB'  # Light blue for in progress
        
        # Apply styling
        styled_df = df.style.apply(lambda x: [style_status(val) if i == 2 else '' 
                                            for i, val in enumerate(x)], axis=1)
        
        # Configure column properties
        column_config = {
            "Object": st.column_config.TextColumn(
                "Object",
                width="small"
            ),
            "Criteria": st.column_config.TextColumn(
                "Criteria",
                width="large"
            ),
            "Status": st.column_config.TextColumn(
                "Status",
                width="small"
            ),
            "Total no.of rows to be masked": st.column_config.NumberColumn(
                "Total no.of rows to be masked",
                width="small",
                format="%d"
            ),
            "masked": st.column_config.NumberColumn(
                "masked",
                width="small",
                format="%d"
            ),
            "Last Approved Time": st.column_config.DatetimeColumn(
                "Last Approved Time",
                width="medium",
                format="DD-MM-YYYY HH:mm"  # Updated format to match the data
            )
        }
        
        return df, column_config
    
    def show(self):
        st.title("Mask Progress")
        
        # Create and display the progress table
        df, column_config = self.create_progress_table()
        
        # Display the table with configuration
        st.dataframe(
            df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True
        )

if __name__ == "__main__":
    mask_page = MaskProgressPage()
    mask_page.show()