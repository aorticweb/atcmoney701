format:
	isort .
	black .

lint:
	flake8
	black . --check
	isort . --check-only

build_python_test:
	docker build . -t atcmoney_test -f dockerfiles/python_test.dockerfile

provider_tests:
	# TODO:
	# add testing coverage
	docker run --rm atcmoney_test pytest ./providers/smoke_tests

build_and_run_provider_tests: build_python_test provider_tests
