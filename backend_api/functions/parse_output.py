import ast

def parse_text(text_input: str)-> list:
    return ast.literal_eval(text_input)