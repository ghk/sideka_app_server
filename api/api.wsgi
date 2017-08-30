activate_this = '/usr/lib/ckan/default/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from api.api import app as application 
