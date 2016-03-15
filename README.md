# apertium-rules
This is a repository for Apertium coding challenge for GSoC 2016, namely Weighted transfer rules.

## Intro
I first heard about Apertium from the info letter of RBMT summer school in Alacant and I was a bit confused, because I was previously thought that rule-based MT was rendered somewhat obsolete by statistical methods. But then I had a quick chat with Francis and Kira in HSE (for Francis: I'm the lamp guy), and he showed me ukr-rus translation. I was amazed at the good quality of the resulting Russian text. Then we had that meeting about GSoC with Francis and Ekaterina, and after that Francis told me that the idea was to translate in pairs of related languages so the rules can offer smooth transition and as such, Apertium can perform a number of tasks much better than google translate. GT only has huge parallel corpora of English to smth, and as such it does double translation through English asked to transle form non-English to non-English.

I have chosen this task because when I asked Fran what should I look at supposing I'm more of a code monkey than a linguist (and I don't know any languages besides Russian and English anyway), and he pointed at this one and I really liked it because, personally, I hate when the ambiguity has to be solved by just choosing the first alternative from the list (and I have some history of battling case/number ambiguity for Russian nouns). I also like machine learning and related tasks and did quite a bit of it studying as a linguist at HSE.

## The script
The script takes a file if specified, otherwise it reads from standard input and processess one line at a time. It is assumed that input lines are in Apertium stream format and contain analisys of some line in natural language as output by lt-proc. I have only accounted for multiwords where invariable part goes last. I've tested it with English, namely apertium-en-es.en-es.t1x from apertium-en-es with lines preprocessed with en-es.automorf.bin.

The example of input is included in test.txt.

### Usage
```
Usage: ./coverage.py [options] t*x_FILE [INPUT_FILE]

Options:
  -h, --help           show this help message and exit
  -o FILE, --out=FILE  output results to FILE

  output mode:
    Specify what coverages are output, all or LRLM.  If none specified,
    both variants are output.

    -a, --all          output all coverages
    -l, --lrlm         output LRLM coverages
```

### Examples
    $ ./coverage.py -a PATH_TO_t*x_FILE test.txt

will output all coverages by rules from PATH_TO_t*x_FILE for each line in Apertium stream format in test.txt

    $ ./coverage.py -o result.txt PATH_TO_t*x_FILE test.txt

will output all coverages by rules from PATH_TO_t*x_FILE, then only LRLM coverages for each line in Apertium stream format in test.txt to result.txt

    $ echo 'I think that he might have finished it yesterday' | lt-proc PATH_TO_automorph.bin_FILE | ./coverage.py -l PATH_TO_t*x_FILE

will output only LRLM coverages by rules from PATH_TO_t*x_FILE for the line 'I think that he might have finished it yesterday' to standard output.
