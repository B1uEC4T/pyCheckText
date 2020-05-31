# pyCheckText
![flake8](https://github.com/da1910/pyCheckText/workflows/flake8/badge.svg) ![Tox](https://github.com/da1910/pyCheckText/workflows/Tox/badge.svg)
## Requirements
* Python 3.8
* python-dateutil

## Invocation
Run /scripts/checktext.py, arguments are as follows
* --folder_path Path to a folder, check all python files within the folder
* --file_path Path to a single python file which will be checked
* --alias List of aliased function names, provide the alias and then the target. 
  * Example: --alias _ gettext
* --translation_path Path to the locale folder where translations are found. Follows python gettext.find conventions
* --domain Name of translation domain. Follows python gettext.find convensions
* --languages List of language codes to verify
