function_table = {
    "calculate": lambda expression: eval(expression),
    "translate": lambda text, target_lang: f"Translating '{text}' to {target_lang}"
}