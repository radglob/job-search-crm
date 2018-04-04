init:
	pip install pipenv
	pipenv install --dev

test:
	pipenv run python job_search_crm/manage.py test
