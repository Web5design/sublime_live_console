Sublime Text 3 : Live Console
==========================

A [sublime live](https://github.com/sligodave/sublime_live) view that lists all available "sublime consoles".
A "sublime console" is a view of buttons that map to Sublime Text 3 commands.
They are configured by placing a file called "XXXX.sublime-console" in your plugins package directory.

See [sublime live console example](https://github.com/sligodave/sublime_live_console_example) for an example console.

Note: If there is only one console found by the command, then it will be displayed, rather than showing the user a list of available consoles.

The provided command can also be given parameters to explicitly tell it what console to use and thus by pass the list of available consoles.

The idea behind this plugin is:
* Plugin developers could provide a console for the commands available with their plugins.
* Users could also create their own XXXX.sublime-console files that pull together functionality they'd like in one place.

## Install:

You'll need Sublime Text 3

Clone this repository into your Sublime Text *Packages* directory.

	OSX:
	    ~/Library/Application Support/Sublime Text 3
	Linux:
        ~/.config/sublime-text-3/Packages
    Windows:
        %APPDATA%\Sublime Text 3\Packages

    git clone https://github.com/sligodave/sublime_live_console.git LiveConsole
    cd LiveConsole
    git submodule init
    git submodule update

Open Sublime Text 3

Open Sublime Text 3's Python Prompt and run the todo load command:

	CTRL + `
	Type: window.run_command('live_console')

You can of course also create a key mapping to load the live color schemes page.

## Issues / Suggestions:

Send on any suggestions or issues.

## Copyright and license
Copyright 2013 David Higgins

[MIT License](LICENSE)
