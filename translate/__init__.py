# -*- coding:utf-8 -*-
import re
import os
import sys
import random
import logging
import requests
import traceback

from functools import partial
from argparse import ArgumentParser
from abc import ABC, abstractmethod

from . import sites
from .tools import retry_wrapper


__version__ = "1.2.2"


class TranslateAdapter(ABC):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/41.0.2272.76 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        "Accept-Language": "en-US,en;q=0.5",
    }

    def __init__(self):
        self.proxy = {}
        self.load(sites)

    @property
    @abstractmethod
    def web_site(self):
        pass

    @property
    @abstractmethod
    def translate_timeout(self):
        pass

    @property
    @abstractmethod
    def retry_times(self):
        pass

    def __enter__(self):
        self.session = requests.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def set_logger(self, logger=None):
        if not logger:
            self.logger = logging.getLogger()
            self.logger.setLevel(20)
            self.logger.addHandler(logging.StreamHandler(sys.stdout))
        else:
            self.logger = logger
            self.name = logger.name

    def load(self, module_str):
        if isinstance(module_str, str):
            sys.path.insert(0, os.getcwd())
            model = __import__(module_str, fromlist=module_str.split(".")[-1])
        else:
            model = module_str

        for k in dir(model):
            v = getattr(model, k)
            if hasattr(v, "__call__"):
                self.__dict__[k] = partial(v, self)

    @abstractmethod
    def proxy_choice(self):
        pass

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
        self.logger.debug("Error in %s for retry %s times. Error: %s"%(func_name, retry_time, e))
        proxies = self.proxy_choice()
        if proxies:
            args[1].update(proxies)

    def translate(self, src):
        """
        翻译主函数
        :param src: 源
        :return: 结果
        """
        try:
            # 找出大于号和小于号之间的字符，使用换行符连接，进行翻译
            pattern = re.compile(r"(?:^|(?<=>))([\s\S]*?)(?:(?=<)|$)")
            ls = re.findall(pattern, src.replace("\n", ""))
            src_data = "\n".join(x.strip("\t ") for x in ls if x.strip())
            if src_data.strip():
                # 对源中的%号进行转义
                src_escape = src.replace("%", "%%")
                # 将源中被抽离进行翻译的部分替换成`%s`， 如果被抽离部分没有实质内容（为空），则省略
                src_template = re.sub(pattern, lambda x: "%s" if x.group(1).strip() else "", src_escape)
                return retry_wrapper(self.retry_times, self.trans_error_handler)(
                    self._translate)(src_data, self.proxy or self.proxy_choice()
                                     or self.proxy, src_template)
        except Exception:
            self.logger.error("Error in translate, finally, we could not get the translate result. src: %s, Error:  %s"%(
                src, traceback.format_exc()))
        return src

    def _translate(self, src, proxies, src_template):
        return getattr(self, random.choice(self.web_site).strip())(src, proxies, src_template)


class Translate(TranslateAdapter):
    """
        翻译类
    """
    proxy_list = [None]
    web_site = None
    retry_times = None
    translate_timeout = None

    def __init__(self, web_site="baidu,google,qq", proxy_list=None, proxy_auth=None,
                 retry_times=10, translate_timeout=5, load_module=None):
        self.web_site = web_site.split(",")
        self.proxy = {}
        self.proxy_auth = proxy_auth
        self.retry_times = retry_times
        self.translate_timeout = translate_timeout

        if proxy_list and os.path.exists(proxy_list):
            self.proxy_list = [i.strip() for i in open(proxy_list).readlines() if (i.strip() and i.strip()[0] != "#")]
        if load_module:
            self.load(load_module)
        super(Translate, self).__init__()

    def proxy_choice(self):
        return self.proxy_list and self.proxy_list[0] and {"http": "http://%s%s"%(
            "%s@"%self.proxy_auth if self.proxy_auth else "", random.choice(self.proxy_list))}


def main():
    parser = ArgumentParser()
    parser.add_argument("-ws", "--web-site", default="baidu,qq,google",
                        help="Which site do you want to use for translating, split by `,`?")
    parser.add_argument("-pl", "--proxy-list",
                        help="The proxy.list contains proxy to use for translating. default: ./proxy.list")
    parser.add_argument("-pa", "--proxy-auth",
                        help="Proxy password if have. eg. user:password")
    parser.add_argument("-rt", "--retry-times", type=int, default=10,
                        help="If translate failed retry times. default: 10")
    parser.add_argument("-tt", "--translate-timeout", type=int, default=5, help="Translate timeout. default: 5")
    parser.add_argument("-lm", "--load-module",
                        help="The module contains custom web site functions which may use for translate. eg: trans.qq")
    parser.add_argument("src", nargs="+", help="The html you want to translate. ")
    data = vars(parser.parse_args())
    src = data.pop("src")
    with Translate(**dict(filter(lambda x: x[1], data.items()))) as translator:
        translator.set_logger()
        print(translator.translate(" ".join(src)))


if __name__ == "__main__":
    main()