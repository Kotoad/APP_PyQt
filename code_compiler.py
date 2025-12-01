import Utils

class Codecompiler:
    def __init__(self):
        pass
    
    def Start():
        print("Code Compilation Started")
        for block_id, top_info in Utils.top_infos.items():
            if top_info['type'] == 'Start':
                print(f"Start, top_info: out_connection: {top_info['out_connections']}")
                IDS_unspit = str(top_info['out_connections'])
                IDS = IDS_unspit.split("_")[1].strip("']")
                with open("File.py", "a") as file:
                    file.write("import RPi.GPIO as GPIO\n")
                    for block_id, top_info in Utils.top_infos.items():
                        if top_info['type'] == 'Timer':
                            file.write("import time\n")
                            break
                    for var_name, var_info in Utils.variables.items():
                        file.write(f"{var_name} = {var_info['PIN']}\n")
                    file.write("GPIO.setmode(GPIO.BCM)\n")
                    for var_name, var_info in Utils.variables.items():
                        file.write(f"GPIO.setup({var_info['name']}, GPIO.OUT)\n")
                break
        
        while True:
            found_match = False
            for block_id, top_info in Utils.top_infos.items():
                if top_info['type'] != 'Start' and top_info['type'] != 'End':
                    print(f"IDS {IDS}, Top ID {top_info['id']}")
                    if IDS == str(top_info['id']):
                        print(f"Process, top_info: out_connection: {top_info['out_connections']}")
                        if top_info['type'] == 'If':
                            print("If")
                            condition = top_info['value_1'] + " " + top_info['combo_index'] + " " + top_info['value_2']
                            if top_info['value_1'] is not int:
                                for var_name, var_info in Utils.variables.items():
                                    if top_info['value_1'] == var_info['name']:
                                        value_1 = var_info['value']
                            if top_info['value_2'] is not int:
                                for var_name, var_info in Utils.variables.items():
                                    if top_info['value_2'] == var_info['name']:
                                        value_2 = var_info['value']
                            combo_value = top_info['combo_index']
                            if combo_value == "==":
                                with open("File.py", "a") as file:
                                    file.write(f"#condition: {condition}\n")
                                    file.write(f"if {value_1} == {value_2}:\n")
                            elif combo_value == "!=":
                                with open("File.py", "a") as file:
                                    file.write(f"#condition: {condition}\n")
                                    file.write(f"if {value_1} != {value_2}:\n")
                            elif combo_value == "<":
                                with open("File.py", "a") as file:
                                    file.write(f"#condition: {condition}\n")
                                    file.write(f"if {value_1} < {value_2}:\n")
                            elif combo_value == "<=":
                                with open("File.py", "a") as file:
                                    file.write(f"#condition: {condition}\n")
                                    file.write(f"if {value_1} <= {value_2}:\n")
                            elif combo_value == ">":
                                with open("File.py", "a") as file:
                                    file.write(f"#condition: {condition}\n")
                                    file.write(f"if {value_1} > {value_2}:\n")
                            elif combo_value == ">=":
                                with open("File.py", "a") as file:
                                    file.write(f"#condition: {condition}\n")
                                    file.write(f"if {value_1} >= {value_2}:\n")
                        elif top_info['type'] == 'While':
                            print("While")
                            condition = top_info['value_1'] + " " + top_info['combo_index'] + " " + top_info['value_2']
                            if top_info['value_1'] is not int:
                                for var_name, var_info in Utils.variables.items():
                                    if top_info['value_1'] == var_info['name']:
                                        value_1 = var_info['value']
                            if top_info['value_2'] is not int:
                                for var_name, var_info in Utils.variables.items():
                                    if top_info['value_2'] == var_info['name']:
                                        value_2 = var_info['value']
                            combo_value = top_info['combo_index']
                            if combo_value == "==":
                                with open("File.py", "a") as file:
                                    file.write(f"#condition: {condition}\n")
                                    file.write(f"while {value_1} == {value_2}:\n")
                            elif combo_value == "!=":
                                with open("File.py", "a") as file:
                                    file.write(f"#condition: {condition}\n")
                                    file.write(f"while {value_1} != {value_2}:\n")
                            elif combo_value == "<":
                                with open("File.py", "a") as file:
                                    file.write(f"#condition: {condition}\n")
                                    file.write(f"while {value_1} < {value_2}:\n")
                            elif combo_value == "<=":
                                with open("File.py", "a") as file:
                                    file.write(f"#condition: {condition}\n")
                                    file.write(f"while {value_1} <= {value_2}:\n")
                            elif combo_value == ">":
                                with open("File.py", "a") as file:
                                    file.write(f"#condition: {condition}\n")
                                    file.write(f"while {value_1} > {value_2}:\n")
                            elif combo_value == ">=":
                                with open("File.py", "a") as file:
                                    file.write(f"#condition: {condition}\n")
                                    file.write(f"while {value_1} >= {value_2}:\n")
                        elif top_info['type'] == 'Timer':
                            print("Time Delay")
                            with open("File.py", "a") as file:
                                print(f"Time Delay of {top_info['value_1']} seconds")
                                file.write(f"time.sleep({top_info['value_1']})\n")
                        
                        IDS_unspit = str(top_info['out_connections'])
                        IDS = IDS_unspit.split("_")[1].strip("']")
                        print(f"IDS updated to {IDS}")
                        with open("File.py", "a") as file:
                            file.write("Process\n")
                        found_match = True
                        break  # Přeruš vnitřní smyčku a začni znovu
            
            if not found_match:
                break
                
        for block_id, top_info in Utils.top_infos.items():
            if top_info['type'] == 'End':
                if IDS == str(top_info['id']):
                    print("End")
                    with open("File.py", "a") as file:
                        file.write("End\n")