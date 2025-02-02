install-requirements:
	@echo "Installing requirements..."
	@pip install -r requirements.txt

.PHONY: run-ui
run-ui:
	@echo "Running UI..."
	@python ./ui/main.py
