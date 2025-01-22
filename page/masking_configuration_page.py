import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder,JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from protectoMethods import ProtectoAPI

class MaskConfigPage:
    def __init__(self):
        self.protecto_api = ProtectoAPI()
        self.objects = self.protecto_api.get_list_of_objects()
        
    def _create_fields_table(self, fields_data):
        # Convert boolean to Yes/No in the DataFrame
        df = pd.DataFrame(fields_data)
        df['to_be_masked'] = df['to_be_masked'].map({True: 'Yes', False: 'No'})
        
        # Configure grid options
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(
            editable=True,
            resizable=True,
            filterable=True,
            sorteable=True
        )
        
        # Configure specific columns
        gb.configure_column(
            "field",
            editable=False,
            width=150
        )
        
        gb.configure_column(
            "to_be_masked",
            cellEditor='agSelectCellEditor',
            cellEditorParams={
                'values': ['Yes', 'No']
            },
            cellStyle=JsCode("""
                function(params) {
                    if (params.value === 'Yes') {
                        return {'backgroundColor': '#90EE90'};
                    } else {
                        return {'backgroundColor': '#FFB6C1'};
                    }
                }
            """),
            width=120
        )
        
        gb.configure_column(
            "pii_identified",
            editable=False,
            width=150
        )
        
        gb.configure_column(
            "override_pii",
            cellEditor='agSelectCellEditor',
            cellEditorParams={
                'values': ["PERSON", "EMAIL", "NO PII", "URL", "ADDRESS", "PHONE"]
            },
            width=150
        )
        
        gb.configure_column(
            "samples",
            editable=False,
            width=250
        )
        
        # Set grid options
        grid_options = gb.build()
        grid_options['domLayout'] = 'normal'
        
        # Create AgGrid component
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            height=400,
            allow_unsafe_jscode=True,
            theme='streamlit'
        )
        
        # Get updated dataframe
        updated_df = grid_response['data']
        
        # Convert Yes/No back to boolean before returning
        if updated_df is not None:
            updated_df['to_be_masked'] = updated_df['to_be_masked'].map({'Yes': True, 'No': False})
        
        return updated_df

    def show(self):
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"] {
                padding-top: 0;
            }
            .block-container {
                padding-top: 1.0rem;
                max-width: 100%;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.title("Mask Configuration")
        
        # Object Selection
        col1, col2 = st.columns([1, 2])
        
        with col1:
            selected_object = st.selectbox(
                "Object",
                [""] + self.objects,
                key="mask_config_object",
                index=1 + self.objects.index(st.session_state.selected_object)
            )
        
        try:
            # Get and display field metadata
            metadata = self.protecto_api.get_metadata_for_mask(st.session_state.selected_object)
            st.session_state.field_metadata = metadata.get('field_metadata', [])
            st.session_state.show_table = True
        except Exception as e:
            st.error(f"An error occurred while fetching metadata: {str(e)}")
            return
        
        with st.container():
            # Create the table
            edited_fields = self._create_fields_table(st.session_state.field_metadata)
            print(edited_fields)
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col2:
                    schedule_button = st.button("Schedule for masking", type="primary")
            
            # Handle button click after table is created
            if schedule_button and edited_fields is not None:
                try:
                    fields_records = edited_fields.to_dict('records')
                    print(fields_records)
                    
                    result = self.protecto_api.update_mask_metadata(
                        selected_object,
                        st.session_state.query,
                        fields_records
                    )
                    
                    if result.get('is_rows_selected_for_masking'):
                        st.success(result.get('message'))
                        st.session_state.show_table = False
                        if 'field_metadata' in st.session_state:
                            del st.session_state.field_metadata
                    else:
                        st.error("Failed to update mask configuration. Please try again.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    mask_config_page = MaskConfigPage()
    mask_config_page.show()