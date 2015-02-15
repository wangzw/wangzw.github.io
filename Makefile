all: blog resume

blog: 
	cd blog && make publish

resume:
	cd resume && make
	
.PHONY: all blog resume
