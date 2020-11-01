from scrappybara.pipeline.pipeline import Pipeline
from scrappybara.syntax.tagger import Tagger


class ToolkitPipeline(Pipeline):
    """Provides tools for internal use"""

    def __init__(self, batch_size=128):
        super().__init__(batch_size)
        self.__tag = Tagger(self._charset, self._wordset, self._ptags_model, batch_size)

    def extract_lexeme_bags(self, texts):
        """Processes all texts in memory & returns a list of lexeme bags"""
        token_lists, sent_ranges = self._extract_sentences(texts)
        tag_lists = self.__tag(token_lists)
        counter_list = []
        for start, end in sent_ranges:
            tokens = [token for token_list in token_lists[start:end] for token in token_list]
            tags = [tag for tag_list in tag_lists[start:end] for tag in tag_list]
            lemma_tag_list = [(self._lemmatize(token, tag)[0], tag) for token, tag in zip(tokens, tags)]
            counter_list.append(self._count_lexemes(lemma_tag_list))
        return counter_list

    def tag_text(self, text):
        """Tags a single text string"""
        return self.__tag(self._sentencize(text))

    def parse_sentence(self, input_sentence):
        """Parses a single sentence.
        Arg input_sentence can be a string or a list of tokens"""
        if isinstance(input_sentence, list):
            tokens = [input_sentence]
        else:
            tokens = self._sentencize(input_sentence)
        tags, idx_trees, node_dicts, _ = self._parse_tokens(tokens)
        return tokens[0], tags[0], idx_trees[0], node_dicts[0]
