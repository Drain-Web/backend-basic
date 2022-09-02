from django.shortcuts import render
from django.http.response import HttpResponse
from django.http import FileResponse

from rest_framework.decorators import api_view

import mimetypes
import os

# ## CONSTANTS ####################################################################################################### #

IMAGES_FILE_EXT = "png"

# ## TILES ########################################################################################################### #   

@api_view(['GET'])
def open_file(request, product_id, zoom, x, y):

    fdpa = os.path.join(os.path.dirname(os.path.abspath(__file__)), "file_tiles")
    fina = "{0}.{1}".format(y, IMAGES_FILE_EXT)
    fipa = os.path.join(fdpa, product_id, zoom, x, fina)
    return FileResponse(open(fipa, "rb"))