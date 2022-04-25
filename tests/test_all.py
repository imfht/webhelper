import os

from web_helper import *


def test_proxy():
    set_global_random_proxy(os.getenv('ws_token'))
    assert 'from: US' in get_html('https://ip.fht.im').text
