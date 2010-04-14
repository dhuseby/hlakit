all: game

game: game.s
	../../../hlakit.py --platform=NES --include=../../../include/cpu --include=../../../include/platform $<

clean:
	rm -rf bin/*
