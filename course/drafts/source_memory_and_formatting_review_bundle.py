"""Review-only pending bundle. Register individual units once at integration."""
import importlib.util
from pathlib import Path

def register(topic,q,detail):
    for name in ['source_memory_helpers','source_formatting_core','source_formatting_pointers','source_formatting_network','source_formatting_metadata','source_formatting_engine','source_formatting_binary_scan']:
        path=Path(__file__).with_name(name+'.py')
        spec=importlib.util.spec_from_file_location('review_'+name,path)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.register(topic,q,detail)
