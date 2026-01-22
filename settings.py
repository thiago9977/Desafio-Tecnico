from decouple import config

PROXY_ENABLE = config('PROXY_ENABLE', default=False, cast=bool)
PROXY = config('PROXY', default=None)
CHROME_PATH = config('CHROME_PATH', default=None)
