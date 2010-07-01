### url mappings ###

class URLMappings(dict):
    def __missing__(self, x):
        return self['http://localhost:8080']


new_or_old = URLMappings({'http://amsterdam.the-hub.net':'new',
                          'http://bayarea.the-hub.net':'new',
                          'http://berlin.the-hub.net':'new',
                          'http://berkeley.the-hub.net':'new',
                          'http://bombay.the-hub.net':'new',
                          'http://bristol.the-hub.net':'new',
                          'http://brussels.the-hub.net':'new',
                          'http://cairo.the-hub.net':'new',
                          'http://halifax.the-hub.net':'new',
                          'http://islington.the-hub.net':'new',
                          'http://johannesburg.the-hub.net':'new',
                          'http://kingscross.the-hub.net':'new',
                          'http://milan.the-hub.net':'new',
                          'http://madrid.the-hub.net':'new',
                          'http://porto.the-hub.net':'new',
                          'http://rotterdam.the-hub.net':'new',
                          'http://sanfrancisco.the-hub.net':'new',
                          'http://saopaulo.the-hub.net':'new',
                          'http://southbank.the-hub.net':'new',
                          'http://stockholm.the-hub.net':'new',
                          'http://telaviv.the-hub.net':'new',
                          'http://toronto.the-hub.net':'new',
                          'http://vienna.the-hub.net':'new',
                          'http://members.socialinnovation.ca':'old',
                          'http://members.themonksyard.co.uk':'old',
                          'http://hubspacedev.the-hub.net':'new',
                          'http://localhost:8080':'old',
                          'http://members.the-hub.net':'old',
                          'http://test.the-hub.net':'new',
                          'http://test2.the-hub.net':'new',
                          'http://testregion.the-hub.net':'new'}
)



title = URLMappings({'http://amsterdam.the-hub.net': 'Hub Amsterdam',
                     'http://atlanta.the-hub.net': 'Hub Atlanta',
                     'http://athens.the-hub.net': 'Hub Athens',
                     'http://barcelona.the-hub.net': 'Hub Barcelona',
                     'http://bayarea.the-hub.net': 'Hub Bay Area',
                     'http://bergen.the-hub.net': 'Hub Bergen',
                     'http://berlin.the-hub.net': 'Hub Berlin',
                     'http://berkeley.the-hub.net': 'Hub Berkeley',
                     'http://bogota.the-hub.net':'Hub Bogota',
                     'http://bombay.the-hub.net':'Hub Bombay',
                     'http://bristol.the-hub.net':'Hub Bristol',
                     'http://brussels.the-hub.net':'Hub Brussels',
                     'http://cairo.the-hub.net':'Hub Cairo',
                     'http://capetown.the-hub.net':'Hub Cape Town',
                     'http://copenhagen.the-hub.net':'Hub Copenhagen',
                     'http://durban.the-hub.net':'Hub Durban',
                     'http://geneva.the-hub.net':'Hub Geneva',
                     'http://halifax.the-hub.net':'Hub Halifax',
                     'http://helsinki.the-hub.net':'Hub Helsinki',
                     'http://islington.the-hub.net':'Hub Islington',
                     'http://johannesburg.the-hub.net':'Hub Johannesburg',
                     'http://kabul.the-hub.net':"Hub Kabul",
                     'http://kyiv.the-hub.net':"Hub Kyiv",
                     'http://kingscross.the-hub.net':"Hub King's Cross",
                     'http://losangeles.the-hub.net':"Hub Los Angeles",
                     'http://la.the-hub.net':"Hub Los Angeles",
                     'http://madrid.the-hub.net':'Hub Madrid',
                     'http://melbourne.the-hub.net':'Hub Melbourne',
                     'http://milan.the-hub.net':'Hub Milan',
                     'http://montreal.the-hub.net':'Hub Montreal',
                     'http://minneapolis.the-hub.net':'Hub Minneapolis',
                     'http://newyork.the-hub.net':'Hub New York',
                     'http://porto.the-hub.net':'Hub Porto',
                     'http://prague.the-hub.net':'Hub Prague',
                     'http://oaxaca.the-hub.net':'Hub Oaxaca',
                     'http://riga.the-hub.net':'Hub Riga',
                     'http://rotterdam.the-hub.net':'Hub Rotterdam',
                     'http://roverto.the-hub.net':'Hub Roverto',
                     'http://shop.rotterdam.the-hub.net':'Hub Shop - Rotterdam',
                     'http://saopaulo.the-hub.net':'Hub Sao Paulo',
                     'http://sanfrancisco.the-hub.net':'Hub San Francisco',
                     'http://southbank.the-hub.net':'Hub South Bank',
                     'http://stockholm.the-hub.net':'Hub Stockholm',
                     'http://tampere.the-hub.net':'Hub Tampere',
                     'http://telaviv.the-hub.net':'Hub Telaviv',
                     'http://vancouver.the-hub.net':'Hub Vancouver',
                     'http://vienna.the-hub.net':'Hub Vienna',
                     'http://washintondc.the-hub.net':'Hub Washington DC',
                     'http://dc.the-hub.net':'Hub Washington DC',
                     'http://zurich.the-hub.net':'Hub Zurich',
                     'http://toronto.the-hub.net':'Centre for Social Innovation',
                     'http://members.socialinnovation.ca':'Centre for Social Innovation',
                     'http://members.themonksyard.co.uk':'Monks Yard',
                     'http://localhost:8080':'The Hub',
                     'http://hubspacedev.the-hub.net':'The Hub',
                     'http://members.the-hub.net':'The Hub',
                     'http://test.the-hub.net':'The Hub',
                     'http://test2.the-hub.net':'The Hub',
                     'http://testregion.the-hub.net':'The Hub',}
)
site_index_page = URLMappings({'http://localhost:8080':'index.html',
                               'http://prague.the-hub.net':'blog'})

site_folders = URLMappings({'http://localhost:8080':'site_templates.hubspace.',
                            'http://members.socialinnovation.ca':'site_templates.toronto.',
                            'http://toronto.the-hub.net':'site_templates.toronto.'})

site_default_lang = URLMappings({'http://localhost:8080':'en',
                                 'http://athens.the-hub.net':'el',
                                 'http://amsterdam.the-hub.net':'nl',
                                 'http://barcelona.the-hub.net':'es',
                                 'http://berlin.the-hub.net':'de',
                                 'http://bogota.the-hub.net':'es',
                                 'http://copenhagen.the-hub.net':'en',
                                 'http://geneva.the-hub.net':'fr',
                                 'http://helsinki.the-hub.net':'fi',
                                 'http://madrid.the-hub.net':'es',
                                 'http://milan.the-hub.net':'it',
                                 'http://montreal.the-hub.net':'fr',
                                 'http://oaxaca.the-hub.net':'es',
                                 'http://porto.the-hub.net':'pt',
                                 'http://prague.the-hub.net':'cs',
                                 'http://rotterdam.the-hub.net':'nl',
                                 'http://shop.rotterdam.the-hub.net':'nl',
                                 'http://roverto.the-hub.net':'it',
                                 'http://riga.the-hub.net':'lv',
                                 'http://saopaulo.the-hub.net':'pt',
                                 'http://stockholm.the-hub.net':'sv',
                                 'http://tampere.the-hub.net':'fi',
                                 'http://vienna.the-hub.net':'en',
                                 'http://zurich.the-hub.net':'de',})
                                 #'http://bergen.the-hub.net':'no',
                                 #'http://kyiv.the-hub.net':'uk',
# deprecated
analytics_no = URLMappings({'http://localhost:8080':None,
                            'http://the-hub.net':"1",
                            'http://wwww.the-hub.net':"1",
                            'http://islington.the-hub.net':"2"})



