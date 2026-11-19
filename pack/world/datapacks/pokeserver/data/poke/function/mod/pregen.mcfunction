# 야생 첫 스폰 후보(1920,2176 / 2176,1920 둘레) 지형을 서버가 처음 켜질 때 미리 만들어 둠 (Chunky가 조금씩, 렉 없이)
# → 처음 야생에 들어갈 때 그 자리에서 지형을 한꺼번에 만드느라 서버가 멈추는 일이 없음. 서버를 꺼도 다음에 이어서 함.
chunky world poke:wild
chunky center 2048 2048
chunky radius 384
chunky start
data modify storage poke:state pregen set value 1
