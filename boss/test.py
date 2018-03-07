a = ['城市：汉中']
print(a)
import re

r = re.findall('城市：(\w*)', str(a))[0]
print(r)