# -*- coding:utf-8 -*-
import re
import os
import sys
import json
import random
import requests
import traceback

from functools import wraps, partial
from argparse import ArgumentParser


def retry_wrapper(retry_times, error_handler=None):
    """
    重试装饰器
    :param retry_times: 重试次数
    :param error_handler: 重试异常处理函数
    :return:
    """
    def out_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            count = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    count += 1
                    if error_handler:
                        result = error_handler(func.__name__, count, e, *args, **kwargs)
                        if result:
                            count -= 1
                    if count >= retry_times:
                        raise
        return wrapper

    return out_wrapper


class Translate:
    """
        翻译类
    """
    proxy_list = [None]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        "Accept-Language": "en-US,en;q=0.5",
    }

    def __init__(self, proxy_list="./proxy.list", web_site="youdao,baidu", proxy_auth=None, retry_times=10, translate_timeout=5, load_module=None):
        self.web_site = web_site.split(",")
        self.proxy = {}
        self.site_index = 0
        self.proxy_auth = proxy_auth
        self.retry_times = retry_times
        self.translate_timeout = translate_timeout
        self.site_func = dict()

        if os.path.exists(proxy_list):
            self.proxy_list = [i.strip() for i in open(proxy_list).readlines() if (i.strip() and i.strip()[0] != "#")]

        if load_module:
            sys.path.insert(0, os.getcwd())
            attr = vars(__import__(load_module, fromlist=load_module))

            for k, v in attr.items():
                if hasattr(v, "__call__"):
                    self.site_func[k] = v

    def __getattr__(self, item):

        if item in self.site_func:
            return partial(self.site_func[item], self=self)
        raise AttributeError(item)

    def proxy_choice(self):
        """
        顺序循环选取代理
        :return: 代理
        """
        proxy = random.choice(self.proxy_list)

        if proxy:
            if self.proxy_auth:
                return {"http": "http://%s@%s" % (self.proxy_auth, proxy)}
            else:
                return {"http": "http://%s"%proxy}

    def trans_error_handler(self, func_name, retry_time, e, *args, **kwargs):
        """
        error_handler实现参数
        :param func_name: 重试函数的名字
        :param retry_time: 重试到了第几次
        :param e: 需要重试的异常
        :param args: 重试参数的参数
        :param kwargs: 重试参数的参数
        :return: 当返回True时，该异常不会计入重试次数
        """
        print("Error in %s for retry %s times. "
                              "Error: %s"%(func_name, retry_time, e))
        # 更新代理Ip
        args[1].update(self.proxy_choice())

    def site_choice(self):
        """
        顺序循环选择翻译网站
        :return: site
        """
        self.site_index += 1
        return self.web_site[self.site_index%len(self.web_site)]

    def translate(self, src):
        """
        翻译主函数
        :param src: 源
        :return: 结果
        """
        try:
            # 找出大于号和小于号之间的字符，使用换行符连接，进行翻译
            pattern = re.compile(r"(^|>)([\s\S]*?)(<|$)")
            ls = re.findall(pattern, src.replace("\n", ""))
            src_data = "\n".join(x[1] for x in ls if x[1].strip())
            if src_data.strip():
                # 对源中的%号进行转义
                src = src.replace("%", "%%")
                # 将源中被抽离进行翻译的部分替换成`%s`， 如果被抽离部分没有实质内容（为空），则省略
                src_template = re.sub(pattern, lambda x: "%s%s%s"%(
                    x.group(1), "%s" if x.group(2).strip() else "", x.group(3)), src)
                return retry_wrapper(self.retry_times, self.trans_error_handler)(
                    self._translate)(src_data, self.proxy or self.proxy_choice(), src_template)
            else:
                return src
        except Exception:
            print("Error in translate, finally, we could not get the translate result. src: %s, Error:  %s"%(
                src, traceback.format_exc()))
            return ""

    def _translate(self, src, proxies, src_template):
        return getattr(self, self.site_choice().strip())(
            src, proxies, src_template)

    def youdao(self, src_data, proxies, src_template):
        """
        有道翻译的实现
        :param src_data: 原生数据
        :param proxies: 代理
        :param src_template: 原生数据模板
        :return: 结果
        """
        url = "http://fanyi.youdao.com/translate"
        resp = requests.post(url=url, data={
            'keyfrom': 'fanyi.web',
            'i': src_data,
            'doctype': 'json',
            'action': 'FY_BY_CLICKBUTTON',
            'ue': 'UTF-8',
            'xmlVersion': '1.8',
            'type': 'AUTO',
            'typoResult': 'true'}, headers=self.headers,
                             timeout=self.translate_timeout, proxies=proxies)
        return src_template % tuple(map(lambda y: "".join(
            map(lambda x: x["tgt"], y)), json.loads(resp.text)["translateResult"]))

    def baidu(self, src_data, proxies, src_template):
        """
        百度翻译的实现, 百度翻译最长只能翻译5000个字符
        :param src_data: 原生数据
        :param proxies: 代理
        :param src_template: 原生数据模板
        :return: 结果
        """
        url = "http://fanyi.baidu.com/v2transapi"
        resp = requests.post(url=url, data={
            'from': 'en',
            'to': 'zh',
            'transtype': 'realtime',
            'query': src_data,
            'simple_means_flag': 3}, headers=self.headers,
                             timeout=self.translate_timeout, proxies=proxies)
        return src_template % tuple(
            "".join(map(lambda x: x["src_str"], json.loads(resp.text)["trans_result"]['phonetic'])).split("\n"))

    @classmethod
    def parse_args(cls):
        parser = ArgumentParser()
        parser.add_argument("-ws", "--web-site", help="Which site do you want to use for translating, split by `,`? default: baidu,youdao")
        parser.add_argument("-pl", "--proxy-list", help="The proxy.list contains proxy to use for translating. default: ./proxy.list")
        parser.add_argument("-pa", "--proxy-auth", help="Proxy password if have. eg. user:password")
        parser.add_argument("-rt", "--retry-times", type=int, default=10, help="If translate failed retry times. default: 10")
        parser.add_argument("-tt", "--translate-timeout", type=int, default=5, help="Translate timeout. default: 5")
        parser.add_argument("-lm", "--load-module", help="The module contains custom web site functions which may use for translating. eg: trans.google")
        parser.add_argument("src", help="The html you want to translate. ")
        data = vars(parser.parse_args())
        src = data.pop("src")
        return cls(**dict(filter(lambda x: x[1], data.items()))).translate(src)


def main():
    print(Translate.parse_args())


if __name__ == "__main__":
    main()