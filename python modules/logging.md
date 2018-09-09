# python日志模块

## 日志级别

可以通过API设置允许的最低日志级别，只有该级别或以上的日志才会被处理，默认级别为WARNIGN。日志级别由低到高一次为：
- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

## 基本参数设置

通过basicConfig方法初始化日志模块的基本参数，比如日志保存路径，日志级别，日志格式等， 必须在调用日志接口(debug, info, warning等)前初始化，否则是空操作。
```python
import logging

def Initialize_log(filename, level, format):
    # 对level参数做校验，如果参数设置不正确，就使用DEBUG级别
    level = getattr(logging, level.upper(), logging.DEBUG)
    logging.basicConfig(filename = filename, level = level, format = format)
```

### 日志格式

格式选项如下：

    %(name)s            Name of the logger (logging channel)
    %(levelno)s         Numeric logging level for the message (DEBUG, INFO,
                        WARNING, ERROR, CRITICAL)
    %(levelname)s       Text logging level for the message ("DEBUG", "INFO",
                        "WARNING", "ERROR", "CRITICAL")
    %(pathname)s        Full pathname of the source file where the logging
                        call was issued (if available)
    %(filename)s        Filename portion of pathname
    %(module)s          Module (name portion of filename)
    %(lineno)d          Source line number where the logging call was issued
                        (if available)
    %(funcName)s        Function name
    %(created)f         Time when the LogRecord was created (time.time()
                        return value)
    %(asctime)s         Textual time when the LogRecord was created
    %(msecs)d           Millisecond portion of the creation time
    %(relativeCreated)d Time in milliseconds when the LogRecord was created,
                        relative to the time the logging module was loaded
                        (typically at application startup time)
    %(thread)d          Thread ID (if available)
    %(threadName)s      Thread name (if available)
    %(process)d         Process ID (if available)
    %(message)s         The result of record.getMessage(), computed just as
                        the record is emitted

如下的format字符串的格式：日志时间-级别-文件路径-行号-消息内容。注意如果format字符串是从配置文件中读取的话，需要使用2个%符号转义。

    format = "%(asctime)s - %(levelname)s - %(pathname)s - %(lineno)d - %(message)s"
    '''
    2018-09-08 15:07:28,638 - INFO - /Users/victor/Documents/miniURL/util/logger.py - 32 - Adding stream handler to logger
    '''

## 日志模块内部组成

日志有如下几个部分组成：
1. Logger
   
   对外接口，应用程序直接调用这些接口进行参数配置、记录日志。使用logger = logging.getLogger(__name__)获取Logger对象
   - Logger.setLevel() 设置最低的日志级别
   - Logger.addHandler()和Logger.removeHandler() 添加和删除handler
   - Logger.addFilter()和Logger.removeFilter() 添加和删除filter
   - Logger.debug()|info()|warning()|error()|critical() 日志记录接口

2. Handlers
   
    将日志记录发送到目的地，可以将不同级别的日志发送到不同的文件、显示到终端、或者发送电子邮件  
    最常用的2个handlers是logging.StreamHandler和logging.FileHandler  
   - StreamHandler将日志发送到sys.stdout, sys.stderr或任何支持write()和flush()的file-like对象上
   - FileHandler将日志记录到磁盘文件上，它继承自StreamHandler
  
    Handler有3中方法，分别是setLevel()设置日志级别，setFormatter()设置日志格式，addFilter()和removeFilter()配置过滤器  
    Logger的setLevel用于设置日志模块处理的最低级别，而Handler的setLevel用于设置本handler处理的最低日志级别，所以一条日志可能被多个handler处理，被保存到多个不同的文件

3. Filters：日志过滤，根据需要将特定的日志过滤

4. Formatter
   决定日志记录的格式
    ```python
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(pathname)s - %(lineno)d - %(message)s")
    handler.setFormatter(formatter)
    ```

## 配置示例

配置日志模块，将日志保存到磁盘文件，记录所有日志

我们可以通过2种方法配置，第一种是logging.basicConfig，第二种是自己添加Handler和Formatter

1. 如果只有一种handler，可以直接通过logging.basicConfig配置
```python
import logging

# 如果在basicConfig中传入了filename和format参数，会自动生成FileHander和Formatter并注册到Logger
logging.basicConfig(filename = "all.log", level = logging.DEBUG, format = "%(asctime)s - %(levelname)s - %(pathname)s - %(lineno)d - %(message)s")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.debug('debug info')
logger.error('error info')
```

2. 如果需要多种handler，可以通过addHandler逐个添加
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

f_handler = logging.FileHandler('all.log')
f_handler.setLevel(logging.DEBUG)
f_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(pathname)s - %(lineno)d - %(message)s")
f_handler.setFormatter(f_formatter)

logger.addHandler(f_handler)

logger.debug('debug info')
logger.error('error info')
```

2种配置输出的日志信息除了行号外都是一样的：

2018-09-09 00:18:32,351 - DEBUG - logger.py - 13 - debug info  
2018-09-09 00:18:32,351 - ERROR - logger.py - 14 - error info
