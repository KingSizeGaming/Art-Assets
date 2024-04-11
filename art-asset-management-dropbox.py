import dropbox
import pathlib
import streamlit as st
from datetime import datetime
from io import BytesIO
from PIL import Image
import base64
from supabase import create_client, Client

SUPABASE_URL = st.secrets["supabase_url"]
SUPABASE_KEY = st.secrets["supabase_key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


ACCESS_TOKEN = st.secrets["dropbox_access_token"]

def login():
    if 'user' not in st.session_state:
        st.session_state['user'] = None

    if st.session_state['user'] is None:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Sign in"):
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state['token'] = supabase.auth.get_session().access_token
            user = supabase.auth.get_user(st.session_state['token'])

            if user is None:
                st.error("Invalid email or password")
            else:
                st.session_state['user'] = user
                st.success("Sign in successfully")
                st.experimental_rerun()  # Rerun the script to reflect the new login state

login()


            


if st.session_state['user'] is not None:

    def dropbox_connect():
        """Create a Dropbox client instance."""
        return dropbox.Dropbox(ACCESS_TOKEN)
    def dropbox_upload_file(local_file_path, dropbox_folder_path):
        """Upload a file to Dropbox from a local path, with an attempt at versioning to avoid overwrites."""
        dbx = dropbox_connect()
        timestamp = datetime.now().strftime("_%Y%m%d%H%M%S")  # For version control
        # add a timestamp to the nd for versioning
        file_name = pathlib.Path(local_file_path).stem
        file_extension = pathlib.Path(local_file_path).suffix
        versioned_file_name = f"{file_name}{timestamp}{file_extension}"
        versioned_dropbox_path = f"{dropbox_folder_path}/{versioned_file_name}".replace(
            "\\", "/"
        )
        try:
            with open(local_file_path, "rb") as f:
                meta = dbx.files_upload(
                    f.read(), versioned_dropbox_path, mode=dropbox.files.WriteMode.add
                )
                st.success(f"File uploaded successfully to {versioned_dropbox_path}")
                return meta
        except Exception as e:
            st.error(f"Error uploading file to Dropbox: {e}")
            return None
    def list_files(path):
        """List all files within the specified path."""
        dbx = dropbox_connect()
        try:
            files = dbx.files_list_folder(path).entries
            file_names = [
                file.name for file in files if isinstance(file, dropbox.files.FileMetadata)
            ]
            return file_names
        except Exception as e:
            st.error(f"Failed to list files: {e}")
            return []
    def list_folders(path=""):
        """List all folders within the specified path."""
        dbx = dropbox_connect()
        try:
            folders = dbx.files_list_folder(path).entries
            folder_names = [
                folder.name
                for folder in folders
                if isinstance(folder, dropbox.files.FolderMetadata)
            ]
            return folder_names
        except Exception as e:
            st.error(f"Failed to list folders: {e}")
            return []
    def render_file_selection(games_path):
        """Render the file selection process."""
        games = list_folders(games_path)
        selected_game = st.selectbox("Select a game:", games)
        game_path = f"{games_path}/{selected_game}"
        assets = list_folders(game_path)
        selected_asset = st.selectbox("Select an asset to modify:", assets)
        asset_path = f"{game_path}/{selected_asset}"
        versions = list_files(asset_path)
        selected_version = st.selectbox("Select the asset version to download:", versions)
        version_path = f"{asset_path}/{selected_version}"
        return version_path
    def download_button(file_bytes, file_name, button_text):
        """Generate a download button for the given file."""
        st.download_button(
            label=button_text,
            data=file_bytes,
            file_name=file_name,
            mime="application/octet-stream",
        )
    def render_download_tab(games_path):
        """Render the download tab with file selection and preview/download options."""
        st.header("Download Asset")
        selected_file_path = render_file_selection(games_path)
        if selected_file_path:  # Make sure a path is selected
            dbx = dropbox_connect()
            _, res = dbx.files_download(selected_file_path)
            # Preview
            if selected_file_path.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                image = Image.open(BytesIO(res.content))
                st.image(image, caption=selected_file_path.split("/")[-1])
            # Download
            download_button(res.content, selected_file_path.split("/")[-1], "Download")
    def render_dropbox_explorer():
        """Render the Dropbox explorer for uploading files."""
        folder_options = [
            "game1",
            "game2",
            "game3",
        ]  # This needs to be replaced with the actual folder structure
        selected_folder = st.selectbox("Choose a folder to upload to:", folder_options)
        uploaded_file = st.file_uploader("Choose a file to upload", key="file_uploader")
        if uploaded_file is not None and st.button("Upload"):
            current_path = f"/{selected_folder}"
            dropbox_file_path = f"{current_path}/{uploaded_file.name}"
            temp_file_path = f"./temp_{uploaded_file.name}"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            dropbox_upload_file(temp_file_path, dropbox_file_path)
            pathlib.Path(temp_file_path).unlink(missing_ok=True)
    def asset_management_dashboard():
        """Render the asset management dashboard (placeholder)."""
        st.subheader("Asset Management Dashboard")
        st.write("Asset management dashboard functionality goes here.")
    if __name__ == "__main__":
        st.title("Dropbox Asset Manager")
        tab1, tab2, tab3 = st.tabs(
            ["Upload Asset", "Download Asset", "Asset Management Dashboard"]
        )
        with tab1:
            render_dropbox_explorer()
        with tab2:
            games_path = ""
            render_download_tab(games_path)
        with tab3:
            asset_management_dashboard()
