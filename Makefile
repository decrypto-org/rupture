all: syntax test

syntax:
	# Syntax check python backend
	# TODO: get rid of these exceptions
	find backend -iname '*.py'|grep -v '/env/'|xargs pep8 --ignore E501,E402,E126,E121,W293,E226,E303
	# Syntax check sniffer python
	find sniffer -iname "*.py"|grep -v '/env/'|xargs pep8 --ignore E501,E402,E126,E121,W293,E226
	# Syntax check realtime JS
	find realtime -iname "*.js"|grep -v '/node_modules/'|xargs jshint
	# Syntax check client JS
	find client -iname "*.js"|grep -v '/node_modules/'|grep -v '/dist/'|xargs jshint
	# Syntax check MD files
	# TODO: enable this
	# mdl etc
test:
	cd backend && python manage.py test
	cd sniffer && python test_sniff.py
	cd realtime && npm run test
