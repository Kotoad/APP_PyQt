import Utils

class Codecompiler:
    def __init__(self):
        pass
    
    def Start():
        
        
        
        for block_id, top_info in Utils.top_infos.items():
            if top_info['type'] == 'Start':
                print(f"Start, top_info: out_connection: {top_info['out_connections']}")
                IDS_unspit = str(top_info['out_connections'])
                IDS = IDS_unspit.split("_")[1].strip("']")
                with open("File.py", "a") as file:
                    file.write("import RPi.GPIO as GPIO\n")
                    for block_id, top_info in Utils.top_infos.items():
                        if top_info['type'] == 'Mid':
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