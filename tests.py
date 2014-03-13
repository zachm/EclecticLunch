import unittest

import mock

from wireer import Wireer

class WireerTestCase(unittest.TestCase):
    def test__happy_case(self):
        w = Wireer()

        v1 = lambda: None
        v2 = lambda: None

        assert w.route('arg1', kw='kwarg1')(v1) is v1
        assert w.route('arg2', kw='kwarg2')(v2) is v2

        app = mock.Mock(name='app')

        w.wire_up(app)

        assert app.route.call_args_list == [
            mock.call('arg1', kw='kwarg1'),
            mock.call('arg2', kw='kwarg2'),
        ]

        assert app.route.return_value.call_args_list == [
            mock.call(v1),
            mock.call(v2),
        ]


if __name__ == '__main__':
        unittest.main()
