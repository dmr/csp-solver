minisat:
	git clone https://github.com/niklasso/minisat.git
	cd minisat && make config prefix=.
	cd minisat && make
	cd minisat && make install
	cp minisat/bin/minisat /usr/local/bin/
