all: ZhanweiWang-CN.pdf ZhanweiWang.pdf

%.pdf: %.tex
	pdflatex $<

clean:
	rm -rf *.aux *.log *.dvi *.pdf

.PHONY: all clean
