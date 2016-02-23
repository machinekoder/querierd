all:
	@echo "Nothing to build"

install_module:
	@echo "Installing Python module"
	python setup.py install --record files.txt

install_service:
	@echo "Installing QuerierD service"
	cp lib/systemd/system/querierd.service /lib/systemd/system
	systemctl daemon-reload
	systemctl start querierd.service
	systemctl enable querierd.service

install: install_module install_service

uninstall_module:
	@echo "Removing Python module"
	cat files.txt | xargs rm -rf
	rm files.txt

uninstall_service:
	@echo "Uninstalling QuerierD service"
	systemctl stop querierd.service
	systemctl disable querierd.service
	rm /lib/systemd/system/querierd.service

uninstall: uninstall_module uninstall_service
