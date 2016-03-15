#! /usr/bin/python3

import re, sys
import xml.etree.ElementTree as ET
from optparse import OptionParser

ifname = 'apertium-en-es.en-es.t1x'
any_tag_re = '<[a-z0-9-]+>'
any_num_of_any_tags_re = '({})*'.format(any_tag_re)
any_num_of_any_tags_line_re = '^{}$'.format(any_num_of_any_tags_re)
default_cat = ['default']

example_lines = [
    '^I/I<num><mf><sg>/prpers<prn><subj><p1><mf><sg>$ '
    '^have/have<vbhaver><inf>/have<vbhaver><pres>/have<vblex><inf>/have<vblex><pres>$ '
    '^a/a<det><ind><sg>$ ^cat/cat<n><sg>$ ^and/and<cnjcoo>$ '
    '^a/a<det><ind><sg>$ ^rat/rat<n><sg>$',
    '^I/I<num><mf><sg>/prpers<prn><subj><p1><mf><sg>$ '
    '^think that/think<vblex><inf># that/think<vblex><pres># that$ '
    '^he/prpers<prn><subj><p3><m><sg>$ ^might/might<vaux><inf>$ '
    '^have/have<vbhaver><inf>/have<vbhaver><pres>/have<vblex><inf>/have<vblex><pres>$ '
    '^finished/finish<vblex><past>/finish<vblex><pp>$ '
    '^it/prpers<prn><subj><p3><nt><sg>/prpers<prn><obj><p3><nt><sg>$ '
    '^yesterday/yesterday<adv>$'
    ]

def tag_pattern_to_re(tag_pattern):
    """
    Get a tag pattern as specified in xml.
    Output a regex line that matches what 
    is specified by the pattern.
    """
    if tag_pattern == '': # no tags
        return '^$'
    re_line = '^'
    tag_sequence = tag_pattern.split('.')
    for tag in tag_sequence[:-1]:
        # any tag
        if tag == '*':
            re_line = re_line + any_tag_re
        # specific tag
        else:
            re_line = re_line + '<{}>'.format(tag)
    # any tags at the end
    if tag_sequence[-1] == '*':
        re_line = re_line + any_num_of_any_tags_re
    # specific tag at the end
    else:
        re_line = re_line + '<{}>'.format(tag_sequence[-1])
    return re_line + '$'

def get_cat_dict(transtree):
    """
    Get an xml with transfer rules.
    Build a makeshift inverted index of the rules.
    """
    root = transtree.getroot()
    cat_dict = {}
    for def_cat in root.find('section-def-cats').findall('def-cat'):
        for cat_item in def_cat.findall('cat-item'):
            tag_re = tag_pattern_to_re(cat_item.attrib.get('tags', '*'))
            lemma = cat_item.attrib.get('lemma', '')
            if tag_re not in cat_dict:
                cat_dict[tag_re] = {}
            if lemma not in cat_dict[tag_re]:
                cat_dict[tag_re][lemma] = []
            cat_dict[tag_re][lemma].append(def_cat.attrib['n'])
    return cat_dict

def get_cats_by_line(line, cat_dict):
    """
    Return all possible categories for ALU.
    """
    return [(ALU.split('/', 1)[0].lstrip('^'), get_cats_by_ALU(ALU, cat_dict)) 
                for ALU in re.findall(r'\^.*?\$', line)]

def get_cats_by_ALU(ALU, cat_dict):
    """
    Return set of all possible categories for ALU.
    """
    divided = ALU.lstrip('^').rstrip('$').split('/')
    lemma = divided[0]
    LU_list = divided[1:]
    return set(sum([get_cats_by_LU(LU, cat_dict, lemma) for LU in LU_list], []))

def get_cats_by_LU(LU, cat_dict, lemma):
    """
    Return list of all possible categories for LU.
    """
    partial_lemma = LU.split('<', 1)[0]
    tags = LU[len(partial_lemma):].split('#', 1)[0]
    cat_list = []
    for tag_re in cat_dict:
        if re.match(tag_re, tags):
            cat_list.extend((cat_dict[tag_re].get(lemma, [])))
            cat_list.extend((cat_dict[tag_re].get('', [])))
    if cat_list:
        return cat_list
    return default_cat

def get_pattern_FST(transtree):
    """
    Get an xml with transfer rules.
    Build an improvised pattern FST with nested dictionaries.
    """
    root = transtree.getroot()
    pattern_FST = [{}, None]
    for i, rule in enumerate(root.find('section-rules').findall('rule')):
        curr_level = pattern_FST
        for pattern_item in rule.find('pattern').findall('pattern-item'):
            item_cat = pattern_item.attrib['n']
            if not item_cat in curr_level[0]:
                curr_level[0][item_cat] = [{}, None]
            curr_level = curr_level[0][item_cat]
        curr_level[1] = (str(i), rule.attrib.get('comment', ''))
    return pattern_FST

def rebuild_pattern_r(pattern_FST):
    """
    Recursively rebuild all patterns from pattern FST, just in case.
    """
    rule_list = []
    if pattern_FST[0] != {}:
        for pattern_item in pattern_FST[0]:
            pattern_list = [[pattern_item] + pattern_tail 
                for pattern_tail in rebuild_pattern_r(pattern_FST[0][pattern_item])]
            rule_list.extend(pattern_list)
    if pattern_FST[1] is not None:
        rule_list.append([pattern_FST[1]])
    return rule_list

def output_patterns(pattern_FST):
    """
    Output all patterns to file in linear fashion.
    """
    pattern_list = rebuild_pattern_r(pattern_FST)
    pattern_list.sort(key=lambda x: int(x[-1][0]))
    with open('rules.txt', 'w', encoding='utf-8') as rfile:
        for pattern in pattern_list:
            rfile.write('{: <4}\n  {}\n  {}\n'.format(pattern[-1][0], ' '.join(pattern[:-1]), pattern[-1][1]))

def calculate_coverage_r(pattern_FST, line, state):
    """
    Recursively find all possible pattern combinations
    for preprocessed line where each word has a list
    of categories assigned to it.
    
    Output is a list of lists, each list consists
    of elements of (type, word/num, cat/comm),
    where type is either 'w' (word) or 'r' (rule).
    
    If type is 'w' then the next two items are the word
    and the category assigned to it respectively.

    If type is 'r' then the next two items are the rule
    number and its commentary from the xml representation.

    The rule entry in the list marks the end of pattern
    for this rule.

    line is current line with ambiguous categories assigned
    to words, state is a state of our makeshift FST represented
    by its level.
    """
    if not line:
        if state[1] is not None:
            return [[('r',) + state[1]]]
        return []

    coverage_list = []
    current_item = line[0]

    for cat in (current_item[1] & set(state[0].keys())):
        pattern_list = [[('w', current_item[0], cat)] + pattern_tail for pattern_tail in calculate_coverage_r(pattern_FST, line[1:], state[0][cat])]
        coverage_list.extend(pattern_list)

    if state[1] is not None:
        pattern_list = [[('r',) + state[1]] + pattern_tail for pattern_tail in calculate_coverage_r(pattern_FST, line, pattern_FST)]
        coverage_list.extend(pattern_list)
    return coverage_list

def parse_coverage_list(coverage_list):
    """
    Get list of lists representing coverages
    (as output by calculate_coverage_r) and return
    a list of regrouped coverages.
    """
    return [parse_coverage(coverage) for coverage in coverage_list]

def parse_coverage(coverage):
    """
    Get a list representing one coverage
    (as output by calculate_coverage_r) and return
    a list where elements are (list_of_words, rule).
    """
    groups = []
    current_group = []
    for token in coverage:
        if token[0] == 'w':
            current_group.append(token[1])
        elif token[0] == 'r':
            groups.append((current_group, token[1:]))
            current_group = []
    return groups

def print_all_coverages(coverage_list):
    for coverage in coverage_list:
        print_groups(coverage)
    print()

def print_groups(coverage):
    output_str = '' 
    for group in coverage:
        output_str = output_str + \
            ' ({} {})'.format(group[1][0], ' '.join(group[0]))
    print(output_str.strip())

def signature(coverage):
    return tuple([len(group[0]) for group in coverage])

def get_LRLM(coverage_list):
    sorted_list = sorted(coverage_list, key=signature)
    signature_max = signature(sorted_list[0])
    LRLM_list = []
    for item in sorted_list:
        if signature(item) == signature_max:
            LRLM_list.append(item)
        else:
            return LRLM_list
    return LRLM_list

def process_line(line, cat_dict, pattern_FST):
    """
    Get line in stream format and print all coverages and LRLM only.
    """
    print(line + '\n')
    line = get_cats_by_line(line, cat_dict)
    coverage_list = calculate_coverage_r(pattern_FST, line, pattern_FST)
    print('All coverages:')
    print_all_coverages(parse_coverage_list(coverage_list))
    print('LRLM only:')
    print_all_coverages(parse_coverage_list(get_LRLM(coverage_list)))

def get_options():
    """
    Parse commandline arguments
    """
    usage = "USAGE: ./%prog [-o FILE] t*x_FILE [INPUT_FILE]"
    op = OptionParser(usage=usage)

    op.add_option("-o", "--out", dest="ofname",
                  help="output results to FILE", metavar="FILE")

    (opts, args) = op.parse_args()
    if len(args) > 3:
        op.error("Too many arguments.")
        op.print_help()
        sys.exit(1)

    return opts, args

if __name__ == "__main__":
    opts, args = get_options()

    txfname = args[0]

    transtree = ET.parse(txfname)
    cat_dict = get_cat_dict(transtree)

    pattern_FST = get_pattern_FST(transtree)
    output_patterns(pattern_FST)

    # use stdin if it's full                                                        
    if not sys.stdin.isatty():
        input_stream = sys.stdin
    # otherwise, read the given filename                                            
    else:
        try:
            input_filename = args[1]
        except IndexError:
            message = 'need filename as first argument if stdin is not full'
            raise IndexError(message)
        else:
            input_stream = open(input_filename, 'rU')

    for line in input_stream:
        process_line(line, cat_dict, pattern_FST)

    #    print line # do something useful with each line

    #txfname = args[0]
    #ifname = args[1]

    #with open(ifname, 'r') as ifile:
    #    lines = ifile.readlines()

    #for line in lines:
