# RequestHelper

The requests helper program.

## 使用方法

```python
from web_helper import *

title = get_html(f'https://baidu.com', obey_robot=False).to_soup().find('title').text
assert title == '百度一下，你就知道'
```

## 使用代理

```python
from web_helper import *

set_global_random_proxy('ws_token')  # 设置全局代理,TOKEN 前往: https://proxy.webshare.io/subscription/ 获取
title = get_html(f'https://baidu.com', obey_robot=False).to_soup().find('title').text
assert title == '百度一下，你就知道'
```

## 设置日志级别

```python
from web_helper import *
import sys

logger.remove()
logger.add(sys.stdout, level="TRACE")

title = get_html(f'https://baidu.com', obey_robot=False).to_soup().find('title').text
assert title == '百度一下，你就知道'
```

## 安装仓库

```bash
pip install requests-helper
```