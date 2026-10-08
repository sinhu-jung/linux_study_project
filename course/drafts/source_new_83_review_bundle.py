from pathlib import Path
import importlib.util
def register(topic,q,detail):
 for name in ['source_new_68_review_bundle.py', 'source_array_sort.py', 'source_list_sort.py']:
  spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.register(topic,q,detail)
