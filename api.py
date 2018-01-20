"""
Scriptul acesta ia un text input si tokenizeaza cuvintele folosind
http://nlptools.info.uaic.ro/WebNpChunkerRo/
http://nlptools.info.uaic.ro/WebNpChunkerRo/docs/Ro%20NP%20chunking%20using%20GGS%20-%20CONSILR%202011.pdf
"""

import requests
import sys
import re
import os
import string
import json

from hashlib import md5
from html import unescape
from libs.models import WordStructure, PhraseCache
from lxml import etree

def get_phrases(file_path):
    if not os.path.exists(file_path):
        print('Invalid path: {}'.format(file_path))
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read().strip().split('.')
    data = [item.strip() for item in data if item]
    return data

def parse_phrase(phrase):
    phrase = ''.join([c for c in phrase if c not in string.punctuation.replace('-', '') and c != '\ufeff'])
    phrase = phrase.strip().lower()

    _md5 = md5(phrase.encode()).hexdigest()
    try:
        PhraseCache.get(PhraseCache.md5==_md5)
    except PhraseCache.DoesNotExist:
        print('new_phrase')
        result = query_noun_phrase_chunker(phrase)
        print(len(phrase), len(result))
        for word, lemma, pos, case in result:
            word = word.strip()
            if not word:
                continue
            entry = WordStructure(text=word, lemma=lemma, pos=pos, case=case)
            entry.save()
        PhraseCache(phrase=phrase, md5=_md5).save()
    phrase = [item.strip() for item in phrase.split() if item]
     
    result_data = []
    i = 0
    while i < len(phrase):
        word = phrase[i]
        try:
            word_struct = WordStructure.get(WordStructure.text == word)
        except WordStructure.DoesNotExist:
            if i == len(phrase) - 1:
                break
            word = word + ' ' + phrase[i+1]
            try:
                word_struct = WordStructure.get(WordStructure.text == word)
            except WordStructure.DoesNotExist:
                print('should not happen', i)
                i += 1
                continue
            else:
                result_data.append((word_struct.id, word_struct.text, word_struct.lemma, word_struct.pos))
                i += 2
        else:
            result_data.append((word_struct.id, word_struct.text, word_struct.lemma, word_struct.pos))
            i += 1
    return result_data
        
def query_noun_phrase_chunker(phrase):
    request = requests.post('http://nlptools.info.uaic.ro/WebNpChunkerRo/NpChunkerRoServlet',
                            data={'sent': phrase})
    data = request.text
    info = re.findall(r"<span onclick='selectWord\(this,\s*(\{.+\}?)\)'.+?>(.+?)<\/span>", data)
    return_data = []
    for meta, word in info:
        meta = meta.lower()
        word = unescape(word.lower())
        meta = re.sub('([{,: ])(\w+)([},:])','\\1\"\\2\"\\3',meta)
        meta = json.loads(meta)
        # meta = yaml.load(meta)
        lemma = meta.get('lemma', '')
        pos = meta.get('pos', '')
        case = meta.get('case', '')
        return_data.append((word, lemma, pos, case))
    return return_data

def process(phrases):
    top = etree.Element('text')
    for phrase in phrases:
        result = parse_phrase(phrase)
        for token, word, lemma, pos in result:
            child = etree.SubElement(top, 'token', {'id': str(token), 'lemma': lemma, 'pos': pos})
            child.text = word
    return top
    

if __name__ == '__main__':
    file_path = sys.argv[1]
    phrases = get_phrases(file_path)
    root = process(phrases)
    with open('result.xml', 'w', encoding='utf-8') as f:
        f.write(etree.tostring(root).decode('utf-8'))
    # result = parse_phrase(phrases[0])

    # with open('result.json', 'w', encoding='utf-8') as f:
    #     json.dump(result, f, ensure_ascii=False)
