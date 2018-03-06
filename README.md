# 超简单超好用的外语转中文翻译程序
适合翻译html，其中html标签不会被翻译，仅翻译标签之间的有效字符
## 结构图
![](https://github.com/ShichaoMa/translate_html/blob/master/translator.jpg)
## INSTALL
```
pip install translate-html

madeMac-mini:toolkit mashichao$ translate -ws bing "what a fuck day it is."
真是该死的一天
madeMac-mini:toolkit mashichao$ translate -ws google "what a fuck day it is."
什么是他妈的一天。
madeMac-mini:toolkit mashichao$ translate -ws qq "what a fuck day it is."
今天真是个该死的日子。
madeMac-mini:toolkit mashichao$ translate -ws baidu "what a fuck day it is."
他妈的是多么糟糕的一天。
```

## USAGE
```
usage: translate.py [-h] [-ws WEB_SITE] [-pl PROXY_LIST] [-pa PROXY_AUTH]
                    [-rt RETRY_TIMES] [-tt TRANSLATE_TIMEOUT]
                    [-lm LOAD_MODULE]
                    src

positional arguments:
  src                   The html you want to translate.

optional arguments:
  -h, --help            show this help message and exit
  -ws WEB_SITE, --web-site WEB_SITE
                        Which site do you want to use for translating, split
                        by `,`? default: baidu,youdao
  -pl PROXY_LIST, --proxy-list PROXY_LIST
                        The proxy.list contains proxy to use for translate.
                        default: ./proxy.list
  -pa PROXY_AUTH, --proxy-auth PROXY_AUTH
                        Proxy password if have. eg. user:password
  -rt RETRY_TIMES, --retry-times RETRY_TIMES
                        If translate failed retry times. default: 10
  -tt TRANSLATE_TIMEOUT, --translate-timeout TRANSLATE_TIMEOUT
                        Translate timeout. default: 5
  -lm LOAD_MODULE, --load-module LOAD_MODULE
                        The module contains custom web site functions which
                        may translate. eg: trans.google
```

## HELLOWORLD
### demo1
直接翻译
```
ubuntu@dev:~/myprojects/translate_html$ translate my
我的
ubuntu@dev:~/myprojects/translate_html$ translate "<div>my</div><table name='this is a name' style='width: 100px;color: blue'>The style property inside the tag  won't be translate</table>"
<div>我的</div><table name='this is a name' style='width: 100px;color: blue'>标签内的样式属性不会被翻译</table>
```
### demo2
自定义翻译函数
```
vi functions.py

# -*- coding:utf-8 -*-

def custom_translate(self, src_data, proxies, src_template):
    """
    :param src_data: 原生数据
    :param proxies: 代理
    :param src_template: 原生数据模板
    :return: 结果
    """
    return "仅用来测试，无论翻译什么都是这句话"

ubuntu@dev:~/myprojects/translate_html$ translate -lm functions -ws custom_translate name
仅用来测试，无论翻译什么都是这句话
```
### demo3
使用代理进行翻译
```
ubuntu@dev:~/myprojects/translate_html$ translate -pl proxy_list -pa xxxx:xxxxxxxxx name
名称
```
### demo4
在python代码中使用翻译
```
In [1]: from translate import Translate

In [2]: with Translate("google") as t:
   ...:     print(t.translate("my"))
   ...:
我的

In [3]: data = """</code></pre>
   ...: <h2 id="Installing-and-running-from-PyPI">Installing and running from PyPI</h2>
   ...: <p>You can install httpbin as a library from PyPI and run it as a WSGI app.  For example, using Gunicorn:</p>
   ...: <pre><code class="bash">$ pip install httpbin
   ...: $ gunicorn httpbin:app
   ...: </code></pre>
   ...: <h2 id="Changelog">Changelog</h2>
   ...: <ul>
   ...: <li>0.2.0: Added an XML endpoint.  Also fixes several bugs with unicode, CORS headers, digest auth, and more.</li>
   ...: <li>0.1.2: Fix a couple Python3 bugs with the random byte endpoints, fix a bug when uploading files without a Content-Type header set.</li>
   ...: <li>0.1.1: Added templates as data in setup.py</li>
   ...: <li>0.1.0: Added python3 support and (re)publish on PyPI</li>
   ...: </ul>
   ...: <h2 id="AUTHOR">AUTHOR</h2>
   ...: """

In [4]: with Translate("baidu") as t:
   ...:     print(t.translate(data))
   ...:
</code></pre><h2 id="Installing-and-running-from-PyPI">安装和运行从PyPI</h2><p>你可以安装httpbin从PyPI图书馆作为一个WSGI应用程序运行。例如，使用gunicorn：</p><pre><code class="bash">美元httpbin pip安装gunicorn美元httpbin：APP</code></pre><h2 id="Changelog">更新日志</h2><ul><li>0.2.0：添加一个XML端点。还修复了几个bug Unicode，CORS的标题，摘要认证，更。</li><li>2：与随机字节端点解决两Python3的bug，修复了一个bug，当上传文件没有内容类型标头设置。</li><li>0.1.1：添加模板作为数据在setup.py</li><li>0.1.0：添加Python3支持和（再）发布在PyPI</li></ul><h2 id="AUTHOR">作者</h2>

In [5]: with Translate(web_site="custom_translate", load_module="translate.functions") as t:
   ...:     print(t.translate(data))
   ...:
   ...:
仅用来测试，无论翻译什么都是这句话
```

