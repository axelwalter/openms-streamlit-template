import numpy as np
import streamlit as st
from src.view import *
from src.common import *
from src.masstable import *
from streamlit_plotly_events import plotly_events

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

    # two main containers
    spectra_container, mass_container = st.columns(2)

    # getting data
    selected = experiment_df[experiment_df['Experiment Name'] == st.session_state.selected_experiment]
    selected_anno_file = selected['Annotated Files'][0]
    selected_deconv_file = selected['Deconvolved Files'][0]

    ## for now, test data
    spec_df, tolerance, massoffset, chargemass = get_mass_table(selected_anno_file, selected_deconv_file)

    with spectra_container:
        # drawing 3D spectra viewer (1st column, top)
        st.subheader('Signal View')
        signal_plot_container = st.empty() # initialzie space for drawing 3d plot

        # drawing spectra table (1st column, bottom)
        st.subheader('Spectrum Table')
        df_for_table = spec_df[['Scan', 'MSLevel', 'RT']]
        df_for_table['#Masses'] = [len(ele) for ele in spec_df['MinCharges']]
        df_for_table.reset_index(inplace=True)
        # spectra_container.dataframe(df_for_table, use_container_width=True)
        st.session_state["index_for_signal_view"] = drawSpectraTable(df_for_table)

        with signal_plot_container.container():
            response = st.session_state["index_for_signal_view"]
            if response["selected_rows"]:
                # st.dataframe(response["selected_rows"])
                selected_index = response["selected_rows"][0]["index"]
                # st.write(selected_index["index"])
                plot3DSignalView(spec_df.loc[selected_index])

    # if not df_MS1.empty:
    #     st.markdown("### Peak Map and MS2 spectra")
    #     c1, c2 = st.columns(2)
    #     c1.number_input(
    #         "2D map intensity cutoff",
    #         1000,
    #         1000000000,
    #         5000,
    #         1000,
    #         key="cutoff",
    #     )
    #     if not df_MS2.empty:
    #         c2.markdown("##")
    #         c2.markdown("💡 Click anywhere to show the closest MS2 spectrum.")
    #     st.session_state.view_fig_map = plot_2D_map(
    #         df_MS1,
    #         df_MS2,
    #         st.session_state.cutoff,
    #     )
    #     # Determine RT and mz positions from clicks in the map to get closest MS2 spectrum
    #     if not df_MS2.empty:
    #         map_points = plotly_events(st.session_state.view_fig_map)
    #         if map_points:
    #             rt = map_points[0]["x"]
    #             prec_mz = map_points[0]["y"]
    #         else:
    #             rt = df_MS2.iloc[0, 2]
    #             prec_mz = df_MS2.iloc[0, 0]
    #         spec = df_MS2.loc[
    #             (
    #                 abs(df_MS2["RT"] - rt) + abs(df_MS2["precursormz"] - prec_mz)
    #             ).idxmin(),
    #             :,
    #         ]
    #         plot_ms_spectrum(
    #             spec,
    #             f"MS2 spectrum @precursor m/z {round(spec['precursormz'], 4)} @RT {round(spec['RT'], 2)}",
    #             "#00CC96",
    #         )
    #     else:
    #         st.plotly_chart(st.session_state.view_fig_map, use_container_width=True)
    #
    #     # BPC and MS1 spec
    #     st.markdown("### Base Peak Chromatogram (BPC)")
    #     st.markdown("💡 Click a point in the BPC to show the MS1 spectrum.")
    #     st.session_state.view_fig_bpc = plot_bpc(df_MS1)
    #
    #     # Determine RT positions from clicks in BPC to show MS1 at this position
    #     bpc_points = plotly_events(st.session_state.view_fig_bpc)
    #     if bpc_points:
    #         st.session_state.view_MS1_RT = bpc_points[0]["x"]
    #     else:
    #         st.session_state.view_MS1_RT = df_MS1.loc[0, "RT"]
    #
    #     spec = df_MS1.loc[df_MS1["RT"] == st.session_state.view_MS1_RT].squeeze()
    #
    #     plot_ms_spectrum(
    #         spec,
    #         f"MS1 spectrum @RT {spec['RT']}",
    #         "#EF553B",
    #     )

if __name__ == "__main__":
    # try:
    content()
    # except:
    #     st.warning(ERRORS["visualization"])
