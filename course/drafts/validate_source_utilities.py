"""Validate authored drafts without changing the version under repeated review."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

builder = module('curriculum_builder', ROOT/'tools/build_curriculum.py')
previous = list(builder.module.TOPICS)
start = len(previous)
draft = module('utilities_draft', ROOT/'course/drafts/source_utilities.py')
draft.register(builder.module.topic, builder.module.q, builder.module.detail)
topics = builder.module.TOPICS[start:]
titles = {item['title'] for item in previous}
prompts = {q['prompt'] for item in previous for q in item['questions']}
plans_path = ROOT/'course/planned_topics.json'
plans = json.loads(plans_path.read_text(encoding='utf-8'))
planned = {item['title']: item for item in plans}
number = max(int(item['key'].split('-')[-1]) for item in plans) + 1
anchors = []
for index, topic in enumerate(topics, start+17):
    assert topic['title'] not in titles, topic['title']
    titles.add(topic['title'])
    code, excerpt = builder.source(topic['path'], topic['symbol'])
    assert topic['symbol'] in code
    assert len(topic['why']) >= 30 and len(topic['principle']) >= 60 and len(topic['use']) >= 40
    assert len(topic['questions']) == 2 and len(topic['details']) >= 2
    for question in topic['questions']:
        assert question['prompt'] not in prompts, question['prompt']
        prompts.add(question['prompt'])
        assert question['correct'] != question['wrong'] and len(question['explanation']) >= 20
    item = planned.get(topic['title'])
    if not item:
        item = {'key': f'planned-{number:03d}'}
        number += 1
        plans.append(item)
    item.update(title=topic['title'], source=topic['path'], symbol=topic['symbol'], area=topic['area'])
    anchors.append(dict(planned_lesson=f'os{index:02d}', title=topic['title'], path=topic['path'], excerpt=excerpt))
plans_path.write_text(json.dumps(plans, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
validation = dict(sha='adc218676eef25575469234709c2d87185ca223a', draft_lessons=len(topics),
                  questions=sum(len(item['questions']) for item in topics), anchors=anchors)
(ROOT/'course/drafts/source_utilities_validation.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f'PASS {len(topics)} drafts, {validation["questions"]} distinct worked questions and exact source anchors')
