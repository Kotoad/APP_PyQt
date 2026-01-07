"""
EXAMPLE_IMPLEMENTATION.py

Complete working example showing how to use BlockDefinitions and BlockInstance
Copy these patterns to update your existing code
"""

from resources.guides.BlockDefinitions import BlockLibrary, InputType
from resources.guides.BlockInstance import BlockInstance

# ============================================================================
# EXAMPLE 1: Creating a new block programmatically
# ============================================================================

def example_create_block():
    """Create block from scratch"""
    
    # Create instance with default values
    block = BlockInstance(
        block_id='if_block_1',
        block_type='If',
        x=100,
        y=200
    )
    
    # Inputs are auto-initialized from BlockDefinitions
    print(f"value_1_name: {block.get_input('value_1_name')}")  # 'var1'
    print(f"operator: {block.get_input('operator')}")          # '=='
    print(f"value_2_name: {block.get_input('value_2_name')}")  # 'var2'
    
    # Update inputs
    block.set_input('value_1_name', 'motor_speed')
    block.set_input('operator', '>')
    block.set_input('value_2_name', '100')
    
    return block


# ============================================================================
# EXAMPLE 2: Saving block to ProjectData format
# ============================================================================

def example_save_block(block: BlockInstance):
    """Save block to your ProjectData dict"""
    
    data = block.to_dict()
    
    # This produces your current format:
    # {
    #     'block_id': 'if_block_1',
    #     'type': 'If',
    #     'x': 100,
    #     'y': 200,
    #     'value_1_name': 'motor_speed',
    #     'operator': '>',
    #     'value_2_name': '100',
    #     'in_connections': [],
    #     'out_connections': []
    # }
    
    # Save to Utils
    Utils.top_infos[block.block_id] = data
    return data


# ============================================================================
# EXAMPLE 3: Loading block from ProjectData
# ============================================================================

def example_load_block(block_id):
    """Load block from your existing ProjectData"""
    
    # Get from your current data structure
    block_data = Utils.top_infos[block_id]
    
    # Convert to BlockInstance
    block = BlockInstance.from_dict(block_data)
    
    # Now you have clean access:
    print(f"Block type: {block.block_type}")
    print(f"Operator: {block.get_input('operator')}")
    
    return block


# ============================================================================
# EXAMPLE 4: In BlockGraphicsItem - property access
# ============================================================================

class BlockGraphicsItemExample:
    """Your existing BlockGraphicsItem class"""
    
    def __init__(self, block_id, block_type, x, y, parent_canvas):
        # === Create instance for data storage ===
        self.instance = BlockInstance(
            block_id=block_id,
            block_type=block_type,
            x=x,
            y=y
        )
        
        # Keep all your other UI code...
        self.block_id = block_id
        self.block_type = block_type
        self.canvas = parent_canvas
    
    # === CONVENIENCE PROPERTIES - Your existing code still works ===
    
    @property
    def value_1_name(self):
        """Your code reads from instance"""
        return self.instance.get_input('value_1_name')
    
    @value_1_name.setter
    def value_1_name(self, value):
        """Your code writes to instance"""
        self.instance.set_input('value_1_name', value)
        self.update()  # Redraw the block
    
    @property
    def operator(self):
        return self.instance.get_input('operator')
    
    @operator.setter
    def operator(self, value):
        self.instance.set_input('operator', value)
        self.update()
    
    # ... same pattern for other properties ...
    
    def save_to_file(self):
        """Save this block to ProjectData"""
        data = self.instance.to_dict()
        Utils.top_infos[self.block_id] = data
    
    def paint(self, painter, option, widget):
        """Your existing paint() code doesn't change!"""
        # All your drawing code stays the same
        # The data now comes from self.instance instead of individual properties
        pass


# ============================================================================
# EXAMPLE 5: In code_compiler.py - processing blocks
# ============================================================================

class CodeCompilerExample:
    """Updated CodeCompiler"""
    
    def process_block(self, block_id):
        """Process single block - SIMPLIFIED"""
        
        if not block_id:
            return
        
        # Get from your existing structure
        block_data = Utils.top_infos[block_id]
        
        # === NEW: Wrap in BlockInstance ===
        block = BlockInstance.from_dict(block_data)
        
        print(f"Processing block {block_id} of type {block.block_type}")
        
        # === DISPATCH: All inputs guaranteed valid ===
        handler_name = f'handle_{block.block_type.lower()}'
        handler = getattr(self, handler_name, None)
        
        if handler:
            handler(block)  # Pass the clean BlockInstance
        else:
            print(f"Unknown block type: {block.block_type}")
    
    def handle_if_block(self, block: BlockInstance):
        """Handler now receives clean BlockInstance"""
        
        # YOUR CUSTOM INPUTS - always available
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
    
    def handle_switch_block(self, block: BlockInstance):
        """Another handler example"""
        
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
    
    def handle_timer_block(self, block: BlockInstance):
        """Timer handler - super simple now"""
        
        duration = block.get_input('sleep_time')
        self.writeline(f"time.sleep({duration}/1000)")
        
        next_block = self.get_next_block(block.block_id)
        if next_block:
            self.process_block(next_block)


# ============================================================================
# EXAMPLE 6: Validation
# ============================================================================

def example_validation():
    """Show validation in action"""
    
    block = BlockInstance('timer_1', 'Timer')
    
    try:
        # This will fail - negative sleep time
        block.set_input('sleep_time', '-100')
        print("Set sleep_time to -100")
    except Exception as e:
        print(f"Validation failed: {e}")
    
    # This works - positive sleep time
    block.set_input('sleep_time', '1000')
    print(f"Set sleep_time to {block.get_input('sleep_time')}")


# ============================================================================
# EXAMPLE 7: Querying block definitions
# ============================================================================

def example_query_definitions():
    """Query what inputs a block type needs"""
    
    # Get definition for If block
    definition = BlockLibrary.get_definition('If')
    
    print(f"Block type: {definition.block_type}")
    print(f"Label: {definition.label}")
    print(f"Description: {definition.description}")
    
    # Get all input names
    input_names = BlockLibrary.get_input_names('If')
    print(f"Inputs: {input_names}")  # ['value_1_name', 'operator', 'value_2_name']
    
    # Get specific input definition
    operator_def = BlockLibrary.get_input_def('If', 'operator')
    print(f"Operator input type: {operator_def.input_type}")
    print(f"Default: {operator_def.default_value}")
    
    # Check outputs
    definition = BlockLibrary.get_definition('If')
    print(f"Outputs: {[out.name for out in definition.outputs]}")  # ['out1', 'out2']


# ============================================================================
# MIGRATION CHECKLIST
# ============================================================================

MIGRATION_CHECKLIST = """
✅ STEP 1: Add new files to project
   - Copy BlockDefinitions.py
   - Copy BlockInstance.py

✅ STEP 2: Update BlockGraphicsItem (spawn_elements_pyqt.py)
   - Add: from BlockInstance import BlockInstance
   - In __init__: Create self.instance = BlockInstance(...)
   - Add @property methods that delegate to self.instance
   - Everything else stays the same!

✅ STEP 3: Update CodeCompiler (code_compiler.py)
   - Replace process_block() to use BlockInstance.from_dict()
   - Update handlers to accept BlockInstance parameter
   - Use block.get_input() instead of block['key']

✅ STEP 4: Test incrementally
   - Load existing project → verify blocks load
   - Create new block → verify it saves
   - Change input in UI → verify it compiles correctly
   - Compile code → verify output is correct

✅ STEP 5: Verify backward compatibility
   - All ProjectData format is unchanged
   - Existing saved projects load without modification
   - Code generation produces identical output
"""

print(MIGRATION_CHECKLIST)
