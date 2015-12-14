# wikipedia-philosophy

A simple Python script that plays Wikipedia's ["Getting to Philosophy" game](https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy) for you.

## Usage
Fire up your favorite terminal emulator, grant the script execute permission, and run the script with the initial Wikipedia page name as the first parameter. On a typical linux distro, the transcript might look like this.

```
$ chmod +x example.py
$ ./example.py "Python (programming language)"
General-purpose programming language
Computer software
Computer
Computer program
Instruction set
Computer architecture
Electronic engineering
Engineering
Mathematics
Quantity
Property (philosophy)
Modern philosophy
Philosophy
---
Took 13 link(s)
```

## Dependencies
The script depends on the following Python libraries that may or may not come pre-installed on your system.
* [Requests](http://docs.python-requests.org/)
* [lxml](http://lxml.de/)
