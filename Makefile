.PHONY: test score validate roadmap clean

test:
	python3 -m pytest tests/ -v

score:
	python3 -m src.cli score --features data/features_catalog.json

validate:
	python3 -m src.cli validate --features data/features_catalog.json --baselines data/pm_baselines.json

roadmap:
	python3 -m src.cli roadmap --features data/features_catalog.json --capacity 45

clean:
	rm -rf __pycache__ src/__pycache__ src/*/__pycache__ tests/__pycache__ .pytest_cache
