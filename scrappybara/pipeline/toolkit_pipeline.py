from scrappybara.pipeline.pipeline import Pipeline


class ToolkitPipeline(Pipeline):
    """Provides tools for internal use"""

    def __init__(self, batch_size=128):
        super().__init__(batch_size)

    def extract_lexeme_bags(self, texts):
        """Processes all texts in memory & returns a list of lexeme bags"""
        tokens, sent_ranges = self._extract_sentences(texts)
        _, _, node_dicts, _ = self._process_tokens(tokens)
        lexeme_bags = []
        for start, end in sent_ranges:
            lexeme_bags.append(self._count_lexemes(node_dicts[start:end]))
        return lexeme_bags

    def parse_sentence(self, input_sentence):
        """Parses a single sentence.
        Arg input_sentence can be a string or a list of tokens"""
        if isinstance(input_sentence, list):
            tokens = [input_sentence]
        else:
            tokens = self.__sentencize(input_sentence)
        tags, idx_trees, node_dicts, _ = self._process_tokens(tokens)
        return tokens[0], tags[0], idx_trees[0], node_dicts[0]
