dist_dir = dist

test:
	py.test --doctest-modules graphiit tests

dist: build-dist
	twine upload $(dist_dir)/*

test-dist: build-dist
	twine upload --repository-url https://test.pypi.org/legacy/ $(dist_dir)/*

build-dist: clean-dist
	python setup.py sdist bdist_wheel --dist-dir=$(dist_dir)

clean-dist:
	rm -rf $(dist_dir)
