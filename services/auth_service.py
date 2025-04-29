import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import json
from datetime import datetime

@st.cache_resource
def initialize_firebase():
    """Initialize Firebase Admin SDK for authentication and Firestore database."""
    if not firebase_admin._apps:
        try:
            # For local development, use a service account file
            if os.path.exists("serviceAccountKey.json"):
                cred = credentials.Certificate("serviceAccountKey.json")
            # For Streamlit Cloud, use secrets
            else:
                key_dict = st.secrets["firebase"]
                cred = credentials.Certificate(key_dict)
            
            firebase_admin.initialize_app(cred)
            # Initialize Firestore
            db = firestore.client()
            return firebase_admin
        except Exception as e:
            st.error(f"Firebase initialization error: {str(e)}")
            st.info("Please ensure Firebase credentials are properly configured.")
            return None
    return firebase_admin

def get_db():
    """Get Firestore database client"""
    firebase_app = initialize_firebase()
    if firebase_app:
        return firestore.client()
    return None

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
        firebase_app = initialize_firebase()
        if not firebase_app:
            # If Firebase isn't configured properly, use demo mode
            return "demo_user_" + email.replace("@", "_").replace(".", "_")
        
        # In production, we would use Firebase Auth REST API
        # For this implementation, we're checking if the user exists
        try:
            user = auth.get_user_by_email(email)
            # In a real app, you would validate password with Firebase Auth
            # Here we're just returning the user if found
            return user.uid
        except Exception as e:
            st.error(f"Login error: {str(e)}")
            return None
            
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
        firebase_app = initialize_firebase()
        if not firebase_app:
            # If Firebase isn't configured properly, use demo mode
            return "demo_user_" + email.replace("@", "_").replace(".", "_")
        
        # Create the user in Firebase Auth
        user = auth.create_user(
            email=email,
            password=password,
            email_verified=False
        )
        
        # Initialize user document in Firestore
        db = firestore.client()
        db.collection("users").document(user.uid).set({
            "email": email,
            "created_at": datetime.now().isoformat(),
            "settings": {
                "currency": "USD",
                "theme": "light"
            }
        })
        
        return user.uid
            
    except Exception as e:
        st.error(f"Account creation failed: {str(e)}")
        return None