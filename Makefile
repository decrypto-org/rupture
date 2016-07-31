all: syntax test

syntax:
	# Syntax check python backend
	# TODO: get rid of these exceptions
	find backend -iname '*.py'|grep -v '/env/'|xargs pep8 --ignore E501,E402,E126,E121
	# Syntax check sniffer python
	find sniffer -iname "*.py"|grep -v '/env/'|xargs pep8 --ignore E501,E226
	# Syntax check realtime JS
	find realtime -iname "*.js"|grep -v '/node_modules/'|xargs jshint
	# Syntax check client JS
	find client -iname "*.js"|grep -v '/node_modules/'|grep -v '/dist/'|grep -v '/lcov-report/'|xargs jshint
	# Syntax check MD files
	mdl --rules ~MD036 etc
test:
	cd backend && python manage.py test
	cd sniffer && nosetests --with-coverage --cover-package=app,sniffer
	cd realtime && npm run test
	cd client && npm run test
	coverage combine backend/.coverage sniffer/.coverage
