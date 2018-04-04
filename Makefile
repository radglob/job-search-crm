init:
	pip install pipenv
	pipenv install --dev

test:
	cd job_search_crm && pipenv run python manage.py test
