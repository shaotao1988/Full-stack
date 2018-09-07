# 简介

魔术方法是python中名字以双下划线开始和结尾的方法，是语言内置的实现某些特殊功能的机制。

# 构造和初始化

当生成一个对象时，首先会调用__new__(cls, ...)方法返回对象的实例，然后调用__init__(self, ...)并传入之前创建好的实例作为它的第一个参数（__init__没有返回值），...是生成对象时传递的参数。

注意子类不会自动调用父类的__init__方法，除非自己在子类中显式调用。

```python
# 单例必须在__new__中实现，因为调用__init__时新的实例已经创建好了
class Singleton(object):
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class MyClass():
    
    def __new__(cls, *args, **kwargs):
        print("__new__ in MyClass")
        return super().__new__(cls, *args, **kwargs)
    
    def __init__(self, *args, **kwargs):
        print("__init__ in MyClass")
        
        
class MySubClass(MyClass):
    
    def __new__(cls, *args, **kwargs):
        print("__new__ in MySubClass")
        return super().__new__(cls, *args, **kwargs)
    
    def __init__(self, *args, **kwargs):
        print("__init__ in MySubClass")
        super().__init__(self, *args, **kwargs)
        
MySubClass()
# Outputs:
'''
__new__ in MySubClass
__new__ in MyClass
__init__ in MySubClass
__init__ in MyClass
__init__ finished in MySubClass
'''
```

# 运算符重载

Python中可以使用魔术方法实现C++中的运算符重载功能。

1. 比较
```python
# 如果比较的规则是一致的，可以使用cmp方法避免重复，如果规则不一致，建议分别实现
__cmp__(self, other)
# ==
__eq__(self, other)
# !=
__ne__(self, other)
# <
__lt__(self, other)
# >
__gt__(self, other)
# <=
__le__(self, other)
# >=
__ge__(self, other)

```

2. 数字运算符

```python
__add__(self, other)
__sub__(self, other)
__mul__(self, other)
__div__(self, other)
__floordiv__(self, other)
__mod__(self, other)
# +instance
__pos__(self)
# -instance
__neg__(self)
# abs
__abs__(self)
# 取反
__invert__(self)
# 取整到
__round__(self, n)
# floor
__floor__(self)
# ceil
__ceil__(self)
```

3. 类型转换

```python
__int__(self)
__long__(self)
__float__(self)
__oct__(self)
__hex__(self)
```

# Representing classes

```python
__str__(self)
__repr__(self)
```

# 控制属性访问
```python
# 只有当访问的属性没有定义时，才会调用到这个方法
__getattr__(self, name)
__setattr__(self, name, value)
__delattr__(self, name)

def __setattr(self, name, value):
    # self.name = value 
    # 造成死循环，因为变量被设置时，调用的就是__setattr__方法
    self.__dict__[name] = value
    # 其它自定义行为
```

# 实现自定义容器

```python
# 返回容器内成员的长度
__len__(self)
# self[key]
__getitem__(self, key)
# self[key] = value
__setitem__(self, key, value)
# del self[key]
__delitem__(self, key)
# for x in container时调用，必须返回self
__iter__(self)
# in或not in时调用
__contains__(self, item)
```

# 可调用的对象
```python
# x()
__call__(self, *args)
```

# 上下文管理器

上下文管理器负责为with语句中的对象完成setup和cleanup的动作，分别由__enter__和__exit__完成
```python
class Manager():
    
    def __init__(self, obj):
        self.obj = obj
    
    def __enter__(self):
        print('enter')
        return self.obj
    
    def __exit__(self, exception_type, exception_val, trace):
        print('exit')
        try:
            self.obj.close()
        except AttributeError:
            print('not closable')
        finally:
            return True

i = 5
        
with Manager(i):
    print('i is {}'.format(i))

# outputs
'''
enter
i is 5
exit
not closable
'''    
```
