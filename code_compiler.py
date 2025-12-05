import Utils
class CodeCompiler:
    def __init__(self):
        self.file = None
        self.indent_level = 0
        self.indent_str = "    "  # 4 spaces
    
    def compile(self):
        """Main entry point"""
        self.file = open("File.py", "w")
        print("Compiling code to File.py...")
        self.write_imports()
        self.write_setup()
        
        # Find Start block
        start_block = self.find_block_by_type('Start')
        if start_block:
            next_id = self.get_next_block(start_block['id'])
            self.process_block(next_id)
        
        self.write_cleanup()
        self.file.close()
    
    def process_block(self, block_id):
        """Process single block - dispatch to handler"""
        if not block_id:
            return
        
        block = Utils.top_infos[block_id]
        
        print(f"Processing block {block_id} of type {block['type']}")
        
        if block['type'] == 'If':
            self.handle_if_block(block)
        elif block['type'] == 'While':
            self.handle_while_block(block)
        elif block['type'] == 'Timer':
            self.handle_timer_block(block)
        elif block['type'] == 'End':
            self.handle_end_block(block)
        elif block['type'] == 'Switch':
            self.handle_switch_block(block)
        else:
            print(f"Unknown block type: {block['type']}")
            pass
        
    def write_imports(self):
        self.file.write("import RPi.GPIO as GPIO\n")
        for block_id, top_info in Utils.top_infos.items():
            if top_info['type'] == 'Timer':
                self.file.write("import time\n")
                break
    
    def write_setup(self):
        for dev_name, dev_info in Utils.devices.items():
            self.file.write(f"{dev_info['name']} = {dev_info['value']}\n")
        self.file.write("GPIO.setmode(GPIO.BCM)\n")
        for dev_name, dev_info in Utils.devices.items():
            if dev_info['type'] == 'Output':
                self.file.write(f"GPIO.setup({dev_info['name']}, GPIO.OUT)\n")
            elif dev_info['type'] == 'Input':
                self.file.write(f"GPIO.setup({dev_info['name']}, GPIO.IN)\n")
            else:
                print(f"Unknown device type: {dev_info['type']}")
    def write_cleanup(self):
        self.file.write("GPIO.cleanup()\n")
    
    def find_block_by_type(self, block_type):
        """Find first block of given type"""
        for block_id, top_info in Utils.top_infos.items():
            if top_info['type'] == block_type:
                return top_info
        return None
    
    def get_next_block(self, current_block_id):
        """Get the block connected to output of current block"""
        current_info = Utils.top_infos[current_block_id]
        
        # Get first out_connection
        if current_info['out_connections']:
            first_connection_id = current_info['out_connections'][0]
            
            # Find which block this connection goes to
            for block_id, info in Utils.top_infos.items():
                if first_connection_id in info['in_connections']:
                    return block_id
        return None 
    
    def resolve_value(self, value_str):
        """Convert value to actual value - handle variable or literal"""
        if self.is_variable_reference(value_str):
            print(f"Resolving variable reference: {value_str}")
            # Look up variable's current runtime value
            for var_id, var_info in Utils.variables.items():
                if var_info['name'] == value_str:
                    print(f"Found variable {value_str} with value {var_info['value']}")
                    return var_info['value']  # Or actual value storage
        return value_str  # It's a literal
    
    def is_variable_reference(self, value_str):
        """Check if value is a variable name (not a number)"""
        try:
            float(value_str)  # Can convert to number?
            print(f"{value_str} is a literal number.")
            return False      # It's a literal number
        except ValueError:
            print(f"{value_str} is a variable reference.")
            return True 
        
    def writeline(self, text):
        """Write indented line"""
        indent = self.indent_str * self.indent_level
        self.file.write(indent + text + "\n")
        
    def write_condition(self, type,  value1, operator, value2):
        """Write condition code - DRY principle"""
        text = f"{type} {value1} {operator} {value2}:"
        print(f"Writing condition: {text}")
        self.writeline(text)
    
    def get_comparison_operator(self, combo_value):
        print(f"Mapping combo value '{combo_value}' to operator")
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
        current_info = Utils.top_infos[current_block_id]
        
        # Find connection from specified output circle
        for conn_id in current_info['out_connections']:
            conn_info = Utils.paths.get(conn_id)
            if conn_info and conn_info['from_circle'] == output_circle:
                # Find which block this connection goes to
                for block_id, info in Utils.top_infos.items():
                    if conn_id in info['in_connections']:
                        return block_id
        return None
    
    def handle_if_block(self, block):
        value_1 = self.resolve_value(block['value_1'])
        value_2 = self.resolve_value(block['value_2'])
        print(f"Resolved If block values: {value_1}, {value_2}")
        operator = self.get_comparison_operator(block['combo_value'])
        print(f"Using operator: {operator}")
        out1_id = self.get_next_block_from_output(block['id'], 'out1')  # True path
        out2_id = self.get_next_block_from_output(block['id'], 'out2')  # False path
        print(f"If block outputs: out1 -> {out1_id}, out2 -> {out2_id}")
        self.write_condition(
            "if", value_1, operator, value_2
        )
        self.indent_level += 1
        self.process_block(out1_id)
        print(f"Completed If true branch, now handling else branch")
        self.indent_level -= 1
        self.writeline("else:")
        print(f"Processing else branch for If block")
        self.indent_level += 1
        self.process_block(out2_id)
        
        self.indent_level -= 1
    
    def handle_while_block(self, block):
        value_1 = self.resolve_value(block['value_1'])
        value_2 = self.resolve_value(block['value_2'])
        print(f"Resolved While block values: {value_1}, {value_2}")
        operator = self.get_comparison_operator(block['combo_value'])
        print(f"Using operator: {operator}")
        out1_id = self.get_next_block_from_output(block['id'], 'out1')  # True path
        out2_id = self.get_next_block_from_output(block['id'], 'out2')  # False path
        print(f"While block outputs: out1 -> {out1_id}, out2 -> {out2_id}")
        self.write_condition(
            "while", value_1, operator, value_2
        )
        self.indent_level += 1
        print(f"Processing While true branch for While block")
        self.process_block(out1_id)
        self.indent_level -= 1
        print(f"Processing While false branch for While block")
        self.process_block(out2_id)
        
    def handle_timer_block(self, block):
        self.writeline(f"time.sleep({block['value_1']})")
        
        next_id = self.get_next_block(block['id'])
        if next_id:
            print(f"Processing next block after Timer: {next_id}")
        self.process_block(next_id)
    
    def handle_switch_block(self, block):
        switch_value = block['switch_value']
    
    # ✅ Check if it's already a boolean
        if isinstance(switch_value, bool):
            Switch_value = switch_value
        else:
            # Only resolve if it's a string (variable reference or literal)
            Switch_value = self.resolve_value(switch_value)
        
        Var_1 = self.resolve_value(block['value_1'])
        
        print(f"Resolved Switch block value: {Switch_value} (type: {type(Switch_value).__name__})")
        
        if Switch_value is True:
            print(f"Writing GPIO HIGH for Switch block")
            self.writeline(f"GPIO.output({Var_1}, GPIO.HIGH)")
        elif Switch_value is False:
            print(f"Writing GPIO LOW for Switch block")
            self.writeline(f"GPIO.output({Var_1}, GPIO.LOW)")
        else:
            print(f"Unknown Switch value {Switch_value}, defaulting to LOW")
            self.writeline(f"GPIO.output({Var_1}, GPIO.LOW)")
        
        next_id = self.get_next_block(block['id'])
        if next_id:
            print(f"Processing next block after Switch: {next_id}")
        self.process_block(next_id)
    
    def handle_end_block(self, block):
        print(f"Handling End block {block['id']}")
        # End block - no action needed, just return
        return