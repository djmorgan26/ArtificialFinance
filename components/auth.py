import streamlit as st
from services.auth_service import login_user, create_user

def render_auth_ui():
    """Render authentication UI for user login/signup"""
    st.sidebar.markdown('<div class="section-header">User Account</div>', unsafe_allow_html=True)
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    if st.session_state.user_id is None:
        auth_status = st.sidebar.radio("", ["Login", "Create Account"])
        
        if auth_status == "Login":
            email = st.sidebar.text_input("Email")
            password = st.sidebar.text_input("Password", type="password")
            
            if st.sidebar.button("Login"):
                user_id = login_user(email, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.sidebar.success("Logged in successfully!")
                    st.experimental_rerun()
                else:
                    st.sidebar.error("Login failed. Please check your credentials.")
        else:
            email = st.sidebar.text_input("Email")
            password = st.sidebar.text_input("Password", type="password")
            confirm_password = st.sidebar.text_input("Confirm Password", type="password")
            
            if st.sidebar.button("Create Account"):
                if password != confirm_password:
                    st.sidebar.error("Passwords do not match")
                else:
                    user_id = create_user(email, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.sidebar.success("Account created successfully!")
                        st.experimental_rerun()
                    else:
                        st.sidebar.error("Account creation failed. Please try again.")
    else:
        st.sidebar.write(f"Logged in as: {st.session_state.user_id}")
        if st.sidebar.button("Logout"):
            st.session_state.user_id = None
            # Clear other session data
            for key in list(st.session_state.keys()):
                if key != "user_id":
                    del st.session_state[key]
            st.experimental_rerun()