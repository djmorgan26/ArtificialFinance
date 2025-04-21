import streamlit as st
import firebase_admin
from firebase_admin import firestore
from datetime import datetime
from services.auth_service import initialize_firebase

def get_db():
    """Get Firestore database client"""
    firebase_app = initialize_firebase()
    if firebase_app:
        return firestore.client()
    return None

def save_column_mappings(user_id, file_id, mappings):
    """
    Save column mappings to Firestore
    
    Args:
        user_id: User ID
        file_id: Identifier for the file
        mappings: Column mapping dictionary
        
    Returns:
        Success boolean
    """
    db = get_db()
    if not db:
        return False
    
    try:
        mapping_doc = {
            "file_name": file_id,
            "mappings": mappings,
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat()
        }
        
        db.collection("users").document(user_id).collection("mappings").add(mapping_doc)
        return True
    except Exception as e:
        st.error(f"Error saving mappings: {str(e)}")
        return False

def get_existing_mappings(user_id, file_name):
    """
    Check if the user has previously mapped columns for similar files
    
    Args:
        user_id: User ID
        file_name: Name of the current file
        
    Returns:
        Dictionary with existing mappings if found, None otherwise
    """
    if not user_id:
        return None
    
    db = get_db()
    if not db:
        return None
    
    try:
        # Query Firestore for similar mappings
        mappings_ref = db.collection("users").document(user_id).collection("mappings")
        
        # Find mappings with similar file names
        similar_mappings = mappings_ref.where("file_name", "==", file_name).limit(1).get()
        
        if not similar_mappings:
            return None
        
        # Return the most recently used mapping
        for doc in similar_mappings:
            mapping_data = doc.to_dict()
            
            # Update the last_used timestamp
            doc.reference.update({"last_used": datetime.now().isoformat()})
            
            return mapping_data["mappings"]
        
        return None
    except Exception as e:
        st.warning(f"Could not retrieve existing mappings: {str(e)}")
        return None

def update_column_mappings(user_id, file_id, updated_mappings):
    """
    Update existing column mappings in Firestore
    
    Args:
        user_id: User ID
        file_id: Identifier for the file
        updated_mappings: Updated column mapping dictionary
        
    Returns:
        Success boolean
    """
    db = get_db()
    if not db:
        return False
    
    try:
        mapping_doc = {
            "file_name": file_id,
            "mappings": updated_mappings,
            "updated_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat()
        }
        
        # Find and update existing mapping document
        mappings_ref = db.collection("users").document(user_id).collection("mappings")
        existing_docs = mappings_ref.where("file_name", "==", file_id).limit(1).get()
        
        for doc in existing_docs:
            doc.reference.update(mapping_doc)
            return True
        
        # If no existing mapping found, create new
        mappings_ref.add(mapping_doc)
        return True
        
    except Exception as e:
        st.error(f"Error updating mappings: {str(e)}")
        return False