init:
	pip install pipenv
	pipenv install --dev

test:
	cd job_search_crm && pipenv run python manage.py test

coverage:
	cd job_search_crm && \
		pipenv run coverage run --source="." manage.py test && \
		pipenv run coverage report
