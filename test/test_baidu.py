"""
i = null

function names(r) {
        var o = r.match(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g);
        if (null === o) {
            var t = r.length;
            t > 30 && (r = "" + r.substr(0, 10) + r.substr(Math.floor(t / 2) - 5, 10) + r.substr(-10, 10))
        } else {
            for (var e = r.split(/[\uD800-\uDBFF][\uDC00-\uDFFF]/), C = 0, h = e.length, f = []; h > C; C++)
                "" !== e[C] && f.push.apply(f, a(e[C].split(""))),
                C !== h - 1 && f.push(o[C]);
            var g = f.length;
            g > 30 && (r = f.slice(0, 10).join("") + f.slice(Math.floor(g / 2) - 5, Math.floor(g / 2) + 5).join("") + f.slice(-10).join(""))
        }
        var u = void 0
          , l = "" + String.fromCharCode(103) + String.fromCharCode(116) + String.fromCharCode(107);
        u = null !== i ? i : (i = window[l] || "") || "";
        for (var d = u.split("."), m = Number(d[0]) || 0, s = Number(d[1]) || 0, S = [], c = 0, v = 0; v < r.length; v++) {
            var A = r.charCodeAt(v);
            128 > A ? S[c++] = A : (2048 > A ? S[c++] = A >> 6 | 192 : (55296 === (64512 & A) && v + 1 < r.length && 56320 === (64512 & r.charCodeAt(v + 1)) ? (A = 65536 + ((1023 & A) << 10) + (1023 & r.charCodeAt(++v)),
            S[c++] = A >> 18 | 240,
            S[c++] = A >> 12 & 63 | 128) : S[c++] = A >> 12 | 224,
            S[c++] = A >> 6 & 63 | 128),
            S[c++] = 63 & A | 128)
        }
        for (var p = m, F = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(97) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(54)), D = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(51) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(98)) + ("" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(102)), b = 0; b < S.length; b++)
            p += S[b],
            p = n(p, F);
        return p = n(p, D),
        p ^= s,
        0 > p && (p = (2147483647 & p) + 2147483648),
        p %= 1e6,
        p.toString() + "." + (p ^ m)
    }

function n(r, o) {
        for (var t = 0; t < o.length - 2; t += 3) {
            var a = o.charAt(t + 2);
            a = a >= "a" ? a.charCodeAt(0) - 87 : Number(a),
            a = "+" === o.charAt(t + 1) ? r >>> a : r << a,
            r = "+" === o.charAt(t) ? r + a & 4294967295 : r ^ a
        }
        return r
    }
"""
import re
import math


import ctypes

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
    return int_overflow(n >> i)


def n(r, o):
    for t in range(0, len(o) - 2, 3):
        a = o[t + 2]
        a = ord(a) - 87 if a >= "a" else int(a)
        a = unsigned_right_shitf(r, a) if "+" == o[t + 1] else r << a
        r = r + a & 4294967295 if "+" == o[t] else r ^ a
    return r


def gen_sign(gtk, message):
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


print(gen_sign("320305.131321201", "you"))

from translate import Translate

with Translate("baidu") as t:
    t.set_logger()
    print(t.translate("my name is tom, what about yours?"))