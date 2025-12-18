# IMPLEMENTATION QUICK-START GUIDE

## 🎯 THIS WEEK: ADD 6 BLOCK HANDLERS

All following same pattern. Takes ~1 hour per handler.

---

## STEP 1: UNDERSTAND THE PATTERN

Open **code_compiler.py** and find `handle_while_block()`:

```python
def handle_while_block(self, block):
    # Get parameters
    value_1 = self.resolve_value(block['value_1_name'], block['value_1_type'])
    value_2 = self.resolve_value(block['value_2_name'], block['value_2_type'])
    operator = self.get_comparison_operator(block['operator'])
    
    # Get output connections
    out1_id = self.get_next_block_from_output(block['id'], 'out1')
    out2_id = self.get_next_block_from_output(block['id'], 'out2')
    
    # Write code
    self.write_condition("while", value_1, operator, value_2)
    self.indent_level += 1
    self.process_block(out1_id)
    self.indent_level -= 1
    
    self.process_block(out2_id)
```

**Pattern:** Get → Resolve → Write → Continue

---

## HANDLER 1: FOR LOOP (30 min)

Add after `handle_while_block()`:

```python
def handle_for_block(self, block):
    """For loop: for i in range(start, end, step)"""
    try:
        variable_name = block.get('variable_name', 'i')
        start_value = self.resolve_value(block['start_value'], block['start_type'])
        end_value = self.resolve_value(block['end_value'], block['end_type'])
        step = block.get('step', 1)
        
        print(f"[FOR] {variable_name} in range({start_value}, {end_value}, {step})")
        
        # Write for loop
        self.writeline(f"for {variable_name} in range({start_value}, {end_value}, {step}):")
        
        # Process loop body
        self.indent_level += 1
        body_id = self.get_next_block_from_output(block['id'], 'out1')
        if body_id:
            self.process_block(body_id)
        self.indent_level -= 1
        
        # Continue after loop
        after_id = self.get_next_block_from_output(block['id'], 'out2')
        if after_id:
            self.process_block(after_id)
            
    except Exception as e:
        print(f"ERROR in for block: {e}")
```

**Test:**
- Create GUI program: Start → For(0,5,1) → Print → End
- Compile
- Check File.py has: `for i in range(0, 5, 1):`

---

## HANDLER 2: SET VARIABLE (20 min)

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

## HANDLER 3: MATH OPERATION (30 min)

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
        
        # Map operation names to operators
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

## HANDLER 4: PRINT/DEBUG (15 min)

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

## HANDLER 5: ANALOG READ (30 min)

```python
def handle_analog_read_block(self, block):
    """Analog read: ADC input"""
    try:
        pin = block.get('pin', 0)
        output_var = block.get('output_variable', 'adc_value')
        
        print(f"[ANALOG_READ] Pin {pin} → {output_var}")
        
        if self.GPIO_compile:
            # Raspberry Pi - read digital value
            self.writeline(f"Variables['{output_var}']['value'] = GPIO.input({pin})")
            
        elif self.MC_compile:
            # Pico W - use built-in ADC
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

## HANDLER 6: PWM WRITE (30 min)

```python
def handle_pwm_write_block(self, block):
    """PWM write: analog output"""
    try:
        pin = block.get('pin', 0)
        frequency = self.resolve_value(block.get('frequency', '1000'), 'int')
        duty_cycle = self.resolve_value(block.get('duty_cycle', '50'), 'int')
        
        print(f"[PWM] Pin {pin}, {frequency}Hz, {duty_cycle}%")
        
        if self.GPIO_compile:
            # Raspberry Pi
            self.writeline(f"pwm_{pin} = GPIO.PWM({pin}, {frequency})")
            self.writeline(f"pwm_{pin}.start({duty_cycle})")
            
        elif self.MC_compile:
            # Pico W
            if not hasattr(self, '_pwm_imported'):
                self.file.write("from machine import PWM, Pin\n")
                self._pwm_imported = True
            
            self.writeline(f"pwm_{pin} = PWM(Pin({pin}))")
            self.writeline(f"pwm_{pin}.freq({frequency})")
            # 0-100% → 0-65535
            self.writeline(f"pwm_{pin}.duty_u16(int({duty_cycle} * 655))")
        
        next_id = self.get_next_block(block['id'])
        if next_id:
            self.process_block(next_id)
            
    except Exception as e:
        print(f"ERROR in pwm_write block: {e}")
```

---

## UPDATE process_block() METHOD

Find the existing `process_block()` method and add new handlers:

```python
def process_block(self, block_id):
    """Process single block - dispatch to handler"""
    if not block_id:
        return
    
    block = Utils.top_infos.get(block_id)
    if not block:
        print(f"Block {block_id} not found!")
        return
    
    block_type = block['type']
    print(f"[PROCESS] {block_id}: {block_type}")
    
    # ADD THESE LINES:
    if block_type == 'For':
        self.handle_for_block(block)
    elif block_type == 'SetVariable':
        self.handle_set_variable_block(block)
    elif block_type == 'Math':
        self.handle_math_operation_block(block)
    elif block_type == 'Print':
        self.handle_print_block(block)
    elif block_type == 'AnalogRead':
        self.handle_analog_read_block(block)
    elif block_type == 'PWMWrite':
        self.handle_pwm_write_block(block)
    # ... existing handlers below ...
    elif block_type == 'If':
        self.handle_if_block(block)
    # ... etc
```

---

## 🧪 TEST EACH ONE

### Test For Loop:
Program: `Start → For(0,5,1) → Print("i=") → End`
Expected in File.py:
```python
for i in range(0, 5, 1):
    print('i=')
```

### Test Math:
Program: `Start → SetVar(a,5) → Math(a*2→result) → Print(result) → End`
Expected:
```python
Variables['a']['value'] = 5
Variables['result']['value'] = Variables['a']['value'] * 2
print('result:', Variables['result']['value'])
```

### Test PWM:
Program: `Start → PWMWrite(pin=0, freq=1000, duty=75) → End`
Expected:
```python
pwm_0 = PWM(Pin(0))
pwm_0.freq(1000)
pwm_0.duty_u16(int(75 * 655))
```

---

## WEEK 2: ADD VALIDATION

Create new method in CodeCompiler:

```python
def validate_project(self):
    """Check project before compiling"""
    errors = []
    
    # Check Start block exists
    if not self.find_block_by_type('Start'):
        errors.append("No Start block!")
    
    # Check End block exists
    if not self.find_block_by_type('End'):
        errors.append("No End block!")
    
    # Check each block has required fields
    for block_id, block in Utils.top_infos.items():
        block_type = block['type']
        
        if block_type == 'For':
            if not block.get('variable_name'):
                errors.append(f"For block {block_id}: No variable!")
        
        elif block_type == 'Math':
            if not block.get('output_variable'):
                errors.append(f"Math block {block_id}: No output var!")
    
    return len(errors) == 0, errors
```

Update compile():
```python
def compile(self):
    # ... existing code ...
    
    # ADD THIS:
    is_valid, errors = self.validate_project()
    if not is_valid:
        print("ERRORS:")
        for e in errors:
            print(f"  - {e}")
        return False
    
    # ... rest of compile ...
```

---

## ✅ CHECKLIST FOR SUCCESS

- [ ] Added handle_for_block() ← 30 min
- [ ] Added handle_set_variable_block() ← 20 min
- [ ] Added handle_math_operation_block() ← 30 min
- [ ] Added handle_print_block() ← 15 min
- [ ] Added handle_analog_read_block() ← 30 min
- [ ] Added handle_pwm_write_block() ← 30 min
- [ ] Updated process_block() dispatcher ← 10 min
- [ ] Added validate_project() ← 30 min
- [ ] Tested with 3-block program ← 30 min
- [ ] Tested on Pico W hardware ← 1 hour

**TOTAL: ~4 hours actual work = MVP READY ✅**

---

## 💡 IF YOU GET STUCK

1. Check existing handler (If, While, Switch)
2. Follow same pattern
3. Copy the provided code_snippets_ready_to_use.py
4. Test immediately after adding each handler
5. Print debug messages: `print(f"[DEBUG] {variable_name} = {value}")`

---

## 🚀 YOU'VE GOT THIS!

Each function follows the same pattern. ~30-60 min per function.
By end of week 1, you'll have a working visual code generator!

Let's go! 💪
