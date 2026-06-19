import re
from ast import literal_eval

class TextCleaner():
    def __init__(self):
        # https://docs.python.org/3/library/stdtypes.html#text-and-binary-sequence-type-methods-summary
        _tokens = {
                '_WS' : r'\s+',  # https://docs.python.org/3/library/stdtypes.html#bytearray.isspace
                '_EM' : r'[a-zA-Z0-9._-]+@[a-zA-Z0-9\-]+\.[a-zA-Z]{1,4}',
                '_U' : r'\w+:\/\/\S+', # Before fixing underscores
                '_SM' : r'[-_]+(?=[^EM|U])', 
                '_QT' : r'[\'"]+', 
                '_DD' :  r'(?<=\b)(?:[A-Za-z]\.){2,}|\.$',
                '_SP' : r'[^A-Za-z0-9_]+', 
                '_UC' : r'\?+', 
                }

        _punctuations = {
                # TOKEN : PATTERN
                # Punctuations (before)(pattern)(after)
                '_BQ' : r'([^\?!])(\?{2,})(\Z|[^\?!])',
                '_BX' : r'([^\?!])(!{2,})(\Z|[^\?!])',
                '_Q' : r'([^\?!])(\?)(\Z|[^\?!])',
                '_X' : r'([^\?!])(!)(\Z|[^\?!])',
                '_SS' : r'([^\.])(\.{2,})(\Z|[^\.])',
                '_EL' : r'([a-zA-Z])(\1{2,})(.)',
                }

        self.UnderscoreTokens = { k : re.compile(v) for k, v in _tokens.items()}
        self.PunctuationTokens = { k : re.compile(v) for k, v in _punctuations.items()}
        self.count = -1

        self.pipeline = {
            "original"                  : None,
            "normalized"                : self.normalize_literal_string,
            "htmlParsed"                : None,
            "whiteSpacedFixed"          : self.FixWhiteSpace, # Before tokenizing
            "symbolsRemoved"            : self.RemoveSymbols, # !imp before tokenizing
            "specialRemoved"            : self.RemoveSpecialCharacters, # !imp before tokenizing
            "quotesRemoved"             : self.RemoveQuotes,
            "punctuationMarksTokenized" : self.TokenizePunctuationMarks, # !imp after email and url fix
            "dotsFixed"                 : self.FixDots, # !imp after email and url fix
        }

    def __doc__(self):
        return f"Test"


    def counter(self):
        self.count += 1
        return self.count


    def reset_count(self, topic: str):
        self.count = -1

    def normalize_literal_string(self, x: str):
        """
        Attempts to safely interpret string-encoded Python literals.
        If input is a string, it tries `ast.literal_eval()` to convert
        quoted and escaped literals into their Python value. Only keeps the
        parsed result if it is still a string; otherwise returns the original.
        Used to clean noisy text data where values may be double-quoted
        or escaped as Python-style string representations.

        Fixes:
        1. Quotes
        1. Escape Sequences
        """
        try:
            result = literal_eval(x)
        except SyntaxError as e:
            quote = x[0]
            fixed = quote + x[1:-1].replace(quote, f'\\{quote}') + quote
            result = literal_eval(fixed)

        return result if isinstance(result, str) else x


    def FixWhiteSpace(self, text:str):
        """
        In a string, fix:
            1. Whitespaces <- replaces white spaces as defined by '_WS' with a
               single space character.
            1. Surrounding whitespaces <- deletes leading and trailing whitespace.
        """
        if not isinstance(text, str):
            try:
                text = str(text)
            except ValueError as e:
                return None
        return self.UnderscoreTokens['_WS'].sub(r' ', text).strip()


    def RemoveSymbols(self, text:str):
        """
        In a string, fix:
            1. Replaces an '_' or '-' character with a single ' ' character.
            1. Run after tokenizing urls and emails
        """
        return self.UnderscoreTokens['_SM'].sub(r'', text).strip()


    def RemoveQuotes(self, text:str):
        """
        In a string, fix:
            1. Whitespaces <- replaces white spaces as defined by '_WS' with a
               single space character.
            1. Surrounding whitespaces <- deletes leading and trailing whitespace.
        """
        return self.UnderscoreTokens['_QT'].sub(r'', text).strip()


    def TokenizeEmail(self, text:str):
        return self.UnderscoreTokens['_EM'].sub('_EM', text)


    def TokenizeURL(self, text:str):
        return self.UnderscoreTokens['_U'].sub('_U', text)


    def TokenizePunctuationMarks(self, text: str):
        before = r'\1'
        after = r'\3'
        for token in self.PunctuationTokens.keys():
            replacement = f"{before} {token}\n{after}"
            text = self.PunctuationTokens[token].sub(replacement, text)
        return text.strip()


    def FixDots(self, text: str):
        """
        1. Fix abbreviations. U.S.A. -> USA
        1. Remove '.' characters at the end of a string.
        """
        text =  self.UnderscoreTokens['_DD'].sub(
          lambda m: m.group().replace('.', ''), text)

        return text.strip()

    def TokenizeUnicodeCharacters(self, text: str):
        text = self.UnderscoreTokens['_UC'].sub(r' _UC ', text)
        return text

    def RemoveSpecialCharacters(self, text: str):
        # return self.UnderscoreTokens['_SP'].sub(r' ', text).strip()
        return text
        

    def tolower(self, text: str):
        # return self.UnderscoreTokens['_SP'].sub(r' ', text).strip()
        return text.lower()


class Tokenizer():
  pass

def main():
    pass


if __name__ == "__main__":
    main()
