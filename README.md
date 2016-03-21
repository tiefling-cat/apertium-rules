# apertium-rules
This is a repository for Apertium coding challenge for GSoC 2016, namely Weighted transfer rules.

## Intro
I first heard about Apertium from the info letter of RBMT summer school in Alacant. Honestly saying, I was a bit confused, because I previously thought that rule-based MT was rendered somewhat obsolete by statistical methods. But after that I had a quick chat with Francis in HSE. Francis showed me ukr-rus translation, and I was amazed at the quality of the resulting Russian text. Then we had that meeting about GSoC with Francis and Ekaterina, and after that Francis told me that the main idea was to translate in pairs of related languages. Google Translate only has huge parallel corpora of English to smth, so it does double translation through English when asked to translate from non-English to non-English whereas Apertium can provide superior results translating directly. I also see that there are pairs of not-so-closely-related languages, but I imagine they might also be useful because of the direct nature of the translation, just a bit more tricky to elaborate.

I asked Francis what ideas for Alacant and GSoC I should look at supposing I'm more of a code monkey than a linguist (and I don't know any languages besides Russian and English anyway). He pointed at this one and I really liked it because, personally, I hate when ambiguity has to be solved by just choosing the first alternative from the list (and I have some history of battling case/number ambiguity of Russian nouns). I also love machine learning and related tasks and did quite a few of ML tasks studying as a linguist at HSE.

## The script
### Input
The script reads lines from the input file if specified, otherwise it reads from standard input, and processess one line at a time. It is assumed that an input line is either contains analisys of some line in natural language as output by lt-proc or the output of Apertium POS tagger (disambiguated forms).

#### Example input
* test_morpho.txt is an output from lt-proc.
* test_pos.txt is a faked output from POS tagger.

#### Other input limitations
* The script only accounts for multiwords where invariable part goes last.
* The script doesh't handle superblanks.

### Output
For each line in input file, the script outputs the line as is and the obtained coverages in following format:

    (96 I) (121 think that) (96 he) (199 might have finished it) (219 yesterday)

The numbers are given to the rules in order they appear in the rules file.

### Usage
```
Usage: ./coverage.py [-a|-l] [-o OUTPUT_FILE] -r RULES_FILE [INPUT_FILE]

Options:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --out=OUTPUT_FILE
                        output results to OUTPUT_FILE.
  -r RULES_FILE, --rules=RULES_FILE
                        use RULES_FILE t*x file for calculating coverages.

  output mode:
    Specify what coverages to output, all or LRLM.  If none specified,
    outputs both variants.

    -a, --all           output all coverages
    -l, --lrlm          output LRLM coverages
```

### Tests
So far I've tested it with English, namely apertium-en-es.en-es.t1x from apertium-en-es with lines preprocessed by lt-proc with en-es.automorf.bin.

### Examples
    $ ./coverage.py -a -r PATH_TO_t*x_FILE test.txt

will output all coverages by rules from PATH_TO_t*x_FILE for each line in test.txt to standard output.

    $ ./coverage.py -o result.txt -r PATH_TO_t*x_FILE test.txt

will output all coverages by rules from PATH_TO_t*x_FILE, then only LRLM coverages, for each line in test.txt to result.txt.

    $ echo 'I think that he might have finished it yesterday' | lt-proc PATH_TO_automorph.bin_FILE | ./coverage.py -l -r PATH_TO_t*x_FILE

will output only LRLM coverages by rules from PATH_TO_t*x_FILE for the line 'I think that he might have finished it yesterday' to standard output.
