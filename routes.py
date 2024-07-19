#coding: utf-8

BASE = ''
routes_in = (
    (BASE + '/search', BASE + '/unovainvest/default/search'),
    (BASE + '/results', BASE + '/unovainvest/default/results'),
    app = dict(default_language = 'pt-br',
    languages = ['en', 'pt-br'],
    )

routes_out = [(x, y) for (y, x) in routes_in]
