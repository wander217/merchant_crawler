import random
import string

N = 10
password: str = ''.join(random.choices(string.ascii_letters + string.digits, k=N))
print(password)
