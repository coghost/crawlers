# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '2018/7/4 5:17 PM'
__description__ = '''
## 提高效率

- [python中协程](http://python.jobbole.com/87156/)
- [yield vs yield from](https://blog.csdn.net/u010161379/article/details/51645264)
- [yield/send到yield from再到async/await](https://blog.csdn.net/soonfly/article/details/78361819)
- [GIL](https://www.cnblogs.com/stubborn412/p/4033651.html)

## 步骤

1. 多线程, 手动实现线程池
2. 多进程, 进程池
3. asyncio
4. aiohttp
5. celery
 
'''

import os
import sys

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

if __name__ == '__main__':
    pass
