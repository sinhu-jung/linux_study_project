#!/usr/bin/env python3
"""Build authored topic lessons using exact v6.12 source excerpts.

No model/API is used here. Teaching text and worked questions are authored in
course/topics.py. Missing source anchors fail the build, never become fake code.
"""
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent
support_spec = importlib.util.spec_from_file_location('reading_support', ROOT / 'course/reading_support.py')
support = importlib.util.module_from_spec(support_spec)
support_spec.loader.exec_module(support)
GIT = os.environ.get('STUDY_GIT', '/opt/homebrew/bin/git' if Path('/opt/homebrew/bin/git').exists() else 'git')
spec = importlib.util.spec_from_file_location('authored_topics', ROOT / 'course/topics.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
units_path = ROOT/'course/units.json'
for unit_name in json.loads(units_path.read_text(encoding='utf-8')) if units_path.exists() else []:
    unit_spec = importlib.util.spec_from_file_location(unit_name.replace('.py',''), ROOT/'course'/unit_name)
    unit = importlib.util.module_from_spec(unit_spec)
    unit_spec.loader.exec_module(unit)
    unit.register(module.topic, module.q, module.detail)

def source(path, symbol, occurrence=1):
    lines = subprocess.check_output([GIT, '-C', str(ROOT / 'linux'), 'show', 'HEAD:' + path]).decode().splitlines()
    # Start on a declaration/definition or Makefile assignment, never a call site.
    pattern = re.compile(r'\b' + re.escape(symbol) + r'\s*\(')
    candidates = []
    for i, line in enumerate(lines):
        rust_declaration = path.endswith('.rs') and line.startswith(symbol)
        kconfig_declaration = Path(path).name.startswith('Kconfig') and bool(re.match(r'^(?:config|menuconfig)\s+' + re.escape(symbol) + r'\s*$', line))
        make_assignment = (Path(path).name in ('Makefile', 'Kbuild') or path.endswith('.mk')) and bool(re.match(r'^' + re.escape(symbol) + r'\s*(?::=|\+=|\?=|=)', line.lstrip()))
        register_declaration = path.endswith(('.h', '.c')) and bool(re.match(r'^register\s+unsigned\s+long\s+' + re.escape(symbol) + r'\s+asm\s*\(\"[A-Za-z0-9_]+\"\)\s*;', line))
        rst_heading = path.endswith('.rst') and line.strip() == symbol and i + 1 < len(lines) and bool(re.fullmatch(r'[=~^`:+#-]+', lines[i+1].strip()))
        assembler_macro = path.endswith(('.h', '.S', '.s')) and bool(re.match(r'^\s*\.macro\s+' + re.escape(symbol) + r'(?:\s|$)', line))
        typedef_pointer = path in ('arch/arm64/include/asm/alternative.h', 'include/linux/stop_machine.h', 'include/linux/of_reserved_mem.h', 'include/linux/of_irq.h') and bool(re.match(r'^typedef\s+[^;]*\(\s*\*\s*' + re.escape(symbol) + r'\s*\)\s*\(', line))
        struct_instance = path == 'arch/arm64/kernel/alternative.c' and bool(re.match(r'^static\s+const\s+struct\s+\w+\s+' + re.escape(symbol) + r'\s+\w*\s*=\s*\{', line))
        enum_member = path in ('scripts/dtc/libfdt/libfdt_internal.h', 'include/linux/irqreturn.h') and bool(re.match(r'^\s*' + re.escape(symbol) + r'\s*=', line))
        enum_declaration = path in ('arch/arm64/include/asm/fixmap.h', 'include/linux/irqreturn.h') and bool(re.match(r'^enum\s+' + re.escape(symbol) + r'\s*\{', line))
        object_macro = path in ('arch/arm64/include/asm/alternative-macros.h', 'arch/arm64/include/asm/insn-def.h', 'arch/arm64/include/asm/fixmap.h', 'include/asm-generic/fixmap.h', 'arch/arm64/mm/fixmap.c', 'scripts/dtc/libfdt/libfdt_env.h', 'scripts/dtc/libfdt/fdt.h', 'scripts/dtc/libfdt/libfdt_internal.h', 'scripts/dtc/libfdt/libfdt.h', 'include/linux/libfdt.h', 'include/linux/libfdt_env.h', 'include/linux/of_irq.h') and bool(re.match(r'^#define\s+' + re.escape(symbol) + r'(?:\s|$)', line))
        kernel_fdt_include = path in ('lib/fdt.c', 'lib/fdt_ro.c', 'lib/fdt_wip.c', 'lib/fdt_rw.c', 'lib/fdt_sw.c', 'lib/fdt_strerror.c', 'lib/fdt_empty_tree.c', 'lib/fdt_addresses.c', 'include/linux/libfdt.h') and symbol.startswith('#include ') and line.strip() == symbol
        irq_return_typedef = path == 'include/linux/irqreturn.h' and bool(re.match(r'^typedef\s+enum\s+irqreturn\s+' + re.escape(symbol) + r'\s*;', line))
        kernel_fdt_typedef = path == 'include/linux/libfdt_env.h' and bool(re.match(r'^typedef\s+__be(?:16|32|64)\s+' + re.escape(symbol) + r'\s*;', line))
        array_declaration = bool(re.match(r'^[^\s/*#].*\b' + re.escape(symbol) + r'\s*\[[^]]*\]\s*=\s*\{', line))
        struct_declaration = bool(re.match(r'^struct\s+' + re.escape(symbol) + r'\s*\{', line))
        if not pattern.search(line) and not kconfig_declaration and not make_assignment and not rust_declaration and not array_declaration and not kernel_fdt_include and not kernel_fdt_typedef and not irq_return_typedef and not typedef_pointer and not struct_instance and not enum_member and not enum_declaration and not object_macro and not assembler_macro and not rst_heading and not register_declaration and not struct_declaration and not (path.endswith('Makefile.build') and line.lstrip().startswith(symbol)) and not (symbol.startswith('SYSCALL_') and symbol in line):
            continue
        stripped = line.lstrip()
        if stripped.startswith(('/*', '*', '//')):
            continue
        # Signatures may be macro definitions or a symbol on its own line.
        if enum_member or assembler_macro or rst_heading or kconfig_declaration or line.startswith(('#define', symbol)) or (path.endswith('Makefile.build') and line.lstrip().startswith(symbol)) or (line and not line[0].isspace() and not line.startswith(('return', 'EXPORT_'))):
            if path.endswith('.c') and not line.startswith('#') and not symbol.isupper() and not symbol.startswith('SYSCALL_'):
                # Forward prototypes are not implementations. Look through a
                # multiline signature for its first body/declaration delimiter.
                signature = '\n'.join(lines[i:i + 24])
                delimiter = re.search(r'[;{]', signature)
                if delimiter and delimiter.group() == ';':
                    continue
            candidates.append(i)
    if not candidates:
        raise ValueError(f'{path}: definition anchor missing: {symbol}')
    if not isinstance(occurrence, int) or occurrence < 1 or occurrence > len(candidates):
        raise ValueError(f'{path}: definition occurrence out of range: {symbol} #{occurrence}')
    start = candidates[occurrence - 1]
    end = min(start + 26, len(lines))
    # Do not end inside a block comment; retain exact source, not ellipses.
    while end < len(lines) and '\n'.join(lines[start:end]).count('/*') > '\n'.join(lines[start:end]).count('*/'):
        end += 1
    return '\n'.join(lines[start:end]) + '\n', {'start': start + 1, 'end': end, 'anchor': symbol}

def build():
    path = ROOT / 'course/lessons.json'
    current = json.loads(path.read_text(encoding='utf-8'))
    base = [item for item in current if not item.get('authored_topic')]
    new = []
    errors = []
    for index, item in enumerate(module.TOPICS, 17):
        try:
            code, excerpt = source(item['path'], item['symbol'], item.get('source_occurrence', 1))
        except (ValueError, subprocess.CalledProcessError) as error:
            errors.append(str(error))
            continue
        questions = []
        scenarios = []
        for number, question in enumerate(item['questions']):
            choices = [question['correct'], question['wrong']]
            if number % 2 == 0:
                choices.reverse()
            questions.append({'prompt': question['prompt'], 'options': choices,
                              'answer': choices.index(question['correct']), 'explanation': question['explanation']})
            scenarios.append({'title': f'조건 {number + 1}: {question["prompt"]}', 'steps': [
                {'diagram': question['prompt'], 'explanation': '먼저 위 원리와 적용 조건을 이용해 결과를 예측해보세요.'},
                {'diagram': question['correct'], 'explanation': question['explanation']},
            ]})
        language_guide = ('이 원문은 assembler 매크로입니다. .macro/.endm·인자 치환·레지스터·명령·전처리 조건과 실제 실행 문맥을 구별하세요.' if item['path'].endswith('asm_pointer_auth.h') else '이 원문은 reStructuredText 문서입니다. 제목·절·문단·설정 이름과 예시를 구별하며 C 실행 코드로 해석하지 마세요.' if item['path'].endswith('.rst') else 'Rust의 &T는 빌린 참조이고 Drop은 값의 수명이 끝날 때 정리를 수행합니다. unsafe 경계는 호출자와 구현자가 추가 불변식을 지켜야 하는 부분입니다.' if item['path'].endswith('.rs') else 'C의 ->는 포인터가 가리키는 구조체의 필드 접근입니다. &는 주소를 얻고 *는 포인터 선언·역참조에 쓰입니다. 전처리 매크로와 Makefile은 C 함수와 구별하세요.')
        guide = [f'{item["symbol"]}: 이 발췌와 전체 파일을 연결해 읽는 기준 지점입니다.',
                 item['principle'], language_guide,
                 '발췌 뒤에 함수가 이어질 수 있습니다. 원본 링크에서 호출 전제, 오류 경로, 해제 경로를 함께 확인하세요.']
        annotation = ('/* 학습 해설\n * ' + '\n * '.join([item['title'], item['why'], item['principle'], item['use']]) + '\n */\n' + code)
        new.append({'id': f'os{index:02d}', 'title': item['title'], 'area': item['area'],
                    'track': 'os', 'kind': 'kernel', 'authored_topic': True, 'path': item['path'],
                    'intro': item['why'], 'goal': item['title'], 'excerpt': excerpt,
                    'concepts': [{'title': '왜 필요한가', 'text': item['why']},
                                 {'title': '기술·자료구조·알고리즘의 원리', 'text': item['principle']},
                                 {'title': '사용 방법과 적용 조건', 'text': item['use']}],
                    'practice': {'platform': 'Linux·WSL의 조회 또는 이 학습실의 고정된 v6.12 원본 탐색. 환경에 따라 명령·기능이 없거나 권한이 필요할 수 있습니다.',
                                 'command': item['observation'], 'expected': '확인할 원리: ' + item['principle']},
                    'guide': guide, 'questions': questions, 'annotated': annotation, 'deep_dive':item.get('details', []),
                    'experiment': {'scenarios': scenarios},
                    'references': [{'title': '고정 버전 원본과 앞뒤 문맥', 'url': '/explorer#' + item['path'] + '?line=' + str(excerpt['start'])}]})
    if errors:
        raise SystemExit('\n'.join(errors))
    for lesson in base + new:
        support.enrich(lesson)
    path.write_text(json.dumps(base + new, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os_lessons = [item for item in base + new if item.get('track') == 'os']
    syllabus = ['# Linux v6.12 OS 학습 교재와 문제·답지', '',
                f'{len(os_lessons)}개 수업. 실제 원본은 각 파일·행 범위로 연결됩니다.', '',
                '이 교재는 명시된 수업 목록의 해설과 문제를 제공합니다. Linux 전체 구현의 모든 세부 기능·드라이버·아키텍처·알고리즘을 망라했다는 인증서는 아닙니다.', '']
    for lesson in os_lessons:
        syllabus += [f'## {lesson["id"]}. {lesson["title"]}', '',
                     f'분야: {lesson.get("area", "OS 시작")} · 원본: `{lesson["path"]}` {lesson["excerpt"]["start"]}–{lesson["excerpt"]["end"]}행', '']
        reading = lesson['reading_support']
        for section in reading['walkthrough']:
            syllabus += [f'### 쉽게 풀어 읽기 · {section["title"]}', '', section['text'], '']
        foundation = reading['foundation']
        syllabus += [f'### 분야 공통 기초 · {foundation["title"]}', '', foundation['text'], '']
        syllabus += ['<details>', '<summary>본문에 나온 용어 풀이</summary>', '']
        for section in reading['terms']:
            syllabus += [f'**{section["title"]}**', '', section['text'], '']
        syllabus += ['</details>', '']
        for concept in lesson['concepts']:
            syllabus += [f'### {concept["title"]}', '', concept['text'], '']
        for section in lesson.get('deep_dive', []):
            syllabus += [f'### {section["title"]}', '', section['text'], '']
        syllabus += ['### 사용·관찰 실습', '', lesson['practice']['command'], '', '### 문제와 풀이', '']
        for number, question in enumerate(lesson['questions'], 1):
            syllabus += [f'{number}. {question["prompt"]}', '',
                         '\n'.join(f'   - {option}' for option in question['options']), '',
                         f'   **정답:** {question["options"][question["answer"]]}', '', f'   **풀이:** {question["explanation"]}', '']
    (ROOT / 'course/syllabus.md').write_text('\n'.join(syllabus), encoding='utf-8')
    areas = {}
    for lesson in os_lessons:
        areas.setdefault(lesson.get('area', 'OS 시작'), []).append(lesson['id'])
    (ROOT / 'course/coverage.json').write_text(json.dumps({
        'version': 'v6.12', 'lessons': len(os_lessons),
        'questions': sum(len(l['questions']) for l in os_lessons), 'areas': areas,
        'requirements': ['필요한 이유', '동작 원리', '사용 방법·조건', '고정 원본 연결', '조건별 예측·풀이', '문제', '정답·해설'],
        'scope': f'현재 작성된 {len(os_lessons)}개 수업의 명세. 미작성 항목은 requirements.json과 source-audit.json에서 추적하며 작성 수만으로 전체 완료를 판단하지 않음.',
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(new)} authored topics; {len(base) + len(new)} lessons total')

if __name__ == '__main__':
    build()
