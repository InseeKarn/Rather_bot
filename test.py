import random

num_ran = random.uniform(0.0, 100)

print(round(num_ran, 2), round(100.0 - round(num_ran, 2), 2))