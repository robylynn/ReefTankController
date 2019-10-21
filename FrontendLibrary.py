import dash_core_components as dcc
import HAL
import os

CACHE_CONFIG = {
    # try 'filesystem' if you don't want to setup redis
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379')
}

def build_port_selector_dropdown(value=None, port_types=HAL.PORT_TYPES):
    return dcc.Dropdown(id="new-port-select-dropdown",
                        options=list({"label": port, "value": port} for port in port_types),
                        #value=list({"label": value, "value": value}),
                        value=value,
                        )

def build_device_selector_dropdown_options_list(hardware_configuration={}):
    return [{"label": 'New Device...', "value": "new_device"}] + [
        {"label": device + ' (' + hardware_configuration['devices'][device]['device_type'] + ')', "value": device} for
        device in hardware_configuration['devices']]
    # return dcc.Dropdown(id=id,
    #                     options=list({"label": device, "value": device} for device in sorted(list(device_types.keys()))),
    #                     #value=list({"label": value, "value": value}),
    #                     value=value,
    #                     )

def build_route_selector_options_list(hardware_configuration={}):
    return [{'label': hardware_configuration['devices'][device]['name'] + ' (' + str(
        len(hardware_configuration['routes'][hardware_configuration['devices'][device]['name']])) + ' segment(s))',
            'value': hardware_configuration['devices'][device]['name']} for device in hardware_configuration['devices'].keys()]

def build_device_type_selector_dropdown(id="device-type-select-dropdown", value=None, device_types=HAL.SUPPORTED_DEVICES):
    return dcc.Dropdown(id=id,
                        options=list({"label": device, "value": device} for device in sorted(list(device_types.keys()))),
                        #value=list({"label": value, "value": value}),
                        value=value,
                        )

def build_driver_type_selector_dropdown(id="driver-select-dropdown", value=None, device_type=None, driver_types=HAL.SUPPORTED_DEVICES):
    if device_type != '' and device_type != None:
        supported_drivers = HAL.INSTALLED_DRIVERS[device_type]
    else:
        supported_drivers = []
    return dcc.Dropdown(id=id,
                        options=list({"label": driver, "value": driver} for driver in supported_drivers),
                        #value=list({"label": value, "value": value}),
                        value=value,
                        )

def build_pin_selector_dropdown(value=None, GPIO_pins=HAL.GPIO_PINS):
    return dcc.Dropdown(id="new-port-select-dropdown",
                        options=list({"label": pin, "value": pin} for pin in GPIO_pins),
                        #value=list({"label": value, "value": value}),
                        value=value
                        )

# def build_complete_attribute_option_list():
#     combined_attribute_keys = []
#     for device_type in HAL.SUPPORTED_DEVICES.keys():
#         combined_attribute_keys += list(HAL.SUPPORTED_DEVICES[device_type].keys())
#     return sorted(list(set((combined_attribute_keys))))

def lookup_port_by_name(port_name=None, configured_ports=None):
    for port in configured_ports:
        if port.name == port_name:
            return port
    return False

def lookup_device_by_name(device_name=None, configured_devices=None):
    for device in configured_devices:
        if device.name == device_name:
            return device
    return False

def lookup_port_index_in_hardware_configuration(port=None, port_configuration=None):
    for port_index in range(len(port_configuration)):
        if port.name == port_configuration[port_index].name:
            return port_index
    return -1