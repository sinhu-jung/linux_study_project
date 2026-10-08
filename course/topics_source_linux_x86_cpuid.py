"""Scattered x86 CPUID feature discovery."""
ROWS = [('x86 분산 CPUID 기능 탐지: 조회 범위와 레지스터 비트의 연결',
  'CPU·아키텍처',
  'arch/x86/kernel/cpu/scattered.c',
  'init_scattered_cpuid_features',
  'CPU 기능 비트는 하나의 레지스터에 모두 모여 있지 않습니다. 조회 leaf와 subleaf, 반환 레지스터, 비트 위치를 함께 알아야 하므로 표로 규칙을 저장하고 공통 루프로 해석하면 기능마다 '
  '비슷한 분기를 복제하지 않아도 됩니다.',
  'cpuid_bits의 각 항목에는 커널 feature 번호, reg, bit, level, sub_leaf가 있습니다. init_scattered_cpuid_features는 feature가 0인 '
  '끝 항목 전까지 순회합니다. cpuid_eax(level & 0xffff0000)로 그 영역의 최대 level을 읽고 max가 요청보다 작거나 level|0xffff보다 크면 건너뜁니다. 통과하면 '
  'cpuid_count로 EAX·EBX·ECX·EDX 네 결과를 받고 선택한 regs[reg]의 (1<<bit)가 켜졌을 때 set_cpu_cap을 호출합니다.',
  'level=7이면 먼저 leaf 0에서 최대값을 읽습니다. 최대값이 6이면 leaf 7은 조회하지 않습니다. level=0x80000007이면 기준은 0x80000000입니다. 표의 '
  'FAST_CPPC는 이 leaf의 EDX bit15이므로 그 결과가 0x8000이면 이 기능을 표시합니다. regs 배열의 비트 번호와 커널 feature 번호는 서로 다른 좌표입니다.',
  '왜 없는 비트를 지우거나 기능을 실행하는 함수는 아닌가',
  '검사 결과 비트가 없을 때 clear_cpu_cap을 호출하는 else 분기는 없습니다. 따라서 기존 설정을 전부 초기화하는 함수로 쓰면 안 됩니다. set_cpu_cap은 해당 cpuinfo의 '
  '기능 표시이며 이 코드가 특정 명령이나 장치를 활성화하는 전체 절차는 아닙니다. MBA는 표에 Intel과 AMD의 서로 다른 CPUID 위치가 각각 있고 같은 커널 feature로 연결됩니다. '
  '표는 level 순으로 유지하라는 주석이 있지만 실제 루프는 이진 검색이 아니라 순차 순회입니다.',
  ('level=7인데 leaf0의 최대 level이 6이면?',
   '해당 항목을 건너뜁니다.',
   'leaf7을 무조건 실행하고 비트를 읽습니다.',
   'max_level<cb->level 검사에서 continue합니다.'),
  ('원하는 하드웨어 비트가 0이면 기존 커널 feature도 지우나요?',
   '아닙니다. 이 함수에는 해당 else 처리나 clear가 없습니다.',
   '그렇습니다. 표를 읽을 때마다 모두 초기화합니다.',
   '비트가 1일 때 set_cpu_cap만 호출합니다. 기존 상태 초기화 책임과 탐지를 구분해야 합니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"leaf·subleaf·레지스터 비트·커널 feature 번호를 구별해 표를 따라가세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("검토 범위","v6.12의 표와 탐지 함수 본문을 대조했습니다. 각 CPU 기술 자체의 전체 설명이나 실제 하드웨어 CPUID 실행 검증은 이 수업 범위가 아닙니다.")])
