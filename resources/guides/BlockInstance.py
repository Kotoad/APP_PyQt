"""
BlockInstance.py - Runtime block data
Wraps your custom input properties with validation
Handles serialization to/from ProjectData
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from resources.guides.BlockDefinitions import BlockLibrary, BlockTypeDef


@dataclass
class BlockInstance:
    """One block on the canvas with all its data"""
    
    # Metadata
    block_id: str
    block_type: str  # "If", "Switch", etc
    x: float = 0
    y: float = 0
    
    # YOUR CUSTOM INPUTS - same names, same structure
    # Just organized in ONE place instead of scattered properties
    custom_inputs: Dict[str, Any] = field(default_factory=dict)
    
    # Connections (from your current code)
    input_connections: List[str] = field(default_factory=list)
    output_connections: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize inputs with defaults"""
        if not self.custom_inputs:
            definition = BlockLibrary.get_definition(self.block_type)
            for input_name, input_def in definition.inputs.items():
                self.custom_inputs[input_name] = input_def.default_value
    
    def get_input(self, input_name: str) -> Any:
        """Get custom input value"""
        return self.custom_inputs.get(input_name)
    
    def set_input(self, input_name: str, value: Any) -> None:
        """Set custom input with validation"""
        try:
            definition = BlockLibrary.get_definition(self.block_type)
        except ValueError:
            # Block type not found, just store it
            self.custom_inputs[input_name] = value
            return
        
        input_def = definition.inputs.get(input_name)
        
        if not input_def:
            # Input not in definition, but store it anyway
            self.custom_inputs[input_name] = value
            return
        
        # Validate if validation function provided
        if input_def.validation_fn:
            try:
                if not input_def.validation_fn(value):
                    raise ValueError(f"Validation failed for {input_name}: {value}")
            except Exception as e:
                print(f"Validation error: {e}")
                return
        
        self.custom_inputs[input_name] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to ProjectData format
        COMPATIBLE with your current code
        """
        return {
            'block_id': self.block_id,
            'type': self.block_type,
            'x': self.x,
            'y': self.y,
            # YOUR CUSTOM INPUTS - same keys as before
            'value_1_name': self.custom_inputs.get('value_1_name', ''),
            'value_1_type': self.custom_inputs.get('value_1_type', 'N/A'),
            'value_2_name': self.custom_inputs.get('value_2_name', ''),
            'value_2_type': self.custom_inputs.get('value_2_type', 'N/A'),
            'operator': self.custom_inputs.get('operator', '=='),
            'switch_state': self.custom_inputs.get('switch_state', False),
            'sleep_time': self.custom_inputs.get('sleep_time', '1000'),
            'in_connections': self.input_connections,
            'out_connections': self.output_connections
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BlockInstance':
        """
        Deserialize from ProjectData
        COMPATIBLE with your current format
        """
        instance = cls(
            block_id=data.get('block_id', ''),
            block_type=data.get('type', 'Start'),
            x=data.get('x', 0),
            y=data.get('y', 0),
            input_connections=data.get('in_connections', []),
            output_connections=data.get('out_connections', [])
        )
        
        # Load all your custom inputs from dict
        instance.custom_inputs['value_1_name'] = data.get('value_1_name', '')
        instance.custom_inputs['value_1_type'] = data.get('value_1_type', 'N/A')
        instance.custom_inputs['value_2_name'] = data.get('value_2_name', '')
        instance.custom_inputs['value_2_type'] = data.get('value_2_type', 'N/A')
        instance.custom_inputs['operator'] = data.get('operator', '==')
        instance.custom_inputs['switch_state'] = data.get('switch_state', False)
        instance.custom_inputs['sleep_time'] = data.get('sleep_time', '1000')
        
        return instance
