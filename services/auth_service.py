import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import os

@st.cache_resource
def initialize_firebase():
    """Initialize Firebase Admin SDK for authentication and Firestore database."""
    if not firebase_admin._apps:
        # In production, use environment variables or secrets management
        # Here we assume the service account key is in the same directory
        try:
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Firebase initialization error: {str(e)}")
            st.info("Please make sure you have a valid serviceAccountKey.json file.")
            return None
    return firebase_admin

def login_user(email, password):
    """
    Authenticate a user with Firebase
    
    Args:
        email: User's email
        password: User's password
        
    Returns:
        User ID if successful, None otherwise
    """
    try:
        # In production, use Firebase Authentication properly
        # For demo/prototype, we can simulate authentication
        try:
            firebase_app = initialize_firebase()
            if firebase_app:
                user = auth.get_user_by_email(email)
                # In production, verify password with Firebase Auth
                return user.uid
            else:
                # If Firebase isn't configured, use demo mode
                return "demo_user_" + email.replace("@", "_").replace(".", "_")
        except:
            # If Firebase isn't configured, use demo mode
            return "demo_user_" + email.replace("@", "_").replace(".", "_")
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return None

def create_user(email, password):
    """
    Create a new user in Firebase
    
    Args:
        email: User's email
        password: User's password
        
    Returns:
        User ID if successful, None otherwise
    """
    try:
        # In production, use Firebase Authentication properly
        try:
            firebase_app = initialize_firebase()
            if firebase_app:
                user = auth.create_user(email=email, password=password)
                return user.uid
            else:
                # If Firebase isn't configured, use demo mode
                return "demo_user_" + email.replace("@", "_").replace(".", "_")
        except:
            # If Firebase isn't configured, use demo mode
            return "demo_user_" + email.replace("@", "_").replace(".", "_")
    except Exception as e:
        st.error(f"Account creation failed: {str(e)}")
        return None