# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 17:31:23 2021

@author: Josh
"""

import requests
import json
import sys
import copy
import re

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
        name of filee to be saved.
    data : list
        data to be wrote to file.

    Returns
    -------
    None.

    '''
    file_name = re.sub('\.(.*)', '', file_name)
    with open(f'{file_name}.json', 'w') as outfile:
        json.dump(data, outfile)

def sort_quads(unsorted_data):
    '''
    A Mutable operation on an unsorted dataset, sorting into a collection of
    wet and dry objects, this operation destroys the original dataset, in doing so
    it becomes more memory effecicent and is 100ms faster than iterating over a
    looped variation of the same operation. if wished to keep un-mutated please
    pass in a deep copy of the original data
    
    Parameters
    ----------
    unsorted_data : Dictionary
        Unsorted eleemnts and 3d XYZ coord's. (p & q)

    Returns
    -------
    list: Wet elements
    list: Dry elements
    '''
    unsorted_data = copy.deepcopy(unsorted_data)
    return [unsorted_data['q'].pop() for q in reversed(unsorted_data['q'])
        if any(unsorted_data['p'][p][2] < 0 for p in q)], unsorted_data['q']

def main():
    url = sys.argv[1:] or 'https://assets.wave-venture.com/simple_challenge_data.json'
    if (unsorted_data_t := get_data(url)):
        try:
            unsorted_data = json.loads(unsorted_data_t.text)
        except:
            print('Error Parsing Json - Json contains invalid structures')
        wet, dry = sort_quads(unsorted_data)
        store_data('wet', wet)
        store_data('dry', dry)
        
if __name__ == "__main__":
    main()
    
"""
My interpritation of the problem presented is that 'Q' the list of quadrilaterals
as such presenting 4 points EG[23, 22, 0, 1], these points correspond to the index 
of 'P' representing the 3d position X,Y,Z. The problem is to sort Q based on  
any part being below water level (wet) my solution is based around this assumption.

As such the result is wet.json contains all quads where some part of the geometry
sits below water level and dry.json contains alll quads that are completely removed
from the water.
"""