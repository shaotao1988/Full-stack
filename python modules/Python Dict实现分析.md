# Python dict 实现分析

## 内存布局
Dict使用hash表实现的，内部使用2个数组实现，一个entry为3，slot为8的Dict实现如下：

1. hash索引表dk_indices

    |indices数组|
    |:-|
    |EMPTY(-1)|
    |2|
    |DUMMY(-2)|
    |0|
    |EMPTY(-1)|
    |EMPTY(-1)|
    |1|
    |DUMMY(-2)|

    有三种取值：
    
    1. index    >=0，表示当前slot存放有数据，数据在dk_entries表中的索引为index
    2. EMPTY    -1，初始状态，表示当前slot还没有存放过数据
    3. DUMMY    -2，表示当前slot的值已经被删除，由于使用开放寻址解决冲突，所以不能直接设置为EMPTY

    indices 数组成员占用空间大小可随 hash 数组大小变化而变化：

    |单成员占用空间| hash表大小（必须是2的幂次）|
    |:-:         |:-:|
    |int8       |<=2\**7|
    |int16      |[2\**8, 2\**15]|
    |int32      |2\**16，2\**31]|
    |int64     | >=2\**32|

    由于EMPTY和DUMMY状态用负数表示，所以indices成员都用有符号整型表示。

2. entries数组

    保存键值对以及键的hash值信息，上面indices数组保存的就是数据在entries数组的索引。

    |键的hash值|键|值|
    |:-:|:-:|:-:|
    |24573|key1|value1|
    |45378|key2|value2|
    |27509|key3|value3|


使用几个数组存储的好处:

- 节约内存

    为防止冲突，indices数组是相对稀疏的，如果在这个数组中直接保存键的hash值以及键值对信息，大量的EMPTY和DUMMY槽会浪费很多内存

- 加速对dict的遍历

    将对indices数组的遍历改为对entries数组的遍历，因为indices数组是稀疏的，而entries数组是密集的，遍历时可减少内存访问

    另外，由于键值对在entries数组中是按插入顺序存储的，所以按entries数据遍历字典时，也会按照键值对的插入顺序遍历，自动变为有序字典。


Dict的其他信息：

- 创建Dict的初始大小：8
- 装载因子：2/3，数据超过slot的2/3后会触发扩容
- 增长率：也就是扩容后hash表的大小，为当前dict中键值对个数的3倍

常用技巧

- 以序列中的元素为 keg 生成值为空的字典

    `dict.fromkeys(seqn) #可接收额外参数做默认值`

- 计数

    ```python
    for e in seqn:
        d[e] = d.get(e, 0)+1
    ```

- 值为列表时对值进行追加，可把2次 lookup 变为1次

    ```python
    for pagenumber, page in enumerate (pages)：
        for word in page:
            d.setdefault(word,[]).append(pagenumber)
    ```

## 源码剖析

主要看一下dict在内存中是如何封装的，以及一些dict常用操作是怎么实现的，具体hash算法的细节不讨论。

### dict的创建

```c
static PyObject *
new_dict(PyDictKeysObject *keys, PyObject **values)
{
    ...
    PyDictObject *mp = PyObject_GC_New(PyDictObject, &PyDict_Type);
    mp->ma_keys = keys;
    mp->ma_values = values;
    mp->ma_used = 0;
    mp->ma_version_tag = DICT_NEXT_VERSION();
    return (PyObject *)mp;
}
```

这段代码涉及到几个对象：字典对象PyDictObject，键对象PyDictKeysObject，值对象PyObject，以及键值对PyDictKeyEntry，我们按由易到难讲解

1. PyObject

    PyObject是Python的基础数据结构，基本上Python所有数据对象的起始位置都存放着一个PyObject结构体
    ```c
    typedef struct _object {
        _PyObject_HEAD_EXTRA   # 调试用的宏
        Py_ssize_t ob_refcnt;  # 引用计数
        PyTypeObject *ob_type; # 数据类型
    } PyObject;
    ```

    创建dict时，值对象被转换为PyObject对象指针，只有当键和值分离存储(split dict)时才会传入值，大部分时候是NULL(combined dict)。

2. PyDictKeyEntry

    保存单条键值对的结构体。

    ```c
    typedef struct {
        /* me_key对应的hash值，起到缓存作用，避免每次用到的时候都计算. */
        Py_hash_t me_hash;
        PyObject *me_key;
        /* combined table有取值，如果是split table则为NULL，其value存放在PyDictObject结构中 */
        PyObject *me_value; 
    } PyDictKeyEntry;
    ```

3. PyDictKeysObject

    键对象，实际承载hash表和键值对信息，键值对PyDictKeyEntry的列表放在该结构体的末尾。

    ```c
    struct _dictkeysobject {
        /* 引用计数 */
        Py_ssize_t dk_refcnt;

        /* hash表dk_indices数组的大小，必须是2的指数次幂 */
        Py_ssize_t dk_size;

        /* hash表查找函数，有通用查找函数，也有专门针对str类型的键做了优化的查找函数 */
        dict_lookup_func dk_lookup;

        /* dk_entries的可用条目数，当删除键值对时，空间不会释放，因此dk_usable不会增加. */
        Py_ssize_t dk_usable;

        /* dk_entries已使用条目数，包括DUMMY状态的条目. */
        Py_ssize_t dk_nentries;

        /* 第一部分已经讲过，hash表dk_indices数组，保存的是键值对在entries数组中的索引 */
        char dk_indices[];  /* char is required to avoid strict aliasing. */

        /* 结构体最后面跟随的是真正的键值对信息 PyDictKeyEntry dk_entries[dk_usable];  */
    };
    ```

    dk_entries表附加在该结构体末尾，通过宏来访问dk_entries中的元素：

    ```c
    #define DK_ENTRIES(dk) \
    ((PyDictKeyEntry*)(&((int8_t*)((dk)->dk_indices))[DK_SIZE(dk) * DK_IXSIZE(dk)]))
    ```

    `DK_SIZE(dk)`是dk_indices数组的大小，`DK_IXSIZE(dk)`是dk_indices数组单个元素占用空间大小，第一部分提到有int8,int16,int32,int64这样几种，分别对应单字节、双字节、四字节、八字节大小。

    因此`dk->dk_indices[DK_SIZE(dk) * DK_IXSIZE(dk)]`实际上就是dk_indices的末尾，也就是dk_entries的开始位置了，最后通过`PyDictKeyEntry*`将地址做类型转换。

4. PyDictObject

    Python字典对外呈现的数据结构。

    ```c
    typedef struct {
        /* 封装了PyObject结构体，保存引用计数和数据类型信息 */
        PyObject_HEAD

        /* 字典中保存的条目数，不包括DUMMY元素的个数；PyDictKeysObject的dk_nentries包含DUMMY元素的个数 */
        Py_ssize_t ma_used;

        /* 字典的版本号，全局唯一，当有字典创建或被修改时设置 */
        uint64_t ma_version_tag;

        /* 字典的键信息，即上面第3个结构体 */
        PyDictKeysObject *ma_keys;

        /* 如果ma_values为空，则value跟key合并存储在ma_keys中
           否则， ma_keys中只保存键信息，不保存值信息*/
        PyObject **ma_values;
    } PyDictObject;
    ```

### dict查询

查询的逻辑比较直接，直接看代码：

```c
PyObject *
_PyDict_GetItem_KnownHash(PyObject *op, PyObject *key, Py_hash_t hash)
{
    Py_ssize_t ix;
    PyDictObject *mp = (PyDictObject *)op;
    PyObject *value;

    /* lookup函数根据hash值定位到indices数组的slot，再根据slot保存的值定位到entries数组上保存的键值对
       如果key相等，则找到了*/
    ix = (mp->ma_keys->dk_lookup)(mp, key, hash, &value);
    /*只有EMPTY或DUMMY是负数，说明字典没有这个键*/
    if (ix < 0) {
        return NULL;
    }
    return value;
}
```

我们再分析一下比较关键的lookup函数，也就是根据key的hash值查找到key，如果key不在dict中，则返回key应该存放的位置：
```c
static Py_ssize_t _Py_HOT_FUNCTION
lookdict(PyDictObject *mp, PyObject *key,
         Py_hash_t hash, PyObject **value_addr)
{
    size_t i, mask, perturb;

    PyDictKeysObject *dk = mp->ma_keys;
    PyDictKeyEntry *ep0 = DK_ENTRIES(dk);
    /* #define DK_MASK(dk) (((dk)->dk_size)-1) */
    /* 由于slot大小，也就是dk->dk_size是2的指数次幂，mask就是二进制位上全取1，比如2**8-1 */
    mask = DK_MASK(dk);
    /* 下面取i的操作只取hash值的低位，相当于将hash值针对hash表大小取余，舍弃了hash值的高位 */
    /* 这里保存一下原始hash值，当冲突出现，或者探测路径上出现DUMMY值时，还可以利用原始hash值的高位再次参与二次探测，即下面for循环尾部重新计算i的过程 */
    perturb = hash;
    i = (size_t)hash & mask;

    for (;;) {
        /* 取出indices数组下标i位置存储的值，这个值为EMPTY表示slot空闲，为DUMMY表示slot上的数据已经被删除了，如果>=0则表示key对应的键值对存储在dk_entries数组中的索引 */
        Py_ssize_t ix = dictkeys_get_index(dk, i);
        if (ix == DKIX_EMPTY) {
            *value_addr = NULL;
            return ix;
        }
        /* 在indices数组中找到了，还要检查一下key是否确实是相等的，因为可能出现冲突，也就是不同的key被hash到了同一个slot上 */
        if (ix >= 0) {
            /* PyDictKeyEntry *ep0 = DK_ENTRIES(dk)，也就是entries数组的起始地址 */
            PyDictKeyEntry *ep = &ep0[ix];
            if (ep->me_key == key) {
                *value_addr = ep->me_value;
                return ix;
            }
        }
        /* 上面检查了ix为EMPTY以及ix>=0的情况，剩下的就是ix>=0但是key冲突了，或者ix为DUMMY的情况(也就是hash探测的路径上出现了被删除的键值对)，需要继续往下探测 */
        perturb >>= PERTURB_SHIFT;
        i = (i*5 + perturb + 1) & mask;
    }
    Py_UNREACHABLE();
}
```

### dict.pop

```c
PyObject *
_PyDict_Pop_KnownHash(PyObject *dict, PyObject *key, Py_hash_t hash, PyObject *deflt)
{
    /* ...省略非关键代码 */
    /* 根据hash规则，利用indices数组查找并返回key对应的键值对在entries数组中的索引 */
    ix = (mp->ma_keys->dk_lookup)(mp, key, hash, &old_value);
    /* 根据hash值找indices数组中slot的位置 */
    hashpos = lookdict_index(mp->ma_keys, hash, ix);
    /* dict大小减一 */
    mp->ma_used--;
    mp->ma_version_tag = DICT_NEXT_VERSION();
    /* 把indices数组对应位置设置为DUMMY */
    dictkeys_set_index(mp->ma_keys, hashpos, DKIX_DUMMY);
    ep = &DK_ENTRIES(mp->ma_keys)[ix];
    old_key = ep->me_key;
    /* 将字典的PyDictKeysObject结构体中保存的指定键值对信息清空 */
    ep->me_key = NULL;
    ep->me_value = NULL;
    Py_DECREF(old_key);

    return old_value;
}
```

从代码可以看到，在删除字典里的元素时，只是将PyDictObject结构中的ma_used更新，并没有更新PyDictKeysObject结构中的dk_usable(可用条目数)和dk_nentries(已用条目数)，所以这部分空间是不会实时释放的。

个人理解是因为entries是一个数组，删除数组中的元素代价比较高是O(n)，而dict.pop期望的复杂度是O(1)，而dict中的条目被删完之后就会自动被GC回收，另外当dict扩容时，会主动清理掉被删掉的条目来释放DUMMY占用空间，详细参考下面`dict赋值`部分的解析。

### dict赋值

分update和新增2种情况。

```c
static int
insertdict(PyDictObject *mp, PyObject *key, Py_hash_t hash, PyObject *value)
{
    Py_ssize_t ix = mp->ma_keys->dk_lookup(mp, key, hash, &old_value);
    /* 新增场景 */
    if (ix == DKIX_EMPTY) {
        
        if (mp->ma_keys->dk_usable <= 0) {
            /* 对entries数组扩容 */
            if (insertion_resize(mp) < 0)
                goto Fail;
        }
        /* 在indices中根据hash规则找到空槽位 */
        Py_ssize_t hashpos = find_empty_slot(mp->ma_keys, hash);
        /* 新插入的键值对放到entries的末尾 */
        ep = &DK_ENTRIES(mp->ma_keys)[mp->ma_keys->dk_nentries];
        /* 更新indices数组 */
        dictkeys_set_index(mp->ma_keys, hashpos, mp->ma_keys->dk_nentries);
        ep->me_key = key;
        ep->me_hash = hash;
        ep->me_value = value;
        mp->ma_used++;
        mp->ma_version_tag = DICT_NEXT_VERSION();
        mp->ma_keys->dk_usable--;
        mp->ma_keys->dk_nentries++;
        return 0;
    }

    /* update场景，需要先看下value是否有变化，如果没有变化就不用处理了 */
    if (old_value != value) {
        DK_ENTRIES(mp->ma_keys)[ix].me_value = value;
        mp->ma_version_tag = DICT_NEXT_VERSION();
    }

    return 0;
}
```

dict在扩容的时候，在insertion_resize中会主动清理DUMMY状态的entry以释放空间：

```c
static int
dictresize(PyDictObject *mp, Py_ssize_t minsize)
{
    ...
    /* 首先计算扩容后的hash表大小，传入参数minisize为mp->ma_used的3倍 */
    /* 找到比minisize大的最小的2的幂次方 */
    Py_ssize_t newsize;
    for (newsize = PyDict_MINSIZE;
         newsize < minsize && newsize > 0;
         newsize <<= 1)
        ;

    /* 原dict中真实的entry数 */
    numentries = mp->ma_used;
    oldkeys = mp->ma_keys;
    oldentries = DK_ENTRIES(oldkeys);
    /* 按新大小申请空间 */
    mp->ma_keys = new_keys_object(newsize);
    newentries = DK_ENTRIES(mp->ma_keys);
    /* 在dict.pop部分提到，当删除一个键值对时，只会将entries数组对应的元素设置为NULL，不会将dk_nentries减1 */
    /* 所以如果dk_nentries跟mp->ma_used相等，说明没有删除过元素，因此直接把老的键值对信息整个拷贝过来 */
    if (oldkeys->dk_nentries == numentries) {
        memcpy(newentries, oldentries, numentries * sizeof(PyDictKeyEntry));
    }
    else {
        /* 否则需要遍历字典来过滤DUMMY值 */
        PyDictKeyEntry *ep = oldentries;
        for (Py_ssize_t i = 0; i < numentries; i++) {
            /* 跳过空的键值对以节约空间，这些是已经被删掉的元素 */
            while (ep->me_value == NULL)
                ep++;
            newentries[i] = *ep++;
        }
    }
```

### dict遍历

根据dict创建部分对PyDictKeysObject结构的讲解，dict遍历的代码如下。

```c
/*d为要遍历的dict*/
i = 0
PyDictKeyEntry *entry_ptr = &DK_ENTRIES(d->ma_keys)[i];
while (i < n && entry_ptr->me_value == NULL) {
    ... do_something with entry_ptr ...
    entry_ptr++;
    i++;
}
```

实际上是直接取dk_entries中的数据，而不是从hash表dk_indices中先取下标，再去dk_entries中取数据。因为dk_indices是比较稀疏的，而dk_entries是比较密集的，只包括当前dict中的元素以及被删掉的闲置空槽位。

同时，由于dk_entries数组是按顺序添加的，因此也可以保证dict是有序的，也就是遍历的顺序跟元素插入的顺序是一致的。

## 总结

Python的dict是用hash存储的键值对信息，内部使用2个数组来实现，采用开放寻址来避免冲突，提高了内存使用效率。

参考： https://mail.python.org/pipermail/python-dev/2012-December/123028.html
