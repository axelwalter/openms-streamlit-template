import streamlit as st
import pandas as pd
import io
from pathlib import Path
import shutil
import sys
import uuid


def page_setup():
    # streamlit configs
    st.set_page_config(
        page_title="OpenMS FLASHDeconvViewer App",
        page_icon="assets/OpenMS.png",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items=None,
    )
    if "workspace" not in st.session_state:
        # Local: workspace name at startup: default-workspace
        if "local" in sys.argv:
            st.session_state.location = "local"
            st.session_state["workspace"] = Path("default-workspace")
        # Online: create a random key as workspace name
        else:
            st.session_state.location = "online"
            st.session_state["workspace"] = Path(str(uuid.uuid1()))
    # Make sure important directories exist
    st.session_state["workspace"].mkdir(parents=True, exist_ok=True)

    # needed directories
    important_dirs = ["deconv-mzMLs", "anno-mzMLs", "fasta-files"]
    for dirnames in important_dirs:
        st.session_state[dirnames] = Path(st.session_state["workspace"], dirnames)
        st.session_state[dirnames].mkdir(parents=True, exist_ok=True)

def v_space(n, col=None):
    for _ in range(n):
        if col:
            col.write("#")
        else:
            st.write("#")


def open_df(file):
    separators = {"txt": "\t", "tsv": "\t", "csv": ","}
    try:
        if type(file) == str:
            ext = file.split(".")[-1]
            if ext != "xlsx":
                df = pd.read_csv(file, sep=separators[ext])
            else:
                df = pd.read_excel(file)
        else:
            ext = file.name.split(".")[-1]
            if ext != "xlsx":
                df = pd.read_csv(file, sep=separators[ext])
            else:
                df = pd.read_excel(file)
        # sometimes dataframes get saved with unnamed index, that needs to be removed
        if "Unnamed: 0" in df.columns:
            df.drop("Unnamed: 0", inplace=True, axis=1)
        return df
    except:
        return pd.DataFrame()


def show_table(df, title, col=""):
    text = f"##### {title}\n{df.shape[0]} rows, {df.shape[1]} columns"
    if col:
        col.markdown(text)
        col.download_button(
            "Download Table",
            df.to_csv(sep="\t").encode("utf-8"),
            title.replace(" ", "-") + ".tsv",
        )
        col.dataframe(df)
    else:
        st.markdown(text)
        st.download_button(
            "Download Table",
            df.to_csv(sep="\t").encode("utf-8"),
            title.replace(" ", "-") + ".tsv",
        )
        st.dataframe(df)


def download_plotly_figure(fig, col=None, filename=""):
    buffer = io.BytesIO()
    fig.write_image(file=buffer, format="png")

    if col:
        col.download_button(
            label=f"Download Figure",
            data=buffer,
            file_name=filename,
            mime="application/png",
        )
    else:
        st.download_button(
            label=f"Download Figure",
            data=buffer,
            file_name=filename,
            mime="application/png",
        )


def reset_directory(path: Path):
    shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def sidebar(page=""):
    with st.sidebar:
        if page == "main":
            st.markdown("### Workspaces")
            if st.session_state["location"] == "online":
                new_workspace = st.text_input("enter workspace", "")
                if st.button("**Enter Workspace**") and new_workspace:
                    st.session_state["workspace"] = Path(new_workspace)
                st.info(
                    f"""💡 Your workspace ID:

**{st.session_state['workspace']}**

You can share this unique workspace ID with other people.

⚠️ Anyone with this ID can access your data!"""
                )
            elif st.session_state["location"] == "local":
                # Show available workspaces
                options = [
                    file.name
                    for file in Path(".").iterdir()
                    if file.is_dir()
                    and file.name
                    not in (
                        ".git",
                        ".gitignore",
                        ".streamlit",
                        "example-data",
                        "pages",
                        "src",
                        "assets",
                    )
                ]
                chosen_workspace = st.selectbox(
                    "choose existing workspace",
                    options,
                    index=options.index(str(st.session_state["workspace"])),
                )
                if chosen_workspace:
                    st.session_state["workspace"] = Path(chosen_workspace)

                # Create or Remove workspaces
                st.text_input("create/remove workspace", "", key="create-remove")
                path = Path(st.session_state["create-remove"])
                if st.button("**Create Workspace**") and path.name:
                    path.mkdir(parents=True, exist_ok=True)
                    st.session_state["workspace"] = path
                if st.button("⚠️ Delete Workspace") and path.exists:
                    shutil.rmtree(path)
                    st.session_state["workspace"] = Path("default-workspace")
            st.markdown("***")

        # TODO: revive this later
        elif page == "files":
            # Show currently available mzML files
            st.markdown("### Uploaded Files")
            for f in sorted(Path(st.session_state["deconv-mzML-files"]).iterdir()):
                if f.name in st.session_state:
                    checked = st.session_state[f.name]
                else:
                    checked = True
                st.checkbox(f.name, checked, key=f.name)

            for f in sorted(Path(st.session_state["fasta-files"]).iterdir()):
                if f.name in st.session_state:
                    checked = st.session_state[f.name]
                else:
                    checked = True
                st.checkbox(f.name, checked, key=f.name)

        #     # Option to remove files
        #     v_space(1)
        #     st.markdown("⚠️ **Remove files**")
        #     c1, c2 = st.columns(2)
        #     if c1.button("**All**"):
        #         reset_directory(st.session_state["mzML-files"])
        #
        #     if c2.button("**Un**selected"):
        #         for file in [
        #             Path(st.session_state["mzML-files"], key)
        #             for key, value in st.session_state.items()
        #             if key.endswith("mzML") and not value  # e.g. unchecked
        #         ]:
        #             file.unlink()
        #         st.experimental_rerun()
        #
            st.markdown("***")
        st.image("assets/OpenMS.png", "powered by")


WARNINGS = {
    "no-workspace": "No online workspace ID found, please visit the start page first.",
    "missing-mzML": "Upload or select some mzML files first!",
}

ERRORS = {
    "general": "Something went wrong.",
    "workflow": "Something went wrong during workflow execution.",
    "visualization": "Something went wrong during visualization of results.",
}
