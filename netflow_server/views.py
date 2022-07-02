from django.shortcuts import render
from django.http.response import JsonResponse

from rest_framework.decorators import api_view

import json
import os

# ## CONSTANTS ####################################################################################################### #

NETFLOW_FILE_EXT = "json"
NETFLOW_FOLDER_NAME = "files"

# ## TILES ########################################################################################################### #   

@api_view(['GET'])
def open_file(request, netflow_id):

    fdpa = os.path.join(os.path.dirname(os.path.abspath(__file__)), NETFLOW_FOLDER_NAME)
    fipa = os.path.join(fdpa, "{0}.{1}".format(netflow_id, NETFLOW_FILE_EXT))
    with open(fipa, "r") as r_file:
        file_data = json.load(r_file)
    return JsonResponse(file_data)