import pickle as pickle
import csv
import json
import logging
import os

from nba.db.pgsql import NBAPostgres
from nba.players import NBAPlayers
from nba.scrapers.fantasylabs import FantasyLabsNBAScraper


class NBAAgent(object):
    '''
    Base class to perform script-like tasks
    Use subclasses to replace standalone scripts so can use common API and tools
    Would be helpful to map a bunch of generic actions so don't need to remember composed parts
    Example: instead of self.nbadb.insert it would be self.insert, which handles the necessary internal plumbing for you

    '''

    def __init__(self, **kwargs):
        '''

        Args:
            cookies:
            cache_name:
            safe:
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.nbap = NBAPlayers()

        if db:
            self.db = NBAPostgres()

        self.safe = safe
        self.scraper = FantasyLabsNBAScraper(cookies=cookies, cache_name=cache_name)

    def _read_csv (self, csv_fname):
        '''
        Takes csv file and returns dictionary

        Arguments:
            csv_fname (str): name of file to read/parse

        Returns:
            List of dicts, key is name, value is id

        '''

        list_of_dicts = []

        if os.path.exists(csv_fname):
            with open (csv_fname, 'r') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)

                for row in reader:
                    list_of_dicts.append(dict(list(zip(headers, row))))

        else:
            raise ValueError('{0} does not exist'.format(csv_fname))

        return list_of_dicts

    def _read_json (self, json_fname):
        '''
        Takes json file and returns data structure

        Arguments:
            json_fname: name of file to read/parse

        Returns:
            parsed json

        '''
        
        if os.path.exists(json_fname):
            with open(json_fname, 'r') as infile:
                data = json.load(infile)
               
        else:
            raise ValueError('{0} does not exist'.format(json_fname))

        return data
        
    def _read_pickle (self, pkl_fname):
        '''
        Takes pickle file and returns data structure

        Arguments:
            json_fname: name of file to read/parse

        Returns:
            parsed json

        '''
        
        if os.path.exists(pkl_fname):
            with open(pkl_fname, 'rb') as infile:
                data = pickle.load(infile)
               
        else:
            raise ValueError('{0} does not exist'.format(pkl_fname))

        return data       

    def read_file(self, fname):
        '''
        Pass filename, it returns data structure. Decides based on file extension.
        '''

        ext = os.path.splitext(fname)[1]

        if ext == '.csv':
            return self._read_csv(fname)
            
        elif ext == '.json':
            return self._read_json(fname)

        elif ext == 'pkl':
            return self._read_pickle(fname)

        else:
            raise ValueError('{0} is not a supported file extension'.format(ext))

    def _save_csv (self, data, csv_fname, fieldnames, sep=';'):
        '''
        Takes datastructure and saves as csv file

        Arguments:
            data: python data structure
            csv_fname: name of file to save
            fieldnames: list of fields

        Returns:
            None
        '''

        try:
            with open(csv_fname, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

        except:
            logging.exception('could not save csv file')

    def _save_json (self, data, json_fname):
        '''
        Takes data and saves to json file

        Arguments:
            data: python data structure
            json_fname: name of file to save

        '''
        
        try:
            with open(json_fname, 'wb') as outfile:
                json.dump(data, outfile)

        except:
            logging.exception('{0} does not exist'.format(json_fname))
       
    def _write_pickle (self, data, pkl_fname):
        '''
        Saves data structure to pickle file

        Arguments:
            data: python data structure
            pkl_fname: name of file to save

        '''
        
        try:
            with open(pkl_fname, 'wb') as outfile:
                pickle.dump(data, outfile)

        except:
            logging.exception('{0} does not exist'.format(pkl_fname))

    def save_file(self, data, fname):
        '''
        Pass filename, it returns datastructure. Decides based on file extension.
        '''

        ext = os.path.splitext(fname)[1]

        if ext == '.csv':
            self._save_csv(data=data, csv_fname=fname, fieldnames=data[0])
            
        elif ext == '.json':
            self._save_json(fname)

        elif ext == 'pkl':
            self._save_pickle(fname)

        else:
            raise ValueError('{0} is not a supported file extension'.format(ext))

if __name__ == '__main__':
    pass    
