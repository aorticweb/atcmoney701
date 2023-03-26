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
	docker run --rm atcmoney_test pytest ./libs/providers/smoke_tests

build_and_run_provider_tests: build_python_test provider_tests

common_tests:
	# TODO:
	# add testing coverage
	docker run --rm atcmoney_test pytest ./libs/common/tests

build_and_run_common_tests: build_python_test common_tests


build_cli_test:
	docker build . -t atcmoney_cli_test -f dockerfiles/cli_test.dockerfile

cli_tests:
	# TODO:
	# add testing coverage
	docker run  --rm atcmoney_cli_test  pytest ./cli/atcmoney_cli/tests --pdb

build_and_run_cli_tests: build_cli_test cli_tests