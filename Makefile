minisat:
	git clone https://github.com/niklasso/minisat.git
	cd minisat && make config prefix=.
	cd minisat && make
	cd minisat && make install

minisat_to_home_bin: minisat
	mkdir -p ~/bin
	cp minisat/bin/minisat ~/bin/
