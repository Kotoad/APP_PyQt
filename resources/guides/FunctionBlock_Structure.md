# Function Block Architecture Guide

## Overview
Your system has visual function blocks that need to:
1. **Accept inputs** (parameters, conditions, values)
2. **Store configuration** (what the block does)
3. **Produce outputs** (results, connections to next blocks)
4. **Communicate** between UI and processing layers

---

## Current Issues in Your Code

### Problem 1: Inconsistent Input/Output Naming
- `value_1_name` / `value_2_name` (confusing naming)
- Some blocks use `switch_state`, others use `sleep_time`
- No clear distinction between **input types** and **input values**

### Problem 2: Mixed Responsibility
- Block graphics (`BlockGraphicsItem`) handles drawing AND data storage
- Event handlers scattered across multiple classes
- Compiler (`CodeCompiler`) has to hunt through loose data structures

### Problem 3: No Clear Contract
- Blocks don't define what inputs they need
- No validation of input types
- No way to know required vs optional inputs

---

## Recommended Architecture

### Tier 1: Block Configuration (Data Layer)

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union

class InputType(Enum):
    """Standard input types for blocks"""
    DEVICE = "device"
    VARIABLE = "variable"
    LITERAL = "literal"
    CONDITION = "condition"
    CUSTOM = "custom"

class OutputType(Enum):
    """Output connection types"""
    FLOW = "flow"           # Normal execution flow
    TRUE_PATH = "true"      # Conditional true branch
    FALSE_PATH = "false"    # Conditional false branch

@dataclass
class BlockInput:
    """Defines a single input for a block"""
    name: str                       # "device", "value_1", "condition"
    input_type: InputType           # What kind of input
    value: Union[str, int, float]   # Current value
    default: Union[str, int, float] # Fallback value
    description: str = ""           # UI tooltip
    required: bool = True           # Must be filled?
    validation_rule: Optional[callable] = None  # Custom validator

@dataclass
class BlockOutput:
    """Defines a single output connection"""
    name: str
    output_type: OutputType
    display_label: str = "Output"

@dataclass
class BlockDefinition:
    """Complete definition of what a block is and needs"""
    block_type: str
    label: str
    description: str
    width: int = 100
    height: int = 54
    color: str = "#87CEEB"
    
    # Inputs this block requires/accepts
    inputs: List[BlockInput] = None
    
    # Outputs this block can produce
    outputs: List[BlockOutput] = None
    
    def __post_init__(self):
        if self.inputs is None:
            self.inputs = []
        if self.outputs is None:
            self.outputs = []
```

### Tier 2: Block Instance (Instance Data)

```python
@dataclass
class BlockInstance:
    """Runtime instance of a block in the canvas"""
    block_id: str           # Unique identifier
    definition: BlockDefinition  # What kind of block
    x: float                # Position
    y: float
    
    # Input values - keyed by input.name
    input_values: dict      # {"device": "motor_1", "condition": "=="}
    
    # Connections - list of connection IDs
    input_connections: List[str] = None    # Incoming paths
    output_connections: List[str] = None   # Outgoing paths
    
    def __post_init__(self):
        if self.input_connections is None:
            self.input_connections = []
        if self.output_connections is None:
            self.output_connections = []
        
        # Initialize input_values from defaults
        if not self.input_values:
            self.input_values = {}
            for inp in self.definition.inputs:
                self.input_values[inp.name] = inp.default
    
    def get_input(self, input_name: str):
        """Get current value for an input"""
        return self.input_values.get(input_name)
    
    def set_input(self, input_name: str, value):
        """Set input value with validation"""
        inp_def = next((i for i in self.definition.inputs if i.name == input_name), None)
        if not inp_def:
            raise ValueError(f"Input '{input_name}' not defined for {self.definition.block_type}")
        
        # Validate
        if inp_def.validation_rule and not inp_def.validation_rule(value):
            raise ValueError(f"Invalid value for {input_name}: {value}")
        
        self.input_values[input_name] = value
    
    def to_dict(self):
        """Convert to serializable format"""
        return {
            'block_id': self.block_id,
            'type': self.definition.block_type,
            'x': self.x,
            'y': self.y,
            'inputs': self.input_values,
            'input_connections': self.input_connections,
            'output_connections': self.output_connections
        }
```

### Tier 3: Block Definitions Library

```python
class BlockLibrary:
    """Registry of all available block definitions"""
    
    DEFINITIONS = {
        'Start': BlockDefinition(
            block_type='Start',
            label='Start',
            description='Program entry point',
            width=100,
            height=36,
            color='#90EE90',
            inputs=[],
            outputs=[BlockOutput('out', OutputType.FLOW)]
        ),
        
        'End': BlockDefinition(
            block_type='End',
            label='End',
            description='Program exit point',
            width=100,
            height=36,
            color='#FF6B6B',
            inputs=[BlockInput('in', InputType.FLOW, '', 'none')],
            outputs=[]
        ),
        
        'If': BlockDefinition(
            block_type='If',
            label='If',
            description='Conditional branch',
            width=100,
            height=54,
            color='#87CEEB',
            inputs=[
                BlockInput('left_value', InputType.LITERAL, '', '', 'Left side of condition'),
                BlockInput('operator', InputType.LITERAL, '==', '==', 'Comparison operator'),
                BlockInput('right_value', InputType.LITERAL, '', '', 'Right side of condition'),
            ],
            outputs=[
                BlockOutput('true', OutputType.TRUE_PATH, 'True'),
                BlockOutput('false', OutputType.FALSE_PATH, 'False')
            ]
        ),
        
        'Switch': BlockDefinition(
            block_type='Switch',
            label='Switch',
            description='Turn device on/off',
            width=100,
            height=54,
            color='#87CEEB',
            inputs=[
                BlockInput('device', InputType.DEVICE, '', '', 'Which device', required=True),
                BlockInput('state', InputType.LITERAL, 'ON', 'ON', 'ON or OFF'),
            ],
            outputs=[BlockOutput('out', OutputType.FLOW)]
        ),
        
        'Timer': BlockDefinition(
            block_type='Timer',
            label='Wait',
            description='Pause execution',
            width=140,
            height=36,
            color='#87CEEB',
            inputs=[
                BlockInput(
                    'duration_ms', 
                    InputType.LITERAL, 
                    '1000', 
                    '1000', 
                    'Milliseconds to wait',
                    validation_rule=lambda x: int(x) > 0
                ),
            ],
            outputs=[BlockOutput('out', OutputType.FLOW)]
        ),
        
        'Button': BlockDefinition(
            block_type='Button',
            label='Button',
            description='Wait for button press',
            width=100,
            height=54,
            color='#D3D3D3',
            inputs=[
                BlockInput('device', InputType.DEVICE, '', '', 'Which button'),
            ],
            outputs=[
                BlockOutput('pressed', OutputType.TRUE_PATH, 'Pressed'),
                BlockOutput('not_pressed', OutputType.FALSE_PATH, 'Not Pressed')
            ]
        ),
    }
    
    @classmethod
    def get(cls, block_type: str) -> BlockDefinition:
        """Get definition for a block type"""
        if block_type not in cls.DEFINITIONS:
            raise ValueError(f"Unknown block type: {block_type}")
        return cls.DEFINITIONS[block_type]
```

---

## Integration with UI Layer

### Updating BlockGraphicsItem

```python
class BlockGraphicsItem(QGraphicsItem, QObject):
    """Now uses BlockInstance for data"""
    
    def __init__(self, x, y, block_instance: BlockInstance, parent_canvas):
        super().__init__()
        
        # Store the data model
        self.block_instance = block_instance
        self.canvas = parent_canvas
        
        # Set position
        self.setPos(x, y)
        
        # Visual properties from definition
        definition = block_instance.definition
        self.width = definition.width
        self.height = definition.height
        self.color = definition.color
        
        # Setup drawing
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
    
    def paint(self, painter, option, widget):
        """Paint uses definition, not hardcoded logic"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw body with definition color
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(QPen(QColor('black'), 2))
        
        body_rect = QRectF(6, 0, self.width, self.height)
        painter.drawRoundedRect(body_rect, 3, 3)
        
        # Draw label from definition
        painter.setPen(QPen(QColor('black')))
        font = QFont('Arial', 10, QFont.Weight.Normal)
        painter.setFont(font)
        
        painter.drawText(body_rect, Qt.AlignmentFlag.AlignCenter, 
                        self.block_instance.definition.label)
        
        # Draw input circles for each input
        for i, inp in enumerate(self.block_instance.definition.inputs):
            self._draw_input_circle(painter, i)
        
        # Draw output circles for each output
        for i, out in enumerate(self.block_instance.definition.outputs):
            self._draw_output_circle(painter, i)
    
    def get_input_data(self, input_name: str):
        """Get current input value"""
        return self.block_instance.get_input(input_name)
    
    def set_input_data(self, input_name: str, value):
        """Update input value"""
        self.block_instance.set_input(input_name, value)
        self.update()  # Redraw
```

### Updating Inspector/Settings Window

```python
class BlockInspectorPanel:
    """UI for editing block properties"""
    
    def show_block_properties(self, block_graphics: BlockGraphicsItem):
        """Show inputs based on definition"""
        definition = block_graphics.block_instance.definition
        
        # Clear previous widgets
        self.clear_layout()
        
        # Create input widget for each input
        for inp in definition.inputs:
            label = QLabel(inp.description or inp.name)
            
            if inp.input_type == InputType.DEVICE:
                # Dropdown with available devices
                combo = QComboBox()
                combo.addItems([d['name'] for d in Utils.devices.values()])
                combo.currentTextChanged.connect(
                    lambda v, name=inp.name: 
                    block_graphics.set_input_data(name, v)
                )
            
            elif inp.input_type == InputType.VARIABLE:
                # Dropdown with available variables
                combo = QComboBox()
                combo.addItems([v['name'] for v in Utils.variables.values()])
                combo.currentTextChanged.connect(
                    lambda v, name=inp.name: 
                    block_graphics.set_input_data(name, v)
                )
            
            elif inp.input_type == InputType.LITERAL:
                # Text input
                line_edit = QLineEdit()
                line_edit.setText(str(inp.value))
                line_edit.textChanged.connect(
                    lambda v, name=inp.name: 
                    block_graphics.set_input_data(name, v)
                )
                widget = line_edit
            
            self.add_row(label, widget)
```

---

## Integration with Code Compiler

### Cleaner Compiler with Type Safety

```python
class CodeCompiler:
    """Generates executable code"""
    
    def __init__(self):
        self.file = None
        self.indent_level = 0
        self.indent_str = "    "
    
    def compile(self):
        """Main entry point"""
        self.file = open("File.py", "w")
        
        # Find start block
        start_block = self.find_block_by_type('Start')
        if start_block:
            self.write_imports()
            self.write_setup()
            self.process_block(start_block.block_id)
            self.write_cleanup()
        
        self.file.close()
    
    def process_block(self, block_id: str):
        """Process a single block instance"""
        block = Utils.get_block(block_id)  # Now returns BlockInstance
        
        # Dispatch based on type
        handler = getattr(self, f'handle_{block.definition.block_type.lower()}', None)
        if handler:
            handler(block)
        else:
            print(f"No handler for {block.definition.block_type}")
    
    def handle_if(self, block: BlockInstance):
        """Generate If condition code"""
        left = self.resolve_value(block.get_input('left_value'))
        operator = block.get_input('operator')
        right = self.resolve_value(block.get_input('right_value'))
        
        self.writeline(f"if {left} {operator} {right}:")
        self.indent_level += 1
        
        # Process true path
        true_output = block.definition.outputs[0]  # True output
        next_block = self.get_next_block(block_id, true_output.name)
        self.process_block(next_block)
        
        self.indent_level -= 1
        self.writeline("else:")
        self.indent_level += 1
        
        # Process false path
        false_output = block.definition.outputs[1]  # False output
        next_block = self.get_next_block(block_id, false_output.name)
        self.process_block(next_block)
        
        self.indent_level -= 1
    
    def handle_switch(self, block: BlockInstance):
        """Generate device control code"""
        device = self.resolve_value(block.get_input('device'))
        state = block.get_input('state')
        
        if self.GPIO_compile:
            gpio_state = 'GPIO.HIGH' if state == 'ON' else 'GPIO.LOW'
            self.writeline(f"GPIO.output({device}, {gpio_state})")
        elif self.MC_compile:
            pin_state = '1' if state == 'ON' else '0'
            self.writeline(f"{device}.value({pin_state})")
        
        # Continue to next block
        next_block = self.get_next_block_by_output(block, 'out')
        if next_block:
            self.process_block(next_block)
    
    def resolve_value(self, value_str: str):
        """Convert value reference to code"""
        # Is it a device name?
        for dev_id, dev_info in Utils.devices.items():
            if dev_info['name'] == value_str:
                return f"Devices['{value_str}']['PIN']"
        
        # Is it a variable name?
        for var_id, var_info in Utils.variables.items():
            if var_info['name'] == value_str:
                return f"Variables['{value_str}']['value']"
        
        # It's a literal
        return str(value_str)
```

---

## Summary: Input/Output Pattern

### From User Side (UI)
```
User interacts with Inspector
    ↓
BlockGraphicsItem.set_input_data(name, value)
    ↓
BlockInstance.set_input(name, value)  ← VALIDATION HERE
    ↓
Utils.save_to_project_data()
```

### From App Side (Compiler)
```
CodeCompiler.process_block(block_id)
    ↓
Get BlockInstance from Utils
    ↓
block.get_input('input_name')  ← ALWAYS PRESENT & VALID
    ↓
handle_X_block(block)  ← Generate code
```

---

## Key Benefits

1. **Single Source of Truth** - BlockDefinition defines what each block needs
2. **Type Safety** - Inputs validated when set, not during compilation
3. **Clear Contracts** - Every block documents its inputs/outputs
4. **Easy Testing** - Can create BlockInstance without UI
5. **Scalability** - Adding new block type = just add to DEFINITIONS dict
6. **Less Bugs** - Compiler can assume all inputs are valid
