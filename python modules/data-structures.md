# 枚举

```python
import enum

class Color(enum.Enum):
    BLUE = 1
    RED = 2
    GREEN = 3
    BLACK = 4
    WHITE = 5

print('{:5}: {}'.format(Color.BLUE.name, Color.BLUE.value))
print('{:5}: {}'.format(Color.RED.name, Color.RED.value))

'''
BLUE : 1
RED  : 2
'''

for color in Color:
    print('{:5}: {}'.format(color.name, color.value))

'''
BLUE : 1
RED  : 2
GREEN: 3
BLACK: 4
WHITE: 5
'''
```

Enum只支持identity和equality比较，不支持排序（大于、小于）
如果要支持排序，可以用IntEnum类

```python
green = Color.GREEN
print('green is Color.GREEN:', green is Color.GREEN)
print('green == Color.GREEN:', green == Color.GREEN)

'''
green is Color.GREEN: True
green == Color.GREEN: True
'''
```

也可以直接通过Enum类的构造函数来定义枚举类
```python
Color = enum.Enum(value = 'Color', names = ('BLUE, RED, GREEN, BLACK, WHITE'))
for color in Color:
    print('{:5}: {}'.format(color.name, color.value))

'''
BLUE : 1
RED  : 2
GREEN: 3
BLACK: 4
WHITE: 5
'''
```

# 集合

包含一些除了list, dict和tuple以外的内置类型

## ChainMap

将多个dict前后相接组合成一个大dict，按加入的顺序排列
```python
import collections

a = {'a': 'A', 'c': 'C'}
b = {'b': 'B', 'c': 'D'}
m = collections.ChainMap(a, b)

print(m['a'], m['b'], m['c'])
print('Keys={}'.format(list(m.keys())))
print('Values={}'.format(list(m.values())))

'''
A B C
Keys=['b', 'a', 'c']
Values=['B', 'A', 'C']
'''
```
内部实际上是把这些dict保存在一个list中，并且是以引用的方式保存的，所以修改a、b中的元素，会反应到m当中去，修改m也会反应到a、b中去
```python
print(m.maps)
'''
[{'a': 'A', 'c': 'C'}, {'b': 'B', 'c': 'D'}]
'''

m['c'] = 'E' #只有a中的'c'被修改
print(m.maps)
print(a)
print(b)
'''
[{'a': 'A', 'c': 'E'}, {'b': 'B', 'c': 'D'}]
{'a': 'A', 'c': 'E'}
{'b': 'B', 'c': 'D'}
'''
```
ChainMap也提供了不修改原始数据的方法new_child，赋值时会在已有的dict前面插入一个新的dict：
```python
m2 = m.new_child()
print(m2)
m2['c'] = 'F'
print(m2)
print(a)
print(b)
'''
ChainMap({}, {'a': 'A', 'c': 'E'}, {'b': 'B', 'c': 'D'})
ChainMap({'c': 'F'}, {'a': 'A', 'c': 'E'}, {'b': 'B', 'c': 'D'})
{'a': 'A', 'c': 'E'}
{'b': 'B', 'c': 'D'}
'''
```
