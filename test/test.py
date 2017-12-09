import unittest

from translate import Translate


class TestTranslate(unittest.TestCase):

    def assertContainEqual(self, first, second, msg=None):
        if not first.count(second):
            msg = self._formatMessage(msg, "%s is not contain %s"%(first, second))
            self.fail(msg)
    #
    # def test_baidu(self):
    #     with Translate("baidu") as t:
    #         t.set_logger()
    #         self.assertContainEqual(t.translate("my name is tom, what about yours?"), "我")

    def test_google(self):
        with Translate("google") as t:
            self.assertContainEqual(t.translate("my name is tom, what about yours?"), "我")
    #
    # def test_qq(self):
    #     with Translate("qq") as t:
    #         self.assertContainEqual(t.translate("my name is tom, what about yours?"), "我")


if __name__ == "__main__":
    unittest.main()
