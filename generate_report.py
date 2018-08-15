from pathlib import Path
import pybo
import os


def read_folder(foldername):
    folder = Path(foldername)
    for file in folder.rglob('*.txt'):
        content = file.read_text(encoding='utf-8-sig')
        yield content


def parse_vocab(File):
    lines = File.split('\n')
    # split lines containing more than one word
    words = []
    for line in lines:
        if ' ' in line:
            words.extend(line.split(' '))
        else:
            words.append(line)
    # remove empty words
    words = [word for word in words if word != '']
    # remove shads and tseks from words
    words = [word.rstrip().rstrip('།').rstrip('་') for word in words]
    return words


def parse_vocab_folder(outfile):
    vocab_path = Path('input/lists')
    vocab = []
    for f in read_folder(str(vocab_path)):
        vocab.extend(parse_vocab(f))
    out = '\n'.join(sorted(list(set(vocab))))
    Path(outfile).write_text(out, encoding='utf-8-sig')


def instanciate_tokenizer():
    vocab_file = Path('input/lists/full-vocab.txt')
    parse_vocab_folder(str(vocab_file))
    tok = pybo.BoTokenizer('POS', user_word_list=[str(vocab_file)])
    os.remove(str(vocab_file))
    return tok


def mark_vernacular(tokens):
    vern = False
    has_shad = False
    for token in tokens:
        if '༺' in token.content:
            vern = True
        if '༻' in token.content:
            vern = False
            has_shad = False

        if vern:
            if '།' in token.content and '༺' not in token.content:
                has_shad = True
            if token.type == 'syl':
                if has_shad:
                    token._['vern'] = 'trans'
                else:
                    token._['vern'] = 'vern'
    return tokens


def mark_no_ortho(tokens):
    no_ortho = False
    for token in tokens:
        if '༙' in token.content:
            no_ortho = not no_ortho

        if no_ortho and token.type == 'syl':
            token._['no_ortho'] = True
    return tokens



if __name__ == '__main__':
    # prepare the tokenizer to include the vernacular wordlists
    tok = instanciate_tokenizer()

    # tokenize
    folder = Path('input/corpus-folder')
    for file in folder.rglob('*.txt'):
        content = file.read_text(encoding='utf-8-sig')
        tokens = tok.tokenize(content)
        tokens = mark_vernacular(tokens)
        tokens = mark_no_ortho(tokens)
        print('ok')