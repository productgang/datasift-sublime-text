import sublime, sublime_plugin, sys, os, json, string, threading
sys.path[0:0] = [os.path.join(os.path.dirname(__file__), "lib"),]
import datasift

class DatasiftThread(threading.Thread):
    operation = ''

    def __init__(self, operation, command, data):
        self.result = False
        self.operation = operation
        self._command = command
        self._data = data
        threading.Thread.__init__(self)

    def run(self):
        self.result = self._command.execute(self._data)

class DatasiftCommand(sublime_plugin.TextCommand):
    def _get_settings(self):
        retval = {
            'api_name': False,
            'api_key': False,
            'sample_size': 10,
            'json_indent': None
        }
        settings = self.view.settings()
        for key in retval:
            retval[key] = settings.get('datasift_%s' % key) or retval[key]
        if not retval['api_name'] or not retval['api_key']:
            sublime.error_message('%s: Username and/or API key not set!' % (__name__))
            return False
        return retval

    def _check_thread(self, thread, i = 0):
        if thread.is_alive():
            seq = ['/', '\\']
            if i >= len(seq):
                i = 0
            operation = 'Running Datasift command'
            if len(thread.operation) > 0:
                operation = thread.operation
            self.view.set_status('datasift', '[%s] DataSift: %s' % (seq[i], operation))
            sublime.set_timeout(lambda: self._check_thread(thread, i + 1), 100)
            return

        self.view.erase_status('datasift')
        if thread.result == False:
            sublime.error_message('An unknown error occurred')
        elif thread.result['success'] == False:
            sublime.error_message(thread.result['message'])
        else:
            if 'clipboard' in thread.result['data']:
                sublime.set_clipboard(thread.result['data']['clipboard'])
            sublime.message_dialog(thread.result['message'])

    def _result(self, success, message, data = {}):
        return { 'success': success, 'message': message, 'data': data }

    def _append_text(self, view, text):
        try:
            edit = view.begin_edit('datasift')
            view.insert(edit, view.size(), text)
            view.end_edit(edit)
        except RuntimeError, e:
            if string.find(str(e), 'Must call on main thread') > -1:
                sublime.set_timeout(lambda: self._append_text(view, text), 1)
            else:
                raise

class DatasiftValidateCommand(DatasiftCommand):
    def run(self, edit):
        csdl = self.view.substr(sublime.Region(0, self.view.size()))
        thread = DatasiftThread('Validating CSDL', self, { 'settings': self._get_settings(), 'csdl': csdl })
        thread.start()
        self._check_thread(thread)

    def execute(self, data):
        try:
            datasift_user = datasift.User(data['settings']['api_name'], data['settings']['api_key'])
            if not datasift_user:
                return self._result(False, '%s: Failed to create the Datasift user object!' % (__name__))
            else:
                datasift_user.create_definition(data['csdl']).validate()
                return self._result(True, '%s: CSDL validated successfully' % (__name__))
        except datasift.InvalidDataError as e:
            return self._result(False, str(e))
        except datasift.CompileFailedError as e:
            return self._result(False, 'CSDL syntax error: %s' % str(e))
        except datasift.APIError as (e, c):
            return self._result(False, str(e))

class DatasiftCompileCommand(DatasiftCommand):
    def run(self, edit):
        csdl = self.view.substr(sublime.Region(0, self.view.size()))
        thread = DatasiftThread('Compiling CSDL', self, { 'settings': self._get_settings(), 'csdl': csdl })
        thread.start()
        self._check_thread(thread)

    def execute(self, data):
        try:
            datasift_user = datasift.User(data['settings']['api_name'], data['settings']['api_key'])
            if not datasift_user:
                return self._result(False, '%s: Failed to create the Datasift user object!' % (__name__))
            else:
                stream_hash = datasift_user.create_definition(data['csdl']).get_hash()
                return self._result(True, '%s: CSDL compiled successfully, hash %s has been copied into your clipboard.' % (__name__, stream_hash), { 'clipboard': stream_hash })
        except datasift.InvalidDataError as e:
            return self._result(False, str(e))
        except datasift.CompileFailedError as e:
            return self._result(False, 'CSDL syntax error: %s' % str(e))
        except datasift.APIError as (e, c):
            return self._result(False, str(e))

class DatasiftConsumeSampleCommand(DatasiftCommand):
    def run(self, edit):
        csdl = self.view.substr(sublime.Region(0, self.view.size()))
        new_view = self.view.window().new_file()
        new_view.set_name('DataSift Sample')
        new_view.set_syntax_file('Packages/JavaScript/JSON.tmLanguage')
        thread = DatasiftThread('Consuming sample interactions', self, { 'settings': self._get_settings(), 'csdl': csdl, 'view': new_view })
        thread.start()
        self._check_thread(thread)

    def execute(self, data):
        try:
            datasift_user = datasift.User(data['settings']['api_name'], data['settings']['api_key'])
            if not datasift_user:
                return self._result(False, '%s: Failed to create the Datasift user object!' % (__name__))
            else:
                consumer = datasift_user.create_definition(data['csdl']).get_consumer(DatasiftEventHandler(self, data), 'http')
                consumer.consume()
                consumer.run_forever()
                plural = ''
                if data['settings']['sample_size'] != 1:
                    plural = 's'
                return self._result(True, 'Finished consuming %s sample interaction%s' % (data['settings']['sample_size'], plural))
        except datasift.InvalidDataError as e:
            return self._result(False, str(e))
        except datasift.CompileFailedError as e:
            return self._result(False, 'CSDL syntax error: %s' % str(e))
        except datasift.APIError as (e, c):
            return self._result(False, str(e))

class DatasiftEventHandler(datasift.StreamConsumerEventHandler):
    def __init__(self, command, data):
        self.command = command
        self.data = data
        self.counter = data['settings']['sample_size']
        self.first = True

    def on_connect(self, consumer):
        self.command._append_text(self.data['view'], '[\n')

    def on_interaction(self, consumer, interaction, hash):
        suffix = ','
        if self.counter == 1:
            suffix = ''
        self.command._append_text(self.data['view'], '%s%s\n' % (json.dumps(interaction, indent=(self.data['settings']['json_indent'] or None)), suffix))
        self.counter -= 1
        if self.counter == 0:
            consumer.stop()

    def on_warning(self, consumer, message):
        self.command._append_text('WARNING: %s' % (message))

    def on_error(self, consumer, message):
        self.command._append_text('ERR: %s' % (message))

    def on_disconnect(self, consumer):
        self.command._append_text(self.data['view'], ']\n')
