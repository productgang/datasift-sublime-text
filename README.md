datasift-sublime-text
=====================

DataSift Sublime Text Plugin to validate and compile CSDL, and to consume a sample set of interactions. It also includes syntax highlighting for CSDL.

Installation
------------

Just copy the `DataSift` directory found inside the `datasift-sublime-text` directory into your Sublime Text packages directory located in `~/.config/sublime-text-2/Packages/`.

To set your API username and key, add them to your user preferences. To change the number of interactions retrieved by the Consume Sample command set that in your user preferences.


```javascript
{
	"datasift_api_name": "development",
	"datasift_api_key": "yourapikey",
	"datasift_sample_size": 10,
	"datasift_json_indent": 4
}
```


Usage
-----

The syntax highlighting will automatically active for files with the extension .csdl, alternatively you can activate it by selecting View -> Syntax -> DataSift CSDL.

To validate CSDL code just hit Cmd + Shift + V (Ctrl + Shift + V on Windows / Linux) or alternatively go to Tools -> DataSift -> Validate.

To compile CSDL code just hit Cmd + Shift + C (Ctrl + Shift + C on Windows / Linux) or alternatively go to Tools -> DataSift -> Compile. If your code validates it will automatically copy the stream hash into your clipboard.

To consume a sample number of interactions use the menu option at Tools -> DataSift -> Consume sample interactions. A new file will be opened and the interactions will be inserted one per line as they are received.

You can change the keyboard mapping in the .sublime-keymap files.

These commands are also available in the context menus.
