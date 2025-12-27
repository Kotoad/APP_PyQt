"""
INTEGRATION_PATCHES.py

Copy-paste these code sections into your existing files.
Each section shows exactly where to add code.

NO BREAKING CHANGES - your existing code keeps working!
"""

# ============================================================================
# PATCH 1: spawn_elements_pyqt.py - BlockGraphicsItem class
# ============================================================================
# Add this to __init__ method (after super().__init__())

PATCH_1_LOCATION = "BlockGraphicsItem.__init__ after super().__init__()"

PATCH_1_CODE = '''
# === NEW: Create BlockInstance for data ===
from BlockInstance import BlockInstance

self.instance = BlockInstance(
    block_id=block_id,
    block_type=block_type,
    x=x,
    y=y
)
'''

# Then replace all property assignments with these CONVENIENCE PROPERTIES
# Add these @property methods to BlockGraphicsItem class:

PATCH_1_PROPERTIES = '''
# === CONVENIENCE PROPERTIES - Keep your existing code working ===

@property
def value_1_name(self):
    """Read from instance"""
    return self.instance.get_input('value_1_name')

@value_1_name.setter
def value_1_name(self, value):
    """Write to instance"""
    self.instance.set_input('value_1_name', value)
    self.update()  # Redraw

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
'''

# ============================================================================
# PATCH 2: code_compiler.py - process_block method
# ============================================================================

PATCH_2_LOCATION = "CodeCompiler.process_block method - REPLACE ENTIRE METHOD"

PATCH_2_CODE = '''
def process_block(self, block_id):
    """Process single block - SIMPLIFIED"""
    
    if not block_id:
        return
    
    # Get block data from your existing Utils
    block_data = Utils.top_infos[block_id]
    
    # === NEW: Wrap in BlockInstance for clean access ===
    from BlockInstance import BlockInstance
    block = BlockInstance.from_dict(block_data)
    
    print(f"Processing block {block_id} of type {block.block_type}")
    
    # === DISPATCH: Type-safe, all inputs guaranteed valid ===
    handler_name = f'handle_{block.block_type.lower()}'
    handler = getattr(self, handler_name, None)
    
    if handler:
        handler(block)
    else:
        print(f"Unknown block type: {block.block_type}")
'''

# ============================================================================
# PATCH 3: code_compiler.py - handler methods (SIMPLIFIED)
# ============================================================================

PATCH_3_LOCATION = "CodeCompiler - Update handler methods like handle_if_block"

PATCH_3_IF_HANDLER = '''
def handle_if_block(self, block):
    """Generate If condition - SIMPLIFIED"""
    
    # YOUR CUSTOM INPUTS - always available and valid
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
'''

PATCH_3_SWITCH_HANDLER = '''
def handle_switch_block(self, block):
    """Generate device control - SIMPLIFIED"""
    
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
'''

PATCH_3_TIMER_HANDLER = '''
def handle_timer_block(self, block):
    """Generate timer - MUCH SIMPLER"""
    
    duration = block.get_input('sleep_time')  # Always present, valid
    self.writeline(f"time.sleep({duration}/1000)")
    
    next_block = self.get_next_block(block.block_id)
    if next_block:
        self.process_block(next_block)
'''

# ============================================================================
# PATCH 4: Imports.py - Add new imports
# ============================================================================

PATCH_4_LOCATION = "Imports.py - Add to lazy import section"

PATCH_4_CODE = '''
def get_block_definitions():
    """Lazy import BlockDefinitions"""
    from BlockDefinitions import BlockLibrary
    return BlockLibrary

def get_block_instance():
    """Lazy import BlockInstance"""
    from BlockInstance import BlockInstance
    return BlockInstance
'''

# Then add to __all__:
PATCH_4_EXPORTS = '''
__all__ = [
    # ... existing exports ...
    'get_block_definitions',
    'get_block_instance',
]
'''

# ============================================================================
# QUICK INTEGRATION STEPS
# ============================================================================

QUICK_STEPS = """
1. CREATE NEW FILES:
   - Copy BlockDefinitions.py to your project folder
   - Copy BlockInstance.py to your project folder

2. UPDATE spawn_elements_pyqt.py:
   - In BlockGraphicsItem.__init__, add PATCH_1_CODE after super().__init__()
   - Add PATCH_1_PROPERTIES as methods to BlockGraphicsItem class
   - NO OTHER CHANGES to paint(), _draw_text(), etc.

3. UPDATE code_compiler.py:
   - Replace process_block() with PATCH_2_CODE
   - Replace handle_if_block() with PATCH_3_IF_HANDLER
   - Replace handle_switch_block() with PATCH_3_SWITCH_HANDLER
   - Replace handle_timer_block() with PATCH_3_TIMER_HANDLER
   - Keep other handlers (handle_button_block, handle_while_block, etc.)

4. TEST:
   - Load existing project → should work unchanged
   - Create new block → should work unchanged
   - Compile code → should generate same output

5. VERIFY:
   - Change block input in UI → check it saves to ProjectData
   - Compile → check generated code is correct
"""

print(QUICK_STEPS)
