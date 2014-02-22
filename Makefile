MARKDOWN = pandoc -s --highlight-style pygments --from markdown_github+pandoc_title_block --to html

all: $(patsubst %.md,%.html,$(wildcard *.md)) Makefile

clean:
	rm -f $(patsubst %.md,%.html,$(wildcard *.md))
	rm -f *.bak *~

%.html: %.md
	$(MARKDOWN) --template $(patsubst %.md,%.tpl,$<) $< --output $@
