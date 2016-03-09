
try:
    import cPickle as pickle
except:
    import pickle

import logging
import os

import pandas as pd

from nba.players import NBAPlayers
from nba.seasons import NBASeasons


class NBAAgent(object):
    '''
    Base class to perform script-like tasks
    Use subclasses to replace standalone scripts so can use common API and tools
    Would be helpful to map a bunch of generic actions so don't need to remember composed parts
    Example: instead of self.nbadb.insert it would be self.insert, which handles the necessary internal plumbing for you

    '''

    def __init__(self, db=True, safe=True):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        self.nbap = NBAPlayers()
        self.nbas = NBASeasons()
        
    def _read_csv (self, csv_fname, headers=True):
        '''
        Takes csv file and returns dictionary

        Arguments:
            csv_fname: name of file to read/parse

        Returns:
            List of dicts, key is name, value is id

        '''
        
        if os.file.exists(csv_fname):
            frame = pd.read_csv(csv_fname, headers=headers)

            if frame:
                list_of_dicts = frame.to_dict('records')
            else:
                raise ValueError('frame does not exist - cannot create list_of_dicts')
                
        else:
            raise ValueError('{0} does not exist'.format(csv_fname))
            
    def _read_json (self, json_fname):
        '''
        Takes json file and returns data structure

        Arguments:
            json_fname: name of file to read/parse

        Returns:
            parsed json

        '''
        
        if os.file.exists(json_fname):
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
        
        if os.file.exists(pkl_fname):
            with open(pkl_fname, 'rb') as infile:
                data = pickle.load(infile)
               
        else:
            raise ValueError('{0} does not exist'.format(pkl_fname))

        return data       

    def read_file(self, fname):
        '''
        Pass filename, it returns datastructure. Decides based on file extension.
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

    def _save_csv (self, data, csv_fname, sep=';', date_format='%Y-%m-%d'):
        '''
        Takes datastructure and saves as csv file

        Arguments:
            data: python data structure
            csv_fname: name of file to save

        '''

        try:
            frame = pd.DataFrame(data)
            frame.to_csv(csv_fname, index=False, sep=sep, date_format=date_format)

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
       
    def _read_pickle (self, data, pkl_fname):
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
            self._save_csv(data, fname)
            
        elif ext == '.json':
            self._save_json(fname)

        elif ext == 'pkl':
            self._save_pickle(fname)

        else:
            raise ValueError('{0} is not a supported file extension'.format(ext))

    def website(self, webdir):
        '''
        Generates static website to upload to S3 bucket
        This needs to be rewritten generically to create pages of tables
        from a list of dictionaries
        ''' 

        #########################################
        # generate the HTML or other files here #

        pass

if __name__ == '__main__':
    pass    
