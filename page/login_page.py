from sqlalchemy import create_engine,text
from sqlalchemy.exc import SQLAlchemyError
import streamlit as st

class TiDBConnection:
    """Manages database connections to TiDB."""
    
    def __init__(self):
        self.host = 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com'
        self.port = '4000'
        self.user = '216JHCeM1VMy5o7.root'
        self.password = 'GfKyfKqB76MTL2EC'
        self.database = 'test'
        self.ca_path = "cert/isrgrootx1.pem"
        
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
        
    def register_user(self, client_id: str, username: str, private_key: str, 
                     environment_name: str, audience_url: str, environment_url: str) -> bool:
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
                
                print("\n--- Checking if users table exists ---")
                result = conn.execute(text("SHOW TABLES LIKE 'users'")).fetchone()
                if not result:
                    print("Users table does not exist. Creating table...")
                    conn.execute(text("""
                        CREATE TABLE users (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            client_id VARCHAR(255),
                            username VARCHAR(255) NOT NULL,
                            private_key_hash TEXT NOT NULL,  
                            environment_name VARCHAR(255),
                            audience_url VARCHAR(255),
                            environment_url VARCHAR(255)
                        )
                    """))
                    conn.commit()
                    print("✓ Users table created successfully")
                else:
                    print("✓ Users table already exists")
                
                print("✓ User does not exist, proceeding with registration")
                
                print("\n--- Creating New User ---")
                print("Using private key as hash...")
                private_key_hash = private_key
                print("✓ Private key stored")
                
                print("Inserting user into database...")
                conn.execute(
                    text("""
                        INSERT INTO users (client_id, username, private_key_hash, environment_name, audience_url, environment_url)
                        VALUES (:client_id, :username, :private_key_hash, :environment_name, :audience_url, :environment_url)
                    """),
                    {
                        "client_id": client_id,
                        "username": username,
                        "private_key_hash": private_key_hash,
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
            
    def authenticate_user(self, environment_name: str) -> bool:
        """Authenticate a user based on environment name."""
        try:
            engine = self.db_connection.connect()
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT client_id, username, private_key_hash, audience_url, environment_url, environment_name 
                        FROM users WHERE environment_name = :environment_name
                    """),
                    {"environment_name": environment_name}
                ).fetchone()
                
                if result:
                    print("Setting session state for user:")
                    print("Client ID:", result.client_id)
                    print("Username:", result.username)
                    print("Private Key Hash:", result.private_key_hash)
                    print("Audience URL:", result.audience_url)
                    print("Environment URL:", result.environment_url)
                    
                    st.session_state.user = {
                        'client_id': result.client_id,
                        'username': result.username,
                        'private_key_hash': result.private_key_hash,
                        'audience_url': result.audience_url,
                        'environment_url': result.environment_url
                    }
                    st.session_state.environment_name = result.environment_name
                    st.session_state.audience_url = result.audience_url
                    st.session_state.environment_url = result.environment_url
                    print(result.private_key_hash)
                    return bool(result)
                    
        except SQLAlchemyError as e:
            st.error(f"Database error: {str(e)}")
            return False

class LoginPage:
    """Manages the login page UI and interactions."""
    
    def __init__(self):
        self.user_manager = UserManager()
        
    def get_environment_names(self):
        """Fetch all environment names from the database."""
        engine = self.user_manager.db_connection.connect()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT environment_name FROM users")).fetchall()
            return [row[0] for row in result]
        
    def display(self):
        """Display the login/registration page."""
        if 'page' not in st.session_state:
            st.session_state.page = 'login'

        st.title("Select Environment")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            tab1, tab2 = st.tabs(["Select Environment", "Register Environment"])
            
            with tab1:
                with st.form(key='login_form'):
                    environment_names = self.get_environment_names()
                    environment_name = st.radio(
                        "Select Environment:",
                        options=environment_names,
                        key="environment_radio"
                    )
                    submit_button = st.form_submit_button("Select")
                    if submit_button and environment_name:
                        if self.user_manager.authenticate_user(environment_name):
                            st.session_state.authenticated = True
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials please register the Environment first")
            
            with tab2:
                with st.form(key='register_form'):
                    reg_client_id = st.text_input("Client ID")
                    reg_username = st.text_input("Username")
                    private_key = st.text_input("Private Key", type="password")
                    environment = st.text_input('Enter Environment Name:')
                    environment_url = st.text_input('Environment URL:')
                    audience_url = st.text_input('Audience URL:')
                    submit_button = st.form_submit_button("Register")
                    
                    if submit_button and reg_client_id and reg_username and private_key:
                        if self.user_manager.register_user(
                            reg_client_id, reg_username, private_key,
                            environment, audience_url, environment_url
                        ):
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