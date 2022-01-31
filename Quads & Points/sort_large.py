# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 13:51:30 2021

@author: Josh
"""

import sys
import requests
import json
import re

class Point(object):
    
    def __init__(self, x, y, z, key):
        self.__key = key
        self.__x = x
        self.__y = y
        self.__z = z
        
    @property
    def key(self):
        return self.__key
      
    @property
    def x(self):
        return self.__x
    
    @property
    def y(self):
        return self.__y
    
    @property
    def z(self):
        return self.__z
    
    @key.setter
    def key(self, key):
        self.__key = key
        
    def __repr__(self):
       return repr([self.x, self.y, self.z ])
    
class quadrilateral(object):
    
    def __init__(self, p_1, p_2, p_3, p_4):
        self.wet = False
        self.tl = p_1 #tl = top_left
        self.tr = p_2 #tr = top_right
        self.bl = p_3 #tl = bottom_left
        self.br = p_4 #tl = bottom_right
        
    @property
    def wet(self):
        return self.__wet
        
    @property
    def tl(self):
        return self.__tl
    
    @property
    def tr(self):
        return self.__tr
    
    @property
    def bl(self):
        return self.__bl
    
    @property
    def br(self):
        return self.__br
    
    @tl.setter
    def tl(self, tl):
        self.__tl = tl
        self.__evaluate(tl.z)
        
    @tr.setter
    def tr(self, tr):
        self.__tr = tr
        self.__evaluate(tr.z)
     
    @bl.setter
    def bl(self, bl):
        self.__bl = bl
        self.__evaluate(bl.z)
      
    @br.setter
    def br(self, br):
        self.__br = br
        self.__evaluate(br.z)
        
    @wet.setter
    def wet(self, wet):
        self.__wet = wet
             
    def __evaluate(self, z):
        if not self.wet and z < 0:
            self.wet = True
            
    def points(self):
        return {self.tl, self.tr, self.bl, self.br}
    
    def value(self):
        return [self.tl.key, self.tr.key, self.bl.key, self.br.key]
    
    def __repr__(self):
        return repr(self.value())
        
def get_data(url, timeout = 60, redirects=False):
    '''
    An oepration to retrieve data from a given Url
    
    Parameters
    ----------
    url : str
        Url to request.
    timeout : Int
        Amount of time to wait before killing a connection.
    redirects: Bool
        allows redirects if true
    Returns
    -------
    Request Object.

    '''
    try:
        response = requests.get(url, allow_redirects=redirects, timeout=timeout)
        if response.status_code >= 500:
            raise Exception(f'Server error: {response}')
        elif response.status_code >= 400:
            raise Exception(f'Client error response: {response}')
        elif response.status_code >= 300:
            raise Exception(f'Redirection message: {response}')
        else:
            return response
    except requests.exceptions.ConnectTimeout:
        print('operation \'Get_data\' failed on request - system returning \'None\'')
        return None   
   
def store_data(file_name, data):
    '''
    Parameters
    ----------
    file_name : str
        name of file to be saved.
    data : list
        data to be wrote to file.
    Returns
    -------
    None.

    '''
    file_name = re.sub('\.(.*)', '', file_name)
    text_file = open(f'{file_name}.json', "w")
    text_file.write(format_data(data))
    text_file.close()     
   
def format_data(data):
    '''
    Makes a set of points removing duplicates then re-index's the quads by
    changing the referenced key within the Point object this in turn changes 
    the referenced var within the Quad obj
    
    Parameters
    ----------
    data : list
        list of quads.
    Returns
    -------
    Json String - quads and points.

    '''
    points = set()
    for quad in data:
        points.update(quad.points())
    for idx, p in enumerate(points):
        p.key = idx
    return f'{{"q": {data}, "p": {list(points)} }}'
    
def map_data(data):
    '''
    Maps the points to point objects then creates a quad referencing said objects
    also determines if a quad is wet the references allow for later mutation of
    idx values to be produced when mapping to json.
    
    Parameters
    ----------
    data : dict
        dict of unsorted quads and points
    Returns
    -------
    2 Lists of quads, wet and dry

    '''
    points, quads, wet, dry = data['p'], data['q'], [], []
    for _count, p in enumerate(points):
        points[_count] = Point(*p, _count)
    for quad in quads:
        q = quadrilateral(*(map(lambda n: points[n], quad)))
        wet.append(q) if q.wet else dry.append(q)
    return wet, dry

def main():
    url = sys.argv[1:] or 'https://assets.wave-venture.com/simple_challenge_data.json'
    if (unsorted_data_t := get_data(url)):
        try:
            unsorted_data = json.loads(unsorted_data_t.text)
        except:
            print('Error Parsing Json - Json contains invalid structures')
        (lambda x, y : (store_data('wet', x), store_data('dry', y)))(*map_data(unsorted_data))
        
if __name__ == "__main__":
    main()
    
'''
I made this as i was unsure if you wanted the output format to be the same as the 
input format EG {'q': [[idx_1, idx_2, idx_3, idx_4]...], 'p': [[x, y, z], [x, y, z]...]}

if this was the case since each quad relies on the index of the point within the list
to act as a pointer towards the xyz values then the pointers reference would have 
to change due to not being able to use the exact same list of points as not all points 
may be present this is more so a concern on a scaled system where we would be producing
duplicate point lists of irrelevant data if we where to include the originals within 
dry.json and wet.json. As such changing the point list changes the idx value of 
each quadrilateral and each will have to be re-mapped to the new output. 

Here we achieve this by continuesly referencing the same object and changing the value
in each address space as such changing the key within each point list in format data, this
will automaticaly mutate the pointer key within the quadrilateral object. The
logic here is messy but is probably the most efficient way of doing this without deep copying 
and utilizing more system memory this also has the benefit of saving on speed 
since we declare and iterate less than if we where continuesly using temporary objects 
lists and object update calls.

NB: if you do not need the points and just require the quads that are wet and dry
'sort.py' does this in a lot faster and more efficient manour.
'''