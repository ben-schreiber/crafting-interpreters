SRC_DIR := com/craftinginterpreters/lox
JC := javac
JCFLAGS := -cp $(SRC_DIR)/

.SUFFIXES: .java
.PHONY: all clean

jlox:
	$(JC) $(JCFLAGS) $(SRC_DIR)/*.java

tool:
	$(JC) com/craftinginterpreters/tool/*.java

all: jlox tool

clean:
	rm com/craftinginterpreters/{lox,tool}/*.class