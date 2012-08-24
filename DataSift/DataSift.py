import sublime, sublime_plugin, urllib, urllib2, json

class DatasiftCompileCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		csdl = self.view.substr(sublime.Region(0, self.view.size()))
		api_name = self.view.settings().get('datasift_api_name')
		api_key = self.view.settings().get('datasift_api_key')
		validate_endpoint = self.view.settings().get('datasift_validate_endpoint', 'http://api.datasift.com/validate?%s')
		compile_endpoint = self.view.settings().get('datasift_compile_url', 'http://api.datasift.com/compile?%s')
		if not api_name or not api_key:
			sublime.error_message('%s: Username and/or API key not set!' % (__name__))
			return
		options_encoded = urllib.urlencode({
			'csdl': csdl,
			'username': api_name,
			'api_key': api_key
		})
		try:
			http_file = urllib2.urlopen(compile_endpoint%options_encoded)
			result = json.loads(http_file.read())
			sublime.set_clipboard(result['hash'])
			sublime.message_dialog('%s: CSDL compiled successfully, hash %s has been copied into your clipboard.' % (__name__, result['hash']))
		except (urllib2.HTTPError) as (e):
			err = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
			if e.code == 401:
				err = '%s: Authorization failed!' % (__name__)
			if e.code == 400:
				print e
				err = '%s: CSDL validation failed!' % (__name__)
			sublime.error_message(err)
		except (urllib2.URLError) as (e):
			err = '%s: URL error %s contacting API' % (__name__, str(e.reason))
			sublime.error_message(err)
