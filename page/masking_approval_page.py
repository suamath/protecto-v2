import streamlit as st
import pandas as pd
from protectoMethods import ProtectoAPI

class MaskingApprovalPage:
    def __init__(self):
        self.protecto_api = ProtectoAPI()
        if 'selected_object' not in st.session_state:
            st.session_state.selected_object = None
        if 'is_approved' not in st.session_state:
            st.session_state.is_approved = False
            
    def handle_save(self, object_name, edited_df):
        # Identify records marked for no_mask
        no_mask_records = edited_df[edited_df['is_masked'] == 'no_mask']['Id'].tolist()
        if no_mask_records:
            result = self.protecto_api.update_no_mask_for_record(object_name, no_mask_records)
            st.success(result['message'])
            return result
        else:
            st.warning("No records marked for no_mask")
        return None

    def handle_retry_all(self, object_name, edited_df):
        # Call retry_for_masking with retry_all=True and empty record list
        result = self.protecto_api.retry_for_masking(object_name, True, [])
        if not result['is_retry_enabled']:
            st.success(result['message'])
        return result

    def handle_retry(self, object_name, edited_df):
        # Get records marked for retry
        retry_records = edited_df[edited_df['retry'] == True]['Id'].tolist()
        if retry_records:
            # Call retry_for_masking with specific records
            result = self.protecto_api.retry_for_masking(object_name, False, retry_records)
            if not result['is_retry_enabled']:
                st.success(result['message'])
            return result
        else:
            st.warning("Please select records to retry")
        return None

    def handle_approve(self, object_name):
        result = self.protecto_api.approve_for_masking(object_name)
        if not result['is_approve_enabled']:
            st.session_state.is_approved = True
            st.success(result['message'])
            st.rerun()
        return result

    def handle_download(self, object_name):
        # Get records from API
        records = self.protecto_api.download_records(object_name)
        
        if records:
            # Flatten the records
            flattened_records = []
            for record in records:
                flat_record = {}
                # Add regular fields
                for key, value in record.items():
                    if key != 'attributes' and not isinstance(value, dict):
                        flat_record[key] = value
                    elif key == 'Address' and isinstance(value, dict):
                        # Flatten address fields with prefix
                        for addr_key, addr_value in value.items():
                            flat_record[f'Address_{addr_key}'] = addr_value
                flattened_records.append(flat_record)
            
            # Convert to DataFrame
            df = pd.DataFrame(flattened_records)
            
            # Convert DataFrame to CSV
            csv = df.to_csv(index=False)
            
            # Create download button
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{object_name}_records.csv",
                mime="text/csv"
            )
        else:
            st.warning("No records available for download")

    def create_dynamic_table(self, selected_object):
        # Get data for the selected object
        result = self.protecto_api.get_query_execution_result(selected_object)
        
        if not result['records']:
            st.warning("No records found for the selected object.")
            return None
            
        # Flatten the nested 'attributes' dictionary
        flattened_records = []
        for record in result['records']:
            flat_record = {}
            # Add regular fields
            for key, value in record.items():
                if key != 'attributes' and not isinstance(value, dict):
                    flat_record[key] = value
            
            # Ensure retry field exists with boolean value
            flat_record['retry'] = bool(record.get('retry', False))
            flattened_records.append(flat_record)
            
        df = pd.DataFrame(flattened_records)
        
        # Ensure retry column exists
        if 'retry' not in df.columns:
            df['retry'] = False
            
        # Reorder columns
        first_columns = ['retry', 'Id', 'Username', 'is_masked', 'error']
        other_columns = [col for col in df.columns if col not in first_columns]
        df = df[first_columns + other_columns]

        # Create dynamic column configuration
        column_config = {
            'retry': st.column_config.CheckboxColumn(
                'Select',
                width='small',
                default=False,
                help="Select to retry this record",
                disabled=st.session_state.is_approved
            ),
            'Id': st.column_config.TextColumn(
                'Record id',
                width='medium',
                disabled=True
            ),
            'is_masked': st.column_config.SelectboxColumn(
                'New column(Is Masked)',
                width='medium',
                options=['to_be_masked', 'no_mask']
            ),
            'error': st.column_config.TextColumn(
                'Error',
                width='medium',
                disabled=True
            )
        }
        
        # Add other columns dynamically
        for col in df.columns:
            if col not in ['retry', 'Username', 'Id', 'is_masked', 'error']:
                column_config[col] = st.column_config.TextColumn(
                    col,
                    width='medium',
                    disabled=True
                )

        # Create and display the dataframe
        edited_df = st.data_editor(
            df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
        )
        
        return edited_df
    
    def show(self):
        st.title("Masking Approval")
        
        # Get the objects and queries scheduled for masking
        scheduled_objects = self.protecto_api.get_objects_and_query_scheduled_for_masking()
        
        # Create columns for layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            object_names = [obj["object_name"] for obj in scheduled_objects]
            selected_object = st.selectbox(
                "Object",
                options=object_names,
                key="object_selectbox",
                disabled=st.session_state.is_approved
            )
        
        with col2:
            if selected_object:
                selected_query = next(
                    (obj["query"] for obj in scheduled_objects 
                     if obj["object_name"] == selected_object),
                    ""
                )
                st.text_input("Query", value=selected_query, disabled=True)
        
        # Display the dynamic table if an object is selected
        if selected_object:
            st.divider()
            
            # Add action buttons in a row
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
            
            # Get button states
            is_approve_retry = self.protecto_api.is_approve_and_retry_enabled(selected_object)
            
            # Create table and get edited dataframe
            edited_df = self.create_dynamic_table(selected_object)
            
            # Only show buttons if we have data
            if edited_df is not None:
                with col3:
                    approve_button = st.button(
                        "Approve",
                        type="primary",
                        use_container_width=True,
                        disabled=not is_approve_retry['is_approve_enabled']
                    )
                with col4:
                    retry_button = st.button(
                        "Retry",
                        type="secondary",
                        use_container_width=True,
                        disabled=not is_approve_retry['is_retry_enabled'] or st.session_state.is_approved
                    )
                with col5:
                    self.handle_download(selected_object)
                
                if approve_button:
                    self.handle_save(selected_object, edited_df)
                    self.handle_approve(selected_object)
                    
                if retry_button:
                    self.handle_retry(selected_object, edited_df)

if __name__ == "__main__":
    masking_page = MaskingApprovalPage()
    masking_page.show()