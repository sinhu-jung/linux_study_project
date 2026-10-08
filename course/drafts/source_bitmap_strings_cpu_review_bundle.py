from pathlib import Path
import importlib.util
def register(topic,q,detail):
 for name in ["source_bitmap_strings.py","source_cpu_masks.py"]:
  spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.register(topic,q,detail)
