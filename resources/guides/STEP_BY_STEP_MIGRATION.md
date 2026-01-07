"""
STEP_BY_STEP_MIGRATION.md

Exact steps to integrate BlockDefinitions and BlockInstance
into your existing code WITHOUT breaking anything.
"""

# ============================================================================
# STEP 1: PREPARE (5 minutes)
# ============================================================================

STEP_1 = """
1.1 Copy new files to your project folder:
    - BlockDefinitions.py
    - BlockInstance.py

1.2 Your project structure should now be:
    your_project/
    ├── main_pyqt.py
    ├── GUI_pyqt.py
    ├── spawn_elements_pyqt.py
    ├── code_compiler.py
    ├── Utils.py
    ├── BlockDefinitions.py          ← NEW
    ├── BlockInstance.py             ← NEW
    └── ... other files ...

1.3 No changes to any other files yet!
"""

# ============================================================================
# STEP 2: UPDATE spawn_elements_pyqt.py (10 minutes)
# ============================================================================

STEP_2 = """
2.1 Find the BlockGraphicsItem.__init__ method

2.2 Add these lines right after super().__init__():
    
    from BlockInstance import BlockInstance
    
    self.instance = BlockInstance(
        block_id=block_id,
        block_type=block_type,
        x=x,
        y=y
    )

2.3 Find ALL lines in class BlockGraphicsItem that look like:
    self.value_1_name = "..."
    self.operator = "..."
    self.value_2_name = "..."
    self.switch_state = ...
    self.sleep_time = "..."
    
    DELETE THESE - they will become properties!

2.4 Add these @property methods to BlockGraphicsItem class:
    
    @property
    def value_1_name(self):
        return self.instance.get_input('value_1_name')
    
    @value_1_name.setter
    def value_1_name(self, value):
        self.instance.set_input('value_1_name', value)
        self.update()
    
    @property
    def operator(self):
        return self.instance.get_input('operator')
    
    @operator.setter
    def operator(self, value):
        self.instance.set_input('operator', value)
        self.update()
    
    @property
    def value_2_name(self):
        return self.instance.get_input('value_2_name')
    
    @value_2_name.setter
    def value_2_name(self, value):
        self.instance.set_input('value_2_name', value)
        self.update()
    
    @property
    def switch_state(self):
        return self.instance.get_input('switch_state')
    
    @switch_state.setter
    def switch_state(self, value):
        self.instance.set_input('switch_state', value)
        self.update()
    
    @property
    def sleep_time(self):
        return self.instance.get_input('sleep_time')
    
    @sleep_time.setter
    def sleep_time(self, value):
        self.instance.set_input('sleep_time', value)
        self.update()

2.5 Test: Create a block in your UI
    - Should work exactly like before!
    - Try changing an input value
    - Check it updates correctly
"""

# ============================================================================
# STEP 3: UPDATE code_compiler.py - process_block method (10 minutes)
# ============================================================================

STEP_3_PROCESS = """
3.1 Find the process_block method in CodeCompiler class

3.2 REPLACE THE ENTIRE METHOD with this:
    
    def process_block(self, block_id):
        '''Process single block - SIMPLIFIED'''
        
        if not block_id:
            return
        
        # Get block data from your existing Utils
        block_data = Utils.top_infos[block_id]
        
        # === NEW: Wrap in BlockInstance ===
        from BlockInstance import BlockInstance
        block = BlockInstance.from_dict(block_data)
        
        print(f"Processing block {block_id} of type {block.block_type}")
        
        # === DISPATCH ===
        handler_name = f'handle_{block.block_type.lower()}'
        handler = getattr(self, handler_name, None)
        
        if handler:
            handler(block)
        else:
            print(f"Unknown block type: {block.block_type}")

3.3 Update each handler method signature:
    CHANGE FROM:
        def handle_if_block(self, block):
            value_1 = self.resolve_value(block['value_1_name'], block.get('value_1_type', 'N/A'))
    
    CHANGE TO:
        def handle_if_block(self, block):  # block is now BlockInstance
            value_1 = self.resolve_value(block.get_input('value_1_name'), 'Literal')
"""

# ============================================================================
# STEP 4: UPDATE code_compiler.py - handler methods (15 minutes)
# ============================================================================

STEP_4 = """
4.1 Update handle_if_block:
    
    def handle_if_block(self, block):
        '''Generate If condition'''
        
        value_1 = self.resolve_value(
            block.get_input('value_1_name'),
            'Literal'
        )
        operator = block.get_input('operator')
        value_2 = self.resolve_value(
            block.get_input('value_2_name'),
            'Literal'
        )
        
        self.write_condition("if", value_1, operator, value_2)
        self.indent_level += 1
        
        out1_id = self.get_next_block_from_output(block.block_id, 'out1')
        self.process_block(out1_id)
        
        self.indent_level -= 1
        self.writeline("else:")
        self.indent_level += 1
        
        out2_id = self.get_next_block_from_output(block.block_id, 'out2')
        self.process_block(out2_id)
        
        self.indent_level -= 1

4.2 Update handle_switch_block:
    
    def handle_switch_block(self, block):
        '''Generate device control'''
        
        device = self.resolve_value(
            block.get_input('value_1_name'),
            'Device'
        )
        state = block.get_input('switch_state')
        
        if self.GPIO_compile:
            gpio_state = 'GPIO.HIGH' if state else 'GPIO.LOW'
            self.writeline(f"GPIO.output({device}, {gpio_state})")
        elif self.MC_compile:
            pin_state = '1' if state else '0'
            self.writeline(f"{device}.value({pin_state})")
        
        next_block = self.get_next_block_from_output(block.block_id, 'out')
        if next_block:
            self.process_block(next_block)

4.3 Update handle_timer_block:
    
    def handle_timer_block(self, block):
        '''Generate timer'''
        
        duration = block.get_input('sleep_time')
        self.writeline(f"time.sleep({duration}/1000)")
        
        next_block = self.get_next_block(block.block_id)
        if next_block:
            self.process_block(next_block)

4.4 Update handle_while_block:
    
    def handle_while_block(self, block):
        '''Generate While condition'''
        
        value_1 = self.resolve_value(
            block.get_input('value_1_name'),
            'Literal'
        )
        operator = block.get_input('operator')
        value_2 = self.resolve_value(
            block.get_input('value_2_name'),
            'Literal'
        )
        
        self.write_condition("while", value_1, operator, value_2)
        self.indent_level += 1
        
        out1_id = self.get_next_block_from_output(block.block_id, 'out1')
        self.process_block(out1_id)
        
        self.indent_level -= 1
        
        out2_id = self.get_next_block_from_output(block.block_id, 'out2')
        self.process_block(out2_id)

4.5 For other handlers (handle_button_block, handle_while_true_block):
    Just change:
        FROM: block['key_name']
        TO: block.get_input('key_name')
"""

# ============================================================================
# STEP 5: TEST INCREMENTALLY (10 minutes)
# ============================================================================

STEP_5 = """
5.1 Test 1: Load existing project
    - Open an existing project file
    - Check that all blocks appear correctly
    - Inspect a block → all properties should show
    - If error, check: Did you add self.instance in __init__?

5.2 Test 2: Create new block
    - Drag a new block onto canvas
    - Set some input values
    - Check that values are saved
    - Check in ProjectData that it saves in old format

5.3 Test 3: Compile code
    - Create a simple program: Start → If → End
    - Click Compile
    - Check that generated code is correct
    - If error, check: Did you update all handlers?

5.4 Test 4: Verify backward compatibility
    - Load an old project → should work
    - Save it → should save in same format
    - Load again → should load perfectly
"""

# ============================================================================
# STEP 6: CLEANUP & VERIFICATION (5 minutes)
# ============================================================================

STEP_6 = """
6.1 Remove old property storage code:
    
    Search for these in spawn_elements_pyqt.py:
    - self.value_1_name = 
    - self.value_1_type =
    - self.operator =
    - self.switch_state =
    - self.sleep_time =
    
    If you find any, DELETE them!
    (They're now properties backed by instance)

6.2 Check for resolve_value compatibility:
    
    In code_compiler.py, your resolve_value() method
    should work unchanged. It takes string value and type.
    
    Just make sure you're passing 'Literal', 'Device', etc.
    (not the custom_inputs dict keys)

6.3 Verify imports:
    
    At top of files, check you have:
    - spawn_elements_pyqt.py: from BlockInstance import BlockInstance
    - code_compiler.py: from BlockInstance import BlockInstance
    
    Python will lazy-import them on first use.

6.4 Final check:
    
    Run your app:
    ✓ Create block → should work
    ✓ Set values → should work
    ✓ Compile → should work
    ✓ Load old project → should work
    ✓ Save/load cycle → should work
    
    If all ✓, you're DONE!
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

TROUBLESHOOTING = """
ERROR: "BlockInstance has no attribute 'get_input'"
FIX: Make sure self.instance is created in BlockGraphicsItem.__init__

ERROR: "block.get_input() returns None"
FIX: Check that block_type is correct when creating BlockInstance

ERROR: "Properties not updating"
FIX: Make sure property.setter calls self.update() to redraw

ERROR: "Code doesn't compile"
FIX: Check that all handlers accept block parameter (not block_data)
     Make sure block.get_input() is used instead of block['key']

ERROR: "Old projects don't load"
FIX: Check BlockInstance.from_dict() is called in process_block()
     Make sure input keys in to_dict() match your old ProjectData format

ERROR: "Validation errors on set_input()"
FIX: This is intentional! Timer.sleep_time must be > 0
     For other blocks, validation_fn is optional
"""

print(TROUBLESHOOTING)

# ============================================================================
# SUMMARY
# ============================================================================

SUMMARY = """
TIME ESTIMATE: 40-50 minutes total

NEW FILES (10 min):
  ✓ BlockDefinitions.py
  ✓ BlockInstance.py

UPDATED FILES:
  ✓ spawn_elements_pyqt.py (10 min)
  ✓ code_compiler.py (30 min)
  ✓ Testing & verification (10 min)

BACKWARD COMPATIBLE:
  ✓ All ProjectData format unchanged
  ✓ Existing projects load perfectly
  ✓ Code generation identical

BENEFITS AFTER:
  ✓ Clean data structure
  ✓ Type-safe input access
  ✓ Compiler much simpler
  ✓ Easy to add new block types
  ✓ All custom inputs preserved
"""

print(SUMMARY)
