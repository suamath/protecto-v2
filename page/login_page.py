from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import streamlit as st
import time
from dotenv import load_dotenv
import os

class TiDBConnection:
    """Manages database connections to TiDB."""
    
    def __init__(self):
        load_dotenv('config.env')  # Load variables from .env file
        self.host = os.getenv('TIDB_HOST')
        self.port = os.getenv('TIDB_PORT')
        self.user = os.getenv('TIDB_USER')
        self.password = os.getenv('TIDB_PASSWORD')
        self.database = os.getenv('TIDB_DATABASE')
        self.ca_path = os.getenv('TIDB_CA_PATH')

        print(f"Current working directory: {os.getcwd()}")
        
    def connect(self):
        """Establishes connection to TiDB database."""
        print("\n=== Starting TiDB Connection Process ===")
        print(f"Attempting to connect to:")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print(f"Database: {self.database}")
        print(f"User: {self.user}")
        print(f"Password: {'*' * len(self.password)}")
        
        connection_url = f"mysql+mysqldb://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        
        ssl_args = {
            "ssl": {
                "ca": self.ca_path,
                "ssl_mode": "VERIFY_IDENTITY"
            }
        }
        
        try:
            engine = create_engine(connection_url, connect_args=ssl_args)
            with engine.connect() as connection:
                print("✓ Successfully connected!")
                result = connection.execute(text("show databases;"))
                print("\nDatabases:")
                for row in result:
                    print(f"- {row[0]}")

                connection.execute(text("USE test;"))
                result = connection.execute(text("SHOW TABLES;"))
                print("\nTables in test database:")
                for row in result:
                    print(f"- {row[0]}")
            return engine
        except SQLAlchemyError as e:
            print(f"\n✗ Error: {str(e)}")
            return None

class UserManager:
    """Manages user registration and authentication."""
    
    def __init__(self):
        self.db_connection = TiDBConnection()
        
    def register_user(self,client_id: str, username: str, private_key: str, password: str, environment_name: str, audience_url: str, environment_url: str) -> bool:
        """Register a new user in the database."""
        print("\n=== Starting Registration Process ===")
        print(f"Attempting to register:")
        print(f"Client ID: {client_id}")
        print(f"Username: {username}")
        print(f"Private Key: {private_key}")
        print(f"Environment Name: {environment_name}")
        print(f"Audience URL: {audience_url}")
        print(f"Environment URL: {environment_url}")
        try:
            print("\n--- Connecting to Database ---")
            engine = self.db_connection.connect()
            print("✓ Database connection successful")
            
            with engine.connect() as conn:
                print("\n--- Switching to test Database ---")
                conn.execute(text("USE test;"))
                print("✓ Switched to test database")
                
                # print("\n--- Dropping environment_details table if it exists ---")
                # conn.execute(text("DROP TABLE IF EXISTS environment_details"))
                # print("✓ environment_details table dropped successfully")
                
                
                print("\n--- Checking if environment_details table exists ---")
                result = conn.execute(text("SHOW TABLES LIKE 'environment_details'")).fetchone()
                if not result:
                    print("environment_details table does not exist. Creating table...")
                    # Create the environment_details table if it doesn't exist
                    conn.execute(text("""
                        CREATE TABLE environment_details (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            client_id VARCHAR(255),
                            username VARCHAR(255) NOT NULL,
                            private_key_hash TEXT NOT NULL,
                            password VARCHAR(255) NOT NULL,
                            environment_name VARCHAR(255),
                            audience_url VARCHAR(255),
                            environment_url VARCHAR(255)
                        )
                    """))
                    conn.commit()
                    print("✓ environment_details table created successfully")
                else:
                    print("✓ environment_details table already exists")
                
                print("✓ User does not exist, proceeding with registration")
                
                print("\n--- Creating New User ---")
                print("Hashing private key...")
                #private_key_hash = hash_private_key(private_key)
                private_key_hash = private_key
                print("✓ Private key hashed")
                
                print("Inserting user into database...")
                conn.execute(
                    text("""
                        INSERT INTO environment_details (client_id, username, private_key_hash, password, environment_name, audience_url, environment_url)
                        VALUES (:client_id, :username, :private_key_hash, :password, :environment_name, :audience_url, :environment_url)
                    """),
                    {
                        "client_id": client_id,
                        "username": username,
                        "private_key_hash": private_key_hash,
                        "password": password,
                        "environment_name": environment_name,
                        "audience_url": audience_url,
                        "environment_url": environment_url
                    }
                )
                conn.commit()
                print("✓ User successfully registered")
                return True
                
        except SQLAlchemyError as e:
            error_msg = f"Database error: {str(e)}"
            print(f"✗ {error_msg}")
            st.error(error_msg)
            return False
        finally:
            print("\n=== Registration Process Complete ===")
            
    def authenticate_user(self, **kwargs) -> bool:
        """Authenticate a user based on provided parameters."""
        try:
            print("\n=== Starting Authentication Process ===")
            print(f"Received parameters: {kwargs}")
            
            engine = self.db_connection.connect()
            print("✓ Database engine connected")
            
            with engine.connect() as conn:
                print("\n--- Fetching Table Fields ---")
                fields_result = conn.execute(text("DESCRIBE environment_details")).fetchall()
                fields = [row[0] for row in fields_result if row[0] != 'id']
                print(f"Table fields: {fields}")

                print("\n--- Fetching All User Data ---")
                query = "SELECT * FROM environment_details"
                result = conn.execute(text(query)).fetchall()

                if result:
                    print("\n--- Users Found ---")
                    for row in result:
                        user_data = {field: getattr(row, field) for field in fields}
                        print(user_data)
                else:
                    print("\n✗ No users found")

                
                print("\n--- Building WHERE clause ---")
                where_clauses = [f"{key} = :{key}" for key in kwargs.keys()]
                where_statement = " AND ".join(where_clauses)
                print(f"WHERE clause: {where_statement}")
                
                query = f"SELECT * FROM environment_details WHERE {where_statement}"
                print(f"\n--- Executing Query ---\n{query}")
                print(f"With parameters: {kwargs}")
                
                result = conn.execute(
                    text(query),
                    kwargs
                ).fetchone()
                
                if result:
                    print("\n--- User Found ---")
                    print("Setting session state values:")
                    
                    # Dynamically create session state user dictionary
                    st.session_state.user = {
                        field: getattr(result, field) for field in fields
                    }
                    print(f"Session state user: {st.session_state.user}")
                    
                    # Set all field values in session state
                    for field in fields:
                        if hasattr(result, field):
                            setattr(st.session_state, field, getattr(result, field))
                            print(f"Set {field} = {getattr(result, field)}")
                    
                    print("\n✓ Authentication successful")
                    return True
                
                print("\n✗ User not found")
                return False
                    
        except SQLAlchemyError as e:
            error_msg = f"Database error: {str(e)}"
            print(f"\n✗ {error_msg}")
            st.error(error_msg)
            return False
        finally:
            print("\n=== Authentication Process Complete ===")

class LoginPage:
    """Manages the login page UI and interactions."""
    
    def __init__(self):
        self.user_manager = UserManager()
        
    def get_table_fields(self):
        """Fetch fields from users table"""
        engine = self.user_manager.db_connection.connect()
        if not engine:
            st.error("Could not connect to database")
            return []
            
        try:
            with engine.connect() as conn:
                result = conn.execute(text("DESCRIBE environment_details")).fetchall()
                fields = [row[0] for row in result if row[0] != 'id']
                return fields
        except SQLAlchemyError as e:
            st.error(f"Error fetching fields: {e}")
            return []
        
    def get_environment_names(self):
        """Fetch all environment names from the database."""
        engine = self.user_manager.db_connection.connect()
        if not engine:
            st.error("Could not connect to database")
            return []
            
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT DISTINCT environment_name FROM environment_details")).fetchall()
                return [row[0] for row in result if row[0]]  # Filter out None values
        except SQLAlchemyError as e:
            st.error(f"Error fetching environment names: {e}")
            return []
        
    def display(self):
        """Display the login/registration page."""
        if 'page' not in st.session_state:
            st.session_state.page = 'login'
            
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False

        st.title("Select Environment")
        
        # Get table fields dynamically
        table_fields = self.get_table_fields()
        
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            tab1, tab2 = st.tabs(["Select Environment", "Register Environment"])
            
            with tab1:
                environment_names = self.get_environment_names()
                if not environment_names:
                    st.warning("No environments available. Please register one first.")
                    return
                
                with st.form(key='login_form', clear_on_submit=True):
                    environment_name = st.radio(
                        "Select Environment:",
                        options=environment_names,
                        key="environment_radio"
                    )
                    
                    # Only show username, client_id and private_key_hash for login
                    login_fields = os.getenv('LOGIN_FIELDS', '').split(',') if os.getenv('LOGIN_FIELDS') else []

                    credentials = {}
                    
                    for field in login_fields:
                        field_value = st.text_input(
                            field.replace('_', ' ').title(),
                            type='password' if field == 'private_key_hash' else 'default',
                            key=f"login_{field}"
                        )
                        credentials[field] = field_value
                    
                    submit_button = st.form_submit_button("Login")
                    
                    if submit_button:
                        if not all(credentials.values()):
                            st.error("Please fill in all fields")
                            return
                            
                        auth_params = {
                            'environment_name': environment_name,
                            **credentials
                        }
                        
                        if self.user_manager.authenticate_user(**auth_params):
                            st.session_state.authenticated = True
                            st.success("Login successful!")
                            time.sleep(1)  # Give time for success message
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please try again.")
                            
            with tab2:
                with st.form(key='register_form'):
                    reg_client_id = st.text_input("Client ID")
                    reg_username = st.text_input("Username")
                    private_key = st.text_input("Private Key", type="password")
                    password = st.text_input("Password", type="password")
                    environment = st.text_input('Enter Environment Name:')
                    environment_url = st.text_input('Environment URL:')
                    audience_url = st.text_input('Audience URL:')
                    submit_button = st.form_submit_button("Register")
                    
                    if submit_button and reg_client_id and reg_username and private_key and password:
                        if  self.user_manager.register_user(reg_client_id, reg_username, private_key, password, environment, audience_url, environment_url):
                            st.success("Registration successful! Please login.")
                            st.session_state.page = 'login'
                            st.rerun()
                        else:
                            st.error("Registration failed. Please try again.")
                            st.rerun()

# Usage
if __name__ == "__main__":
    login_page = LoginPage()
    login_page.display()