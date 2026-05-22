from rest_framework.decorators import api_view

@api_view(['GET'])
def crash_test(request):
    raise Exception("Test Glitchtip")