# -*- coding:utf-8 -*-
import os
import random

from argparse import ArgumentParser
from toolkit.translator.translate_adapter import TranslateAdapter

__version__ = "1.2.4"


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
    parser.add_argument("-ws", "--web-site", default="baidu,qq,google,bing",
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
