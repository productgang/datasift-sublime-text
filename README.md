datasift-sublime-text
=====================

DataSift Sublime Text Plugin to validate and compile CSDL

Installation
------------

Just copy the DataSift directory into your Sublime Text packages directory (open it by going to Preferences -> Browse Packages...)

To set your API username and key, add them to your user preferences.


```javascript
{
	"datasift_api_name": "development",
	"datasift_api_key": "yourapikey"
}
```


Usage
-----

To compile CSDL code just hit Cmd + Shift + C (Ctrl + Shift + C on Windows / Linux) or alternatively go to Tools -> Datasift Compile. If your coda validates it will automatically copy the stream hash into your clipboard. You can change the keyboard mapping in the .sublime-keymap files.