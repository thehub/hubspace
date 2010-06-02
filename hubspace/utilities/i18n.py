from turbogears.i18n.utils import _get_locale
from turbogears.toolbox.admi18n.catalog import parse, merging
from turbogears.toolbox.admi18n.pygettext import pot_header
import time
import logging

from turbogears import identity
import formencode
import cherrypy
from hubspace.configuration import site_default_lang
import os
import glob
from pkg_resources import resource_filename

from pycountry import languages
languages_dict = dict((a.alpha2, a.name) for a in languages.objects if hasattr(a, 'alpha2'))
languages_list = languages_dict.items()
languages_list.sort(lambda a, b: a[1] > b[1])

from hubspace.model import Location

applogger = logging.getLogger("hubspace")

def get_location_from_base_url():
    try:
        return Location.select(Location.q.url==cherrypy.request.base)[0]
    except IndexError:
        try:
            # try w/o www. Ref: website #89
            url_wo_www = cherrypy.request.base.replace("://www.", "")
            return Location.select(Location.q.url==url_wo_www)[0]
        except IndexError:
            pass
    return Location.get(1)

hubspace_lang_code = lambda location: location.locale + '_'+ location.name.lower().replace(' ', '')

def get_hubspace_user_locale():
    if identity.not_anonymous():
        if identity.current.user.homeplace:
            return hubspace_lang_code(identity.current.user.homeplace)
        else:
            return 'en' # user doesn't have a home location
    else:
        return hubspace_lang_code(get_location_from_base_url())

def install_new_locale(locale):
    applogger.info("installing new locale: %s" % locale)
    tool = tool_instance()
    tool.add_languages([locale])
    tool.compile_message_catalogs(locale)
    applogger.info("installed new locale: %s" % locale)
    return True

def get_hubspace_locale():
    """get the locale based on the home hub of the user or the base_url and the name of the hub
    """
    #if user is not logged in, then reset the locale
    if identity.not_anonymous() and '_' not in cherrypy.session.get('locale', ''):
        cherrypy.session['locale'] = ''
    locale = cherrypy.session.get('locale', '')
    if locale:
        return locale

    if identity.current.anonymous:
        locale = site_default_lang.get(cherrypy.request.base, 'en')
    else:
        locale = get_hubspace_user_locale()

    cherrypy.session['locale'] = locale
    tool = tool_instance()

    if os.path.exists(tool.get_locale_catalog(locale, "messages")):
        if not os.path.exists(tool.get_locale_mo(locale, "messages")):
            tool.compile_message_catalogs(locale)
        #should maybe test for each domain separately?
        return cherrypy.session.get('locale')

    install_new_locale(locale)
    return cherrypy.session.get('locale')

def get_po_path(location=None):
    if location:
        locale = hubspace_lang_code(location)
    else:
        locale = get_hubspace_user_locale()
    return tool_instance().get_locale_catalog(locale, "messages")
    

################## I18N #########################
from turbogears.command.i18n import InternationalizationTool, copy_file
from turbogears.toolbox.admi18n import msgfmt
from turbogears.i18n import tg_gettext
    

def tool_instance(domain="messages"):
    tool = InternTool('1.0.3')
    tool.locale_dir = 'locales'
    tool.domain = domain #not important?
    #override 'add_languages' so that if .mo doesn't exist we create an empty .po with equivalent name and compile a new .mo.
    return tool


class InternTool(InternationalizationTool):
    """Modified TG InternationalizationTool for inplace translation and to deal with multi-domain translation e.g. actually creating locale translations of Turbogears and Formencode validators!
    """
    def add_languages(self, codes):
        """For some reason for Turbogears.po and Formencode.po a version was never created and put in the new locale dir. Instead they tried to copy the .mo files and if they didn't exist did nothing - this wouldn't allow a user to contribute a translation which seems wrong. Lets instead copy the .po file if there is one, and otherwise copy the .mo.
        """
        app_potfile = self.get_potfile_path()
        if not os.path.isfile(app_potfile):
            print "Run 'tg-admin i18n collect' first to create", app_potfile
            return
        for code in codes:
            app_catalog = self.get_locale_catalog(code)
            langdir = os.path.dirname(app_catalog)
            if not os.path.exists(langdir):
                os.makedirs(langdir)
            same_lang = self.same_lang_files(code)
            if same_lang:
                for fname in same_lang:
                    self._copy_file_withcheck(fname, os.path.join(langdir, fname.split('/')[-1]))
                return
            self.create_pofile_for_module(formencode.api.get_localedir(), code, 'FormEncode')
            self.create_pofile_for_module(resource_filename("turbogears.i18n", "data"), code, 'TurboGears')
            self._copy_file_withcheck(app_potfile, app_catalog)


    def create_pofile_for_module(self, base_localedir, code, domain):
        """If a po file already exists (for that code) in the module locale directory - copy that over to the applications locales directory, otherwise copy the pot file to a new directory.
        """
        catalog = self.get_locale_catalog(code=code, domain=domain)
        source_po = os.path.join(base_localedir, code, "LC_MESSAGES", "%s.po"%domain)
        if not os.path.exists(source_po):
            source_po = os.path.join(base_localedir, code.split('_')[0], "LC_MESSAGES", "%s.po"%domain)
        if os.path.exists(source_po):
            self._copy_file_withcheck(source_po, catalog)        
            return 
            
        source_po = os.path.join(base_localedir, "%s.pot"%domain)
        if not os.path.exists(catalog):
            cat = open(catalog, 'w')
            timestamp = time.strftime('%Y-%m-%d %H:%M')
            t = {'time': timestamp, 'version': '1.5', 'charset':'utf-8'}
            cat.write(pot_header % t)
            cat.close()
        merging(parse(source_po), catalog)

    def _copy_file_withcheck(self, sourcefile, targetfile):
        if not (os.path.exists(targetfile)):
            copy_file(sourcefile, targetfile)
            print 'Copy', sourcefile, 'to', targetfile
        else:
            print "File %s exists, use --force to override" % targetfile
            
    def get_locale_catalog(self, code, domain=None):
        if not domain:
            domain = self.domain
        return os.path.join(self.locale_dir, code, 'LC_MESSAGES', '%s.po' % domain)

    def get_locale_mo(self, code, domain=None):
        if not domain:
            domain = self.domain
        return os.path.join(self.locale_dir, code, 'LC_MESSAGES', '%s.mo' % domain)

    def get_potfile_path(self, domain=None):
        if not domain:
            domain = self.domain
        return os.path.join(self.locale_dir, '%s.pot' % self.domain)
    
    def compile_message_catalogs(self, locale='*'):
        """ works for single locale or all locales - just for efficiency when recompiling a single locale
        """
        for fname in glob.glob(self.locale_dir +'/'+ locale + '/LC_MESSAGES/*.po'):
            dest = fname.replace('.po','.mo')
            msgfmt.make(fname, dest)
            if os.path.exists(dest):
                print 'Compiled %s OK' % fname
            else:
                print 'Compilation of %s failed!' % fname

    def list_message_catalogs(self, locale=None):
        files = []
        if not locale:
            for name in glob.glob(self.locale_dir + '/*'):
                if os.path.isdir(name):
                    fname = os.path.join(name, 'LC_MESSAGES', '%s.po' % self.domain)
                    if os.path.isfile(fname):
                        files.append(fname)
        else:
            for name in glob.glob(self.locale_dir +'/'+ locale + '/LC_MESSAGES'):
                if os.path.isdir(name):
                    fname = os.path.join(name, '%s.po' % self.domain)
                    if os.path.isfile(fname):
                        files.append(fname)
        return files

    def same_lang_files(self, locale):
        """probably a better idea to stick with the existing local of the users home location unless a new local is explicity created for a location e.g. en_berlin
        """
        try:
            lang_code = locale.split('_')[0]
        except:
            lang_code = locale
        directory = None
        for name in glob.glob(self.locale_dir +'/'+ lang_code + '_*/LC_MESSAGES'):
            if os.path.isdir(name):
                directory = name
                break
        if not directory:
            return None 
        files = []
        for file_name in glob.glob(directory + '/*.po'):        
            files.append(file_name)
        return files
