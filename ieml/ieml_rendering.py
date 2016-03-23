"""Classes here take care of rendering objects to valid IEML string"""

class GenericIEMLRenderer:
    oplus_sign = "\u2295"
    otimes_sign = "\u2297"

    @staticmethod
    def wrap_with_brackets(input_string):
        return "[" + input_string + "]"

    @staticmethod
    def wrap_with_parenthesis(input_string):
        return "(" + input_string + ")"

class PropositionGraphRenderer(GenericIEMLRenderer):
    pass

class WordGraphRenderer(GenericIEMLRenderer):

    def render_sum(self, sum_terms):

        if isinstance(sum_terms, list):
            with_brackets = [self.wrap_with_brackets(term) for term in sum_terms]
            return self.oplus_sign.join(with_brackets)
        elif isinstance(sum_terms, str):
            return self.wrap_with_brackets(sum_terms)

    def render_multiplication(self, factor1, factor2):
        return self.wrap_with_parenthesis(factor1) \
               + self.otimes_sign \
               + self.wrap_with_parenthesis(factor2)