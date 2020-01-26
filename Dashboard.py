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
import Statics

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
df = pd.read_csv(os.path.join(APP_PATH, os.path.join("data", "spc_data.csv")))

params = list(df)
max_length = len(df)
#params = ['Temperature', 'Low Side Pressure', 'High Side Pressure', 'pH', 'ORP', 'EC', 'Water Level', 'Flow']
#subsystems = ['Temperature Controller', 'High Side Pressure Controller', 'Calcium Reactor Controller', 'O3 Reactor Controller', 'Light Controller']

#ports = ['Digital Output', 'Digital Input', 'Analog Output', 'Analog Input', 'I2C Port', 'TTL Serial Port', 'RS-485 Port']
#configured_ports = [{'name': 'Heater_1_SSR_Port', 'type': 'DO', 'signal0_pin': 'GPIO0', 'signal1_pin': None, 'power_pin': '5V'}, {'name': 'Heater_2_SSR_Port', 'type': 'DO', 'signal0_pin': 'GPIO1', 'signal1_pin': None, 'power_pin': '5V'}]
# configured_ports = [ControllerLibrary.Port(name='Heater_1_SSR_Port', port_type='DO', signal0_pin='GPIO0'),
#                     ControllerLibrary.Port(name='Heater_2_SSR_Port', port_type='DO', signal0_pin='GPIO1'),
#                     ControllerLibrary.Port(name='Return_Pump_Serial_Port', port_type='TTL_Serial', signal0_pin='GPIO2', signal1_pin='GPIO3')]
#
# configured_devices = [ControllerLibrary.Device(name='Heater_1_SSR', port_type='DO', signal0_pin='GPIO0'),
#                       ControllerLibrary.Device(name='Heater_2_SSR', port_type='DO', signal0_pin='GPIO1'),
#                       ControllerLibrary.Device(name='Return_Pump_VFD', port_type='TTL_Serial', signal0_pin='GPIO2', signal1_pin='GPIO3')]

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


def InitializeFrontend(hardware_configuration=None, system_manager=None, synchronizer=None):
    app = dash.Dash(
        __name__,
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
        external_stylesheets=['datatable_style.css']
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
            return build_controller_settings_tab(hardware_configuration), stopped_interval
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
        #system_manager.command_queue.put("update")
        return [update_signal + 1]

    @app.callback(
        output=[
            Output("device-config-panel", "children"),
            Output("device-type-selector-dropdown", "value"),
            #Output("driver-selector-dropdown", "value"),
            #Output("device-table", "data")
            # Output("ud_portname_input", "value"),
            # Output("ud_porttype_input", "value"),
            # Output("ud_lsl_input", "value"),
            # Output("ud_ucl_input", "value"),
            # Output("ud_lcl_input", "value"),
        ],
        inputs=[Input("device-select-dropdown", "value")],#, Input("device-update-signal", "children")],
        state=[State("hardware-config-store", "data")],
    )
    def update_device_config_dropdowns(device_name, hardware_configuration):
        hardware_configuration = ControllerLibrary.UnpackHardwareConfiguration(hardware_configuration)

        if device_name == None:
            #raise PreventUpdate
            return build_device_config_panel(None, hardware_configuration) + [None]

        device_table_data = []
        if device_name == "new_device":
            device_type = ""
            driver = ""
            #device_table_data = []
        else:
            device_type = hardware_configuration['devices'][device_name]['device_type']
            driver = hardware_configuration['devices'][device_name]['driver']

            # for attr in ControllerLibrary.HAL.SUPPORTED_DEVICES[device_type]:
            #     if ControllerLibrary.HAL.DEVICE_ATTRIBUTE_TYPES[attr] == 'text' and attr in hardware_configuration['devices'][device_name].keys():
            #         device_table_data += [{"attribute_name": attr,
            #                                "attribute_value": hardware_configuration['devices'][device_name][attr]}]

        #device_table_data = [{"attribute_name": attr, "attribute_value": hardware_configuration['devices'][device_name][attr]} for attr in hardware_configuration['devices'][device_name].keys()]


                #{"attribute_name": "address", "attribute_value": "0x00"}]

        return build_device_config_panel(device_name, hardware_configuration) + \
               [device_type]#, device_table_data]

    @app.callback(
        output=[Output("device-table", "data"),
                Output("driver-selector-dropdown", "options"),
                Output("driver-selector-dropdown", "value")],
        inputs=[Input("device-type-selector-dropdown", "value")],
        state=[State("device-select-dropdown", "value"),
               State("hardware-config-store", "data")],
    )
    def update_device_config_table(device_type, device_name, hardware_configuration):
        device_table_data = []
        #device_type = hardware_configuration['devices'][device_name]['device_type']
        if device_name != 'new_device' and device_name != None:
            driver = hardware_configuration['devices'][device_name]['driver']
            for attr in Statics.SUPPORTED_DEVICES[device_type]:
                if Statics.DEVICE_ATTRIBUTE_TYPES[attr] == 'text' and attr in hardware_configuration['devices'][device_name].keys():
                    device_table_data += [{"attribute_name": attr,
                                           "attribute_value": hardware_configuration['devices'][device_name][attr]}]
            driver_options = [{'label': driver, 'value': driver} for driver in
                              Statics.INSTALLED_DRIVERS[device_type]]
        elif device_type != '' and device_type != None:
            if device_type == None:
                pass
            driver = Statics.INSTALLED_DRIVERS[device_type][0]
            for attr in Statics.SUPPORTED_DEVICES[device_type]:
                if Statics.DEVICE_ATTRIBUTE_TYPES[attr] == 'text':
                    device_table_data += [{"attribute_name": attr,
                                           "attribute_value": ''}]
                driver_options = [{'label': driver, 'value': driver} for driver in Statics.INSTALLED_DRIVERS[device_type]]
        else:
            raise PreventUpdate

        return device_table_data, driver_options, driver


    @app.callback(
        inputs=[Input("route-select-dropdown", "value")],
        output=[Output("route-table", "data"),
                Output("route-table", "dropdown")],
        state=[State("hardware-config-store", "data")]
    )
    def update_route_select_table(selected_route, hardware_configuration):
        if selected_route == None:
            raise PreventUpdate

        hardware_configuration = ControllerLibrary.UnpackHardwareConfiguration(hardware_configuration)
        #pass
        #data = []
        # for route_segment_ndx in range(0, len(hardware_configuration['routes'][selected_route])):
        #     data += [{"route_segment": str(route_segment_ndx), "endpoint": hardware_configuration['routes'][selected_route][route_segment_ndx]}]
        data = [{"segment_index": str(route_segment_ndx),"endpoint": hardware_configuration['routes'][selected_route][route_segment_ndx]} for route_segment_ndx in range(0, len(hardware_configuration['routes'][selected_route]))]
        #options = {'endpoint': {'options': [{'label': hardware_configuration['devices'][device]['name'], 'value': hardware_configuration['devices'][device]['name']} for device in hardware_configuration['devices'].keys()]}}
        # options2 = {'endpoint': {'options': [{'label': "Raspberry Pi", 'value': 'rpi'}] + \
        #                                    [{'label': hardware_configuration['devices'][device]['name'],
        #                                      'value': hardware_configuration['devices'][device]['name']} for device in
        #                                     hardware_configuration['devices'].keys()]}}
        options = {'endpoint': {'options': []}}
        for device in hardware_configuration['devices'].keys():
            device_name = hardware_configuration['devices'][device]['name']
            if device_name != selected_route:# and device_name not in hardware_configuration['routes'][selected_route]:
                options['endpoint']['options'] += [{'label': hardware_configuration['devices'][device]['name'], 'value': hardware_configuration['devices'][device]['name']}]
        #options['endpoint']['options']}}
        return data, options

    @app.callback(
        output=Output("controller-parameters-table", "data"),
        inputs=[
            Input("controller-type-selector-dropdown", "value"),
            Input("controller-output-type-selector-dropdown", "value"),
            Input("controller-sensor-selector-dropdown", "value"),
            Input("controller-actuator-selector-dropdown", "value"),
            Input("interlock-type-selector-dropdown", "value"),
        ],
        state=[
            State("controller-select-dropdown", "value"),
            State("controller-parameters-table", "data"),
            State("hardware-config-store", "data")
        ]
    )
    def update_controller_parameters_table(controller_type, output_type, sensor, actuator, interlock_type, selected_controller, table_data, hardware_configuration):
        if controller_type is None or output_type is None or sensor is None or actuator is None or interlock_type is None:
            raise PreventUpdate

        return [{"attribute_name": 'abc', "attribute_value": 5}]

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
               State("device-type-selector-dropdown", "value"),
               State("driver-selector-dropdown", "value"),
               State("device-table", "data"),
               State("route-table", "data"),
               State("device-select-dropdown", "value"),
               State("route-select-dropdown", "value")]
               #State("device-type-selection-line", "children")]
    )
    def update_hardware(update_button_click_timestamp,
                        delete_button_click_timestamp,
                        add_segment_button_click_timestamp,
                        update_route_button_click_timestamp,
                        hardware_configuration,
                        #configuration_panel_lines,
                        device_type,
                        driver,
                        device_table,
                        route_table,
                        device_name,
                        route_name):
                        #device_type_dropdown_div):
        ordered_timestamps = {update_button_click_timestamp: 'update_device',
                              delete_button_click_timestamp: 'delete_device',
                              add_segment_button_click_timestamp: 'add_segment',
                              update_route_button_click_timestamp: 'update_route'}
        button_clicked = ordered_timestamps[sorted(ordered_timestamps.keys(), reverse=True)[0]]
        hardware_configuration = ControllerLibrary.UnpackHardwareConfiguration(hardware_configuration)
        ctx = dash.callback_context
        button_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
        #if sorted(ordered_timestamps.keys(), reverse=True)[0] == 0:
        if ctx.triggered[0]['value'] == 0:
            raise PreventUpdate
        if button_clicked == 'update-device-btn':
            #if button_click != None:
            try:
                device_definition = hardware_configuration['devices'][device_name]
                hardware_configuration['devices'].pop(device_name, None)
            except KeyError:
                device_definition = {}
            device_definition['device_type'] = device_type
            device_definition['driver'] = driver
            for line in device_table:
                device_definition[line['attribute_name']] = line['attribute_value']
            hardware_configuration['devices'][device_definition['name']] = device_definition
            device_name = device_definition['name']
            hardware_configuration['routes'][device_name] = []
            # device_type = device_type_dropdown_div[1]['props']['children']['props']['value']
            # device_definition = {'device_type': device_type}
            # for line in configuration_panel_lines:
            #     if line['props']['id'] == 'device-config-line':
            #         input_object = line['props']['children'][1]['props']['children']['props']
            #         attribute_name = input_object['id'].split('.')[1]
            #         input_value = input_object['value']
            #         device_definition[attribute_name] = input_value
            # try:
            #     hardware_configuration['devices'][device_definition['name']] = device_definition
            #     hardware_configuration['routes'][device_definition['name']] = ['rpi']
            # except Exception as e:
            #     pass
            #hardware_configuration['updates'] = hardware_configuration['updates'] + 1

            # device_select_dropdown_options = [{"label": 'New Device...', "value": "new_device"}] + [
            #     {"label": hardware_configuration['devices'][device]['name'], "value": hardware_configuration['devices'][device]['name']} for
            #     device in hardware_configuration['devices'].keys()]
            device_select_dropdown_options = FrontendLibrary.build_device_selector_dropdown_options_list(hardware_configuration)
                # [{"label": 'New Device...', "value": "new_device"}] + [
                # {"label": device + ' (' + hardware_configuration['devices'][device]['device_type'] + ')',
                #  "value": device} for device
                # in hardware_configuration['devices']]
            #return [hardware_configuration], device_select_dropdown_options, device_definition['name'], FrontendLibrary.build_route_selector_options_list(hardware_configuration), [route_name]
        elif button_clicked == "delete-device-btn":
            #raise PreventUpdate
            hardware_configuration['devices'].pop(device_name, None)
            hardware_configuration['routes'].pop(route_name, None)
            device_name = None
        elif button_clicked == "add-route-segment-btn":
            hardware_configuration['routes'][route_name] += ['']
            device_select_dropdown_options = FrontendLibrary.build_device_selector_dropdown_options_list(
                hardware_configuration)
            #device_name = hardware_configuration['name']
            #raise PreventUpdate
        elif button_clicked == "update-route-btn":
            #raise PreventUpdate
            hardware_configuration['routes'][route_name] = [segment['endpoint'] for segment in route_table]
            device_select_dropdown_options = FrontendLibrary.build_device_selector_dropdown_options_list(
                hardware_configuration)
        else:
            raise PreventUpdate

        return hardware_configuration, \
               FrontendLibrary.build_device_selector_dropdown_options_list(hardware_configuration), \
               device_name, \
               FrontendLibrary.build_route_selector_options_list(hardware_configuration), \
               route_name


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
    controller_selector_options = FrontendLibrary.build_controller_selector_dropdown_options_list(
        hardware_configuration)
    selected_device = device_selector_options[0]['value']
    selected_controller = controller_selector_options[0]['value']
    return [
        html.Div(
            id="set-hardware-config-intro-container",
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
                                     #value=selected_device
                                ),
                                html.Br(),
                                html.Button("Update Device",
                                          id="update-device-btn",
                                          className="hardware-config-tab-btn",
                                          n_clicks_timestamp=0),
                                html.Button("Delete Device",
                                          id="delete-device-btn",
                                          className="hardware-config-tab-btn",
                                          disabled=False,
                                          n_clicks_timestamp=0)
                        ]),
                        html.Div(
                            id="device-config-menu",
                            children=[
                                html.Div(id="device-config-panel", children=build_device_config_panel(selected_device, hardware_configuration)[0]),
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
                                            className="hardware-config-tab-btn",
                                            disabled=False,
                                            n_clicks_timestamp=0),
                                ]
                        ),

                        html.Div(id='configuration-table-container',
                                 children=[build_route_config_table(hardware_configuration=hardware_configuration)]
                        )


                        ]
                    ),
                ]
            ),

        html.Div(id="controller-settings-section",
                 children=[
                     html.Div(
                         id="hardware-config-subheading",
                         children=html.P("Controllers")),

                     html.Div(
                         id="controllers-menu",
                         children=[
                             html.Div(
                                 id="controller-select-menu",
                                 children=[
                                     html.Label(id="controller-select-title", children="Select Controller"),
                                     html.Br(),
                                     dcc.Dropdown(
                                         id="controller-select-dropdown",
                                         options=controller_selector_options,
                                         # value=selected_device
                                     ),
                                     html.Br(),
                                     html.Button("Update Controller",
                                                 id="update-controller-btn",
                                                 className="hardware-config-tab-btn",
                                                 n_clicks_timestamp=0),
                                     html.Button("Delete Controller",
                                                 id="delete-controller-btn",
                                                 className="hardware-config-tab-btn",
                                                 disabled=False,
                                                 n_clicks_timestamp=0)
                                 ]),
                             html.Div(
                                 id="controller-config-menu",
                                 children=[
                                     html.Div(id="controller-config-panel", children=
                                     build_controller_config_panel(selected_controller, hardware_configuration)[0]),
                                     # html.Br(),
                                 ],
                             ),
                         ],
                     ),
                 ]
                 ),

        html.Div(id='hardware_config_button_clicks', children='update_port:0|add_port:0', style={'display': 'none'}),
        html.Div(id='device-update-signal', children=0, style={'display': 'none'}),
        html.Div(id="dummy_output", children=0, style={'display': 'none'}),
        html.Div(id="dummy_output2", children=0, style={'display': 'none'})
    ]

# def build_controller_settings_tab(hardware_configuration=None):
#     # available_devices = list({"label": device, "value": device} for device in ControllerLibrary.HAL.SUPPORTED_DEVICES)
#     hardware_configuration = ControllerLibrary.UnpackHardwareConfiguration(hardware_configuration)
#     #device_selector_options = FrontendLibrary.build_device_selector_dropdown_options_list(hardware_configuration)
#     controller_selector_options = FrontendLibrary.build_controller_selector_dropdown_options_list(hardware_configuration)
#     #selected_device = device_selector_options[0]['value']
#     return [
#         # Manually select metrics
#         html.Div(
#             id="set-controller-settings-intro-container",
#             # className='twelve columns',
#             children=[
#                 html.P(
#                     "IO and Controller Settings"),
#                 html.Button(
#                     "Save Hardware Configuration to Disk",
#                     id="save-hardware-config-btn",
#                     n_clicks=0,
#                     className="hardware-config-tab-btn"),
#                 html.Button(
#                     "Load Hardware Configuration to Controller",
#                     id="load-hardware-config-to-controller-btn",
#                     n_clicks=0,
#                     className="hardware-config-tab-btn"),
#             ],
#         ),
#
#         html.Div(id="controller-settings-section",
#                  children=[
#                      html.Div(
#                          id="controller-config-subheading",
#                          children=html.P("Controllers")),
#
#                      # Devices menu
#                      html.Div(
#                          id="devices-menu",
#                          children=[
#                              html.Div(
#                                  id="device-select-menu",
#                                  children=[
#                                      html.Label(id="controller-select-title", children="Select Controller"),
#                                      html.Br(),
#                                      dcc.Dropdown(
#                                          id="controller-select-dropdown",
#                                          options=controller_selector_options,
#                                          # value=selected_device
#                                      ),
#                                      html.Br(),
#                                      html.Button("Update Controller",
#                                                  id="update-controller-btn",
#                                                  className="hardware-config-tab-btn",
#                                                  n_clicks_timestamp=0),
#                                      html.Button("Delete Controller",
#                                                  id="delete-controller-btn",
#                                                  className="hardware-config-tab-btn",
#                                                  disabled=False,
#                                                  n_clicks_timestamp=0)
#                                  ]),
#                              html.Div(
#                                  id="device-config-menu",
#                                  children=[
#                                      html.Div(id="device-config-panel", children=
#                                      build_device_config_panel(selected_device, hardware_configuration)[0]),
#                                      # html.Br(),
#                                  ],
#                              ),
#                          ],
#                      ),
#                  ]
#                  ),
#
#         html.Div(id="route-config-section",
#                  children=[
#                      html.Div(id="hardware-config-subheading",
#                               children=html.P("Routing")),
#                      html.Div(
#                          id="routing-menu",
#                          children=[
#                              html.Div(
#                                  id="route-select-menu",
#                                  children=[
#                                      html.Label(id="route-select-title", children="Select Route"),
#                                      html.Br(),
#                                      dcc.Dropdown(
#                                          id="route-select-dropdown",
#                                          options=FrontendLibrary.build_route_selector_options_list(
#                                              hardware_configuration=hardware_configuration)
#                                      ),
#                                      html.Br(),
#                                      html.Button("Add Segment",
#                                                  id="add-route-segment-btn",
#                                                  className="hardware-config-tab-btn",
#                                                  n_clicks_timestamp=0),
#                                      html.Button("Update Route",
#                                                  id="update-route-btn",
#                                                  className="hardware-config-tab-btn",
#                                                  disabled=False,
#                                                  n_clicks_timestamp=0),
#                                  ]
#                              ),
#
#                              html.Div(id='configuration-table-container',
#                                       children=[build_route_config_table(hardware_configuration=hardware_configuration)]
#                                       )
#
#                          ]
#                      ),
#                  ]
#                  )
#         ]

        # html.Div(id='hardware_config_button_clicks', children='update_port:0|add_port:0', style={'display': 'none'}),
        # html.Div(id='device-update-signal', children=0, style={'display': 'none'}),
        # html.Div(id="dummy_output", children=0, style={'display': 'none'}),
        # html.Div(id="dummy_output2", children=0, style={'display': 'none'})
    # return [
    #     # Manually select metrics
    #     html.Div(
    #         id="controller-settings-intro-container",
    #         # className='twelve columns',
    #         children=html.P(
    #             "Set up devices connected to system."
    #         ),
    #     ),
    #     html.Div(
    #         id="port-menu",
    #         children=[
    #             html.Div(
    #                 id="port-name-headers",
    #                 #className="two columns",
    #                 children=[
    #                     html.Label(id="port-name-entry-title", children="Port Name", className="two columns"),
    #                     html.Label(id="port-name-entry-title", children="Port Type", className="two columns"),
    #                 ],
    #             ),
    #             html.Br(),
    #             html.Div(
    #                 id="port-data-entry",
    #                 # className='five columns',
    #                 children=[
    #                     dcc.Input(
    #                         id="port{}-name-text".format("0"),
    #                         type="text",
    #                         placeholder="Port Name",
    #                         className="two columns",
    #                     ),
    #                     dcc.Dropdown(
    #                         id="port-select-dropdown",
    #                         options=list(
    #                             {"label": port, "value": port} for port in ports
    #                         ),
    #                         value=ports[1],
    #                         className="two columns",
    #                     )
    #                 ],
    #             ),
    #             html.Br(),
    #             html.Div(
    #                 id="value-setter-menu",
    #                 # className='six columns',
    #                 children=[
    #                     html.Div(id="value-setter-panel"),
    #                     html.Br(),
    #                     html.Div(
    #                         id="button-div",
    #                         children=[
    #                             html.Button("Update", id="value-setter-set-btn"),
    #                             html.Button(
    #                                 "View current setup",
    #                                 id="value-setter-view-btn",
    #                                 n_clicks=0,
    #                             ),
    #                         ],
    #                     ),
    #                     html.Div(
    #                         id="value-setter-view-output", className="output-datatable"
    #                     ),
    #                 ],
    #             ),
    #         ],
    #     ),
    # ]

# def build_tab_1():
#     return [
#         # Manually select metrics
#         html.Div(
#             id="set-specs-intro-container",
#             # className='twelve columns',
#             children=html.P(
#                 "Use historical control limits to establish a benchmark, or set new values."
#             ),
#         ),
#         html.Div(
#             id="settings-menu",
#             children=[
#                 html.Div(
#                     id="metric-select-menu",
#                     # className='five columns',
#                     children=[
#                         html.Label(id="metric-select-title", children="Subsystem"),
#                         html.Br(),
#                         dcc.Dropdown(
#                             id="metric-select-dropdown",
#                             options=list(
#                                 {"label": subsystem, "value": subsystem} for subsystem in subsystems
#                             ),
#                             value=params[1],
#                         ),
#                     ],
#                 ),
#                 html.Div(
#                     id="value-setter-menu",
#                     # className='six columns',
#                     children=[
#                         html.Div(id="value-setter-panel"),
#                         html.Br(),
#                         html.Div(
#                             id="button-div",
#                             children=[
#                                 html.Button("Update", id="value-setter-set-btn"),
#                                 html.Button(
#                                     "View current setup",
#                                     id="value-setter-view-btn",
#                                     n_clicks=0,
#                                 ),
#                                 html.Button("Add Port", id="update-port-btn"),
#                             ],
#                         ),
#                         html.Div(
#                             id="value-setter-view-output", className="output-datatable"
#                         ),
#                     ],
#                 ),
#             ],
#         ),
#     ]


# def build_hardware_config_line(line_num, label, value, col3):
#     return html.Div(
#         id=line_num,
#         children=[
#             html.Label(label, className="four columns"),
#             html.Label(value, className="four columns"),
#             html.Div(col3, className="four columns"),
#         ],
#         className="row",
#     )

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

# def build_device_config_attribute_addition_line(line_num, device_type=None):#, label, value, col3):
#     if device_type == None:
#         dropdown_options = [{"label": key, "value": key} for key in FrontendLibrary.build_complete_attribute_option_list()]
#     else:
#         dropdown_options = [{"label": key, "value": key} for key in ControllerLibrary.HAL.SUPPORTED_DEVICES[device_type].keys()]
#
#     return html.Div(
#         id=line_num,
#         children=[
#             dcc.Dropdown(options=dropdown_options, className="four columns"),
#             html.Button("Add Attribute", id="add-device-attribute-btn", className="four columns"),
#             #html.Label(label, className="four columns"),
#             #html.Label(value, className="four columns"),
#             #html.Div(col3, className="four columns"),
#         ],
#         className="row",
#     )

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

# def build_device_config_line(div_id=None, device_name=None, device_type=None, attribute=None, input_object_id=None, input_value=None):
#     if attribute == "device_type":
#         input_object_type = ControllerLibrary.HAL.COMMON_DEVICE_ATTRIBUTES[attribute]
#     else:
#         input_object_type = ControllerLibrary.HAL.SUPPORTED_DEVICES[device_type][attribute]
#
#     if device_name == "new_device":
#         #input_object_type = ControllerLibrary.HAL.COMMON_DEVICE_ATTRIBUTES[attribute]
#         input_value = None
#     # else:
#     #     #device = FrontendLibrary.lookup_device_by_name(device, configured_devices)
#     #     #input_object_type = ControllerLibrary.HAL.SUPPORTED_DEVICES[device_type][attribute]
#     #     input_value = "ADC"
#
#     if input_object_type == 'text':
#         input_object = dcc.Input(value=input_value, debounce=True)
#     elif input_object_type == 'device_type_dropdown':
#         input_object = FrontendLibrary.build_device_type_selector_dropdown(value=input_value)#, PORT_TYPES=ports)
#     elif input_object_type == 'address':
#         input_object = FrontendLibrary.build_pin_selector_dropdown(value=input_value)#, PORT_TYPES=ports)
#     else:
#         input_object = dcc.Input(value=input_value, debounce=True)
#     #elif attribute ==
#     #children = [html.Label(attribute, className="four columns")]
#     input_object.className = "four columns"
#     input_object.id = input_object_id
#     return html.Div(
#         id=div_id,
#         children=[
#             html.Label(attribute, className="four columns"),
#             html.Div(input_object)#,className='four columns'),#html.Label(value, className="four columns"),
#             #html.Div(col3, className="four columns"),
#         ],
#         className="row",
#     )

def build_device_config_panel(device_name, hardware_configuration):
    hardware_configuration = ControllerLibrary.UnpackHardwareConfiguration(hardware_configuration)
    if device_name != 'new_device' and device_name != None:
        device_type = hardware_configuration['devices'][device_name]['device_type']
        driver = hardware_configuration['devices'][device_name]['driver']
    else:
        device_type = None
        driver = None

    dropdown_table = [html.Table(id="device-config-table",
        children=[
        html.Tr([html.Td("Device Type", className="halfwidth_cell"), html.Td("Driver", className="halfwidth_cell",style={'width': '50%'})]),
        html.Tr([html.Td(FrontendLibrary.build_device_type_selector_dropdown(id="device-type-selector-dropdown", value=device_type)),
                 html.Td(FrontendLibrary.build_driver_type_selector_dropdown(id="driver-selector-dropdown", device_type=device_type, value=driver))])
        ],
        style={'width': '100%'}

    )]

    configuration_table = [dt.DataTable(id='device-table',
                 columns=[{'name': "Attribute", 'id': "attribute_name"},
                          {'name': "Value", 'id': "attribute_value"}],
                 #data=[{"attribute_name": "name", "attribute_value": ""}, {"attribute_name": "address", "attribute_value": "0x00"}],
                 data = [],
                 style_cell={#'padding': '5px',
                             'color': 'black',
                             'fontSize': 15, 'font-family': '\'Roboto Slab\', serif'},
                 style_header={
                     'backgroundColor': 'gray',
                     'fontWeight': 'bold',
                     'text-align': 'center'
                 },
                 editable=True,
                 style_cell_conditional=[
                     {'if': {'column_id': 'attribute_name'},
                      'width': '30%'}
                 ],
                 row_deletable=True,
                 css=[
                     {"selector": "tr:hover td", "rule": "color: #15A919 !important;"},
                     {"selector": "td", "rule": "border: none !important;"},
                     {
                         "selector": ".dash-cell.focused",
                         "rule": "background-color: #C1C1C1 !important;",
                     },
                     {"selector": "table", "rule": "--accent: #1e2130;"},
                     {"selector": "tr", "rule": "background-color: transparent"},
                 ],
                 )]

    return [dropdown_table + configuration_table]

def build_controller_config_panel(controller_name, hardware_configuration):
    hardware_configuration = ControllerLibrary.UnpackHardwareConfiguration(hardware_configuration)
    if controller_name != 'new_controller' and controller_name != None:
        controller_type = hardware_configuration['controllers'][controller_name]['controller_type']
        #driver = hardware_configuration['devices'][controller_name]['driver']
    else:
        controller_type = None
        sensor = None
        actuator = None
        #driver = None

    dropdown_table = [html.Table(id="controller-config-table",
        children=[
        # html.Tr([html.Td("Device Type", className="halfwidth_cell"), html.Td("Driver", className="halfwidth_cell",style={'width': '50%'})]),
        # html.Tr([html.Td(FrontendLibrary.build_device_type_selector_dropdown(id="device-type-selector-dropdown", value=controller_type)),
        #          html.Td(FrontendLibrary.build_driver_type_selector_dropdown(id="driver-selector-dropdown", device_type=controller_type, value=driver))]),
        #html.Tr([html.Td("Controller Type", className="quarterwidth_cell"), html.Td(FrontendLibrary.build_controller_type_selector_dropdown(id="controller-type-selector-dropdown", value=controller_type), className='horizontal-fill-cell',)]),
        html.Tr([html.Td("Controller Type", className="quarterwidth_cell"), html.Td(
            FrontendLibrary.build_controller_type_selector_dropdown(id="controller-type-selector-dropdown",
                                                                    value=controller_type),
            className='horizontal-fill-cell', )]),
        html.Tr([html.Td("Output Type", className="quarterwidth_cell"), html.Td(
            FrontendLibrary.build_controller_output_type_selector_dropdown(id="controller-output-type-selector-dropdown",
                                                                    value=controller_type),
                                                                    className='horizontal-fill-cell',)]),
        html.Tr([html.Td("Sensor", className="quarterwidth_cell"), html.Td(
            FrontendLibrary.build_controller_sensor_selector_dropdown(
                id="controller-sensor-selector-dropdown",
                value=sensor,
                hardware_configuration=hardware_configuration),
            className='horizontal-fill-cell', )]),
        html.Tr([html.Td("Actuator", className="quarterwidth_cell"), html.Td(
            FrontendLibrary.build_controller_actuator_selector_dropdown(
                id="controller-actuator-selector-dropdown",
                value=actuator,
                hardware_configuration=hardware_configuration),
            className='horizontal-fill-cell', )]),
        html.Tr([html.Td("Interlock Device", className="quarterwidth_cell"), html.Td(
            FrontendLibrary.build_interlock_type_selector_dropdown(id="interlock-type-selector-dropdown",
                                                                    value=controller_type, hardware_configuration=hardware_configuration),
            className='horizontal-fill-cell')])
        ],
        style={'width': '100%'}

    )]

    configuration_table = [dt.DataTable(id='controller-parameters-table',
                 columns=[{'name': "Attribute", 'id': "attribute_name"},
                          {'name': "Value", 'id': "attribute_value"}],
                 #data=[{"attribute_name": "name", "attribute_value": ""}, {"attribute_name": "address", "attribute_value": "0x00"}],
                 data = [],
                 style_cell={#'padding': '5px',
                             'color': 'black',
                             'fontSize': 15, 'font-family': '\'Roboto Slab\', serif'},
                 style_header={
                     'backgroundColor': 'gray',
                     'fontWeight': 'bold',
                     'text-align': 'center'
                 },
                 editable=True,
                 style_cell_conditional=[
                     {'if': {'column_id': 'attribute_name'},
                      'width': '30%'}
                 ],
                 row_deletable=True,
                 css=[
                     {"selector": "tr:hover td", "rule": "color: #15A919 !important;"},
                     {"selector": "td", "rule": "border: none !important;"},
                     {
                         "selector": ".dash-cell.focused",
                         "rule": "background-color: #C1C1C1 !important;",
                     },
                     {"selector": "table", "rule": "--accent: #1e2130;"},
                     {"selector": "tr", "rule": "background-color: transparent"},
                 ],
                 )]

    return [dropdown_table + configuration_table]

def build_route_config_table(route=None, hardware_configuration=None):
    if route != None:
        route_dropdown_options = hardware_configuration['routes'][route]
    else:
        route_dropdown_options = []

    route_table = dt.DataTable(id='route-table',
                 columns=[{'name': "Route Segment Index", 'id': "segment_index"},
                          {'name': "Endpoint", 'id': "endpoint", "presentation": "dropdown"}],
                 #data=[{"segment_index": 1, "endpoint": ""}, {"segment_index": 1, "endpoint": ""}],
                 data = [],
                 style_cell={'padding': '5px',
                             'color': 'black',
                             'fontSize': 15,
                             'font-family': '\'Roboto Slab\', serif'},
                 style_header={
                     'backgroundColor': 'gray',
                     'fontWeight': 'bold',
                     'text-align': 'center'
                 },
                 editable=True,
                 dropdown={
                     'endpoint': {
                         'options': route_dropdown_options
                         #     [
                         #     {'label': 'a', 'value': 'a'},
                         #     {'label': 'b', 'value': 'b'}
                         # ]
                     }
                 },
                 style_cell_conditional=[
                     {'if': {'column_id': 'segment_index'},
                      'width': '30%'}
                 ],
                 row_deletable=True,
                 css=[
                     {"selector": "tr:hover td", "rule": "color: #15A919 !important;"},
                     {"selector": "td", "rule": "border: none !important;"},
                     {
                         "selector": ".dash-cell.focused",
                         "rule": "background-color: #C1C1C1 !important;",
                     },
                     {"selector": "table", "rule": "--accent: #1e2130;"},
                     {"selector": "tr", "rule": "background-color: white"},
                     {"selector": ".dash-cell column-1 dropdown", "rule": "color: white"}
                 ],
                 )
    return route_table

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
                    html.Div(className="double-gauge",
                        children=[
                            html.P("Low Side Pressure"),
                            daq.Gauge(
                                id="progress-gauge",
                                max=0,
                                min=-10,
                                value=-3,  # default size 200 pixel
                            ),
                        ]
                    ),
                    html.Div(className="double-gauge",
                             children=[
                                 html.P("High Side Pressure"),
                                 daq.Gauge(
                                     id="high-side-pressure-gauge",
                                     max=10,
                                     min=0,
                                     value=5,  # default size 200 pixel
                                 ),
                             ]
                    ),
                    # daq.Gauge(
                    #     id="progress-gauge",
                    #     max=max_length * 2,
                    #     min=0,
                    #     value=10,  # default size 200 pixel
                    # ),
                    # daq.LEDDisplay(
                    #     id="operator-led",
                    #     value="1704",
                    #     color="#92e0d3",
                    #     backgroundColor="#1e2130",
                    #     size=50,
                    # ),
                ],
            ),
            # html.Div(
            #     id="card-2",
            #     children=[
            #         html.P("Time to completion"),
            #         daq.Gauge(
            #             id="progress-gauge",
            #             max=max_length * 2,
            #             min=0,
            #             showCurrentValue=True,  # default size 200 pixel
            #         ),
            #     ],
            # ),
            html.Div(
                id="card-3",
                children=[
                    html.P("System Temperature"),
                    daq.Thermometer(
                        id="progress-gauge",
                        max=max_length * 2,
                        min=0,
                        value=88,  # default size 200 pixel
                    ),
                ],
            ),
            html.Div(
                id="card-4",
                children=[
                    html.P("System pH"),
                    daq.Gauge(
                        id="progress-gauge",
                        max=max_length * 2,
                        min=0,
                        value=100,  # default size 200 pixel
                    ),
                    daq.Gauge(
                        id="progress-gauge",
                        max=max_length * 2,
                        min=0,
                        value=100,  # default size 200 pixel
                    ),
                ],
            ),
            html.Div(
                id="card-utility",
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
            # # Piechart
            # html.Div(
            #     id="ooc-piechart-outer",
            #     className="four columns",
            #     children=[
            #         generate_section_banner("% OOC per Parameter"),
            #         generate_piechart(),
            #     ],
            # ),
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
            #histo_trace,
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
            "domain": [0, 1],
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
        # xaxis2={
        #     "title": "Count",
        #     "domain": [0.8, 1],  # 70 to 100 % of width
        #     "titlefont": {"color": "darkgray"},
        #     "showgrid": False,
        # },
        # yaxis2={
        #     "anchor": "free",
        #     "overlaying": "y",
        #     "side": "right",
        #     "showticklabels": False,
        #     "titlefont": {"color": "darkgray"},
        # },
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
                interval=3 * 1000,  # in milliseconds
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


