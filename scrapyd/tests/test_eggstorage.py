try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

from twisted.trial import unittest

from zope.interface.verify import verifyObject

from pkgutil import get_data
from scrapyd.interfaces import IEggStorage
from scrapyd.config import Config
from scrapyd.eggstorage import FilesystemEggStorage

class EggStorageTest(unittest.TestCase):

    def setUp(self):
        d = self.mktemp()
        config = Config(values={'eggs_dir': d})
        self.eggst = FilesystemEggStorage(config)

    def test_interface(self):
        verifyObject(IEggStorage, self.eggst)

    def test_put_get_list_delete(self):
        self.eggst.put(BytesIO(get_data("scrapyd.tests", "mybot.egg")), 'mybot', '01')
        self.eggst.put(BytesIO(get_data("scrapyd.tests", "mybot3.egg")), 'mybot', '03/ver')
        self.eggst.put(BytesIO(get_data("scrapyd.tests", "mybot2.egg")), 'mybot', '02_my branch')

        self.assertEqual(self.eggst.list('mybot'), [
            '01',
            '02_my_branch',
            '03_ver'
        ])
        self.assertEqual(self.eggst.list('mybot2'), [])

        v, f = self.eggst.get('mybot')
        self.assertEqual(v, "03_ver")
        self.assertEqual(f.read(), get_data("scrapyd.tests", "mybot3.egg"))
        f.close()

        v, f = self.eggst.get('mybot', '02_my branch')
        self.assertEqual(v, "02_my branch")
        self.assertEqual(f.read(), get_data("scrapyd.tests", "mybot2.egg"))
        f.close()

        v, f = self.eggst.get('mybot', '02_my_branch')
        self.assertEqual(v, "02_my_branch")
        self.assertEqual(f.read(), get_data("scrapyd.tests", "mybot2.egg"))
        f.close()

        self.eggst.delete('mybot', '02_my branch')
        self.assertEqual(self.eggst.list('mybot'), ['01', '03_ver'])

        self.eggst.delete('mybot', '03_ver')
        self.assertEqual(self.eggst.list('mybot'), ['01'])

        self.eggst.delete('mybot')
        self.assertEqual(self.eggst.list('mybot'), [])
