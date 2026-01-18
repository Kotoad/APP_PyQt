from Imports import get_utils, os, sys, subprocess
Utils = get_utils()
#MARK: Pico Auto Transfer
class PicoWAutoTransfer:
    """Automatic transfer with dependency checking"""
    
    @staticmethod
    def ensure_dependencies():
        """Install required packages if missing"""
        required = ['pyserial', 'mpremote']
        missing = []
        
        for package in required:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing.append(package)
        
        if missing:
            print(f"\n⚠ Installing missing dependencies: {', '.join(missing)}")
            for package in missing:
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", package],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    #print(f"✓ Installed {package}")
                except:
                    print(f"✗ Failed to install {package}")
    
    @staticmethod
    def transfer_file(source="File.py", target="main.py"):
        """Transfer with mpremote (preferred method)"""
        PicoWAutoTransfer.ensure_dependencies()
        
        try:
            # Try mpremote first (more reliable)
            cmd = ["mpremote", "cp", source, f":{target}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                #print(f"✓ Transfer successful: {source} → {target}")
                return True
            else:
                # If mpremote fails, try pyboard
                if "No module named 'serial'" in result.stderr:
                    #print("Installing pyserial...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyserial"])
                    # Retry
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                    if result.returncode == 0:
                        #print(f"✓ Transfer successful (retry): {source} → {target}")
                        return True
                
                print(f"✗ Transfer failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ Transfer timeout - Is Pico W connected and in bootloader mode?")
            return False
        except FileNotFoundError:
            print("✗ mpremote not found - installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mpremote"])
            # Retry recursively
            return PicoWAutoTransfer.transfer_file(source, target)
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return False

#MARK: Code Compiler
class CodeCompiler:
    def __init__(self):
        self.file = None
        self.indent_level = 0
        self.memory_indent_level = 0
        self.indent_str = "    "  # 4 spaces
        self.MC_compile = False  # Microcontroller mode flag
        self.GPIO_compile = False  # GPIO mode flag
        self.compiling_function = None  # Current function being compiled
        self.compiling_what = 'canvas'  # 'canvas' or 'function'
        self.header_lines = []
        self.main_lines = []
        self.function_lines = []
        self.footer_lines = []
        self.last_block = None
        self.btn_in_code = False
        self.led_in_code = False
        self.current_lines = self.header_lines  # Pointer to current lines being written
    
    def compile(self):
        """Main entry point"""
        self.MC_compile = False
        self.GPIO_compile = False
        self.indent_level = 0
        self.header_lines = []
        self.main_lines = []
        self.function_lines = []
        self.footer_lines = []
        self.current_lines = self.header_lines
        print("Compiling code to File.py...")
        #print(f"RPI Model: {Utils.app_settings.rpi_model}")
        #print(f"RPI Model Index: {Utils.app_settings.rpi_model_index}")
        if Utils.app_settings.rpi_model_index == 0:
            print(f"RPI Model selected: {Utils.app_settings.rpi_model} (Index: {Utils.app_settings.rpi_model_index})")
            self.MC_compile = True
        elif Utils.app_settings.rpi_model_index in (1,2,3,4,5,6,7):
            print(f"RPI Model selected: {Utils.app_settings.rpi_model} (Index: {Utils.app_settings.rpi_model_index})")
            self.GPIO_compile = True

        self.write_imports()
        self.write_setup()
        self.current_lines = self.main_lines
        # Find Start block
        start_block = self.find_block_by_type('Start')
        if start_block:
            print(f"Found Start block: {start_block['id']}")
            next_id = self.get_next_block(start_block['id'])
            print(f"Processing blocks starting from: {next_id}")
            self.process_block(next_id)
            
        if self.GPIO_compile:
            self.current_lines = self.footer_lines
            self.write_cleanup()
        file = open("File.py", "w")
        if file:
            file.writelines(self.header_lines)
            file.writelines(self.function_lines)
            file.writelines(self.main_lines)
            file.writelines(self.footer_lines)
            print("✓ Code written to File.py")
        else:
            print("✗ Error opening File.py for writing")
        file.close()

        if self.MC_compile:
            #print("\n--- Transferring to Pico W ---")
            PicoWAutoTransfer.transfer_file("File.py", "main.py")
    
    def process_block(self, block_id):
        """Process single block - dispatch to handler"""
        if not block_id:
            return
        if self.compiling_what == 'canvas':
            block = Utils.main_canvas['blocks'][block_id]
        elif self.compiling_what == 'function':
            block = Utils.functions[self.compiling_function]['blocks'][block_id]
        
        print(f"Processing block {block_id} of type {block['type']}")
        if block['type'] == 'If':
            self.handle_if_block(block)
        elif block['type'] in ('While', 'While_true'):
            self.handle_while_block(block)
        elif block['type'] == 'Timer':
            self.handle_timer_block(block)
        elif block['type'] == 'End':
            self.handle_end_block(block)
        elif block['type'] == 'Switch':
            self.handle_switch_block(block)
        elif block['type'] == 'Button':
            self.handle_button_block(block)
        elif block['type'] in ('Blink_LED', 'Toggle_LED', 'PWM_LED'):
            self.handle_LED_block(block)
        elif block['type'] in ("Sum","Subtract","Multiply","Divide","Modulo","Power","Square_root"):
            self.handle_math_block(block)
        elif block['type'] == 'Function':
            # Function call block
            self.handle_function_block(block)
        else:
            print(f"Unknown block type: {block['type']}")
            pass
    #MARK: Code Headers and Setup
    def write_imports(self):
        print("Writing import statements...")
        if self.GPIO_compile:
            self.writeline("import RPi.GPIO as GPIO\n")
            self.writeline("import time\n")
            
        elif self.MC_compile:
            self.writeline("from machine import Pin\n")
            self.writeline("import time\n")
        
        for block_id, block_info in Utils.main_canvas['blocks'].items():
                if block_info['type'] == 'Button':
                    self.btn_in_code = True
                if block_info['type'] in ('Blink_LED', 'Toggle_LED', 'PWM_LED'):
                    self.led_in_code = True
        for func_id, func_info in Utils.functions.items():
            for block_id, block_info in func_info['blocks'].items():
                if block_info['type'] == 'Button':
                    self.btn_in_code = True
                if block_info['type'] in ('Blink_LED', 'Toggle_LED', 'PWM_LED'):
                    self.led_in_code = True
        if self.btn_in_code:
            self.create_btn_class()
        if self.led_in_code:
            self.create_led_class()

    def write_setup(self):
        print("Writing setup code...")
        if self.GPIO_compile:
            self.writeline("GPIO.setmode(GPIO.BCM)\n")
            self.writeline("Devices_main = {")
            self.indent_level+=1
            for dev_name, dev_info in Utils.devices['main_canvas'].items():
                text = f"\"{dev_info['name']}\":{{\"name\":\"{dev_info['name']}\", \"PIN\": {dev_info['PIN']}, \"type\":\"{dev_info['type']}\"}},"
                self.writeline(text)
            self.indent_level-=1
            self.writeline("}\n")
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level+=1
            self.writeline("if dev_config['type'] == 'Output':")
            self.indent_level+=1
            self.writeline(f"GPIO.setup(dev_config['PIN'], GPIO.OUT)")
            self.indent_level-=1
            self.writeline("elif dev_config['type'] == 'Input':")
            self.indent_level+=1
            self.writeline(f"GPIO.setup(dev_config['PIN'], GPIO.IN)")
            self.indent_level-=1
            self.writeline("elif dev_config['type'] == 'Button':")
            self.indent_level+=1
            self.writeline(f"GPIO.setup(dev_config['PIN'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)")
            self.indent_level-=1
            self.writeline("if dev_config['type'] == 'PWM':")
            self.indent_level+=1
            self.writeline("GPIO.setup(dev_config['PIN'], GPIO.OUT)")
            self.writeline("dev_config['name'] = GPIO.PWM(dev_config['PIN'], 1000)")
            self.writeline("dev_config['name'].start(0)")
            self.writeline("if not hasattr(dev_config['name'], 'CurrentDutyCycle'):")
            self.indent_level+=1
            self.writeline("dev_config['name'].CurrentDutyCycle = 0")
            self.indent_level-=3
            
            self.writeline("Variables_main = {")
            self.indent_level+=1
            for var_name, var_info in Utils.variables['main_canvas'].items():
                text = f"\"{var_info['name']}\":{{"f"\"value\": {var_info['value']}}},"
                self.writeline(text)
            self.indent_level-=1
            self.writeline("}\n")
            
        elif self.MC_compile:
            self.writeline("Devices_main = {")
            self.indent_level+=1
            for dev_name, dev_info in Utils.devices['main_canvas'].items():
                text = f"\"{dev_info['name']}\":{{"f"\"PIN\": {dev_info['PIN'] if dev_info['PIN'] else 'None'}, \"type\":\"{dev_info['type']}\"}},"
                self.writeline(text)
            self.indent_level-=1
            self.writeline("}")
            self.writeline("Variables_main = {")
            self.indent_level+=1
            for var_name, var_info in Utils.variables['main_canvas'].items():
                text = f"\"{var_info['name']}\":{{"f"\"value\": {var_info['value']}}},"
                self.writeline(text)
            self.indent_level-=1
            self.writeline("}\n")
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level+=1
            self.writeline("if dev_config['type'] == 'Output':")
            self.indent_level+=1
            self.writeline(f"dev_name = Pin(dev_config['PIN'], Pin.OUT)")
            self.indent_level-=1
            self.writeline("elif dev_config['type'] == 'Input':")
            self.indent_level+=1
            self.writeline(f"dev_name = Pin(dev_config['PIN'], Pin.IN)")
            self.indent_level-=1
            self.indent_level-=1
                
    def write_cleanup(self):
        self.writeline("GPIO.cleanup()")

    #MARK: Device Classes
    def create_btn_class(self):
        print("Creating Button class...")
        self.writeline("\nclass Button:")
        self.indent_level += 1
        self.writeline("def __init__(self):")
        self.indent_level += 1
        self.writeline("pass")
        self.indent_level -= 1
        self.writeline("def is_pressed(self, pin):")
        self.indent_level += 1
        self.writeline("if GPIO.input(pin) == GPIO.HIGH:")
        self.indent_level += 1
        self.writeline("return True")
        self.indent_level -= 1
        self.writeline("else:")
        self.indent_level += 1
        self.writeline("return False")
        self.indent_level -= 2  # Back to class level
    
    def create_led_class(self):
        print("Creating LED class...")
        self.writeline("\nclass LED:")
        self.indent_level += 1
        self.writeline("def __init__(self):")
        self.indent_level += 1
        self.writeline("pass")
        self.indent_level -= 1
        self.writeline("def Toggle_LED(self, pin):")
        self.indent_level += 1
        self.writeline("if GPIO.input(pin) == GPIO.HIGH:")
        self.indent_level += 1
        self.writeline("GPIO.output(pin, GPIO.LOW)")
        self.indent_level -= 1
        self.writeline("else:")
        self.indent_level += 1
        self.writeline("GPIO.output(pin, GPIO.HIGH)")
        self.indent_level -= 2  # Back to method level
        self.writeline("def Blink_LED(self, pin, duration_ms):")
        self.indent_level += 1
        self.writeline("if GPIO.input(pin) == GPIO.HIGH:")
        self.indent_level += 1
        self.writeline("GPIO.output(pin, GPIO.LOW)")
        self.writeline("time.sleep(duration_ms / 1000)")
        self.writeline("GPIO.output(pin, GPIO.HIGH)")
        self.indent_level -= 1
        self.writeline("else:")
        self.indent_level += 1
        self.writeline("GPIO.output(pin, GPIO.HIGH)")
        self.writeline("time.sleep(duration_ms / 1000)")
        self.writeline("GPIO.output(pin, GPIO.LOW)")
        self.indent_level -= 2  # Back to method level
        self.writeline("def PWM_LED(self, pin, PWM_value):")
        self.indent_level += 1
        self.writeline("for dev_name, dev_config in Devices_main.items():")
        self.indent_level += 1
        self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'PWM':")
        self.indent_level += 1
        self.writeline("pwm_instance = dev_config['name']")
        self.writeline("current_duty = dev_config.get('CurrentDutyCycle', 0)")
        self.indent_level -= 3  # Back to method level
        self.writeline("if PWM_value < current_duty:")
        self.indent_level += 1
        self.writeline("for duty_cycle in range(current_duty, PWM_value + 1):")
        self.indent_level += 1
        self.writeline("pwm_instance.ChangeDutyCycle(duty_cycle)")
        self.writeline("time.sleep(0.05)")
        self.indent_level -= 2
        self.writeline("elif PWM_value > current_duty:")
        self.indent_level += 1
        self.writeline("for duty_cycle in range(current_duty, PWM_value - 1, -1):")
        self.indent_level += 1
        self.writeline("pwm_instance.ChangeDutyCycle(duty_cycle)")
        self.writeline("time.sleep(0.05)")
        self.indent_level -= 2
        self.writeline("dev_config['CurrentDutyCycle'] = PWM_value")
        self.indent_level -= 2  # Back to class level

    #MARK: Helper Methods
    def find_block_by_type(self, block_type):
        """Find first block of given type"""
        if self.compiling_what == 'canvas':
            search_infos = Utils.main_canvas['blocks']
        elif self.compiling_what == 'function':
            search_infos = Utils.functions[self.compiling_function]['blocks']
        for block_id, block_info in search_infos.items():
            if block_info['type'] == block_type:
                return block_info
        return None
    
    def get_next_block(self, current_block_id):
        """Get the block connected to output of current block"""
        print(f"Getting next block from {current_block_id}")
        if self.compiling_what == 'canvas':
            current_info = Utils.main_canvas['blocks'][current_block_id]
        elif self.compiling_what == 'function':
            current_info = Utils.functions[self.compiling_function]['blocks'][current_block_id]
        
        # Get first out_connection
        if current_info['out_connections']:
            first_connection_id = current_info['out_connections'][0]
            
            # Find which block this connection goes to
            if self.compiling_what == 'canvas':
                search_infos = Utils.main_canvas['blocks']
            elif self.compiling_what == 'function':
                search_infos = Utils.functions[self.compiling_function]['blocks']
            for block_id, info in search_infos.items():
                if first_connection_id in info['in_connections']:
                    print(f"Next block is {block_id}")
                    return block_id
        return None 
    
    def resolve_value(self, value_str, value_type):
        """Convert value to actual value - handle variable or literal"""
        if value_type in ('switch', 'N/A'):
            #print(f"Resolving value: {value_str}")
            return value_str  # Return as is for switch
        
        if self.is_variable_reference(value_str):
            #print(f"Resolving variable reference: {value_str}")
            # Look up variable's current runtime value
            if value_type == 'Device':
                print(f"Looking up device: {value_str}")
                print(f"Utils.devices: {Utils.devices}")
                if self.compiling_what == 'canvas':
                    print(f"Searching in main canvas devices")
                    search_devices = Utils.devices['main_canvas']
                elif self.compiling_what == 'function':
                    print(f"Searching in function canvas devices for function {self.compiling_function}")
                    search_devices = Utils.devices['function_canvases'][self.compiling_function]
                print(f"Devices to search: {search_devices}")
                if self.compiling_what == 'canvas':
                    for dev_id, dev_info in search_devices.items():
                        print(dev_info)
                        if dev_info['name'] == value_str:
                            print(f"Found device {value_str} with PIN {dev_info['PIN']}")
                            return f"Devices_main['{value_str}']['PIN']"
                elif self.compiling_what == 'function':
                    return f"{value_str}"
            elif value_type == 'Variable':
                print(f"Looking up variable: {value_str}")
                print(f"Utils.variables: {Utils.variables}")
                if self.compiling_what == 'canvas':
                    print(f"Searching in main canvas variables")
                    search_variables = Utils.variables['main_canvas']
                elif self.compiling_what == 'function':
                    print(f"Searching in function canvas variables for function {self.compiling_function}")
                    search_variables = Utils.variables['function_canvases'][self.compiling_function]
                print(f"Variables to search: {search_variables}")
                if self.compiling_what == 'canvas':
                    for var_id, var_info in search_variables.items():
                        print(var_info)
                        if var_info['name'] == value_str:
                            print(f"Found variable {value_str} with value {var_info['value']}")
                            return f"Variables_main['{value_str}']['value']"
                elif self.compiling_what == 'function':
                    return f"{value_str}"
                
        else:
            print(f"Using literal value: {value_str}")
            pass
        return value_str  # It's a literal
    
    def is_variable_reference(self, value_str):
        """Check if value is a variable name (not a number)"""
        try:
            float(value_str)  # Can convert to number?
            #print(f"{value_str} is a literal number.")
            return False      # It's a literal number
        except ValueError:
            #print(f"{value_str} is a variable reference.")
            return True 
        
    def writeline(self, text):
        """Write indented line"""
        indent = self.indent_str * self.indent_level
        self.current_lines.append(indent + text + "\n")
        
    def write_condition(self, type,  value1, operator, value2):
        """Write condition code - DRY principle"""
        text = f"{type} {value1} {operator} {value2}:"
        #print(f"Writing condition: {text}")
        self.writeline(text)
    
    def get_comparison_operator(self, combo_value):
        #print(f"Mapping combo value '{combo_value}' to operator")
        """Map combo box value to Python operator"""
        operators = {
            "==": "==",
            "!=": "!=",
            "<": "<",
            "<=": "<=",
            ">": ">",
            ">=": ">="
        }
        print(f"Mapped to operator: {operators.get(combo_value, '==')}")
        return operators.get(combo_value, "==")

    def get_next_block_from_output(self, current_block_id, output_circle):
        """Get the block connected to specific output circle of current block"""
        if self.compiling_what == 'canvas':
            current_info = Utils.main_canvas['blocks'][current_block_id]
        elif self.compiling_what == 'function':
            current_info = Utils.functions[self.compiling_function]['blocks'][current_block_id]

        # Find connection from specified output circle
        for conn_id in current_info['out_connections']:
            conn_info = Utils.paths.get(conn_id)
            if conn_info and conn_info['from_circle_type'] == output_circle:
                # Find which block this connection goes to
                if self.compiling_what == 'canvas':
                    search_infos = Utils.main_canvas['blocks']
                elif self.compiling_what == 'function':
                    search_infos = Utils.functions[self.compiling_function]['blocks']
                for block_id, info in search_infos.items():
                    if conn_id in info['in_connections']:
                        return block_id
        return None
    
    #MARK: Block Handlers
    def handle_if_block(self, block):
        #print(f"Handling If block {block}")
        value_1 = self.resolve_value(block['value_1_name'], block['value_1_type'])
        value_2 = self.resolve_value(block['value_2_name'], block['value_2_type'])
        #print(f"Resolved If block values: {value_1}, {value_2}")
        operator = self.get_comparison_operator(block['operator'])
        #print(f"Using operator: {operator}")
        out1_id = self.get_next_block_from_output(block['id'], 'out1')  # True path
        out2_id = self.get_next_block_from_output(block['id'], 'out2')  # False path
        #print(f"If block outputs: out1 -> {out1_id}, out2 -> {out2_id}")
        self.write_condition("if", value_1, operator, value_2)
        self.indent_level += 1
        self.process_block(out1_id)
        #print(f"Completed If true branch, now handling else branch")
        self.indent_level -= 1
        self.writeline("else:")
        #print(f"Processing else branch for If block")
        self.indent_level += 1
        self.process_block(out2_id)
        
        self.indent_level -= 1
    
    def handle_while_block(self, block):
        if block['type'] == 'While_true':
            #print(f"Handling While true block {block}")
            next_id = self.get_next_block(block['id'])
            self.writeline("while True:")
            self.indent_level += 1
            #print(f"Processing While true branch for While true block")
            self.process_block(next_id)
            self.indent_level -= 1
            return
        
        value_1 = self.resolve_value(block['value_1_name'], block['value_1_type'])
        value_2 = self.resolve_value(block['value_2_name'], block['value_2_type'])
        #print(f"Resolved While block values: {value_1}, {value_2}")
        operator = self.get_comparison_operator(block['operator'])
        #print(f"Using operator: {operator}")
        out1_id = self.get_next_block_from_output(block['id'], 'out1')  # True path
        out2_id = self.get_next_block_from_output(block['id'], 'out2')  # False path
        #print(f"While block outputs: out1 -> {out1_id}, out2 -> {out2_id}")
        self.write_condition("while", value_1, operator, value_2)
        self.indent_level += 1
        #print(f"Processing While true branch for While block")
        self.process_block(out1_id)
        self.indent_level -= 1
        #print(f"Processing While false branch for While block")
        self.process_block(out2_id)
           
    def handle_timer_block(self, block):
        self.writeline(f"time.sleep({block['sleep_time']}/1000)")
        
        next_id = self.get_next_block(block['id'])
        if next_id:
            #print(f"Processing next block after Timer: {next_id}")
            pass
        self.process_block(next_id)
    
    def handle_switch_block(self, block):
        switch_state = block['switch_state']
    
    # ✅ Check if it's already a boolean
        if isinstance(switch_state, bool):
            switch_state = switch_state 
        else:
            # Only resolve if it's a string (variable reference or literal)
            switch_state = self.resolve_value(switch_state, 'switch')
        
        Var_1 = self.resolve_value(block['value_1_name'], 'Device')
        
        #print(f"Resolved Switch block value: {switch_state} (type: {type(switch_state).__name__})")
        if self.GPIO_compile:
            if switch_state is True:
                #print(f"Writing GPIO HIGH for Switch block")
                self.writeline(f"GPIO.output({Var_1}, GPIO.HIGH)")
            elif switch_state is False:
                #print(f"Writing GPIO LOW for Switch block")
                self.writeline(f"GPIO.output({Var_1}, GPIO.LOW)")
            else:
                #print(f"Unknown Switch value {switch_state}, defaulting to LOW")
                self.writeline(f"GPIO.output({Var_1}, GPIO.LOW)")
        elif self.MC_compile:
            if switch_state is True:
                #print(f"Writing PIN HIGH for Switch block")
                self.writeline(f"{Var_1}.value(1)")
            elif switch_state is False:
                #print(f"Writing PIN LOW for Switch block")
                self.writeline(f"{Var_1}.value(0)")
            else:
                #print(f"Unknown Switch value {switch_state}, defaulting to LOW")
                self.writeline(f"{Var_1}.value(0)")
        next_id = self.get_next_block(block['id'])
        if next_id:
            #print(f"Processing next block after Switch: {next_id}")
            pass
        self.process_block(next_id)
    
    def handle_button_block(self, block):
        DEV_1 = self.resolve_value(block['value_1_name'], block['value_1_type'])
        out1_id = self.get_next_block_from_output(block['id'], 'out1')  # ON path
        out2_id = self.get_next_block_from_output(block['id'], 'out2')
        #print(f"Resolved Button block device: {DEV_1}")
        if self.GPIO_compile:
            self.writeline(f"if Button().is_pressed({DEV_1}):")
            self.indent_level += 1
            #print(f"Processing Button ON branch for Button block")
            self.process_block(out1_id)
            self.indent_level -= 1
            self.writeline("else:")
            #print(f"Processing Button OFF branch for Button block")
            self.indent_level += 1
            self.process_block(out2_id)
            self.indent_level -= 1
        elif self.MC_compile:
            self.writeline(f"if Button().is_pressed({DEV_1}):")
            self.indent_level += 1
            #print(f"Processing Button ON branch for Button block")
            self.process_block(out1_id)
            self.indent_level -= 1
            self.writeline("else:")
            #print(f"Processing Button OFF branch for Button block")
            self.indent_level += 1
            self.process_block(out2_id)
            self.indent_level -= 1
            
    def handle_function_block(self, block):
        print(f"Handling Function block {block['id']}")
        self.last_block = block
        func_name = block['name']
        print(f"Calling function: {func_name}")
        self.writeline(f"{func_name}(")
        print(f"block internal vars: {block['internal_vars']}")
        print(f"block internal devs: {block['internal_devs']}")
        self.indent_level += 1
        for l_widget, v_info in block['internal_vars']['main_vars'].items():
            print(f"Function argument: {v_info['name']}")
            resolved_value = self.resolve_value(v_info['name'], v_info['type'])
            print(f"Resolved argument value: {resolved_value}")
            self.writeline(f"{resolved_value},")
        for l_widget, d_info in block['internal_devs']['main_devs'].items():
            print(f"Function device argument: {d_info['name']}")
            resolved_value = self.resolve_value(d_info['name'], d_info['type'])
            print(f"Resolved device argument value: {resolved_value}")
            self.writeline(f"{resolved_value},")
        self.indent_level -= 1
        self.writeline(")")
        self.memory_indent_level = self.indent_level
        self.indent_level = 0  # Reset indent for function definition
        self.current_lines = self.function_lines
        self.writeline("")  # Blank line before function
        self.writeline(f"def {func_name}(")
        self.indent_level += 1
        print(f"ref_vars: {block['internal_vars']['ref_vars']}")
        print(f"ref_devs: {block['internal_devs']['ref_devs']}")
        for l_widget, v_info in block['internal_vars']['ref_vars'].items():
            print(f"Function variable parameter: {v_info['name']}")
            self.writeline(f"{v_info['name']},")
        for l_widget, d_info in block['internal_devs']['ref_devs'].items():
            print(f"Function device parameter: {d_info['name']}")
            self.writeline(f"{d_info['name']},")
        self.indent_level -= 1
        self.writeline("):")
        self.indent_level += 1
        self.compiling_what = 'function'
        for f_id, f_info in Utils.functions.items():
            #print(f"{f_id}: {f_info}")
            if f_info['name'] == func_name:
                self.compiling_function = f_info['id']
                break
        print(f"Compiling function: {self.compiling_function}, compiling_what: {self.compiling_what}")
        start_function_block = self.find_block_by_type('Start')
        print(f"Function start block: {start_function_block}")
        next_id = self.get_next_block(start_function_block['id'])
        print(f"Processing function blocks starting from: {next_id}")
        self.process_block(next_id)

    def handle_math_block(self, block):
        value_1 = self.resolve_value(block['value_1_name'], block['value_1_type'])
        value_2 = self.resolve_value(block['value_2_name'], block['value_2_type'])
        result_var = block['result_var_name']
        #print(f"Resolved Math block values: {value_1}, {value_2}, result var: {result_var}")
        if block['type'] == 'Sum':
            self.writeline(f"{result_var} = {value_1} + {value_2}")
        elif block['type'] == 'Subtract':
            self.writeline(f"{result_var} = {value_1} - {value_2}")
        elif block['type'] == 'Multiply':
            self.writeline(f"{result_var} = {value_1} * {value_2}")
        elif block['type'] == 'Divide':
            self.writeline(f"{result_var} = {value_1} / {value_2}")
        elif block['type'] == 'Modulo':
            self.writeline(f"{result_var} = {value_1} % {value_2}")
        elif block['type'] == 'Power':
            self.writeline(f"{result_var} = {value_1} ** {value_2}")
        elif block['type'] == 'Square_root':
            self.writeline(f"{result_var} = {value_1} ** 0.5")
        
        next_id = self.get_next_block(block['id'])
        if next_id:
            #print(f"Processing next block after Math: {next_id}")
            pass
        self.process_block(next_id)
    
    def handle_LED_block(self, block):
        DEV_1 = self.resolve_value(block['value_1_name'], block['value_1_type'])
        if block['type'] == 'Blink_LED':
            duration = block['duration_ms']
            self.writeline(f"LED().Blink_LED({DEV_1}, {duration})")
        elif block['type'] == 'Toggle_LED':
            self.writeline(f"LED().Toggle_LED({DEV_1})")
        elif block['type'] == 'PWM_LED':
            pwm_value = self.resolve_value(block['value_1_name'], block['value_1_type'])
            self.writeline(f"LED().PWM_LED({DEV_1}, {pwm_value})")
        
        next_id = self.get_next_block(block['id'])
        if next_id:
            #print(f"Processing next block after LED: {next_id}")
            pass
        self.process_block(next_id)
    


    def handle_end_block(self, block):
        #print(f"Handling End block {block['id']}")
        if self.compiling_what == 'function':
            print(f"Ending function compilation for {self.compiling_function}")
            self.compiling_what = 'canvas'
            self.compiling_function = None
            self.writeline("")  # Blank line after function
            self.current_lines = self.main_lines
            self.indent_level = self.memory_indent_level
            print(f"Resuming canvas compilation at indent level {self.indent_level}")
            print(f"Last block was function call: {self.last_block}")
            next_id = self.get_next_block(self.last_block['id'])
            self.process_block(next_id)
        else:
            print("End block reached in canvas - no action needed")
        return