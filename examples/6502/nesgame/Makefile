all: game

game: game.s main.s ramdata.s visuals.s main.h font2.chr
	65hla $< -o bin -I ../../include -L ../../lib -listvars -listfuncs -listbanks -listsrc

clean:
	rm -rf bin/*
