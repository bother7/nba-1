import logging
import os

import requests


class BasketballScraper(object):

    def __init__(self, headers=None, cookies=None, cache_name=None, expire_hours=12, as_string=False):
        '''
        Base class for common scraping tasks
        Args:
            headers: dict of headers
            cookies: cookiejar object
            cache_name: should be full path
            expire_hours: int - default 4
            as_string: get string rather than parsed json
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        if not cookies:
            try:
                import cookielib
                cookies = cookielib.MozillaCookieJar()
            except (NameError, ImportError) as e:
                try:
                    import http.cookiejar
                    cookies = http.cookiejar.MozillaCookieJar()
                except Exception as e:
                    pass

        _s = requests.Session()
        _s.cookies = cookies

        if headers:
            _s.headers.update(headers)
        else:
            _s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'})

        if cache_name:
            if not '/' in cache_name:
                cache_name = os.path.join('/tmp', cache_name)
            try:
                from cachecontrol import CacheControlAdapter
                from cachecontrol.heuristics import ExpiresAfter
                from cachecontrol.caches import FileCache
                _s.mount('http://', CacheControlAdapter(cache=FileCache(cache_name), cache_etags = False, heuristic=ExpiresAfter(hours=expire_hours)))
            except ImportError as e:
                try:
                    import requests_cache
                    requests_cache.install_cache(cache_name)
                except:
                    pass
        self.s = _s
        self.urls = []
        self.as_string = as_string

    def get(self, url, payload=None):
        if payload:
            r = self.s.get(url, params={k:payload[k] for k in sorted(payload)})
        else:
            r = self.s.get(url)
        self.urls.append(r.url)
        r.raise_for_status()
        return r.content

    def get_json(self, url, payload=None):
        if payload:
            r = self.s.get(url, params={k:payload[k] for k in sorted(payload)})
        else:
            r = self.s.get(url)
        self.urls.append(r.url)
        r.raise_for_status()
        if self.as_string:
            return r.content
        else:
            return r.json()

    def post(self, url, payload):
        if payload:
            r = self.s.get(url, params={k:payload[k] for k in sorted(payload)})
        else:
            r = self.s.get(url)
        self.urls.append(r.url)
        r.raise_for_status()
        return r.content

if __name__ == "__main__":
    pass