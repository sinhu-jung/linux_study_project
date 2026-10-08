"""Review-only pending90 bundle; integrate individual units once."""
import importlib.util
from pathlib import Path

def register(topic,q,detail):
    for name in ['source_memory_and_formatting_review_bundle','source_bitmap']:
        path=Path(__file__).with_name(name+'.py')
        spec=importlib.util.spec_from_file_location('review_'+name,path)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.register(topic,q,detail)
