.PHONY : clean, default, publish

TEX_FILES   = ms
TMP_SUFFS   = pdf aux bbl blg log dvi ps eps out ent
LATEX       = pdflatex -interaction=nonstopmode -halt-on-error
SUFF        = pdf
RM_TMP      = $(foreach d, ${TEX_FILES}, rm -rf $(foreach suff, ${TMP_SUFFS}, ${d}.${suff})) msNotes.bib
CHECK_RERUN = grep Rerun ms.log
FIGURES     = $(patsubst %.py,%.pdf,$(wildcard figures/*.py))
TECTONIC    = $(shell command -v tectonic >/dev/null && echo true || echo false )

default: ms.pdf

ms.pdf: ms.tex bib.bib $(FIGURES)
	# Generate links to current git commit
	python gen_links.py
	# Compile the paper with either tectonic or pdflatex
	if [ "${TECTONIC}" = "true" ]; then\
		tectonic ms.tex --print --keep-logs;\
	else\
		${LATEX} ms.tex;\
		( ${CHECK_RERUN} && ${LATEX} ms.tex ) || echo "Done.";\
		( ${CHECK_RERUN} && ${LATEX} ms.tex ) || echo "Done.";\
		( ${CHECK_RERUN} && ${LATEX} ms.tex ) || echo "Done.";\
	fi

clean:
	# Remove temporaries and output
	$(RM_TMP)
	rm -rf $(FIGURES)

figures/%.pdf: figures/%.py
	# Generate all figures
	cd $(<D); python $(<F) 2>&1