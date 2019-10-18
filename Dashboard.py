import os
import pathlib

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_table
import plotly.graph_objs as go
import dash_daq as daq

import pandas as pd

#from ControllerLibrary import Port
import ControllerLibrary
import FrontendLibrary
from flask_caching import Cache
#import redis

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
df = pd.read_csv(os.path.join(APP_PATH, os.path.join("data", "spc_data.csv")))

params = list(df)
max_length = len(df)
subsystems = ['Temperature Controller', 'High Side Pressure Controller', 'Calcium Reactor Controller', 'O3 Reactor Controller', 'Light Controller']

#ports = ['Digital Output', 'Digital Input', 'Analog Output', 'Analog Input', 'I2C Port', 'TTL Serial Port', 'RS-485 Port']
#configured_ports = [{'name': 'Heater_1_SSR_Port', 'type': 'DO', 'signal0_pin': 'GPIO0', 'signal1_pin': None, 'power_pin': '5V'}, {'name': 'Heater_2_SSR_Port', 'type': 'DO', 'signal0_pin': 'GPIO1', 'signal1_pin': None, 'power_pin': '5V'}]
configured_ports = [ControllerLibrary.Port(name='Heater_1_SSR_Port', port_type='DO', signal0_pin='GPIO0'),
                    ControllerLibrary.Port(name='Heater_2_SSR_Port', port_type='DO', signal0_pin='GPIO1'),
                    ControllerLibrary.Port(name='Return_Pump_Serial_Port', port_type='TTL_Serial', signal0_pin='GPIO2', signal1_pin='GPIO3')]

configured_devices = [ControllerLibrary.Device(name='Heater_1_SSR', port_type='DO', signal0_pin='GPIO0'),
                      ControllerLibrary.Device(name='Heater_2_SSR', port_type='DO', signal0_pin='GPIO1'),
                      ControllerLibrary.Device(name='Return_Pump_VFD', port_type='TTL_Serial', signal0_pin='GPIO2', signal1_pin='GPIO3')]

#pins = ['GPIO0', 'GPIO1', 'DGND']

suffix_row = "_row"
suffix_button_id = "_button"
suffix_sparkline_graph = "_sparkline_graph"
suffix_count = "_count"
suffix_ooc_n = "_OOC_number"
suffix_ooc_g = "_OOC_graph"
suffix_indicator = "_indicator"

ud_usl_input = daq.NumericInput(
    id="ud_usl_input", className="setting-input", size=200, max=9999999
)
ud_lsl_input = daq.NumericInput(
    id="ud_lsl_input", className="setting-input", size=200, max=9999999
)
ud_ucl_input = daq.NumericInput(
    id="ud_ucl_input", className="setting-input", size=200, max=9999999
)
ud_lcl_input = daq.NumericInput(
    id="ud_lcl_input", className="setting-input", size=200, max=9999999
)

ud_portname_input = dcc.Input(
    id="ud_portname_input", className="setting-input", size=200, max=9999999
)
ud_porttype_input = dcc.Input(
    id="ud_porttype_input", className="setting-input", size=200, max=9999999
)


def InitializeFrontend(hardware_configuration=None, system_manager=None):
    app = dash.Dash(
        __name__,
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )
    #server = app.server
    app.config["suppress_callback_exceptions"] = True

    cache = Cache()
    cache.init_app(app.server, config=FrontendLibrary.CACHE_CONFIG)

    SetAppLayout(app, hardware_configuration)

    @cache.memoize
    def store_hardware_info():
        pass

    @app.callback(
        [Output("app-content", "children"), Output("interval-component", "n_intervals")],
        [Input("app-tabs", "value")],
        [State("n-interval-stage", "data"),
         State("hardware-config-store", "data")],
    )
    def render_tab_content(tab_switch, stopped_interval, hardware_configuration):
        if tab_switch == "tab1":
            #return build_hardware_config_tab(), stopped_interval
            return build_hardware_config_tab(hardware_configuration), stopped_interval
        if tab_switch == "tab2":
            return build_tab_1(), stopped_interval
        return (
            html.Div(
                id="status-container",
                children=[
                    build_quick_stats_panel(),
                    html.Div(
                        id="graphs-container",
                        children=[build_top_panel(stopped_interval), build_chart_panel()],
                    ),
                ],
            ),
            stopped_interval,
        )

    @app.callback(
        output=[Output("dummy_output", "children")],
        inputs=[Input("save-hardware-config-btn", "n_clicks")],
        state=[State("hardware-config-store", "data")]
    )
    def save_hardware_configuration(button_clicks, hardware_configuration):
        if button_clicks:
            ControllerLibrary.SaveHardwareConfiguration(hardware_configuration=hardware_configuration)
        return [0]
        #raise PreventUpdate

    @app.callback(
        output=[Output("dummy_output2", "children")],
        inputs=[Input("load-hardware-config-to-controller-btn", "n_clicks")],
        state=[State("hardware-config-store", "data")]
    )
    def load_hardware_config_to_controller(button_clicks, hardware_configuration):
        if button_clicks:
            #ControllerLibrary.SaveHardwareConfiguration(hardware_configuration=hardware_configuration)
            system_manager.command_queue.put("abc")
        return [0]

    @app.callback(
        output=Output("progress-gauge", "value"),
        inputs=[Input("interval-component", "n_intervals")],
    )
    def update_gauge(interval):
        if interval < max_length:
            total_count = interval
        else:
            total_count = max_length

        return int(total_count)

    # ===== Callbacks to update values based on store data and dropdown selection =====
    # @app.callback(
    #     output=[
    #         Output("value-setter-panel", "children"),
    #         Output("ud_usl_input", "value"),
    #         Output("ud_lsl_input", "value"),
    #         Output("ud_ucl_input", "value"),
    #         Output("ud_lcl_input", "value"),
    #     ],
    #     inputs=[Input("metric-select-dropdown", "value")],
    #     state=[State("value-setter-store", "data")],
    # )
    # def build_value_setter_panel(dd_select, state_value):
    #     return (
    #         [
    #             build_value_setter_toggle(
    #                 "value-setter-panel-toggle",
    #                 "Toggle",
    #                 state_dict[dd_select]["lcl"],
    #                 ud_lcl_input,
    #             ),
    #             build_value_setter_line(
    #                 "value-setter-panel-header",
    #                 "Parameter",
    #                 "Historical Value",
    #                 "Set new value",
    #             ),
    #             build_value_setter_line(
    #                 "value-setter-panel-usl",
    #                 "Upper Specification limit",
    #                 state_dict[dd_select]["usl"],
    #                 ud_usl_input,
    #             ),
    #             build_value_setter_line(
    #                 "value-setter-panel-lsl",
    #                 "Lower Specification limit",
    #                 state_dict[dd_select]["lsl"],
    #                 ud_lsl_input,
    #             ),
    #             build_value_setter_line(
    #                 "value-setter-panel-ucl",
    #                 "Upper Control limit",
    #                 state_dict[dd_select]["ucl"],
    #                 ud_ucl_input,
    #             ),
    #             build_value_setter_line(
    #                 "value-setter-panel-lcl",
    #                 "Lower Control limit",
    #                 state_dict[dd_select]["lcl"],
    #                 ud_lcl_input,
    #             ),
    #         ],
    #         state_value[dd_select]["usl"],
    #         state_value[dd_select]["lsl"],
    #         state_value[dd_select]["ucl"],
    #         state_value[dd_select]["lcl"],
    #     )

    @app.callback(
        output=[
            Output("port-setter-panel", "children"),
            #Output("ud_portname_input", "value"),
            #Output("ud_porttype_input", "value"),
            #Output("ud_lsl_input", "value"),
            #Output("ud_ucl_input", "value"),
            #Output("ud_lcl_input", "value"),
        ],
        inputs=[Input("port-select-dropdown", "value")],
        state=[State("hardware-config-store", "data")],
    )
    def build_port_setter_panel(port_name, hardware_config):#, state_value):
        #port_list = [port if port.name == port_name else None for port in configured_ports]
        # for port in configured_ports:
        #     if port.name == port_name:
        #         break
        port = FrontendLibrary.lookup_port_by_name(port_name=port_name, configured_ports=configured_ports)
        return (
            [
                # build_value_setter_toggle(
                #     "value-setter-panel-toggle",
                #     "Toggle",
                #     state_dict[dd_select]["lcl"],
                #     ud_lcl_input,
                # ),
                build_value_setter_line(
                    "value-setter-panel-header",
                    "Parameter",
                    "Historical Value",
                    "Set new value",
                ),
            ]
            + [build_port_config_line('port_line', port, key) for key in sorted(list(port.__dict__.keys()))],
        )

    @app.callback(
        inputs=[Input("hardware-config-store", "data")],
        output=[Output("device-update-signal", "children")],
        state=[State("device-update-signal", "children")]
    )
    def update_device_update_signal(hardware_configuration, update_signal):
        system_manager.command_queue.put("update")
        return [update_signal + 1]

    @app.callback(
        output=[
            Output("device-config-panel", "children"),
            # Output("ud_portname_input", "value"),
            # Output("ud_porttype_input", "value"),
            # Output("ud_lsl_input", "value"),
            # Output("ud_ucl_input", "value"),
            # Output("ud_lcl_input", "value"),
        ],
        inputs=[Input("device-select-dropdown", "value")],#, Input("device-update-signal", "children")],
        state=[State("hardware-config-store", "data")],
    )
    def build_device_config_panel(device_name, hardware_configuration):
        hardware_configuration = ControllerLibrary.UnpackHardwareConfiguration(hardware_configuration)
        interaction_buttons = [html.Div(
            id="button-div",
            children=[html.Button("Update Device",
                                  id="update-device-btn",
                                  className="hardware-config-tab-btn",
                                  n_clicks_timestamp=0),
                      html.Button("Delete Device",
                                  id="delete-device-btn",
                                  className="hardware-config-tab-btn",
                                  disabled=False,
                                  n_clicks_timestamp=0),
                      ],
            ),
        ]
        if device_name == "new_device":
            interaction_buttons[0].children[1].disabled = True
            device_type_selection_line = build_device_config_line(div_id='device-type-selection-line',
                                                                  device_name=device_name, device_type="Unknown",
                                                                  attribute="device_type",
                                                                  input_object_id="device-type-selection-dropdown")

        else:
            try:
                device_type_selection_line = build_device_config_line(div_id='device-type-selection-line',
                                                                      device_name=device_name, device_type=hardware_configuration['devices'][device_name]['device_type'],
                                                                      attribute="device_type",
                                                                      input_object_id="device-type-selection-dropdown",
                                                                      input_value=hardware_configuration['devices'][device_name]['device_type'])
            except Exception:
                raise PreventUpdate

        return [
            [device_type_selection_line]
            + [html.Div(id="device-attributes-subpanel")]
            + [html.Br()]
            + interaction_buttons
        ]

    @app.callback(
        inputs=[Input("route-select-dropdown", "value")],
        output=[Output("route-config-panel", "children")],
        state=[State("hardware-config-store", "data")]
    )
    def build_route_select_panel(device_name, hardware_configuration):
        #a = 5
        hardware_configuration = ControllerLibrary.UnpackHardwareConfiguration(hardware_configuration)

        # route_panel_header = build_hardware_config_line(
        #     "route-config-panel-header",
        #     "Origin",
        #     "Destination",
        #     "Set new value",
        # )

        route_panel_header = html.Div(
            id="route-config-panel-header",
            children=[
                html.Label("Segment No.", className="four columns"),
                html.Label("Origin", className="four columns"),
                html.Label("Destination", className="four columns")
            #input
            #html.Label(input, className="four columns"),
            #html.Div(col3, className="four columns"),
            ],
            className="row"
        )

        interaction_buttons = [html.Br(), html.Div(
            id="button-div",
            children=[
                # html.Button("Add Segment",
                #                   id="add-route-segment-btn",
                #                   className="hardware-config-tab-btn",
                #                   n_clicks_timestamp=0),
                      html.Button("Update Route",
                                  id="update-route-btn",
                                  className="update-route-btn",
                                  disabled=False,
                                  n_clicks_timestamp=0),
                      ],
            ),
        ]

        route_config_segments = []
        for route_segment_ndx in range(len(hardware_configuration['routes'][device_name])):
            destination_select_options = ['rpi'] + list(hardware_configuration['devices'].keys())
            destination_select_options.remove(hardware_configuration['devices'][device_name]['name'])
            if destination_select_options is None:
                destination_select_options = [{'label': 'No Device Available', 'value': 'none'}]
            else:
                destination_select_options = [{'label':device,'value':device} for device in destination_select_options]
            route_config_segments += [build_route_config_line(id="route-segment-line" + str(route_segment_ndx),
                                                             segment_number=route_segment_ndx,
                                                             label=hardware_configuration['routes'][device_name][route_segment_ndx][0],
                                                             input=dcc.Dropdown(id="route-segment-" + str(route_segment_ndx),
                                                                                options=destination_select_options,
                                                                                className=None),
                                                             className="four columns")]

        # route_config_segments += [html.Div(
        #     id="add-segment-row",
        #     children=[
        #         html.Button("Add Segment",
        #                     id="add-route-segment-btn",
        #                     className="hardware-config-tab-btn",
        #                     n_clicks_timestamp=0),
        #     #input
        #     #html.Label(input, className="four columns"),
        #     #html.Div(col3, className="four columns"),
        #     ],
        #     className="row",
        # )]
        # if device_name == "new_device":
        #     interaction_buttons[0].children[1].disabled = True
        #     device_type_selection_line = build_device_config_line(div_id='device-type-selection-line',
        #                                                           device_name=device_name, device_type="Unknown",
        #                                                           attribute="device_type",
        #                                                           input_object_id="device-type-selection-dropdown")
        #
        # else:
        #     try:
        #         device_type_selection_line = build_device_config_line(div_id='device-type-selection-line',
        #                                                               device_name=device_name, device_type=
        #                                                               hardware_configuration['devices'][device_name][
        #                                                                   'device_type'],
        #                                                               attribute="device_type",
        #                                                               input_object_id="device-type-selection-dropdown",
        #                                                               input_value=
        #                                                               hardware_configuration['devices'][device_name][
        #                                                                   'device_type'])
        #     except Exception:
        #         raise PreventUpdate

        return [[route_panel_header] + route_config_segments]
        # return [
        #     [device_type_selection_line]
        #     + [html.Div(id="device-attributes-subpanel")]
        #     + interaction_buttons
        # ]

    # @app.callback(
    #     inputs=[Input("add-route-segment-btn", "n_clicks")],
    #     output=[Output("route-select-dropdown", "value")],
    #     state=[State("route-config-panel", "children"),
    #            State("route-select-dropdown", "value"),
    #            State("hardware-config-store", "data")]
    # )
    # def add_route_segment(button_clicks, route_config_panel, route, hardware_configuration):
    #     if not button_clicks:
    #         raise PreventUpdate
    #     route_segments = 5
    #
    #     route_config_segments += [build_route_config_line(id="route-segment-line" + str(route_segment_ndx),
    #                                                       segment_number=route_segment_ndx,
    #                                                       label=hardware_configuration['routes'][device_name][
    #                                                           route_segment_ndx][0],
    #                                                       input=dcc.Dropdown(
    #                                                           id="route-segment-" + str(route_segment_ndx),
    #                                                           options=destination_select_options,
    #                                                           className=None),
    #                                                       className="four columns")]
        # complete_route = []
        # for route_segment_ndx in range(0, len(route_config_panel)):
        #     panel_line_items = route_config_panel[route_segment_ndx]['props']
        #     try:
        #         if "route-segment-line" in panel_line_items['id']:
        #             segment_row = panel_line_items['children']
        #             route_destination = panel_line_items['children'][2]['props']['value']
        #             complete_route += [route_destination]
        #     except KeyError:
        #         pass
        # print(complete_route)
            #route_segment = route_config_panel[route_segment_ndx]['props']['children']

    def update_route():
        complete_route = []
        for route_segment_ndx in range(0, len(route_config_panel)):
            panel_line_items = route_config_panel[route_segment_ndx]['props']
            try:
                if "route-segment-line" in panel_line_items['id']:
                    segment_row = panel_line_items['children']
                    route_destination = panel_line_items['children'][2]['props']['value']
                    complete_route += [route_destination]
            except KeyError:
                pass
        print(complete_route)
        # route_segment = route_config_panel[route_segment_ndx]['props']['children']

    @app.callback(
        output=[Output("device-attributes-subpanel", "children")],
        inputs=[Input("device-type-selection-dropdown", "value")],
        state=[State("device-select-dropdown", "value"),
               State("hardware-config-store", "data")]
    )
    def build_device_attributes_subpanel(device_type=None, device_name=None, hardware_configuration=None):
        hardware_configuration = ControllerLibrary.UnpackHardwareConfiguration(hardware_configuration)
        if device_type != None:
            return [
                #[build_device_config_line(div_id='device-config-line', device_name=device_name, device_type=device_type, attribute=key, input_object_id=device_type + '.' + key + '.' + ControllerLibrary.HAL.SUPPORTED_DEVICES[device_type][key]) for key in list(ControllerLibrary.HAL.SUPPORTED_DEVICES[device_type].keys())]
                [build_device_config_line(div_id='device-config-line', device_name=device_name, device_type=device_type,
                                          attribute=key, input_value=hardware_configuration['devices'][device_name][key] if device_name != 'new_device' else '', input_object_id=device_type + '.' + key + '.' +
                                                                         ControllerLibrary.HAL.SUPPORTED_DEVICES[
                                                                             device_type][key]) for key in
                list(ControllerLibrary.HAL.SUPPORTED_DEVICES[device_type].keys())]
                #+ [build_device_config_attribute_addition_line("add-device-attribute-line")]
            ]
        else:
            return ([html.Label("Select Device Type...", className="four columns")])

    # @app.callback(
    #
    # )
    # def build_route_segments_subpanel():
    #     pass

    # ====== Callbacks to update stored data via click =====
    # @app.callback(
    #     output=Output("value-setter-store", "data"),
    #     inputs=[Input("value-setter-set-btn", "n_clicks")],
    #     state=[
    #         State("metric-select-dropdown", "value"),
    #         State("value-setter-store", "data"),
    #         State("ud_usl_input", "value"),
    #         State("ud_lsl_input", "value"),
    #         State("ud_ucl_input", "value"),
    #         State("ud_lcl_input", "value"),
    #     ],
    # )
    # def set_value_setter_store(set_btn, param, data, usl, lsl, ucl, lcl):
    #     if set_btn is None:
    #         return data
    #     else:
    #         data[param]["usl"] = usl
    #         data[param]["lsl"] = lsl
    #         data[param]["ucl"] = ucl
    #         data[param]["lcl"] = lcl
    #
    #         # Recalculate ooc in case of param updates
    #         data[param]["ooc"] = populate_ooc(df[param], ucl, lcl)
    #         return data

    # @app.callback(
    #     #output=Output("port-setter-store", 'configuration'),
    #     output=Output("metric-select-dropdown", "value"),
    #     inputs=[Input("update-port-btn", "n_clicks")],
    #     state=[
    #         State("metric-select-dropdown", "value"),
    #         State("value-setter-store", "data"),
    #         State("ud_usl_input", "value"),
    #         State("ud_lsl_input", "value"),
    #         State("ud_ucl_input", "value"),
    #         State("ud_lcl_input", "value"),
    #     ]
    #             #Input("load_hardware_config-btn", 'n-clicks'),
    #             #Input("add-port-btn", 'n-clicks'),
    #             #Input("port-select-dropdown", 'value'),
    #             #Input("port-setter-panel", 'children')],
    # )
    # def update_port(clicks, port_name=None, port_setter_panel=None):
    #     port = FrontendLibrary.lookup_port_by_name(port_name=port_name, configured_ports=configured_ports)
    #
    #     return 1

    # @app.callback(
    #     output=Output("port-setter-store", "data"),
    #     inputs=[Input("value-setter-set-btn", "n_clicks")],
    #     state=[
    #         State("metric-select-dropdown", "value"),
    #         State("value-setter-store", "data"),
    #         State("ud_usl_input", "value"),
    #         State("ud_lsl_input", "value"),
    #         State("ud_ucl_input", "value"),
    #         State("ud_lcl_input", "value"),
    #     ],
    # )
    # def set_value_setter_store(set_btn, param, data, usl, lsl, ucl, lcl):
    #     if set_btn is None:
    #         return data
    #     else:
    #         data[param]["usl"] = usl
    #         data[param]["lsl"] = lsl
    #         data[param]["ucl"] = ucl
    #         data[param]["lcl"] = lcl
    #
    #         # Recalculate ooc in case of param updates
    #         data[param]["ooc"] = populate_ooc(df[param], ucl, lcl)
    #         return data

    @app.callback(
        output=Output("value-setter-view-output", "children"),
        inputs=[
            Input("value-setter-view-btn", "n_clicks"),
            Input("metric-select-dropdown", "value"),
            Input("value-setter-store", "data"),
        ],
    )
    def show_current_specs(n_clicks, dd_select, store_data):
        if n_clicks > 0:
            curr_col_data = store_data[dd_select]
            new_df_dict = {
                "Specs": [
                    "Upper Specification Limit",
                    "Lower Specification Limit",
                    "Upper Control Limit",
                    "Lower Control Limit",
                ],
                "Current Setup": [
                    curr_col_data["usl"],
                    curr_col_data["lsl"],
                    curr_col_data["ucl"],
                    curr_col_data["lcl"],
                ],
            }
            new_df = pd.DataFrame.from_dict(new_df_dict)
            return dash_table.DataTable(
                style_header={"fontWeight": "bold", "color": "inherit"},
                style_as_list_view=True,
                fill_width=True,
                style_cell_conditional=[
                    {"if": {"column_id": "Specs"}, "textAlign": "left"}
                ],
                style_cell={
                    "backgroundColor": "#1e2130",
                    "fontFamily": "Open Sans",
                    "padding": "0 2rem",
                    "color": "darkgray",
                    "border": "none",
                },
                css=[
                    {"selector": "tr:hover td", "rule": "color: #91dfd2 !important;"},
                    {"selector": "td", "rule": "border: none !important;"},
                    {
                        "selector": ".dash-cell.focused",
                        "rule": "background-color: #1e2130 !important;",
                    },
                    {"selector": "table", "rule": "--accent: #1e2130;"},
                    {"selector": "tr", "rule": "background-color: transparent"},
                ],
                data=new_df.to_dict("rows"),
                columns=[{"id": c, "name": c} for c in ["Specs", "Current Setup"]],
            )

    @app.callback(
        output=Output("port-setter-view-output", "children"),
        inputs=[
            Input("port-setter-view-btn", "n_clicks"),
            Input("port-select-dropdown", "value"),
            Input("port-setter-store", "data"),
        ],
    )
    def show_current_hardware_config(n_clicks, dd_select, store_data):
        if n_clicks > 0:
            curr_col_data = store_data[dd_select]
            new_df_dict = {
                "Specs": [
                    "Upper Specification Limit",
                    "Lower Specification Limit",
                    "Upper Control Limit",
                    "Lower Control Limit",
                ],
                "Current Setup": [
                    curr_col_data["usl"],
                    curr_col_data["lsl"],
                    curr_col_data["ucl"],
                    curr_col_data["lcl"],
                ],
            }
            new_df = pd.DataFrame.from_dict(new_df_dict)
            return dash_table.DataTable(
                style_header={"fontWeight": "bold", "color": "inherit"},
                style_as_list_view=True,
                fill_width=True,
                style_cell_conditional=[
                    {"if": {"column_id": "Specs"}, "textAlign": "left"}
                ],
                style_cell={
                    "backgroundColor": "#1e2130",
                    "fontFamily": "Open Sans",
                    "padding": "0 2rem",
                    "color": "darkgray",
                    "border": "none",
                },
                css=[
                    {"selector": "tr:hover td", "rule": "color: #91dfd2 !important;"},
                    {"selector": "td", "rule": "border: none !important;"},
                    {
                        "selector": ".dash-cell.focused",
                        "rule": "background-color: #1e2130 !important;",
                    },
                    {"selector": "table", "rule": "--accent: #1e2130;"},
                    {"selector": "tr", "rule": "background-color: transparent"},
                ],
                data=new_df.to_dict("rows"),
                columns=[{"id": c, "name": c} for c in ["Specs", "Current Setup"]],
            )

    # Update interval
    @app.callback(
        Output("n-interval-stage", "data"),
        [Input("app-tabs", "value")],
        [
            State("interval-component", "n_intervals"),
            State("interval-component", "disabled"),
            State("n-interval-stage", "data"),
        ],
    )
    def update_interval_state(tab_switch, cur_interval, disabled, cur_stage):
        if disabled:
            return cur_interval

        if tab_switch == "tab1":
            return cur_interval
        return cur_stage

    # Callbacks for stopping interval update
    @app.callback(
        [Output("interval-component", "disabled"), Output("stop-button", "buttonText")],
        [Input("stop-button", "n_clicks")],
        [State("interval-component", "disabled")],
    )
    def stop_production(n_clicks, current):
        if n_clicks == 0:
            return True, "start"
        return not current, "stop" if current else "start"

    # ======= Callbacks for modal popup =======
    @app.callback(
        Output("markdown", "style"),
        [Input("learn-more-button", "n_clicks"), Input("markdown_close", "n_clicks")],
    )
    def update_click_output(button_click, close_click):
        ctx = dash.callback_context

        if ctx.triggered:
            prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if prop_id == "learn-more-button":
                return {"display": "block"}

        return {"display": "none"}

    for param in params[1:]:
        update_param_row_function = create_callback(param)
        app.callback(
            output=[
                Output(param + suffix_count, "children"),
                Output(param + suffix_sparkline_graph, "extendData"),
                Output(param + suffix_ooc_n, "children"),
                Output(param + suffix_ooc_g, "value"),
                Output(param + suffix_indicator, "color"),
            ],
            inputs=[Input("interval-component", "n_intervals")],
            state=[State("value-setter-store", "data")],
        )(update_param_row_function)

    #  ======= button to choose/update figure based on click ============
    @app.callback(
        output=Output("control-chart-live", "figure"),
        inputs=[
            Input("interval-component", "n_intervals"),
            Input(params[1] + suffix_button_id, "n_clicks"),
            Input(params[2] + suffix_button_id, "n_clicks"),
            Input(params[3] + suffix_button_id, "n_clicks"),
            Input(params[4] + suffix_button_id, "n_clicks"),
            Input(params[5] + suffix_button_id, "n_clicks"),
            Input(params[6] + suffix_button_id, "n_clicks"),
            Input(params[7] + suffix_button_id, "n_clicks"),
        ],
        state=[State("value-setter-store", "data"), State("control-chart-live", "figure")],
    )
    def update_control_chart(interval, n1, n2, n3, n4, n5, n6, n7, data, cur_fig):
        # Find which one has been triggered
        ctx = dash.callback_context

        if not ctx.triggered:
            return generate_graph(interval, data, params[1])

        if ctx.triggered:
            # Get most recently triggered id and prop_type
            splitted = ctx.triggered[0]["prop_id"].split(".")
            prop_id = splitted[0]
            prop_type = splitted[1]

            if prop_type == "n_clicks":
                curr_id = cur_fig["data"][0]["name"]
                prop_id = prop_id[:-7]
                if curr_id == prop_id:
                    return generate_graph(interval, data, curr_id)
                else:
                    return generate_graph(interval, data, prop_id)

            if prop_type == "n_intervals" and cur_fig is not None:
                curr_id = cur_fig["data"][0]["name"]
                return generate_graph(interval, data, curr_id)

    # Update piechart
    @app.callback(
        output=Output("piechart", "figure"),
        inputs=[Input("interval-component", "n_intervals")],
        state=[State("value-setter-store", "data")],
    )
    def update_piechart(interval, stored_data):
        if interval == 0:
            return {
                "data": [],
                "layout": {
                    "font": {"color": "white"},
                    "paper_bgcolor": "rgba(0,0,0,0)",
                    "plot_bgcolor": "rgba(0,0,0,0)",
                },
            }

        if interval >= max_length:
            total_count = max_length - 1
        else:
            total_count = interval - 1

        values = []
        colors = []
        for param in params[1:]:
            ooc_param = (stored_data[param]["ooc"][total_count] * 100) + 1
            values.append(ooc_param)
            if ooc_param > 6:
                colors.append("#f45060")
            else:
                colors.append("#91dfd2")

        new_figure = {
            "data": [
                {
                    "labels": params[1:],
                    "values": values,
                    "type": "pie",
                    "marker": {"colors": colors, "line": dict(color="white", width=2)},
                    "hoverinfo": "label",
                    "textinfo": "label",
                }
            ],
            "layout": {
                "margin": dict(t=20, b=50),
                "uirevision": True,
                "font": {"color": "white"},
                "showlegend": False,
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "autosize": True,
            },
        }
        return new_figure

    @app.callback(
        dash.dependencies.Output('subsystem-on-off-output', 'children'),
        [dash.dependencies.Input('subsystem-on-off', 'value')])
    def update_output(value):
        return 'The switch is {}.'.format(value)

    # @app.callback(
    #     inputs=[Input("update-port-btn", "n_clicks")],
    #     output=Output("hardware_config_button_clicks", "children"),
    #     state=[State("hardware_config_button_clicks", "children")]
    # )
    # def update_hardware_config_button_clicks(update_port_button_num_clicks, prev_clicks):
    #     #return
    #     if update_port_button_num_clicks != None:
    #
    #     pass

    # @app.callback(
    #     output=Output("hardware-config-store", "data"),
    #     inputs=[Input("update-port-btn", "n_clicks")],
    #     state=[State("port-select-dropdown", "value"),
    #            State("port-setter-panel", "children"),
    #            State("hardware-config-store", "data")]
    # )
    # def update_port(button_clicks, port_name, port_setter_panel_items, current_hardware_config):
    #     if button_clicks != None and port_name != None:
    #         port = FrontendLibrary.lookup_port_by_name(port_name=port_name, configured_ports=configured_ports)
    #         port = ControllerLibrary.Port()
    #         for item in port_setter_panel_items:
    #             if item['props']['id'] == 'port_line':
    #                 data_line = item['props']['children']
    #                 data_label = data_line[0]['props']['children']
    #                 data_value = data_line[1]['props']['children']['props']['value']
    #                 if data_value != None:
    #                     setattr(port,data_label,data_value)
    #                     #port_index = FrontendLibrary.lookup_port_index_in_hardware_configuration(port=port, port_configuration=current_hardware_config['ports'])
    #         current_hardware_config['ports'][port.name] = port.TextSerialize()
    #                     # if port_index >= 0:
    #                     #     current_hardware_config['ports'][port_index] = port.Serialize()
    #                     # else:
    #                     #     current_hardware_config['ports'] += [port.Serialize()]
    #     return current_hardware_config
    #             #prop_name = prop['props']['children']
    #         #print('updating')
    #
    #         #return {}

#State("hardware-config-store", "data"),
#State("route-select-dropdown", "value"),
#Input("add-route-segment-btn", "n_clicks_timestamp")
#Input("update-route-btn", "n_clicks_timestamp")
#Output("route-select-dropdown", "value")
    @app.callback(
        inputs=[Input("update-device-btn", "n_clicks_timestamp"),
                Input("delete-device-btn", "n_clicks_timestamp"),
                Input("add-route-segment-btn", "n_clicks_timestamp"),
                Input("update-route-btn", "n_clicks_timestamp")],
        output=[Output("hardware-config-store", "data"),
                Output("device-select-dropdown", "options"),
                Output("device-select-dropdown", "value"),
                Output("route-select-dropdown", "options"),
                Output("route-select-dropdown", "value")],
        state=[State("hardware-config-store", "data"),
               State("device-attributes-subpanel", "children"),
               State("route-config-panel", "children"),
               State("device-select-dropdown", "value"),
               State("route-select-dropdown", "value"),
               State("device-type-selection-line", "children")]
    )
    def update_hardware(update_button_click_timestamp, delete_button_click_timestamp, add_segment_button_click_timestamp, update_route_button_click_timestamp, hardware_configuration, configuration_panel_lines, route_panel_lines, device_name, route_name, device_type_dropdown_div):
        ordered_timestamps = {update_button_click_timestamp: 'update_device',
                              delete_button_click_timestamp: 'delete_device',
                              add_segment_button_click_timestamp: 'add_segment',
                              update_route_button_click_timestamp: 'update_route'}
        button_clicked = ordered_timestamps[sorted(ordered_timestamps.keys(), reverse=True)[0]]
        if button_clicked == 'update_device':
            #if button_click != None:
            hardware_configuration = ControllerLibrary.UnpackHardwareConfiguration(hardware_configuration)
            device_type = device_type_dropdown_div[1]['props']['children']['props']['value']
            device_definition = {'device_type': device_type}
            for line in configuration_panel_lines:
                if line['props']['id'] == 'device-config-line':
                    input_object = line['props']['children'][1]['props']['children']['props']
                    attribute_name = input_object['id'].split('.')[1]
                    input_value = input_object['value']
                    device_definition[attribute_name] = input_value
            try:
                hardware_configuration['devices'][device_definition['name']] = device_definition
                hardware_configuration['routes'][device_definition['name']] = [(device_definition['name'], 'rpi')]
            except Exception as e:
                pass
            #hardware_configuration['updates'] = hardware_configuration['updates'] + 1

            # device_select_dropdown_options = [{"label": 'New Device...', "value": "new_device"}] + [
            #     {"label": hardware_configuration['devices'][device]['name'], "value": hardware_configuration['devices'][device]['name']} for
            #     device in hardware_configuration['devices'].keys()]
            device_select_dropdown_options = FrontendLibrary.build_device_selector_dropdown_options_list(hardware_configuration)
                # [{"label": 'New Device...', "value": "new_device"}] + [
                # {"label": device + ' (' + hardware_configuration['devices'][device]['device_type'] + ')',
                #  "value": device} for device
                # in hardware_configuration['devices']]
            return [hardware_configuration], device_select_dropdown_options, device_definition['name'], FrontendLibrary.build_route_selector_options_list(hardware_configuration), [route_name]
        elif button_clicked == "delete_device":
            raise PreventUpdate
        elif button_clicked == "add_segment":
            a=5
        else:
            raise PreventUpdate


    return app, cache#, server

def build_banner(app=None):
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("210 Gallon Reef Tank Dashboard"),
                    html.H6("Water Parameter Control and Monitoring"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.Button(
                        id="learn-more-button", children="LEARN MORE", n_clicks=0
                    ),
                    html.Img(id="logo", src=app.get_asset_url("dongle.png")),
                ],
            ),
        ],
    )


def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab1",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Hardware-config-tab",
                        label="Hardware Configuration",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Controller-settings-tab",
                        label="Tank Controller Settings",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Control-chart-tab",
                        label="Control Charts Dashboard",
                        value="tab3",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    # dcc.Tab(
                    #     id="pH-chart-tab",
                    #     label="pH Data",
                    #     value="tab4",
                    #     className="custom-tab",
                    #     selected_className="custom-tab--selected",
                    # ),
                ],
            )
        ],
    )


def init_df():
    ret = {}
    for col in list(df[1:]):
        data = df[col]
        stats = data.describe()

        std = stats["std"].tolist()
        ucl = (stats["mean"] + 3 * stats["std"]).tolist()
        lcl = (stats["mean"] - 3 * stats["std"]).tolist()
        usl = (stats["mean"] + stats["std"]).tolist()
        lsl = (stats["mean"] - stats["std"]).tolist()

        ret.update(
            {
                col: {
                    "count": stats["count"].tolist(),
                    "data": data,
                    "mean": stats["mean"].tolist(),
                    "std": std,
                    "ucl": round(ucl, 3),
                    "lcl": round(lcl, 3),
                    "usl": round(usl, 3),
                    "lsl": round(lsl, 3),
                    "min": stats["min"].tolist(),
                    "max": stats["max"].tolist(),
                    "ooc": populate_ooc(data, ucl, lcl),
                }
            }
        )

    return ret


def populate_ooc(data, ucl, lcl):
    ooc_count = 0
    ret = []
    for i in range(len(data)):
        if data[i] >= ucl or data[i] <= lcl:
            ooc_count += 1
            ret.append(ooc_count / (i + 1))
        else:
            ret.append(ooc_count / (i + 1))
    return ret


state_dict = init_df()


def init_value_setter_store():
    # Initialize store data
    state_dict = init_df()
    return state_dict

def init_hardware_config_store():
    return {'ports': {}, 'muxes': {}}

def build_hardware_config_tab(hardware_configuration={}):
    #available_devices = list({"label": device, "value": device} for device in ControllerLibrary.HAL.SUPPORTED_DEVICES)
    hardware_configuration = ControllerLibrary.UnpackHardwareConfiguration(hardware_configuration)
    device_selector_options = FrontendLibrary.build_device_selector_dropdown_options_list(hardware_configuration)
    return [
        # Manually select metrics
        html.Div(
            id="set-hardware-config-intro-container",
            # className='twelve columns',
            children=[
                html.P(
                "Configure Controller Ports, Devices, and Routes"),
                html.Button(
                    "Save Hardware Configuration to Disk",
                    id="save-hardware-config-btn",
                    n_clicks=0,
                    className="hardware-config-tab-btn"),
                html.Button(
                    "Load Hardware Configuration to Controller",
                    id="load-hardware-config-to-controller-btn",
                    n_clicks=0,
                    className="hardware-config-tab-btn"),
            ],
        ),

        html.Div(id="device-config-section",
                 children=[
                html.Div(
                    id="hardware-config-subheading",
                    children=html.P("Devices")),

                #Devices menu
                html.Div(
                    id="devices-menu",
                    children=[
                        html.Div(
                            id="device-select-menu",
                            children=[
                                html.Label(id="device-select-title", children="Select Device"),
                                html.Br(),
                                dcc.Dropdown(
                                    id="device-select-dropdown",
                                    options=device_selector_options,
                                    value=device_selector_options[0]['value']
                                ),
                            ],
                        ),
                        html.Div(
                            id="device-config-menu",
                            children=[
                                html.Div(id="device-config-panel"),
                                #html.Br(),
                            ],
                        ),
                    ],
                ),
             ]
         ),

        html.Div(id="route-config-section",
                 children=[
                html.Div(id="hardware-config-subheading",
                         children=html.P("Routing")),
                html.Div(
                    id="routing-menu",
                    children=[
                        html.Div(
                            id="route-select-menu",
                            children=[
                                html.Label(id="route-select-title", children="Select Route"),
                                html.Br(),
                                dcc.Dropdown(
                                    id="route-select-dropdown",
                                    options=FrontendLibrary.build_route_selector_options_list(hardware_configuration=hardware_configuration)
                                ),
                                html.Br(),
                                html.Button("Add Segment",
                                            id="add-route-segment-btn",
                                            className="hardware-config-tab-btn",
                                            n_clicks_timestamp=0),
                                html.Button("Update Route",
                                            id="update-route-btn",
                                            className="update-route-btn",
                                            disabled=False,
                                            n_clicks_timestamp=0),
                                ]
                        ),
                        # html.Div(
                        #     id="route-config-menu",
                        #     children=[
                        #         html.Div(id="route-config-panel"),
                        #         # html.Br(),
                        #         ],
                        #     ),
                        html.Div(id='configuration-table-container', children=[
                            dt.DataTable(id='route-table',
                                         columns=[{'name': "Origin", 'id': "origin"}, {'name': "Destination", 'id': "destination", "presentation": "dropdown"}],
                                         data=[{"origin": 1, "destination": ""}],
                                         style_cell={'padding': '5px',
                                                     'color': 'black'},
                                         style_header={
                                             'backgroundColor': 'gray',
                                             'fontWeight': 'bold'
                                         },
                                         editable=True,
                                         dropdown={
                                             'destination': {
                                                 'options': [
                                                     {'label': 'a', 'value': 'a'},
                                                     {'label': 'b', 'value': 'b'}
                                                 ]
                                             }
                                         }
                                         )
                        ])

                        ]
                    ),
                     # html.Div(id='table-container', children=[
                     #     dt.DataTable(id='route-table',
                     #                  columns=[{'name': "col1", 'id': "col1"}, {'name': "col2", 'id': "col2"}],
                     #                  data=[{"col1": 1, "col2": 2}, {"col1": 1, "col2": 2}],
                     #                  style_cell={'padding': '5px',
                     #                              'color': 'black'},
                     #                  style_header={
                     #                      'backgroundColor': 'gray',
                     #                      'fontWeight': 'bold'
                     #                  },
                     #                  editable=True
                     #                  )
                     # ])
                ]
            ),
                                        # input
                                        # html.Label(input, className="four columns"),
                                        # html.Div(col3, className="four columns"),
                                    #className="row",



        html.Div(id='hardware_config_button_clicks', children='update_port:0|add_port:0', style={'display': 'none'}),
        html.Div(id='device-update-signal', children=0, style={'display': 'none'}),
        html.Div(id="dummy_output", children=0, style={'display': 'none'}),
        html.Div(id="dummy_output2", children=0, style={'display': 'none'})
    ]

def build_controller_settings_tab():
    return [
        # Manually select metrics
        html.Div(
            id="controller-settings-intro-container",
            # className='twelve columns',
            children=html.P(
                "Set up devices connected to system."
            ),
        ),
        html.Div(
            id="port-menu",
            children=[
                html.Div(
                    id="port-name-headers",
                    #className="two columns",
                    children=[
                        html.Label(id="port-name-entry-title", children="Port Name", className="two columns"),
                        html.Label(id="port-name-entry-title", children="Port Type", className="two columns"),
                    ],
                ),
                html.Br(),
                html.Div(
                    id="port-data-entry",
                    # className='five columns',
                    children=[
                        dcc.Input(
                            id="port{}-name-text".format("0"),
                            type="text",
                            placeholder="Port Name",
                            className="two columns",
                        ),
                        dcc.Dropdown(
                            id="port-select-dropdown",
                            options=list(
                                {"label": port, "value": port} for port in ports
                            ),
                            value=ports[1],
                            className="two columns",
                        )
                    ],
                ),
                html.Br(),
                html.Div(
                    id="value-setter-menu",
                    # className='six columns',
                    children=[
                        html.Div(id="value-setter-panel"),
                        html.Br(),
                        html.Div(
                            id="button-div",
                            children=[
                                html.Button("Update", id="value-setter-set-btn"),
                                html.Button(
                                    "View current setup",
                                    id="value-setter-view-btn",
                                    n_clicks=0,
                                ),
                            ],
                        ),
                        html.Div(
                            id="value-setter-view-output", className="output-datatable"
                        ),
                    ],
                ),
            ],
        ),
    ]

def build_tab_1():
    return [
        # Manually select metrics
        html.Div(
            id="set-specs-intro-container",
            # className='twelve columns',
            children=html.P(
                "Use historical control limits to establish a benchmark, or set new values."
            ),
        ),
        html.Div(
            id="settings-menu",
            children=[
                html.Div(
                    id="metric-select-menu",
                    # className='five columns',
                    children=[
                        html.Label(id="metric-select-title", children="Subsystem"),
                        html.Br(),
                        dcc.Dropdown(
                            id="metric-select-dropdown",
                            options=list(
                                {"label": subsystem, "value": subsystem} for subsystem in subsystems
                            ),
                            value=params[1],
                        ),
                    ],
                ),
                html.Div(
                    id="value-setter-menu",
                    # className='six columns',
                    children=[
                        html.Div(id="value-setter-panel"),
                        html.Br(),
                        html.Div(
                            id="button-div",
                            children=[
                                html.Button("Update", id="value-setter-set-btn"),
                                html.Button(
                                    "View current setup",
                                    id="value-setter-view-btn",
                                    n_clicks=0,
                                ),
                                html.Button("Add Port", id="update-port-btn"),
                            ],
                        ),
                        html.Div(
                            id="value-setter-view-output", className="output-datatable"
                        ),
                    ],
                ),
            ],
        ),
    ]


def build_hardware_config_line(line_num, label, value, col3):
    return html.Div(
        id=line_num,
        children=[
            html.Label(label, className="four columns"),
            html.Label(value, className="four columns"),
            html.Div(col3, className="four columns"),
        ],
        className="row",
    )

def build_route_config_line(id=None, segment_number=0, label=None, input=None, className="four columns"):
    input.className = className
    return html.Div(
        id=id,
        children=[
            html.Label(str(segment_number), className=className),
            html.Label(label, className=className),
            input
            #html.Label(input, className="four columns"),
            #html.Div(col3, className="four columns"),
        ],
        className="row",
    )

def build_route_segments_list(device_name=None, consumed_devices=None, hardware_configuration=None):
    route_config_segments = []
    for route_segment_ndx in range(len(hardware_configuration['routes'][device_name])):
        destination_select_options = ['rpi'] + list(hardware_configuration['devices'].keys())
        destination_select_options.remove(hardware_configuration['devices'][device_name]['name'])
        if destination_select_options is None:
            destination_select_options = [{'label': 'No Device Available', 'value': 'none'}]
        else:
            destination_select_options = [{'label': device, 'value': device} for device in destination_select_options]
        route_config_segments += [build_route_config_line(id="route-segment-line" + str(route_segment_ndx),
                                                          segment_number=route_segment_ndx,
                                                          label=hardware_configuration['routes'][device_name][
                                                              route_segment_ndx][0],
                                                          input=dcc.Dropdown(
                                                              id="route-segment-" + str(route_segment_ndx),
                                                              options=destination_select_options,
                                                              className=None),
                                                          className="four columns")]

def build_device_config_attribute_addition_line(line_num, device_type=None):#, label, value, col3):
    if device_type == None:
        dropdown_options = [{"label": key, "value": key} for key in FrontendLibrary.build_complete_attribute_option_list()]
    else:
        dropdown_options = [{"label": key, "value": key} for key in ControllerLibrary.HAL.SUPPORTED_DEVICES[device_type].keys()]

    return html.Div(
        id=line_num,
        children=[
            dcc.Dropdown(options=dropdown_options, className="four columns"),
            html.Button("Add Attribute", id="add-device-attribute-btn", className="four columns"),
            #html.Label(label, className="four columns"),
            #html.Label(value, className="four columns"),
            #html.Div(col3, className="four columns"),
        ],
        className="row",
    )

def build_port_config_line(line_num, port, attribute):
    if attribute == 'name':
        input_object = dcc.Input(value=getattr(port,attribute), debounce=True)
    elif attribute == 'port_type':
        input_object = FrontendLibrary.build_port_selector_dropdown(value=getattr(port,attribute))#, PORT_TYPES=ports)
    elif attribute.__contains__('_pin'):
        input_object = FrontendLibrary.build_pin_selector_dropdown(value=getattr(port, attribute))#, PORT_TYPES=ports)
    else:
        input_object = dcc.Input(value=getattr(port, attribute), debounce=True)
    #elif attribute ==
    #children = [html.Label(attribute, className="four columns")]
    input_object.className = "four columns"
    return html.Div(
        id=line_num,
        children=[
            html.Label(attribute, className="four columns"),
            html.Div(input_object)#,className='four columns'),#html.Label(value, className="four columns"),
            #html.Div(col3, className="four columns"),
        ],
        className="row",
    )

def build_device_config_line(div_id=None, device_name=None, device_type=None, attribute=None, input_object_id=None, input_value=None):
    if attribute == "device_type":
        input_object_type = ControllerLibrary.HAL.COMMON_DEVICE_ATTRIBUTES[attribute]
    else:
        input_object_type = ControllerLibrary.HAL.SUPPORTED_DEVICES[device_type][attribute]

    if device_name == "new_device":
        #input_object_type = ControllerLibrary.HAL.COMMON_DEVICE_ATTRIBUTES[attribute]
        input_value = None
    # else:
    #     #device = FrontendLibrary.lookup_device_by_name(device, configured_devices)
    #     #input_object_type = ControllerLibrary.HAL.SUPPORTED_DEVICES[device_type][attribute]
    #     input_value = "ADC"

    if input_object_type == 'text':
        input_object = dcc.Input(value=input_value, debounce=True)
    elif input_object_type == 'device_type_dropdown':
        input_object = FrontendLibrary.build_device_type_selector_dropdown(value=input_value)#, PORT_TYPES=ports)
    elif input_object_type == 'address':
        input_object = FrontendLibrary.build_pin_selector_dropdown(value=input_value)#, PORT_TYPES=ports)
    else:
        input_object = dcc.Input(value=input_value, debounce=True)
    #elif attribute ==
    #children = [html.Label(attribute, className="four columns")]
    input_object.className = "four columns"
    input_object.id = input_object_id
    return html.Div(
        id=div_id,
        children=[
            html.Label(attribute, className="four columns"),
            html.Div(input_object)#,className='four columns'),#html.Label(value, className="four columns"),
            #html.Div(col3, className="four columns"),
        ],
        className="row",
    )

def build_value_setter_toggle(line_num, label, value, col3):
    return html.Div(
        id=line_num,
        children=[
            html.Label(label, className="four columns"),
            html.Label(value, className="four columns"),
            #html.Div(col3, className="four columns"),
            html.Div(daq.ToggleSwitch(id='subsystem-on-off', value=False), html.Div(id='subsystem-on-off-output'))
        ],
        className="row",
    )

def generate_modal():
    return html.Div(
        id="markdown",
        className="modal",
        children=(
            html.Div(
                id="markdown-container",
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Close",
                            id="markdown_close",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        className="markdown-text",
                        children=dcc.Markdown(
                            children=(
                                """
                        ###### What is this mock app about?
                        This is a dashboard for monitoring real-time process quality along manufacture production line. 
                        ###### What does this app shows
                        Click on buttons in `Parameter` column to visualize details of measurement trendlines on the bottom panel.
                        The sparkline on top panel and control chart on bottom panel show Shewhart process monitor using mock data. 
                        The trend is updated every other second to simulate real-time measurements. Data falling outside of six-sigma control limit are signals indicating 'Out of Control(OOC)', and will 
                        trigger alerts instantly for a detailed checkup. 

                        Operators may stop measurement by clicking on `Stop` button, and edit specification parameters by clicking specification tab.
                    """
                            )
                        ),
                    ),
                ],
            )
        ),
    )


def build_quick_stats_panel():
    return html.Div(
        id="quick-stats",
        className="row",
        children=[
            html.Div(
                id="card-1",
                children=[
                    html.P("Operator ID"),
                    daq.LEDDisplay(
                        id="operator-led",
                        value="1704",
                        color="#92e0d3",
                        backgroundColor="#1e2130",
                        size=50,
                    ),
                ],
            ),
            html.Div(
                id="card-2",
                children=[
                    html.P("Time to completion"),
                    daq.Gauge(
                        id="progress-gauge",
                        max=max_length * 2,
                        min=0,
                        showCurrentValue=True,  # default size 200 pixel
                    ),
                ],
            ),
            html.Div(
                id="utility-card",
                children=[daq.StopButton(id="stop-button", size=160, n_clicks=0)],
            ),
        ],
    )


def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)


def build_top_panel(stopped_interval):
    return html.Div(
        id="top-section-container",
        className="row",
        children=[
            # Metrics summary
            html.Div(
                id="metric-summary-session",
                className="eight columns",
                children=[
                    generate_section_banner("Process Control Metrics Summary"),
                    html.Div(
                        id="metric-div",
                        children=[
                            generate_metric_list_header(),
                            html.Div(
                                id="metric-rows",
                                children=[
                                    generate_metric_row_helper(stopped_interval, 1),
                                    generate_metric_row_helper(stopped_interval, 2),
                                    generate_metric_row_helper(stopped_interval, 3),
                                    generate_metric_row_helper(stopped_interval, 4),
                                    generate_metric_row_helper(stopped_interval, 5),
                                    generate_metric_row_helper(stopped_interval, 6),
                                    generate_metric_row_helper(stopped_interval, 7),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Piechart
            html.Div(
                id="ooc-piechart-outer",
                className="four columns",
                children=[
                    generate_section_banner("% OOC per Parameter"),
                    generate_piechart(),
                ],
            ),
        ],
    )


def generate_piechart():
    return dcc.Graph(
        id="piechart",
        figure={
            "data": [
                {
                    "labels": [],
                    "values": [],
                    "type": "pie",
                    "marker": {"line": {"color": "white", "width": 1}},
                    "hoverinfo": "label",
                    "textinfo": "label",
                }
            ],
            "layout": {
                "margin": dict(l=20, r=20, t=20, b=20),
                "showlegend": True,
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "white"},
                "autosize": True,
            },
        },
    )


# Build header
def generate_metric_list_header():
    return generate_metric_row(
        "metric_header",
        {"height": "3rem", "margin": "1rem 0", "textAlign": "center"},
        {"id": "m_header_1", "children": html.Div("Parameter")},
        {"id": "m_header_2", "children": html.Div("Count")},
        {"id": "m_header_3", "children": html.Div("Sparkline")},
        {"id": "m_header_4", "children": html.Div("OOC%")},
        {"id": "m_header_5", "children": html.Div("%OOC")},
        {"id": "m_header_6", "children": "Pass/Fail"},
    )


def generate_metric_row_helper(stopped_interval, index):
    item = params[index]

    div_id = item + suffix_row
    button_id = item + suffix_button_id
    sparkline_graph_id = item + suffix_sparkline_graph
    count_id = item + suffix_count
    ooc_percentage_id = item + suffix_ooc_n
    ooc_graph_id = item + suffix_ooc_g
    indicator_id = item + suffix_indicator

    return generate_metric_row(
        div_id,
        None,
        {
            "id": item,
            "className": "metric-row-button-text",
            "children": html.Button(
                id=button_id,
                className="metric-row-button",
                children=item,
                title="Click to visualize live SPC chart",
                n_clicks=0,
            ),
        },
        {"id": count_id, "children": "0"},
        {
            "id": item + "_sparkline",
            "children": dcc.Graph(
                id=sparkline_graph_id,
                style={"width": "100%", "height": "95%"},
                config={
                    "staticPlot": False,
                    "editable": False,
                    "displayModeBar": False,
                },
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": state_dict["Batch"]["data"].tolist()[
                                     :stopped_interval
                                     ],
                                "y": state_dict[item]["data"][:stopped_interval],
                                "mode": "lines+markers",
                                "name": item,
                                "line": {"color": "#f4d44d"},
                            }
                        ],
                        "layout": {
                            "uirevision": True,
                            "margin": dict(l=0, r=0, t=4, b=4, pad=0),
                            "xaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                            ),
                            "yaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                            ),
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                        },
                    }
                ),
            ),
        },
        {"id": ooc_percentage_id, "children": "0.00%"},
        {
            "id": ooc_graph_id + "_container",
            "children": daq.GraduatedBar(
                id=ooc_graph_id,
                color={
                    "ranges": {
                        "#92e0d3": [0, 3],
                        "#f4d44d ": [3, 7],
                        "#f45060": [7, 15],
                    }
                },
                showCurrentValue=False,
                max=15,
                value=0,
            ),
        },
        {
            "id": item + "_pf",
            "children": daq.Indicator(
                id=indicator_id, value=True, color="#91dfd2", size=12
            ),
        },
    )


def generate_metric_row(id, style, col1, col2, col3, col4, col5, col6):
    if style is None:
        style = {"height": "8rem", "width": "100%"}

    return html.Div(
        id=id,
        className="row metric-row",
        style=style,
        children=[
            html.Div(
                id=col1["id"],
                className="one column",
                style={"margin-right": "2.5rem", "minWidth": "50px"},
                children=col1["children"],
            ),
            html.Div(
                id=col2["id"],
                style={"textAlign": "center"},
                className="one column",
                children=col2["children"],
            ),
            html.Div(
                id=col3["id"],
                style={"height": "100%"},
                className="four columns",
                children=col3["children"],
            ),
            html.Div(
                id=col4["id"],
                style={},
                className="one column",
                children=col4["children"],
            ),
            html.Div(
                id=col5["id"],
                style={"height": "100%", "margin-top": "5rem"},
                className="three columns",
                children=col5["children"],
            ),
            html.Div(
                id=col6["id"],
                style={"display": "flex", "justifyContent": "center"},
                className="one column",
                children=col6["children"],
            ),
        ],
    )


def build_chart_panel():
    return html.Div(
        id="control-chart-container",
        className="twelve columns",
        children=[
            generate_section_banner("Live SPC Chart"),
            dcc.Graph(
                id="control-chart-live",
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": [],
                                "y": [],
                                "mode": "lines+markers",
                                "name": params[1],
                            }
                        ],
                        "layout": {
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                            "xaxis": dict(
                                showline=False, showgrid=False, zeroline=False
                            ),
                            "yaxis": dict(
                                showgrid=False, showline=False, zeroline=False
                            ),
                            "autosize": True,
                        },
                    }
                ),
            ),
        ],
    )


def generate_graph(interval, specs_dict, col):
    stats = state_dict[col]
    col_data = stats["data"]
    mean = stats["mean"]
    ucl = specs_dict[col]["ucl"]
    lcl = specs_dict[col]["lcl"]
    usl = specs_dict[col]["usl"]
    lsl = specs_dict[col]["lsl"]

    x_array = state_dict["Batch"]["data"].tolist()
    y_array = col_data.tolist()

    total_count = 0

    if interval > max_length:
        total_count = max_length - 1
    elif interval > 0:
        total_count = interval

    ooc_trace = {
        "x": [],
        "y": [],
        "name": "Out of Control",
        "mode": "markers",
        "marker": dict(color="rgba(210, 77, 87, 0.7)", symbol="square", size=11),
    }

    for index, data in enumerate(y_array[:total_count]):
        if data >= ucl or data <= lcl:
            ooc_trace["x"].append(index + 1)
            ooc_trace["y"].append(data)

    histo_trace = {
        "x": x_array[:total_count],
        "y": y_array[:total_count],
        "type": "histogram",
        "orientation": "h",
        "name": "Distribution",
        "xaxis": "x2",
        "yaxis": "y2",
        "marker": {"color": "#f4d44d"},
    }

    fig = {
        "data": [
            {
                "x": x_array[:total_count],
                "y": y_array[:total_count],
                "mode": "lines+markers",
                "name": col,
                "line": {"color": "#f4d44d"},
            },
            ooc_trace,
            histo_trace,
        ]
    }

    len_figure = len(fig["data"][0]["x"])

    fig["layout"] = dict(
        margin=dict(t=40),
        hovermode="closest",
        uirevision=col,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend={"font": {"color": "darkgray"}, "orientation": "h", "x": 0, "y": 1.1},
        font={"color": "darkgray"},
        showlegend=True,
        xaxis={
            "zeroline": False,
            "showgrid": False,
            "title": "Batch Number",
            "showline": False,
            "domain": [0, 0.8],
            "titlefont": {"color": "darkgray"},
        },
        yaxis={
            "title": col,
            "showgrid": False,
            "showline": False,
            "zeroline": False,
            "autorange": True,
            "titlefont": {"color": "darkgray"},
        },
        annotations=[
            {
                "x": 0.75,
                "y": lcl,
                "xref": "paper",
                "yref": "y",
                "text": "LCL:" + str(round(lcl, 3)),
                "showarrow": False,
                "font": {"color": "white"},
            },
            {
                "x": 0.75,
                "y": ucl,
                "xref": "paper",
                "yref": "y",
                "text": "UCL: " + str(round(ucl, 3)),
                "showarrow": False,
                "font": {"color": "white"},
            },
            {
                "x": 0.75,
                "y": usl,
                "xref": "paper",
                "yref": "y",
                "text": "USL: " + str(round(usl, 3)),
                "showarrow": False,
                "font": {"color": "white"},
            },
            {
                "x": 0.75,
                "y": lsl,
                "xref": "paper",
                "yref": "y",
                "text": "LSL: " + str(round(lsl, 3)),
                "showarrow": False,
                "font": {"color": "white"},
            },
            {
                "x": 0.75,
                "y": mean,
                "xref": "paper",
                "yref": "y",
                "text": "Targeted mean: " + str(round(mean, 3)),
                "showarrow": False,
                "font": {"color": "white"},
            },
        ],
        shapes=[
            {
                "type": "line",
                "xref": "x",
                "yref": "y",
                "x0": 1,
                "y0": usl,
                "x1": len_figure + 1,
                "y1": usl,
                "line": {"color": "#91dfd2", "width": 1, "dash": "dot"},
            },
            {
                "type": "line",
                "xref": "x",
                "yref": "y",
                "x0": 1,
                "y0": lsl,
                "x1": len_figure + 1,
                "y1": lsl,
                "line": {"color": "#91dfd2", "width": 1, "dash": "dot"},
            },
            {
                "type": "line",
                "xref": "x",
                "yref": "y",
                "x0": 1,
                "y0": ucl,
                "x1": len_figure + 1,
                "y1": ucl,
                "line": {"color": "rgb(255,127,80)", "width": 1, "dash": "dot"},
            },
            {
                "type": "line",
                "xref": "x",
                "yref": "y",
                "x0": 1,
                "y0": mean,
                "x1": len_figure + 1,
                "y1": mean,
                "line": {"color": "rgb(255,127,80)", "width": 2},
            },
            {
                "type": "line",
                "xref": "x",
                "yref": "y",
                "x0": 1,
                "y0": lcl,
                "x1": len_figure + 1,
                "y1": lcl,
                "line": {"color": "rgb(255,127,80)", "width": 1, "dash": "dot"},
            },
        ],
        xaxis2={
            "title": "Count",
            "domain": [0.8, 1],  # 70 to 100 % of width
            "titlefont": {"color": "darkgray"},
            "showgrid": False,
        },
        yaxis2={
            "anchor": "free",
            "overlaying": "y",
            "side": "right",
            "showticklabels": False,
            "titlefont": {"color": "darkgray"},
        },
    )

    return fig


def update_sparkline(interval, param):
    x_array = state_dict["Batch"]["data"].tolist()
    y_array = state_dict[param]["data"].tolist()

    if interval == 0:
        x_new = y_new = None

    else:
        if interval >= max_length:
            total_count = max_length
        else:
            total_count = interval
        x_new = x_array[:total_count][-1]
        y_new = y_array[:total_count][-1]

    return dict(x=[[x_new]], y=[[y_new]]), [0]


def update_count(interval, col, data):
    if interval == 0:
        return "0", "0.00%", 0.00001, "#92e0d3"

    if interval > 0:

        if interval >= max_length:
            total_count = max_length - 1
        else:
            total_count = interval - 1

        ooc_percentage_f = data[col]["ooc"][total_count] * 100
        ooc_percentage_str = "%.2f" % ooc_percentage_f + "%"

        # Set maximum ooc to 15 for better grad bar display
        if ooc_percentage_f > 15:
            ooc_percentage_f = 15

        if ooc_percentage_f == 0.0:
            ooc_grad_val = 0.00001
        else:
            ooc_grad_val = float(ooc_percentage_f)

        # Set indicator theme according to threshold 5%
        if 0 <= ooc_grad_val <= 5:
            color = "#92e0d3"
        elif 5 < ooc_grad_val < 7:
            color = "#f4d44d"
        else:
            color = "#FF0000"

    return str(total_count + 1), ooc_percentage_str, ooc_grad_val, color

def SetAppLayout(app=None, hardware_configuration=None):
    app.layout = html.Div(
        id="big-app-container",
        children=[
            build_banner(app),
            dcc.Interval(
                id="interval-component",
                interval=2 * 1000,  # in milliseconds
                n_intervals=50,  # start at batch 50
                disabled=True,
            ),
            html.Div(
                id="app-container",
                children=[
                    build_tabs(),
                    # Main app
                    html.Div(id="app-content"),
                ],
            ),
            dcc.Store(id="value-setter-store", data=init_value_setter_store()),
            dcc.Store(id="hardware-config-store", data=hardware_configuration),
            dcc.Store(id="n-interval-stage", data=50),
            generate_modal(),
        ],
    )

# decorator for list of output
def create_callback(param):
    def callback(interval, stored_data):
        count, ooc_n, ooc_g_value, indicator = update_count(
            interval, param, stored_data
        )
        spark_line_data = update_sparkline(interval, param)
        return count, spark_line_data, ooc_n, ooc_g_value, indicator

    return callback


