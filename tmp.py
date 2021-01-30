import numpy as np
import random as rng
import matplotlib.pyplot as plt
import seaborn as sns
import numba
import sys

# @numba.jit(nopython=True)
# def curse(n_iter):
#     n_iter = int(n_iter)
#     tries = np.zeros(n_iter)
#
#     for i in range(n_iter):
#         dc = 1
#         steps = 1
#         while steps < 4:
#             if rng.randint(1, 20) < dc:
#                 steps += 1
#                 dc = 0
#             tries[i] += 1
#             dc += 1
#     return tries
#
#
# tries = curse(1e8)
#
sns.set_style("darkgrid")


# sns.violinplot(x=tries)

# plt.show()


@numba.jit(nopython=True)
def disease(n_iter, CON=16):
    duration = np.zeros(n_iter)
    status = np.zeros(n_iter, dtype=np.int8)
    for i in range(n_iter):
        fatigue = 1
        if (i + 1) % round(n_iter / 4) == 0:
            print(round(100 / n_iter * i))
        t0 = rng.randint(1, 4)
        while fatigue > 0 or fatigue < 6:
            if fatigue < 3:
                check = rng.randint(1, 20) + int((CON - 10) / 2) >= 11
            else:
                check1 = 1 if rng.randint(1,20) + int((CON - 10) / 2) < 11 else 0
                check2 = 1 if rng.randint(1,20) + int((CON - 10) / 2) < 11 else 0
                
                check = True if check1 + check2 == 0 else False
                
                
            if check:
                fatigue -= 1
                t0 += 1
            
            else:
                fatigue += 1
                t0 += 1
            
            duration[i] = t0 - 0.5 + rng.random()
            if fatigue == 0:
                status[i] = 1
                break
            
            elif fatigue == 6:
                status[i] = -1
                break
    
    return duration, status


plt.figure(figsize=(18,10))
sns.set_context("paper")
for i in range(1, 25):
    plt.subplot(6, 4, i)
    print(i)
    duration, status = disease(n_iter=int(1e8), CON=i)
    maxduration = int(round((duration.max()+5)/10)*10)
    
    sns.violinplot(x=status, y=duration, linewidth=0.8, legend= False) # linewidth
    ded = status[status == -1].shape[0]
    alif = status[status == 1].shape[0]
    total = status.shape[0]
    plt.xticks((0, 1), ('{:.2%} Died'.format(ded / total), '{:.2%} Lived'.format(alif / total)))
    plt.ylim(bottom=0)
    plt.yticks(tuple(range(0,maxduration,10)))
    plt.title("Score de Constitution de {} ".format(i))
    sns.despine(offset=0, trim=True)
plt.suptitle('Répartition de la durée d\'une infection à la "Peste des égouts" en fonction de sa finalité et de la '
             'valeur '
             "de Constitution du malade")
plt.tight_layout(h_pad=1, w_pad=1)
plt.show()

plt.figure(figsize=(18,10))
duration, status = disease(n_iter=int(1e8), CON=16)
sns.violinplot(x=status, y=duration, linewidth=0.8, legend= False) # linewidth
ded = status[status == -1].shape[0]
alif = status[status == 1].shape[0]
total = status.shape[0]
plt.yticks(tuple(range(0,maxduration,10)))
plt.xticks((0, 1), ('{:.2%} Died'.format(ded / total), '{:.2%} Lived'.format(alif / total)))
plt.ylim(bottom=0)
sns.despine(offset=0, trim=True)
plt.suptitle('Répartition de la durée d\'une infection à la "Peste des égouts" en fonction de sa finalité pour un '
             "score de Constitution de 16")
plt.tight_layout()
plt.show()