from Imports import get_utils
Utils = get_utils()


class DataControl:
    def __init__(self):
        pass

    def inicilize_date(self, block, block_type, block_id, x, y, name=None):
        """Load data from a block into the application state."""
        # Placeholder for loading data logic
        print(f"Loading data from block: {block_id} of type {block_type}")
        if block_type in ('If', 'While', 'Button'):
            info = {
                'type': block_type.split('_')[0],
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'value_1_name': None,
                'value_1_type': None,
                'value_2_name': None,
                'value_2_type': None,
                'operator': "==",
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == 'Timer':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'sleep_time': "1000",
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == 'Switch':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'value_1_name': None,
                'switch_state': False,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type in ('Start', 'End', 'While_true'):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == "Function":
            info = {
                'type': 'Function',
                'id': block_id,
                'name': name,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'internal_vars': {
                    'main_vars': {},
                    'ref_vars': {},
                },
                'internal_devs': {
                    'main_devs': {},
                    'ref_devs': {},
                },
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type in ("Basic_operations", "Exponential_operations", "Random_number"):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'value_1_name': None,
                'value_1_type': None,
                'value_2_name': None,
                'value_2_type': None,
                'operator': None,
                'result_var_name': None,
                'result_var_type': None,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == "Blink_LED":
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'value_1_name': None,
                'value_1_type': None,
                'sleep_time': "1000",
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == "Toggle_LED":
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'value_1_name': None,
                'value_1_type': None,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == "PWM_LED":
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'value_1_name': None,
                'value_1_type': None,
                'PWM_value': "50",
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        else:
            print(f"Error: Unknown block type {block_type}")
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        return info
    
    def load_from_data(self, block, block_id, block_type, x, y, canvas, from_where):
        """Load block data into the application state."""
        # Placeholder for loading data logic
        if from_where == 'canvas':
            if block_type in ('If', 'While', 'Button'):
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'value_1_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1"),
                    'value_1_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_type', "N/A"),
                    'value_2_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_2_name', "var2"),
                    'value_2_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_2_type', "N/A"),
                    'operator': Utils.project_data.main_canvas['blocks'][block_id].get('operator', "=="),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type == 'Timer':
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'sleep_time': Utils.project_data.main_canvas['blocks'][block_id].get('sleep_time', "1000"),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type == 'Switch':
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'value_1_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1"),
                    'switch_state': Utils.project_data.main_canvas['blocks'][block_id].get('switch_state', False),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type in ('Start', 'End', 'While_true'):
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type in ("Basic_operations", "Exponential_operations", "Random_number"):
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'value_1_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1"),
                    'value_1_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_type', "N/A"),
                    'value_2_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_2_name', "var2"),
                    'value_2_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_2_type', "N/A"),
                    'operator': Utils.project_data.main_canvas['blocks'][block_id].get('operator', None),
                    'result_var_name': Utils.project_data.main_canvas['blocks'][block_id].get('result_var_name', "result"),
                    'result_var_type': Utils.project_data.main_canvas['blocks'][block_id].get('result_var_type', "N/A"),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type == 'Blink_LED':
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'value_1_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1"),
                    'value_1_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_type', "N/A"),
                    'sleep_time': Utils.project_data.main_canvas['blocks'][block_id].get('sleep_time', "1000"),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type == 'Toggle_LED':
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'value_1_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1"),
                    'value_1_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_type', "N/A"),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type == 'PWM_LED':
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'value_1_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1"),
                    'value_1_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_type', "N/A"),
                    'PWM_value': Utils.project_data.main_canvas['blocks'][block_id].get('PWM_value', "50"),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type == 'Function':
                info = {
                    'type': 'Function',
                    'id': block_id,
                    'name': Utils.project_data.main_canvas['blocks'][block_id].get('name', ''),
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'internal_vars': {
                        'main_vars': Utils.project_data.main_canvas['blocks'][block_id]['internal_vars'].get('main_vars', {}),
                        'ref_vars': Utils.project_data.main_canvas['blocks'][block_id]['internal_vars'].get('ref_vars', {}),
                    },
                    'internal_devs': {
                        'main_devs': Utils.project_data.main_canvas['blocks'][block_id]['internal_devs'].get('main_devs', {}),
                        'ref_devs': Utils.project_data.main_canvas['blocks'][block_id]['internal_devs'].get('ref_devs', {}),
                    },
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            else:
                print(f"Error: Unknown block type {block_type}")
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
           
        elif from_where == 'function':
            #print("Storing function canvas block in Utils")
            for function_id, function_info in Utils.functions.items():
                #print(f" Checking function: {function_id}")
                if function_info['canvas'] == canvas:
                    #print(f" Found matching canvas for function: {function_id}")
                    if block_type in ('If', 'While', 'Button'):
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'value_1_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1"),
                            'value_1_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_type', "N/A"),
                            'value_2_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_2_name', "var2"),
                            'value_2_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_2_type', "N/A"),
                            'operator': Utils.project_data.functions[function_id]['blocks'][block_id].get('operator', "=="),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type == 'Timer':
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'sleep_time': Utils.project_data.functions[function_id]['blocks'][block_id].get('sleep_time', "1000"),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type == 'Switch':
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'value_1_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1"),
                            'switch_state': Utils.project_data.functions[function_id]['blocks'][block_id].get('switch_state', False),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type in ('Start', 'End', 'While_true'):
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type in ("Basic_operations", "Exponential_operations", "Random_number"):
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'value_1_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1"),
                            'value_1_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_type', "N/A"),
                            'value_2_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_2_name', "var2"),
                            'value_2_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_2_type', "N/A"),
                            'operator': Utils.project_data.functions[function_id]['blocks'][block_id].get('operator', None),
                            'result_var_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('result_var_name', "result"),
                            'result_var_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('result_var_type', "N/A"),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type == 'Blink_LED':
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'value_1_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1"),
                            'value_1_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_type', "N/A"),
                            'sleep_time': Utils.project_data.functions[function_id]['blocks'][block_id].get('sleep_time', "1000"),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type == 'Toggle_LED':
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'value_1_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1"),
                            'value_1_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_type', "N/A"),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type == 'PWM_LED':
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'value_1_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1"),
                            'value_1_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_type', "N/A"),
                            'PWM_value': Utils.project_data.functions[function_id]['blocks'][block_id].get('PWM_value', "50"),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type == 'Function':
                        info = {
                            'type': 'Function',
                            'id': block_id,
                            'name': Utils.project_data.functions[function_id]['blocks'][block_id].get('name', ''),
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'internal_vars': {
                                'main_vars': Utils.project_data.functions[function_id]['blocks'][block_id]['internal_vars'].get('main_vars', {}),
                                'ref_vars': Utils.project_data.functions[function_id]['blocks'][block_id]['internal_vars'].get('ref_vars', {}),
                            },
                            'internal_devs': {
                                'main_devs': Utils.project_data.functions[function_id]['blocks'][block_id]['internal_devs'].get('main_devs', {}),
                                'ref_devs': Utils.project_data.functions[function_id]['blocks'][block_id]['internal_devs'].get('ref_devs', {}),
                            },
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    else:
                        print(f"Error: Unknown block type {block_type}")
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    break
        return info