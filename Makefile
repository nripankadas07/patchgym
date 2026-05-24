.PHONY: test demo

test:
	pytest -q

demo:
	patchgym demo
