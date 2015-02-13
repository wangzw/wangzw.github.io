all: blog resume

blog: 
	cd blog && make html

resume:
	cd resume && make
	
.PHONY: all blog resume
