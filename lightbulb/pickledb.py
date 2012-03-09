# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import re
import os
import time
import pickle
from collections import OrderedDict


class PickleDB(object):

    db_name = None
    datatype = OrderedDict

    def __init__(self, db_dir=None, file_name=None):
        self.db_dir = os.path.abspath(db_dir)
        self.file_name = self._get_file_name(file_name)
        self.db_abspath = self._get_db_abspath()
        self.data = self._get_data()

    def put(self, key, value):
        self.data[key] = value
        self.write()

    def get(self, key, default_value=None):
        return self.data.get(key, default_value)
                     
    def exists(self):
        return os.path.isfile(self.db_abspath)
  
    def _get_data(self):
        try:
            data = self._read()
        except (IOError, EOFError) as e:
            data =  self.datatype()
        return data

    def _read(self):
        with open(self.db_abspath, "r") as fin:
            data = pickle.load(fin)   
        return data

    def write(self):
        with open(self.db_abspath, "w") as fout:
            pickle.dump(self.data, fout)

    def _get_file_name(self, file_name):
        if file_name is None:
            file_name = "%s.pickle" % self.db_name
        return file_name

    def _get_db_abspath(self):
        return os.path.join(self.db_dir, self.file_name)


#
# DataObject is not being used at the moment (see ARGGG below).
#
# ARGGG!: you can't combine Projects and Changes into one DB; 
# you're using the existence of changelog.pickle to control update
#

class DataObject(object):

    name = None
    datatype = dict
    
    def __init__(self, db_dir):
        self.db = PickleDB(db_dir)
        self.data = self._get_or_init_data(name)
 
    def set(self, name, project_dir):
        self.data[name] = project_dir
        self.db.write()

    def get(self, name):
        return self.data[name]

    def get_all(self):
        return self.data
       
    def _get_or_init_data(self, key):
        # get or init the data object in the DB if it doesn't exist
        project_data = self.db.get(key)        
        if project_data is None:
            project_data = datatype()
            self.db.put(key, project_data)
        return project_data




