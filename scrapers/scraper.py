import logging
import requests
import requests_cache
import time

class EWTScraper(object):
    '''
    Generic class to perform cached scraping of web pages and web services

    Methods:
        get: returns string
        get_json: returns dict

    '''

    def __init__(self, use_cache=1, use_proxy=0, is_polite=1, cache_name='EWT_scraper_cache', cache_backend='sqlite', cache_expire=7200, cookies=None, **kwargs):
        '''
        TODO: set location of cache to better place
        TODO: remove kwargs
        '''

        self.logger = logging.getLogger(__name__)
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'}
        self.cookies = cookies
        self.responses = []

        if use_cache:
            self.logger.debug('EWTScraper: using cache')
            self.cache_name = cache_name
            self.cache_backend = cache_backend
            self.cache_expire = cache_expire
            requests_cache.install_cache(self.cache_name, backend=self.cache_backend, expire_after=self.cache_expire)

        else:
            self.logger.debug('EWTScraper: not using cache')

        if use_proxy:
            import socks
            import socket
            socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
            socket.socket = socks.socksocket
            self.logger.debug('EWTScraper: using proxy')
        else:
            self.logger.debug('EWTScraper: not using proxy')

        self.is_polite=is_polite

        # http://stackoverflow.com/questions/8134444/python-constructor-of-derived-class
        self.__dict__.update(kwargs)

    def get(self, url, payload=None, cookies=None):
        '''
        Returns text of response
        '''

        if payload:
            r = requests.get(url=url, headers=self.headers, params=payload, cookies=cookies)
        else:
            r = requests.get(url=url, headers=self.headers, cookies=cookies)

        r.raise_for_status()
        self.logger.debug(r)

        if self.is_polite:
            time.sleep(1)

        self.responses.append(r)
        return r.text

    def get_json(self, url, payload=None, cookies=None):
        '''
        Returns decoded JSON
        '''
        content = None

        if payload:
            r = requests.get(url=url, headers=self.headers, params=payload, cookies=cookies)
        else:
            r = requests.get(url=url, headers=self.headers, cookies=cookies)

        self.logger.debug(r)
        r.raise_for_status()

        if self.is_polite:
            time.sleep(1)

        self.responses.append(r)
        return r.json()

    def get_save(self, url, fname, payload=None):
        '''
        Returns text of response and saves to file
        '''

        if payload:
            r = requests.get(url=url, headers=self.headers, params=payload, cookies=cookies)
        else:
            r = requests.get(url=url, headers=self.headers, cookies=cookies)

        r.raise_for_status()

        try:
            with open(fname, 'w') as outfile:
                outfile.write(r.text)

        except:
            logging.exception('could not write url {0} to {1}'.format(url, fname))

        if self.is_polite:
            time.sleep(1)

        self.responses.append(r)
        return r.text

    def post(self, url, payload=None, cookies=None):
        '''
        Returns text of response
        '''

        if payload:
            r = requests.post(url=url, headers=self.headers, params=payload, cookies=cookies)
        else:
            r = requests.post(url=url, headers=self.headers, cookies=cookies)

        r.raise_for_status()
        self.logger.debug(r)

        if self.is_polite:
            time.sleep(1)

        return r

if __name__ == "__main__":
    pass