"""Whole-file kexec FDT construction and IMA buffer handoff."""
ROWS = [dict(
    path='drivers/of/kexec.c', title='Kexec FDT 준비: 예약 메모리·initrd·crash·난수와 IMA 전달',
    intro='예약 삭제,주소·크기 파싱,IMA 수신·반환·재설정과 새 FDT 작성의 전체 경로를 분석합니다.',
    principle='다음 커널용 복제본을 수정하는 작업과 현재 커널의 실제 예약 메모리를 반환하는 작업은 구분해야 합니다.',
    use='구간 표현,소유권 이전,복제 후 수정,오류 회수와 보안 상태 전달을 학습합니다.',
    area='kexec · 부팅 · 장치 트리 · 메모리 예약 · IMA · 난수',
    sections=[
        ('상수와 전체 구성', 'GPL-2.0-only 파일은 IMA,kernel,kexec,memblock,libfdt,OF,OF FDT,random,slab,types를 포함합니다. RNG_SEED_SIZE=128바이트,FDT_EXTRA_SPACE=0x1000입니다. 추가 공간은 initrd,bootargs,난수 seed,usable memory와 elfcorehdr 속성 등을 위해 확보합니다. 상수의 존재가 임의 입력 길이에 대한 산술 검증을 대신하지 않습니다.'),
        ('예약 항목의 정확한 일치', 'find_and_del_mem_rsv는 예약 개수를 얻고 각 시작 주소와 크기를 읽습니다. 읽기나 삭제 오류를 -EINVAL로 바꾸며 시작과 크기가 모두 정확히 같은 첫 항목만 삭제합니다. 없으면 -ENOENT입니다. 겹치는 구간을 분할하거나 포함 관계로 삭제하는 알고리즘은 아닙니다. 예약 개수 함수의 음수를 별도 처리하는 분기는 없습니다.'),
        ('주소·크기 cell 파싱', 'get_addr_size_cells는 live tree 루트 /를 찾아 두 cell 수를 얻고 참조를 put합니다. 루트가 없으면 -EINVAL입니다. do_get_kexec_buffer는 속성 길이가 4*(address+size cell 수)보다 짧으면 -ENOENT이고 앞 주소와 뒤 크기를 of_read_number로 읽습니다. 복제 FDT에서 독립적으로 cell 수를 조회하는 것이 아니라 live root를 기준으로 합니다.'),
        ('이전 IMA 버퍼 얻기', 'HAVE_IMA_KEXEC 구성의 init 함수는 chosen의 linux,ima-kexec-buffer를 찾고 없으면 -ENOENT입니다. 파싱 오류를 전파하며 크기 0도 -ENOENT입니다. 시작과 마지막 바이트의 PFN이 page_is_ram인지 검사하고 아니면 -EINVAL입니다. 두 끝점만 검사하므로 내부 모든 페이지의 연속 RAM 여부를 증명하지 않으며 주소+크기 산술의 별도 overflow 검사도 없습니다. 성공 시 __va 주소와 크기를 출력합니다.'),
        ('현재 IMA 버퍼 반환', 'ima_free_kexec_buffer는 live property를 찾아 파싱하고 of_remove_property가 성공한 뒤 memblock_free_late(addr,size)를 호출합니다. 단순히 새 FDT의 예약 표에서 항목을 지우는 동작과 다릅니다. 속성 부재나 파싱·삭제 오류이면 메모리 반환 단계로 진행하지 않습니다.'),
        ('복제본에서 옛 IMA 제거', 'remove_ima_buffer는 HAVE_IMA_KEXEC 비활성이면 아무 작업도 하지 않습니다. 속성이 있으면 파싱을 시도한 뒤 성공 여부와 관계없이 fdt_delprop을 호출하며 삭제 반환값은 검사하지 않습니다. 파싱 성공일 때만 정확한 주소·크기 예약 삭제를 시도하고 성공 시 debug 로그를 남깁니다. void helper이므로 제거 오류를 호출자에게 직접 전달하지 않습니다.'),
        ('새 IMA 설정', 'IMA_KEXEC이면 image의 크기가 0일 때 성공 no-op입니다. 아니면 fdt_appendprop_addrrange로 주소·크기를 기록하고 예약 항목을 추가합니다. 두 단계의 오류는 -EINVAL로 바꿉니다. 비활성 stub은 0입니다. HAVE_IMA_KEXEC의 이전 버퍼 처리와 IMA_KEXEC의 새 버퍼 설정은 다른 구성 조건입니다.'),
        ('새 FDT 할당과 chosen', '공개 setup 함수는 초기 FDT 크기,cmdline 길이,0x1000,extra_fdt_size를 합쳐 kvmalloc하고 실패하면 NULL입니다. fdt_open_into로 복제·확장합니다. 기존 FDT 예약은 정확히 삭제하며 -ENOENT는 허용하고 -EINVAL은 실패합니다. /chosen이 없다는 특정 오류이면 새 노드를 만들고 그 밖의 음수 결과는 실패합니다.'),
        ('이전 crash와 initrd 정보', 'linux,elfcorehdr와 linux,usable-memory-range를 삭제하되 NOTFOUND는 허용합니다. 옛 initrd-start가 있으면 end도 요구하며 두 값의 차이를 크기로 계산합니다. 먼저 정확한 크기로 예약을 지우고 없으면 PAGE_SIZE로 올림한 크기로 다시 찾습니다. 두 번 모두 없다는 결과는 허용합니다. end가 start보다 큰지 별도로 검사하지 않습니다.'),
        ('새 initrd의 실제 분기', '새 initrd 추가 조건은 initrd_len이 아니라 initrd_load_addr가 nonzero인지입니다. start와 addr+len의 end를 u64 속성으로 설정하고 예약을 추가합니다. 주소가 0이면 두 속성을 삭제하며 NOTFOUND는 허용합니다. 이 코드에서 추가 주소·길이의 overflow나 길이 0을 별도로 거르는 분기는 없습니다.'),
        ('Crash kernel 속성', 'image type이 KEXEC_TYPE_CRASH이면 elfcorehdr 주소 범위를 추가하고 그 메모리도 예약합니다. CONFIG_CRASH_DUMP일 때 crashk_res의 포함 끝점으로부터 end-start+1 크기를 계산해 usable-memory-range에 추가합니다. crashk_low_res.end가 nonzero이면 낮은 구간도 append합니다. 정상 kexec에서 이 crash 속성을 무조건 재생성하지 않습니다.'),
        ('명령줄과 두 seed의 차이', 'cmdline이 nonNULL이면 빈 문자열이라도 bootargs로 설정하고 NULL이면 삭제합니다. kaslr-seed는 먼저 기존 값을 삭제한 뒤 RNG가 준비되었을 때만 새 u64를 기록합니다. rng-seed는 준비되면 128바이트 placeholder에 난수를 쓰지만 미준비 경로에는 기존 rng-seed 삭제가 없습니다. 따라서 omitting 로그만 보고 복제본의 오래된 rng-seed까지 반드시 없어졌다고 판단하면 안 됩니다.'),
        ('마지막 처리와 오류 수명', 'linux,booted-from-kexec를 길이 0 속성으로 설정한 뒤 옛 IMA를 제거하고 /chosen offset을 다시 찾아 새 IMA를 설정합니다. out에서 ret이 nonzero이면 kvfree하고 NULL로 반환합니다. 성공은 새 FDT 포인터이며 ERR_PTR가 아닙니다. 중간 수정 rollback 대신 실패한 복제 버퍼 전체를 회수합니다. 이 함수가 실제 kexec 재부팅을 실행하는 것은 아닙니다.'),
        ('전체 범위와 검증', '예약·cell·버퍼 파서,HAVE_IMA_KEXEC 두 함수,옛 IMA 제거,새 IMA와 stub,공개 setup의 모든 분기를 확인했습니다. 예약 삭제와 실제 메모리 해제,로그 의도와 분기 동작을 구분했습니다. 실제 재부팅·crash dump·난수·IMA 실행 검증은 하지 않았습니다.')
    ], questions=[
        ('예약 삭제 helper는 겹치는 구간도 자동 삭제하는가?', '아니다. 시작과 크기가 모두 같은 첫 항목만 삭제한다', '그렇다. 주소가 조금이라도 겹치면 모두 삭제한다', '조건은 두 값의 동등성입니다. 구간 교집합 계산은 없습니다.'),
        ('IMA 버퍼 RAM 검사는 내부 모든 페이지를 순회하는가?', '아니다. 시작과 마지막 바이트의 PFN만 검사한다', '그렇다. 전 페이지를 for문으로 검사한다', 'page_is_ram 호출은 두 끝점에 있습니다. 검증 범위를 과장하면 안 됩니다.'),
        ('공개 FDT setup 실패 반환은?', 'NULL', '항상 ERR_PTR(-EINVAL)', '할당 실패와 out의 오류 회수 모두 NULL입니다. 내부 errno와 공개 반환 형식은 다릅니다.'),
        ('새 initrd를 추가하는 직접 조건은?', 'initrd_load_addr가 0이 아닌지', 'initrd_len이 양수인지 하나만', '본문 if는 주소를 검사합니다. 문서상 권장 입력과 실제 조건을 구분합니다.'),
        ('RNG 미준비 시 기존 두 seed를 모두 명시적으로 삭제하는가?', '아니다. kaslr-seed는 삭제하지만 rng-seed에는 그 삭제 경로가 없다', '그렇다. 두 로그가 동일하므로 코드도 같다', '로그 문구보다 실제 delprop 위치를 추적해야 합니다. 복제본에 기존 값이 남을 수 있습니다.'),
        ('cmdline이 빈 문자열을 가리키는 경우와 NULL은 같은가?', '아니다. 빈 문자열은 설정하고 NULL은 속성을 삭제한다', '그렇다. 둘 다 무조건 삭제한다', '조건은 포인터 존재입니다. 문자열 길이 0과 포인터 NULL을 구분합니다.'),
        ('FDT 예약 삭제와 memblock_free_late는 같은 작업인가?', '아니다. 전자는 데이터 구조 수정,후자는 메모리 반환이다', '그렇다. FDT 항목 삭제가 언제나 실제 메모리를 즉시 반환한다', '새 커널에 전달할 기술과 현재 메모리 관리 상태를 구분해야 합니다.'),
        ('실패 중간에 수정한 새 FDT를 원본대로 한 항목씩 복원하는가?', '아니다. 실패하면 새 버퍼 전체를 kvfree한다', '그렇다. 모든 setprop의 역연산을 순서대로 실행한다', '원본 복제 후 수정이므로 임시 복제본을 버리는 회수 방식입니다. 실제 부팅은 이 함수 밖입니다.')
    ]
)]
