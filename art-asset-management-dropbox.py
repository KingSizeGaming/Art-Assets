import dropbox
import pathlib
import streamlit as st
from datetime import datetime


# Your Dropbox access token
ACCESS_TOKEN = 'sl.BzCMPcRbATZLMxeR7rvd1EDYvyZl2fJQnE2SqieakqxBEKKnfipUSmxUzeLdYs7U6i7_ZDrLMFvGQ_yAZ_kiKRI4D_qqlCDt8tZDNLT8Eklfxb9ujpZBJFF-zKdbhCaA_5WlAfkFzD8WHfQBc_CyT8A'

def dropbox_connect():
    """Create a Dropbox client instance."""
    return dropbox.Dropbox(ACCESS_TOKEN)

def dropbox_upload_file(local_file_path, dropbox_folder_path):
    """Thid will upload a file to Dropbox from a local path, with an attempt at versioning to avoid overwrites."""
    dbx = dropbox_connect()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S") #FOr version control

    # Extract the file name and append the timestamp to the file name
    file_name = pathlib.Path(local_file_path).name
    versioned_file_name = f"{file_name}_{timestamp}"
    versioned_dropbox_path = f"{dropbox_folder_path}/{versioned_file_name}".replace('\\', '/')

    try:
        with open(local_file_path, "rb") as f:
            meta = dbx.files_upload(f.read(), versioned_dropbox_path, mode=dropbox.files.WriteMode.add)
            st.success(f"File uploaded successfully to {versioned_dropbox_path}")
            return meta
    except Exception as e:
        st.error(f'Error uploading file to Dropbox: {e}')

    return None

def render_dropbox_explorer():
    folder_options = ['test1', 'test2'] #Hard coded for now, but can be replaced with a call to list all folders in the Dropbox
    selected_folder = st.selectbox('Choose a folder to upload to:', folder_options)
    
    current_path = f'/{selected_folder}'

    uploaded_file = st.file_uploader("Choose a file to upload", key='file_uploader')
    if uploaded_file is not None and st.button('Upload'):
        dropbox_file_path = f"{current_path}/{uploaded_file.name}"
        
        temp_file_path = f"./temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getvalue()) 
        
        
        dropbox_upload_file(temp_file_path, dropbox_file_path)
        
       
        pathlib.Path(temp_file_path).unlink(missing_ok=True)

if __name__ == "__main__":
    render_dropbox_explorer()




