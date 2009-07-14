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


title = URLMappings({'http://amsterdam.the-hub.net': 'The Hub Amsterdam',
                     'http://bayarea.the-hub.net': 'The Hub Bay Area',
                     'http://berlin.the-hub.net': 'The Hub Berlin',
                     'http://berkeley.the-hub.net': 'The Hub Berkeley',
                     'http://bombay.the-hub.net':'The Hub Bombay',
                     'http://bristol.the-hub.net':'The Hub Bristol',
                     'http://brussels.the-hub.net':'The Hub Brussels',
                     'http://cairo.the-hub.net':'The Hub Cairo',
                     'http://halifax.the-hub.net':'The Hub Halifax',
                     'http://islington.the-hub.net':'The Hub Islington',
                     'http://johannesburg.the-hub.net':'The Hub Johannesburg',
                     'http://kingscross.the-hub.net':"The Hub King's Cross",
                     'http://milan.the-hub.net':'The Hub Milan',
                     'http://madrid.the-hub.net':'The Hub Madrid',
                     'http://porto.the-hub.net':'The Hub Porto',
                     'http://rotterdam.the-hub.net':'The Hub Rotterdam',
                     'http://saopaulo.the-hub.net':'The Hub Sao Paulo',
                     'http://sanfrancisco.the-hub.net':'The Hub San Francisco',
                     'http://southbank.the-hub.net':'The Hub South Bank',
                     'http://stockholm.the-hub.net':'The Hub Stockholm',
                     'http://telaviv.the-hub.net':'The Hub Telaviv',
                     'http://vienna.the-hub.net':'The Hub Vienna',
                     'http://toronto.the-hub.net':'Centre for Social Innovation',
                     'http://members.socialinnovation.ca':'Centre for Social Innovation',
                     'http://members.themonksyard.co.uk':'The Monks Yard',
                     'http://localhost:8080':'The Hub',
                     'http://hubspacedev.the-hub.net':'The Hub',
                     'http://members.the-hub.net':'The Hub',
                     'http://test.the-hub.net':'The Hub',
                     'http://test2.the-hub.net':'The Hub',
                     'http://testregion.the-hub.net':'The Hub',}
)

site_folders = URLMappings({'http://localhost:8080':'site_templates.hubspace.',
                            'http://members.socialinnovation.ca':'site_templates.toronto.',
                            'http://toronto.the-hub.net':'site_templates.toronto.'})

site_default_lang = URLMappings({'http://localhost:8080':'en',
                                 'http://berlin.the-hub.net':'de',
                                 'http://rotterdam.the-hub.net':'nl',
                                 'http://amsterdam.the-hub.net':'nl',
                                 'http://madrid.the-hub.net':'es',
                                 'http://saopaulo.the-hub.net':'pt',
                                 'http://porto.the-hub.net':'pt',
                                 'http://milan.the-hub.net':'it',
                                 'http://stockholm.the-hub.net':'sv'})

analytics_no = URLMappings({'http://localhost:8080':None,
                            'http://the-hub.net':"1",
                            'http://wwww.the-hub.net':"1",
                            'http://islington.the-hub.net':"2"})



