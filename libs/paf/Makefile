NAME = paf
# CXX = clang++ -O3 -flto -Wall -Wextra -Weffc++ -std=c++11 -pedantic -Wno-unused-parameter
CXX = g++ -O3 -flto -Wall -Wextra -Weffc++ -std=c++11 -pedantic -Wno-unused-parameter # with g++-9, the produced executable is ~24% slower to grow patterns than with clang++-9; however ~2% faster to amalgamate them
# CXX = g++ -g -Og -Wall -Wextra -Weffc++ -std=c++11 -pedantic -Wno-unused-parameter
EXTRA_CXXFLAGS = -lboost_program_options
HELP2MAN = help2man -n 'Grow patterns, which hold in a fuzzy tensor, hierarchically amalgamate them and select a subset of the built patterns to sum up this tensor, a disjunctive box cluster model' -N
SRC = src/utilities src/core
DEPS = $(wildcard $(patsubst %,%/*.h,$(SRC))) Parameters.h Makefile
CODE = $(wildcard $(patsubst %,%/*.cpp,$(SRC)))
OBJ = $(patsubst %.cpp,%.o,$(CODE))
ALL = $(DEPS) $(CODE) $(NAME).1.gz COPYING INSTALL README

.PHONY: man install clean dist-gzip dist-bzip2 dist-xz dist
.SILENT: $(NAME) man install clean dist-gzip dist-bzip2 dist-xz dist

%.o: %.cpp $(DEPS)
	$(CXX) -c -o $@ $<

$(NAME): $(OBJ)
	$(CXX) -o $@ $^ $(EXTRA_CXXFLAGS)
	echo "$(NAME) built!"

man:
	$(HELP2MAN) ./$(NAME) | gzip > $(NAME).1.gz

install: $(NAME)
	mv $(NAME) /usr/bin
	cp $(NAME).1.gz /usr/share/man/man1/
	echo "$(NAME) installed!"

clean:
	rm -f $(patsubst %,%/*.o,$(SRC)) $(patsubst %,%/*~,$(SRC)) *~

dist-gzip:
	tar --format=posix --transform 's,^,$(NAME)/,' -czf $(NAME).tar.gz $(ALL)

dist-bzip2:
	tar --format=posix --transform 's,^,$(NAME)/,' -cjf $(NAME).tar.bz2 $(ALL)

dist-xz:
	tar --format=posix --transform 's,^,$(NAME)/,' -cJf $(NAME).tar.xz $(ALL)

dist: dist-bzip2
