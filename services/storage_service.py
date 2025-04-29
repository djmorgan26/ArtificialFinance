import streamlit as st
import firebase_admin
from firebase_admin import firestore
from datetime import datetime
from services.auth_service import initialize_firebase, get_db

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
    if not user_id or user_id.startswith("demo_user_"):
        # Handle demo mode with session state storage
        if 'saved_mappings' not in st.session_state:
            st.session_state.saved_mappings = {}
        st.session_state.saved_mappings[file_id] = {
            "mappings": mappings,
            "last_used": datetime.now().isoformat()
        }
        return True
    
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
    
    # Handle demo mode
    if user_id.startswith("demo_user_"):
        if 'saved_mappings' in st.session_state and file_name in st.session_state.saved_mappings:
            return st.session_state.saved_mappings[file_name]["mappings"]
        return None
    
    db = get_db()
    if not db:
        return None
    
    try:
        # Query Firestore for similar mappings
        mappings_ref = db.collection("users").document(user_id).collection("mappings")
        
        # Find mappings with similar file names
        similar_mappings = mappings_ref.where("file_name", "==", file_name).limit(1).get()
        
        if not similar_mappings or len(list(similar_mappings)) == 0:
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
    # Handle demo mode
    if not user_id or user_id.startswith("demo_user_"):
        if 'saved_mappings' not in st.session_state:
            st.session_state.saved_mappings = {}
        st.session_state.saved_mappings[file_id] = {
            "mappings": updated_mappings,
            "last_used": datetime.now().isoformat()
        }
        return True
    
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
        
        docs_list = list(existing_docs)
        if docs_list:
            for doc in docs_list:
                doc.reference.update(mapping_doc)
                return True
        
        # If no existing mapping found, create new
        mappings_ref.add(mapping_doc)
        return True
        
    except Exception as e:
        st.error(f"Error updating mappings: {str(e)}")
        return False

def save_financial_data(user_id, data_type, data_df):
    """
    Save processed financial data to Firestore
    
    Args:
        user_id: User ID
        data_type: Type of financial data (e.g., 'transactions', 'budget')
        data_df: DataFrame with financial data
        
    Returns:
        Success boolean and document ID
    """
    if not user_id or user_id.startswith("demo_user_"):
        # Demo mode - store in session state
        if 'saved_financial_data' not in st.session_state:
            st.session_state.saved_financial_data = {}
        
        data_id = f"{data_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        st.session_state.saved_financial_data[data_id] = {
            "type": data_type,
            "data": data_df.to_dict(orient="records"),
            "created_at": datetime.now().isoformat()
        }
        return True, data_id
    
    db = get_db()
    if not db:
        return False, None
    
    try:
        # Convert DataFrame to dict for Firestore
        data_dict = {
            "type": data_type,
            "data": data_df.to_dict(orient="records"),
            "created_at": datetime.now().isoformat(),
            "row_count": len(data_df)
        }
        
        # Add to Firestore
        doc_ref = db.collection("users").document(user_id).collection("financial_data").add(data_dict)
        return True, doc_ref.id
    except Exception as e:
        st.error(f"Error saving financial data: {str(e)}")
        return False, None

def get_user_financial_data(user_id, data_type=None):
    """
    Get user's saved financial data from Firestore
    
    Args:
        user_id: User ID
        data_type: Optional filter by data type
        
    Returns:
        Dictionary of financial data documents
    """
    if not user_id:
        return {}
    
    # Handle demo mode
    if user_id.startswith("demo_user_"):
        if 'saved_financial_data' not in st.session_state:
            return {}
        
        if data_type:
            return {k: v for k, v in st.session_state.saved_financial_data.items() 
                   if v.get("type") == data_type}
        return st.session_state.saved_financial_data
    
    db = get_db()
    if not db:
        return {}
    
    try:
        # Query Firestore for user's financial data
        data_ref = db.collection("users").document(user_id).collection("financial_data")
        
        if data_type:
            query = data_ref.where("type", "==", data_type)
        else:
            query = data_ref
            
        # Get the documents
        docs = query.get()
        
        result = {}
        for doc in docs:
            result[doc.id] = doc.to_dict()
            
        return result
    except Exception as e:
        st.warning(f"Could not retrieve financial data: {str(e)}")
        return {}