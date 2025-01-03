# test_num = eval(input())
# pass_number = 0
# for _ in range(test_num):
#     teacher_num = eval(input())
#     teacher_full = input().split()
#     answer_full = input().split()
#     score = 0
#     for it in range(teacher_num):
#         if answer_full[it] == teacher_full[it]:
#             score += 1
#         else:
#             score -= 1
#         if score < 0:
#             break
#     if score >= 0:
#         pass_number += 1
# print(f"通过次数为:{pass_number}")


enemy_num = eval(input("敌人数量:"))
enemy_xue = input("每个敌人血量:")
enemy_xue_lt = enemy_xue.split()
enemy_xue_lt = list(map(int, enemy_xue_lt))
enemy_xue_half_lt = []
use_number = 0
for i in enemy_xue_lt:
    enemy_xue_half_lt.append(int(i/2))
enemy_xue_half_status_lt = [False] * len(enemy_xue_lt)
status = True
tf_count = 0
while status:
    for it in range(len(enemy_xue_lt)):
        if enemy_xue_lt[it] <= 0 or (enemy_xue_lt[it] == 1 and tf_count < len(enemy_xue_lt)):
            continue
        use_number += 1
        if enemy_xue_lt[it] > 0:
            enemy_xue_lt[it] -= 1
            print(f"对[{it+1}]号敌人造成1点伤害")
        if enemy_xue_lt[it] <= enemy_xue_half_lt[it] and not enemy_xue_half_status_lt[it]:
            enemy_xue_lt = [max(0, x - 1) for x in enemy_xue_lt]
            tf_count += 1
            enemy_xue_half_status_lt[it] = True
            print(f"触发天赋，对所有敌人造成一点伤害!")
        print(f"第[{use_number}]次攻击！,剩余敌人血量[{enemy_xue_lt}]")
        print("===="*20)
        if all(x <= 0 for x in enemy_xue_lt):
            print(f"攻击结束,使用了[{use_number}]次攻击结束战斗")
            status = False