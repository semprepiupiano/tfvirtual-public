from django.shortcuts import render

#TODO: Fix 404 page not found before deployment
def handler404(request, exception=None):
    response = render(request, '404.html')
    response.status_code = 404
    return response

def handler500(request, exception=None):
    response = render(request, '500.html')
    response.status_code = 500
    return response