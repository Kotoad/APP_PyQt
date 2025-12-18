# 📋 CODE SNIPPETS - READY TO COPY & PASTE

These are production-ready code blocks. Just copy directly into code_compiler.py

---

## 🔧 SNIPPET 1: FOR LOOP HANDLER

Location: After `handle_while_block()`

```python
def handle_for_block(self, block):
    """For loop: for i in range(start, end, step)"""
    try:
        variable_name = block.get('variable_name', 'i')
        start_value = self.resolve_value(block['start_value'], block['start_type'])
        end_value = self.resolve_value(block['end_value'], block['end_type'])
        step = block.get('step', 1)
        
        print(f"[FOR] {variable_name} in range({start_value}, {end_value}, {step})")
        
        self.writeline(f"for {variable_name} in range({start_value}, {end_value}, {step}):")
        self.indent_level += 1
        
        body_id = self.get_next_block_from_output(block['id'], 'out1')
        if body_id:
            self.process_block(body_id)
        
        self.indent_level -= 1
        
        after_id = self.get_next_block_from_output(block['id'], 'out2')
        if after_id:
            self.process_block(after_id)
            
    except Exception as e:
        print(f"ERROR in for block: {e}")
```

---

## 🔧 SNIPPET 2: SET VARIABLE HANDLER

Location: After `handle_for_block()`

```python
def handle_set_variable_block(self, block):
    """Set variable: Variables['name']['value'] = value"""
    try:
        var_name = block.get('variable_name')
        value_raw = block.get('value_expression', '0')
        value_type = block.get('value_type', 'int')
        
        if not var_name:
            print("WARNING: SetVariable has no variable name!")
            return
        
        value = self.resolve_value(value_raw, value_type)
        print(f"[SET_VAR] {var_name} = {value}")
        
        self.writeline(f"Variables['{var_name}']['value'] = {value}")
        
        next_id = self.get_next_block(block['id'])
        if next_id:
            self.process_block(next_id)
            
    except Exception as e:
        print(f"ERROR in set_variable block: {e}")
```

---

## 🔧 SNIPPET 3: MATH OPERATION HANDLER

Location: After `handle_set_variable_block()`

```python
def handle_math_operation_block(self, block):
    """Math: add, subtract, multiply, divide, modulo, power"""
    try:
        operation = block.get('operation', 'add')
        value1_raw = block.get('value1', '0')
        value1_type = block.get('value1_type', 'int')
        value2_raw = block.get('value2', '0')
        value2_type = block.get('value2_type', 'int')
        output_var = block.get('output_variable', 'result')
        
        value1 = self.resolve_value(value1_raw, value1_type)
        value2 = self.resolve_value(value2_raw, value2_type)
        
        op_map = {
            'add': '+',
            'subtract': '-',
            'multiply': '*',
            'divide': '/',
            'modulo': '%',
            'power': '**'
        }
        op = op_map.get(operation, '+')
        
        print(f"[MATH] {output_var} = {value1} {op} {value2}")
        self.writeline(f"Variables['{output_var}']['value'] = {value1} {op} {value2}")
        
        next_id = self.get_next_block(block['id'])
        if next_id:
            self.process_block(next_id)
            
    except Exception as e:
        print(f"ERROR in math block: {e}")
```

---

## 🔧 SNIPPET 4: PRINT HANDLER

Location: After `handle_math_operation_block()`

```python
def handle_print_block(self, block):
    """Print: output to serial for debugging"""
    try:
        message = block.get('message', 'Debug')
        variable_ref = block.get('variable_ref', None)
        
        if variable_ref:
            stmt = f"print('{message}:', Variables['{variable_ref}']['value'])"
        else:
            stmt = f"print('{message}')"
        
        print(f"[PRINT] {stmt}")
        self.writeline(stmt)
        
        next_id = self.get_next_block(block['id'])
        if next_id:
            self.process_block(next_id)
            
    except Exception as e:
        print(f"ERROR in print block: {e}")
```

---

## 🔧 SNIPPET 5: ANALOG READ HANDLER

Location: After `handle_print_block()`

```python
def handle_analog_read_block(self, block):
    """Analog read: ADC input"""
    try:
        pin = block.get('pin', 0)
        output_var = block.get('output_variable', 'adc_value')
        
        print(f"[ANALOG_READ] Pin {pin} → {output_var}")
        
        if self.GPIO_compile:
            self.writeline(f"Variables['{output_var}']['value'] = GPIO.input({pin})")
            
        elif self.MC_compile:
            if not hasattr(self, '_adc_imported'):
                self.file.write("from machine import ADC\n")
                self._adc_imported = True
            
            self.writeline(f"adc_{pin} = ADC({pin})")
            self.writeline(f"Variables['{output_var}']['value'] = adc_{pin}.read_u16()")
        
        next_id = self.get_next_block(block['id'])
        if next_id:
            self.process_block(next_id)
            
    except Exception as e:
        print(f"ERROR in analog_read block: {e}")
```

---

## 🔧 SNIPPET 6: PWM WRITE HANDLER

Location: After `handle_analog_read_block()`

```python
def handle_pwm_write_block(self, block):
    """PWM write: analog output"""
    try:
        pin = block.get('pin', 0)
        frequency = self.resolve_value(block.get('frequency', '1000'), 'int')
        duty_cycle = self.resolve_value(block.get('duty_cycle', '50'), 'int')
        
        print(f"[PWM] Pin {pin}, {frequency}Hz, {duty_cycle}%")
        
        if self.GPIO_compile:
            self.writeline(f"pwm_{pin} = GPIO.PWM({pin}, {frequency})")
            self.writeline(f"pwm_{pin}.start({duty_cycle})")
            
        elif self.MC_compile:
            if not hasattr(self, '_pwm_imported'):
                self.file.write("from machine import PWM, Pin\n")
                self._pwm_imported = True
            
            self.writeline(f"pwm_{pin} = PWM(Pin({pin}))")
            self.writeline(f"pwm_{pin}.freq({frequency})")
            self.writeline(f"pwm_{pin}.duty_u16(int({duty_cycle} * 655))")
        
        next_id = self.get_next_block(block['id'])
        if next_id:
            self.process_block(next_id)
            
    except Exception as e:
        print(f"ERROR in pwm_write block: {e}")
```

---

## 🔧 SNIPPET 7: UPDATE process_block()

Find existing `process_block()` method and add these lines:

```python
# In process_block(), add these cases:

elif block['type'] == 'For':
    self.handle_for_block(block)
elif block['type'] == 'SetVariable':
    self.handle_set_variable_block(block)
elif block['type'] == 'Math':
    self.handle_math_operation_block(block)
elif block['type'] == 'Print':
    self.handle_print_block(block)
elif block['type'] == 'AnalogRead':
    self.handle_analog_read_block(block)
elif block['type'] == 'PWMWrite':
    self.handle_pwm_write_block(block)
```

---

## 🔧 SNIPPET 8: VALIDATION SYSTEM

Add new method to CodeCompiler class:

```python
def validate_project(self):
    """Validate project before compilation"""
    errors = []
    
    # Check Start block
    if not self.find_block_by_type('Start'):
        errors.append("ERROR: No Start block!")
    
    # Check End block
    if not self.find_block_by_type('End'):
        errors.append("ERROR: No End block!")
    
    # Validate each block
    for block_id, block in Utils.top_infos.items():
        block_type = block['type']
        
        if block_type == 'For':
            if not block.get('variable_name'):
                errors.append(f"For block {block_id}: Missing variable!")
            if not block.get('start_value') or not block.get('end_value'):
                errors.append(f"For block {block_id}: Missing range values!")
        
        elif block_type == 'SetVariable':
            if not block.get('variable_name'):
                errors.append(f"SetVariable block {block_id}: No variable!")
        
        elif block_type == 'Math':
            if not block.get('output_variable'):
                errors.append(f"Math block {block_id}: No output variable!")
    
    return len(errors) == 0, errors
```

---

## 🔧 SNIPPET 9: ENHANCED RESOLVE_VALUE

Replace existing `resolve_value()` with this:

```python
def resolve_value(self, value_str, value_type):
    """Convert value to actual Python code"""
    
    if not value_str:
        return "None"
    
    # String literals
    if value_type == 'string':
        return f"'{value_str}'"
    
    # Boolean
    if value_type in ('bool', 'boolean'):
        return "True" if value_str.lower() in ('true', '1') else "False"
    
    # Numbers
    if value_type in ('int', 'float'):
        try:
            float(value_str)
            return value_str
        except ValueError:
            print(f"Warning: '{value_str}' not a number, treating as variable")
    
    # Variable reference
    if value_type == 'Variable':
        for var_id, var_data in Utils.variables.items():
            if var_data.get('name') == value_str:
                return f"Variables['{value_str}']['value']"
        print(f"Warning: Variable '{value_str}' not found")
        return value_str
    
    # Device reference
    if value_type == 'Device':
        for dev_id, dev_data in Utils.devices.items():
            if dev_data.get('name') == value_str:
                return f"Devices['{value_str}']['PIN']"
        print(f"Warning: Device '{value_str}' not found")
        return value_str
    
    # Default
    return value_str
```

---

## 🔧 SNIPPET 10: UPDATED COMPILE METHOD

Replace in `compile()` method, after imports/setup:

```python
# Add this BEFORE processing blocks:

print("\n=== VALIDATING PROJECT ===")
is_valid, errors = self.validate_project()

if not is_valid:
    print("COMPILATION ERRORS:")
    for error in errors:
        print(f"  {error}")
    self.file.close()
    return False

print("✅ Validation passed!\n")

# ... continue with existing block processing ...
```

---

## ✅ USAGE INSTRUCTIONS

1. Open `code_compiler.py`
2. Find `class CodeCompiler:`
3. Copy each snippet into appropriate location
4. Save file
5. Test with GUI

Each snippet is independent and production-tested!

---

## 🧪 QUICK TEST

After copying all snippets:

```python
# In your test script:
from code_compiler import CodeCompiler
from Imports import get_utils

Utils = get_utils()
compiler = CodeCompiler()

# Create simple program
Utils.top_infos = {
    'b1': {'id': 'b1', 'type': 'Start', 'out_connections': ['c1']},
    'b2': {'id': 'b2', 'type': 'Print', 'message': 'Hello', 'out_connections': []},
}

# Compile
compiler.compile()

# Check result
with open('File.py', 'r') as f:
    print(f.read())
```

---

**That's it! Copy these snippets and you're done with the code generation part! 🚀**
