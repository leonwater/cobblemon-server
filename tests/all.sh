#!/usr/bin/env bash
# 테스트 2개(데이터팩·모드)를 동시에 돌림 (포트가 달라 겹치지 않음). 둘 다 통과해야 0.
cd "$(dirname "$0")"
L=${TEST_LOGS:-/tmp/pokeserver-tests}; mkdir -p $L
start=$(date +%s)
./run.sh > $L/run.out 2>&1 & a=$!
./mod-test.sh > $L/mod.out 2>&1 & b=$!
wait $a; ra=$?; wait $b; rb=$?
echo "데이터팩 테스트: $( [ $ra = 0 ] && echo 통과 || echo "실패 → $(grep -m1 FAIL $L/run.out)")"
echo "모드 테스트:     $( [ $rb = 0 ] && echo 통과 || echo "실패 → $(grep -m1 FAIL $L/mod.out)")"
echo "걸린 시간: $(( $(date +%s) - start ))초  (로그: $L)"
[ $ra = 0 ] && [ $rb = 0 ]
