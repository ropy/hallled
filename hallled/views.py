from pyramid.view import view_config

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'HallLed'}
    
@view_config(renderer='json')
def api_led(request):
	return Response('OK')
