# The MIT License (MIT)

# Copyright (c) 2014 Eli Ribble

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Original license:

# Dreampylib is (c) 2009 by Laurens Simonis.
# Use it at your own risk, do with it whatever you like, 
# but I am not responsible for whatever you do with it.

# Dreampylib - version 1.0
# (c) 2009 by Laurens Simonis

# UUID is needed to generate a nice random uuid for dreamhost
import uuid
import requests
import logging

LOGGER = logging.getLogger('dreampylib')
class _RemoteCommand(object):
    # some magic to catch arbitrary maybe non-existent func. calls
    # supports "nested" methods (e.g. examples.getStateName)
    def __init__(self, name, parent, url):
        
        # Store the name of the 
        self._name = name
        self._cmd  = name.replace('.','-')
        self._parent = parent
        self._url = url
        self._child = None
        
        self._resultKeys = []
        self._status = ""
        self._resultDict = []
        self._resultList = []
        
    
    def status(self):
        if self._child:
            return self._child.status()
        else:
            return self._status
    
    def result_keys(self):
        if self._child:
            return self._child.result_keys()
        else:
            return self._resultKeys
        
    def result_list(self):
        if self._child:
            return self._child.result_list()
        else:
            return self._resultList
        
    def result_dict(self):
        if self._child:
            return self._child.result_dict()
        else:
            return self._resultDict
    
    def __getattr__(self, name):
        self._child = _RemoteCommand("%s.%s" % (self._name, name), self._parent, self._url)
        return self._child
    
    def __call__(self, returnType = None, *args, **kwargs):
        LOGGER.debug("Called %s(%s)", self._name, str(kwargs))
        
        if self._parent.is_connected():
            request = {}
            request.update(kwargs)
            request.update(self._parent._get_user_data())
            
            request['cmd'] = self._cmd
            request['unique_id'] = str(uuid.uuid4())
            
            LOGGER.debug("Request: %s", request)
                
            self._connection = requests.post(self._url, data=request, stream=True)
            return self._parse_result(returnType)
        else:
            return []
        
    def _parse_result(self, returnType):
        '''Parse the result of the request'''
        lines = [l.strip() for l in self._connection.iter_lines(decode_unicode=True)]
        self._status = lines[0]
        
        if self._status == 'success':
            self._resultKeys = keys = lines[1].split('\t')
            
            table = []
            for resultLine in lines[2:]:
                values = resultLine.split('\t')
                self._resultDict.append(dict(zip(keys,values)))
                if len(values) == 1:
                    self._resultList.append(values[0])
                else:
                    self._resultList.append(values)
            
            if returnType == 'list':
                table = self._resultList
            else:
                table = self._resultDict
            
            LOGGER.debug("Table: %s", table)
                    
            return True, 'success', table
        
        else:
            LOGGER.debug('ERROR with %s: %s - %s', self._name, lines[0], lines[1])
            self._status = '%s: %s - %s' % (self._name, lines[0], lines[1])
            return False, lines[0], lines[1]
        
class DreampyLib(object):
    
    def __init__(self, user=None, key=None, url = 'https://api.dreamhost.com'):
        '''Initialises the connection to the dreamhost API.'''
        
        self._user = user
        self._key = key
        self._url = url
        self._lastCommand = None
        self._connected = False
        self._availableCommands = []
        
        if user and key:
            self.connect()

    
    def connect(self, user = None, key = None, url = None):
        if user:
            self._user = user
            
        if key:
            self._key = key
            
        if url:
            self._url = url
            
        self._connected = True
        self._availableCommands = self.api.list_accessible_cmds(returnType = 'list')
        self._connected = True if self._availableCommands[0] != False else False
        if not self._connected:
            self._availableCommands = []
            return False
        return True
        
    def available_commands(self):
        return self._availableCommands
    
    def is_connected(self):
        return self._connected
     
    def result_keys(self):
        if not self._lastCommand:
            return []
        else:
            return self._lastCommand.result_keys()
        
    def result_list(self):
        if not self._lastCommand:
            return []
        else:
            return self._lastCommand.result_list()
        
    def result_dict(self):
        if not self._lastCommand:
            return []
        else:
            return self._lastCommand.result_dict()
        
    def status(self):
        if not self._lastCommand:
            return None
        else:
            return self._lastCommand.status()
        
    def _get_user_data(self):
        return {    'username':  self._user,
                    'key':       self._key,
                }
    
    def __getattr__(self,name):
        self._lastCommand = _RemoteCommand(name, self, self._url)
        return self._lastCommand
        
    def dir(self):
        self.api.list_accessible_cmds()