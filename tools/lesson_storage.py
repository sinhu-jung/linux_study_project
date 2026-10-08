"""Small, ordered JSON parts for Git; the combined file is a local cache."""
import json
import os
from pathlib import Path
import tempfile


def _atomic_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def load_lessons(root):
    course = Path(root) / 'course'
    manifest = course / 'lesson-parts.json'
    if not manifest.exists():  # Migration from the original checkout.
        return json.loads((course / 'lessons.json').read_text(encoding='utf-8'))
    index = json.loads(manifest.read_text(encoding='utf-8'))
    lessons = []
    for name in index['parts']:
        if Path(name).name != name or not name.endswith('.json'):
            raise ValueError('Invalid lesson part name')
        lessons.extend(json.loads((course / 'lesson-parts' / name).read_text(encoding='utf-8')))
    if len(lessons) != index['lessons'] or len({x['id'] for x in lessons}) != len(lessons):
        raise ValueError('Lesson count or IDs do not match the manifest')
    return lessons


def ensure_lessons_cache(root):
    path = Path(root) / 'course/lessons.json'
    text = json.dumps(load_lessons(root), ensure_ascii=False, indent=2) + '\n'
    if not path.exists() or path.read_text(encoding='utf-8') != text:
        _atomic_text(path, text)
    return path


def write_lessons(root, lessons):
    course = Path(root) / 'course'
    parts = []
    # 50 lessons per part bounds diffs and keeps current parts well below 1 MiB.
    for offset in range(0, len(lessons), 50):
        name = f'{offset // 50 + 1:04d}.json'
        _atomic_text(course / 'lesson-parts' / name,
                     json.dumps(lessons[offset:offset + 50], ensure_ascii=False, indent=2) + '\n')
        parts.append(name)
    _atomic_text(course / 'lesson-parts.json', json.dumps(
        {'version': 1, 'lessons': len(lessons), 'parts': parts}, indent=2) + '\n')
    for old in (course / 'lesson-parts').glob('*.json'):
        if old.name not in parts:
            old.unlink()
    ensure_lessons_cache(root)
