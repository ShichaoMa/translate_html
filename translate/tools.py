import re
import ast
import math
import time
import ctypes
import requests


def merge_conflict(src_template, returns):
    return src_template % tuple(returns[:src_template.count("%s")]) + "。".join(returns[src_template.count("%s"):])


def retry_wrapper(retry_times, error_handler=None):
    """
    重试装饰器
    :param retry_times: 重试次数
    :param error_handler: 重试异常处理函数
    :return:
    """
    def out_wrapper(func):
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


def int_overflow(val):
    maxint = 2147483647
    if not -maxint-1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val


def unsigned_right_shitf(n, i):
    # 数字小于0，则转为32位无符号uint
    if n<0:
        n = ctypes.c_uint32(n).value
    # 正常位移位数是为正数，但是为了兼容js之类的，负数就右移变成左移好了
    if i<0:
        return -int_overflow(n << abs(i))
    #print(n)
    return int_overflow(n >> i)


def n(r, o):
    for t in range(0, len(o) - 2, 3):
        a = o[t + 2]
        a = ord(a) - 87 if a >= "a" else int(a)
        a = unsigned_right_shitf(r, a) if "+" == o[t + 1] else r << a
        r = r + a & 4294967295 if "+" == o[t] else r ^ a
    return r


def gen_sign(gtk, message):
    """百度专用生成sign"""
    if len(message) > 30:
        message = message[0: 10] + message[len(message)//2 - 5: len(message)//2 + 5] + message[-10:]
    S = list()
    v = 0
    for ch in message:
        A = ord(ch)
        if 128 > A:
            S.append(A)
        elif 2048 > A:
            S.append(A >> 6 | 192)
        elif 55296 == (64512 & A) and v + 1 < len(message) and 56320 == (64512 & ord(message[v+1])):
            A = 65536 + ((1023 & A) << 10) + (1023 & ord(message[v]))
            S.append(A >> 18 | 240)
            S.append(A >> 12 & 63 | 128)
        else:
            S.append(A >> 12 | 224)
            S.append(A >> 6 & 63 | 128)
            S.append(63 & A | 128)
    m, s = gtk.split(".")
    F = chr(43) + chr(45) + chr(97) + chr(94) + chr(43) + chr(54)
    D = chr(43) + chr(45) + chr(51) + chr(94) + chr(43) + chr(98) + chr(43) + chr(45) + chr(102)
    m = int(m)
    s = int(s)
    r = m
    for b in S:
        r = r + b
        r = n(r, F)
    r = n(r, D)
    r ^= s
    if 0 > r:
        r = (2147483647 & r) + 2147483648

    r %= 1e6
    return "%s.%s" % (int(r), int(r) ^ m)


class TokenAcquirer(object):
    """Google Translate API token generator

    translate.google.com uses a token to authorize the requests. If you are
    not Google, you do have this token and will have to pay for use.
    This class is the result of reverse engineering on the obfuscated and
    minified code used by Google to generate such token.

    The token is based on a seed which is updated once per hour and on the
    text that will be translated.
    Both are combined - by some strange math - in order to generate a final
    token (e.g. 744915.856682) which is used by the API to validate the
    request.

    This operation will cause an additional request to get an initial
    token from translate.google.com.

    Example usage:
        >>> from googletrans.gtoken import TokenAcquirer
        >>> acquirer = TokenAcquirer()
        >>> text = 'test'
        >>> tk = acquirer.do(text)
        >>> tk
        950629.577246
    """

    RE_TKK = re.compile(r'TKK=eval\(\'\(\(function\(\)\{(.+?)\}\)\(\)\)\'\);',
                        re.DOTALL)

    def __init__(self, tkk='0', session=None, host='translate.google.cn'):
        self.session = session or requests.Session()
        self.tkk = tkk
        self.host = host if 'http' in host else 'https://' + host

    def _update(self):
        """update tkk
        """
        # we don't need to update the base TKK value when it is still valid
        now = math.floor(int(time.time() * 1000) / 3600000.0)
        if self.tkk and int(self.tkk.split('.')[0]) == now:
            return

        r = self.session.get(self.host)
        # this will be the same as python code after stripping out a reserved word 'var'
        code = str(self.RE_TKK.search(r.text).group(1)).replace('var ', '')
        # unescape special ascii characters such like a \x3d(=)
        code = code.encode().decode('unicode-escape')

        if code:
            tree = ast.parse(code)
            visit_return = False
            operator = '+'
            n, keys = 0, dict(a=0, b=0)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    name = node.targets[0].id
                    if name in keys:
                        if isinstance(node.value, ast.Num):
                            keys[name] = node.value.n
                        # the value can sometimes be negative
                        elif isinstance(node.value, ast.UnaryOp) and \
                                isinstance(node.value.op, ast.USub):  # pragma: nocover
                            keys[name] = -node.value.operand.n
                elif isinstance(node, ast.Return):
                    # parameters should be set after this point
                    visit_return = True
                elif visit_return and isinstance(node, ast.Num):
                    n = node.n
                elif visit_return and n > 0:
                    # the default operator is '+' but implement some more for
                    # all possible scenarios
                    if isinstance(node, ast.Add):  # pragma: nocover
                        pass
                    elif isinstance(node, ast.Sub):  # pragma: nocover
                        operator = '-'
                    elif isinstance(node, ast.Mult):  # pragma: nocover
                        operator = '*'
                    elif isinstance(node, ast.Pow):  # pragma: nocover
                        operator = '**'
                    elif isinstance(node, ast.BitXor):  # pragma: nocover
                        operator = '^'
            # a safety way to avoid Exceptions
            clause = compile('{1}{0}{2}'.format(
                operator, keys['a'], keys['b']), '', 'eval')
            value = eval(clause, dict(__builtin__={}))
            result = '{}.{}'.format(n, value)

            self.tkk = result

    def _lazy(self, value):
        """like lazy evalution, this method returns a lambda function that
        returns value given.
        We won't be needing this because this seems to have been built for
        code obfuscation.

        the original code of this method is as follows:

           ... code-block: javascript

               var ek = function(a) {
                return function() {
                    return a;
                };
               }
        """
        return lambda: value

    def _xr(self, a, b):
        size_b = len(b)
        c = 0
        while c < size_b - 2:
            d = b[c + 2]
            d = ord(d[0]) - 87 if 'a' <= d else int(d)
            d = (a % 0x100000000) >> d if '+' == b[c + 1] else a << d
            a = a + d & 4294967295 if '+' == b[c] else a ^ d

            c += 3
        return a

    def acquire(self, text):
        b = self.tkk if self.tkk != '0' else ''
        d = b.split('.')
        b = int(d[0]) if len(d) > 1 else 0

        # assume e means char code array
        e = []
        g = 0
        size = len(text)
        for i, char in enumerate(text):
            l = ord(char)
            # just append if l is less than 128(ascii: DEL)
            if l < 128:
                e.append(l)
            # append calculated value if l is less than 2048
            else:
                if l < 2048:
                    e.append(l >> 6 | 192)
                else:
                    # append calculated value if l matches special condition
                    if (l & 64512) == 55296 and g + 1 < size and \
                            ord(text[g + 1]) & 64512 == 56320:
                        g += 1
                        l = 65536 + ((l & 1023) << 10) + ord(text[g]) & 1023
                        e.append(l >> 18 | 240)
                        e.append(l >> 12 & 63 | 128)
                    else:
                        e.append(l >> 12 | 224)
                    e.append(l >> 6 & 63 | 128)
                e.append(l & 63 | 128)
        a = b
        for i, value in enumerate(e):
            a += value
            a = self._xr(a, '+-a^+6')
        a = self._xr(a, '+-3^+b+-f')
        a ^= int(d[1]) if len(d) > 1 else 0
        if a < 0:  # pragma: nocover
            a = (a & 2147483647) + 2147483648
        a %= 1000000  # int(1E6)

        return '{}.{}'.format(a, a ^ b)

    def do(self, text):
        self._update()
        tk = self.acquire(text)
        return tk
