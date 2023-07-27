SRC_DIR := com/craftinginterpreters/lox
JC := javac
JCFLAGS := -cp $(SRC_DIR)/

.SUFFIXES: .java
.PHONY: all clean

all:
	$(JC) $(JCFLAGS) $(SRC_DIR)/*.java

clean:
	rm com/craftinginterpreters/{lox,tool}/*.class