# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required

from lib import render_to


@login_required()
@render_to('index.html')
def index(request):
    return {}