import sublime, sublime_plugin, sys, os
sys.path[0:0] = [os.path.join(os.path.dirname(__file__), "lib"),]
import datasift

def get_datasift_user(settings):
    api_name = settings.get('datasift_api_name')
    api_key = settings.get('datasift_api_key')
    if not api_name or not api_key:
        return False
    return datasift.User(api_name, api_key)

class DatasiftValidateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        csdl = self.view.substr(sublime.Region(0, self.view.size()))
        try:
            datasift_user = get_datasift_user(self.view.settings())
            if not datasift_user:
                sublime.error_message('%s: Username and/or API key not set!' % (__name__))
            else:
                datasift_user.create_definition(csdl).validate()
                sublime.message_dialog('%s: CSDL validated successfully' % (__name__))
        except datasift.InvalidDataError as e:
            sublime.error_message(str(e))
        except datasift.CompileFailedError as e:
            sublime.error_message('Validation failed: %s' % str(e))
        except datasift.APIError as (e, c):
            sublime.error_message(str(e))

class DatasiftCompileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        csdl = self.view.substr(sublime.Region(0, self.view.size()))
        try:
            datasift_user = get_datasift_user(self.view.settings())
            if not datasift_user:
                sublime.error_message('%s: Username and/or API key not set!' % (__name__))
            else:
                definition = datasift_user.create_definition(csdl)
                stream_hash = definition.get_hash()
                sublime.set_clipboard(stream_hash)
                sublime.message_dialog('%s: CSDL compiled successfully, hash %s has been copied into your clipboard.' % (__name__, stream_hash))
        except datasift.InvalidDataError as e:
            sublime.error_message(str(e))
        except datasift.CompileFailedError as e:
            sublime.error_message('Compilation failed: %s' % str(e))
        except datasift.APIError as (e, c):
            sublime.error_message(str(e))
