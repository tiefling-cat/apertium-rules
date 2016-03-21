# apertium-rules
This is a repository for Apertium coding challenge for GSoC 2016, namely Weighted transfer rules.

## Intro
I first heard about Apertium from the info letter of RBMT summer school in Alacant. Honestly saying, I was a bit confused, because I previously thought that rule-based MT was rendered somewhat obsolete by statistical methods. But after that I had a quick chat with Francis in HSE (for Francis: I'm the lamp guy). Francis showed me ukr-rus translation, and I was amazed at the quality of the resulting Russian text. Then we had that meeting about GSoC with Francis and Ekaterina, and after that Francis told me that the idea was to translate in pairs of related languages. Google Translate only has huge parallel corpora of English to smth, so it does double translation through English when asked to translate from non-English to non-English whereas Apertium can provide superior results translating directly.

I asked Fran what ideas for Alacant and GSoC I should look at supposing I'm more of a code monkey than a linguist (and I don't know any languages besides Russian and English anyway). He pointed at this one and I really liked it because, personally, I hate when ambiguity has to be solved by just choosing the first alternative from the list (and I have some history of battling case/number ambiguity for Russian nouns). I also like machine learning and related tasks and did quite a few of ML tasks studying as a linguist at HSE.

## The script
The script opens a file if specified, otherwise it reads from standard input and processess one line at a time. It is assumed that an input line is in Apertium stream format and contains analisys of some line in natural language as output by lt-proc. I have only accounted for multiwords where invariable part goes last. I've tested it with English, namely apertium-en-es.en-es.t1x from apertium-en-es with lines preprocessed by lt-proc with en-es.automorf.bin.

The example input is included in test.txt.

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
