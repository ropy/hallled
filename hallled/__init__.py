from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    # config.add_route('api_led_coa', '/api/led/{command}/{operator}/{amount}')
    # routes targeted to arduino
    config.add_route('api_led_hslm', '/api/led/hslm/{hue}/{saturation}/{lightning}/{modulo}')
    config.add_route('api_led_rgbm', '/api/led/rgbm/{red}/{green}/{blue}/{modulo}')
    config.add_route('api_serialcommand', '/api/raw/{command}')

    # info route
    config.add_route('api_info', '/api/info')
    config.scan()
    return config.make_wsgi_app()

