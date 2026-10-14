"""Render the existing OS syllabus from canonical lessons without regenerating them."""
from lesson_storage import _atomic_text


def render_syllabus(root, lessons, glossary):
    os_lessons = [lesson for lesson in lessons if lesson.get('track') == 'os']
    lines = ['# Linux v6.12 OS 학습 교재와 문제·답지', '',
             f'{len(os_lessons)}개 수업. 설명과 문제는 현재 학습 화면과 같은 수업 데이터에서 가져옵니다.', '',
             '원본 코드와 수정 전 설명은 각 수업 데이터의 technical_original에 보존됩니다. '
             '이 교재는 현재 작성된 OS 수업을 다루며 Linux의 모든 파일을 다루지는 않습니다.', '']
    for lesson in os_lessons:
        lines += [f'## {lesson["id"]}. {lesson["title"]}', '',
                  f'분야: {lesson.get("area", "OS 시작")} · 원본: `{lesson["path"]}`', '']
        excerpt = lesson.get('excerpt')
        if excerpt:
            lines += [f'원본 범위: {excerpt["start"]}–{excerpt["end"]}행', '']
        beginner = lesson.get('beginner', {})
        for label, text in [('친숙한 예로 시작하기', beginner.get('story')),
                            ('무슨 뜻인가요?', beginner.get('meaning', lesson.get('intro'))),
                            ('이번에 배울 것', lesson.get('goal'))]:
            if text:
                lines += [f'### {label}', '', text, '']
        lines += ['### 차례대로 이해하기', '']
        for text in lesson.get('guide', []):
            lines += [text, '']
        for section in lesson.get('concepts', []) + lesson.get('deep_dive', []):
            lines += [f'### {section["title"]}', '', section['text'], '']
        reading = lesson.get('reading_support') or {}
        for section in reading.get('walkthrough', []):
            lines += [f'### 쉽게 풀어 읽기 · {section["title"]}', '', section['text'], '']
        if reading.get('foundation'):
            section = reading['foundation']
            lines += [f'### 분야 공통 기초 · {section["title"]}', '', section['text'], '']
        terms = [glossary[i] for i in lesson.get('reading_aid', {}).get('terms', [])]
        if terms:
            lines += ['<details>', '<summary>본문에 나온 용어 풀이</summary>', '']
            for section in terms:
                lines += [f'**{section["term"]}**', '', section['meaning'], '']
            lines += ['</details>', '']
        if beginner.get('exercise'):
            lines += ['### 종이에 따라 해 보기', '', beginner['exercise'], '']
        practice = lesson.get('practice', {})
        if practice.get('command'):
            lines += ['### 사용·관찰 실습', '', practice['command'], '',
                      practice.get('expected', ''), '']
        lines += ['### 문제와 풀이', '']
        for number, question in enumerate(lesson['questions'], 1):
            lines += [f'{number}. {question["prompt"]}', '',
                      '\n'.join(f'   - {option}' for option in question['options']), '',
                      f'   **정답:** {question["options"][question["answer"]]}', '',
                      f'   **풀이:** {question["explanation"]}', '']
    _atomic_text(root / 'course/syllabus.md', '\n'.join(lines))
