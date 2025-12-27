"""
BlockDefinitions.py - Define what each block type needs
Keep your custom inputs (value_1_name, operator, switch_state, sleep_time)
Just organize them into a structured format
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Callable


class InputType(Enum):
    """Types of inputs blocks accept"""
    DEVICE = "device"
    VARIABLE = "variable"
    LITERAL = "literal"
    OPERATOR = "operator"


@dataclass
class BlockInputDef:
    """Defines ONE input field for a block type"""
    name: str                              # "value_1_name", "operator", "sleep_time"
    input_type: InputType                  # What kind of value
    description: str                       # UI label
    default_value: Any = ""                # Initial value
    required: bool = True                  # Must be set?
    validation_fn: Optional[Callable] = None  # Custom validation


@dataclass
class BlockOutputDef:
    """Defines connection output"""
    name: str                              # "out", "out1", "out2"
    label: str = "Output"                  # UI label


@dataclass
class BlockTypeDef:
    """Complete definition of a block type"""
    block_type: str                        # "If", "Switch", "Timer"
    label: str                             # Display name
    description: str                       # Tooltip
    width: int = 100
    height: int = 54
    color: str = "#87CEEB"
    
    # YOUR CUSTOM INPUTS - organized but unchanged
    inputs: Dict[str, BlockInputDef] = field(default_factory=dict)
    outputs: List[BlockOutputDef] = field(default_factory=list)


# ============================================================================
# BLOCK TYPE LIBRARY - YOUR CUSTOM BLOCKS WITH DEFINITIONS
# ============================================================================

class BlockLibrary:
    """Registry of all your block types"""
    
    DEFINITIONS = {
        # ===== START BLOCK =====
        'Start': BlockTypeDef(
            block_type='Start',
            label='Start',
            description='Program entry point',
            width=100, height=36, color='#90EE90',
            inputs={},  # No inputs
            outputs=[BlockOutputDef('out', 'Next')]
        ),
        
        # ===== END BLOCK =====
        'End': BlockTypeDef(
            block_type='End',
            label='End',
            description='Program exit point',
            width=100, height=36, color='#FF6B6B',
            inputs={},
            outputs=[]
        ),
        
        # ===== IF BLOCK - YOUR CUSTOM 3 INPUTS =====
        'If': BlockTypeDef(
            block_type='If',
            label='If',
            description='Conditional branch',
            width=100, height=54, color='#87CEEB',
            inputs={
                'value_1_name': BlockInputDef(
                    name='value_1_name',
                    input_type=InputType.LITERAL,
                    description='Left value',
                    default_value='var1',
                    required=True
                ),
                'operator': BlockInputDef(
                    name='operator',
                    input_type=InputType.OPERATOR,
                    description='Comparison',
                    default_value='==',
                    required=True
                ),
                'value_2_name': BlockInputDef(
                    name='value_2_name',
                    input_type=InputType.LITERAL,
                    description='Right value',
                    default_value='var2',
                    required=True
                ),
            },
            outputs=[
                BlockOutputDef('out1', 'True'),
                BlockOutputDef('out2', 'False')
            ]
        ),
        
        # ===== TIMER BLOCK - YOUR CUSTOM SLEEP_TIME =====
        'Timer': BlockTypeDef(
            block_type='Timer',
            label='Wait',
            description='Pause execution',
            width=140, height=36, color='#87CEEB',
            inputs={
                'sleep_time': BlockInputDef(
                    name='sleep_time',
                    input_type=InputType.LITERAL,
                    description='Milliseconds',
                    default_value='1000',
                    required=True,
                    validation_fn=lambda x: int(x) > 0
                ),
            },
            outputs=[BlockOutputDef('out', 'Next')]
        ),
        
        # ===== SWITCH BLOCK - YOUR CUSTOM state + device =====
        'Switch': BlockTypeDef(
            block_type='Switch',
            label='Switch',
            description='Control device',
            width=100, height=54, color='#87CEEB',
            inputs={
                'value_1_name': BlockInputDef(
                    name='value_1_name',
                    input_type=InputType.DEVICE,
                    description='Device',
                    default_value='',
                    required=True
                ),
                'switch_state': BlockInputDef(
                    name='switch_state',
                    input_type=InputType.LITERAL,
                    description='ON/OFF',
                    default_value=False,
                    required=True
                ),
            },
            outputs=[BlockOutputDef('out', 'Next')]
        ),
        
        # ===== BUTTON BLOCK - YOUR CUSTOM device input =====
        'Button': BlockTypeDef(
            block_type='Button',
            label='Button',
            description='Wait for button',
            width=100, height=54, color='#D3D3D3',
            inputs={
                'value_1_name': BlockInputDef(
                    name='value_1_name',
                    input_type=InputType.DEVICE,
                    description='Button device',
                    default_value='',
                    required=True
                ),
            },
            outputs=[
                BlockOutputDef('out1', 'Pressed'),
                BlockOutputDef('out2', 'Not Pressed')
            ]
        ),
        
        # ===== WHILE BLOCK - SAME AS IF =====
        'While': BlockTypeDef(
            block_type='While',
            label='While',
            description='Repeat while condition',
            width=100, height=54, color='#87CEEB',
            inputs={
                'value_1_name': BlockInputDef(
                    name='value_1_name',
                    input_type=InputType.LITERAL,
                    description='Left value',
                    default_value='var1'
                ),
                'operator': BlockInputDef(
                    name='operator',
                    input_type=InputType.OPERATOR,
                    description='Comparison',
                    default_value='=='
                ),
                'value_2_name': BlockInputDef(
                    name='value_2_name',
                    input_type=InputType.LITERAL,
                    description='Right value',
                    default_value='var2'
                ),
            },
            outputs=[
                BlockOutputDef('out1', 'Loop'),
                BlockOutputDef('out2', 'Exit')
            ]
        ),
        
        # ===== WHILE_TRUE BLOCK =====
        'While_true': BlockTypeDef(
            block_type='While_true',
            label='While True',
            description='Infinite loop',
            width=100, height=36, color='#87CEEB',
            inputs={},
            outputs=[BlockOutputDef('out', 'Loop')]
        ),
    }
    
    @classmethod
    def get_definition(cls, block_type: str) -> BlockTypeDef:
        """Get definition for a block type"""
        if block_type not in cls.DEFINITIONS:
            raise ValueError(f"Unknown block type: {block_type}")
        return cls.DEFINITIONS[block_type]
    
    @classmethod
    def get_input_names(cls, block_type: str) -> List[str]:
        """Get all input names for a block"""
        definition = cls.get_definition(block_type)
        return list(definition.inputs.keys())
    
    @classmethod
    def get_input_def(cls, block_type: str, input_name: str) -> BlockInputDef:
        """Get specific input definition"""
        definition = cls.get_definition(block_type)
        if input_name not in definition.inputs:
            raise ValueError(f"Block {block_type} has no input '{input_name}'")
        return definition.inputs[input_name]
