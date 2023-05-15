import numpy as np
import streamlit as st
from src.view import *
from src.common import *
from src.masstable import *

@st.cache_data
def draw3DSignalView(df):
    signal_df, noise_df = None, None # initialization
    for index, peaks in enumerate([df['Signal peaks'], df['Noisy peaks']]):
        xs, ys, zs = [], [], []
        for sm in peaks:
            xs.append(sm[1] * sm[-1])
            ys.append(sm[-1])
            zs.append(sm[2])

        out_df = pd.DataFrame({'mass': xs, 'charge': ys, 'intensity': zs})
        if index == 0:
            signal_df = out_df
        else:
            noise_df = out_df
    plot3d = plot3DSignalView(signal_df, noise_df)
    st.plotly_chart(plot3d, use_container_width=True)

def content():
    defaultPageSetup("NativeMS Viewer")

    # if no input file is given, show blank page
    if "experiment-df" not in st.session_state:
        st.error('Upload input files first!')
        return

    # selecting experiment
    experiment_df = st.session_state["experiment-df"]
    st.selectbox(
        "choose experiment", experiment_df['Experiment Name'],
        key="selected_experiment",
    )

    # getting data
    selected = experiment_df[experiment_df['Experiment Name'] == st.session_state.selected_experiment]

    selected_anno_file = selected.iloc[0]['Annotated Files']
    selected_deconv_file = selected.iloc[0]['Deconvolved Files']

    # getting data from mzML files
    spec_df = st.session_state['deconv_dfs'][selected_deconv_file]
    anno_df = st.session_state['anno_dfs'][selected_anno_file]

    #### Showing MS1 heatmap & Scan table ####
    df_for_ms1_deconv = getMSSignalDF(spec_df)
    df_for_spectra_table = getSpectraTableDF(spec_df)
    ms1_heatmap_view, scan_table_view = st.columns(2)
    with ms1_heatmap_view:
        plotMS1HeatMap(df_for_ms1_deconv, "Deconvolved MS1 Heatmap")
    with scan_table_view:
        st.title("") # to add empty space on top
        st.write('**Scan Table**')
        st.session_state["selected_scan"] = drawSpectraTable(df_for_spectra_table, 300)

    #### Spectrum plots ####
    # listening selecting row from the spectra table
    if st.session_state.selected_scan["selected_rows"]:
        selected_index = st.session_state.selected_scan["selected_rows"][0]["index"]
        anno_spec_view, deconv_spec_view = st.columns(2)
        with anno_spec_view:
            plotAnnotatedMS(anno_df.loc[selected_index])
        with deconv_spec_view:
            plotDeconvolvedMS(spec_df.loc[selected_index])

    #### Mass table ####
    # listening selecting row from the spectra table
    if st.session_state.selected_scan["selected_rows"]:
        selected_index = st.session_state.selected_scan["selected_rows"][0]["index"]
        selected_spectrum = spec_df.loc[selected_index]
        # preparing data for plotting (cached)
        mass_df = getMassTableDF(selected_spectrum)
        st.write('**Mass Table** of selected spectrum index: %d'%selected_index)
        # drawing interactive mass table
        st.session_state["selected_mass"] = drawSpectraTable(mass_df, 250)

    #### 3D signal plot ####
    # listening selecting row from the spectra table
    if st.session_state.selected_scan["selected_rows"] and \
            ("selected_mass" in st.session_state) and \
            (st.session_state.selected_mass["selected_rows"]):
        selected_spec = spec_df.loc[st.session_state.selected_scan["selected_rows"][0]["index"]]
        mass_signal_df = getMassSignalDF(selected_spec)

        selected_mass_index = st.session_state.selected_mass["selected_rows"][0]["index"]
        plot3d_view, _ = st.columns([9, 1])# for little space on the right
        with plot3d_view:
            draw3DSignalView(mass_signal_df.loc[selected_mass_index])

if __name__ == "__main__":
    # try:
    content()
    # except:
    #     st.warning(ERRORS["visualization"])
