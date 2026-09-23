import re

stack = []

class Tree:
    def __init__(self, node="", left=None, right=None):
        self.node = node
        self.left = left
        self.right = right

    #Построение дерева
    def build_tree(self):
        while stack:
            self.node = str(stack.pop())
            if self.node == "=" or self.node == "+" or self.node == "*":
                self.left = Tree()
                self.left.build_tree()
                self.right = Tree()
                self.right.build_tree()
                return
            else:
                return

    #Вычисление длины дерева
    def tree_len(self):
        if self.left is None:
            return 0
        l = self.left.tree_len()
        r = self.right.tree_len()
        return 1 + (l if l > r else r)

    #Построение псевдокода
    def build_code(self):
        code = ""
        if self.node == "=":
            code += "\nload " + self.right.build_code()
            code += "\nstore " + self.left.node + ";"
        elif self.node == "+" or self.node == "*":
            code += self.left.build_code() + "\nstore $" + str(self.tree_len()) + ";"
            code += "\nload " + self.right.build_code()
            code += "\n" + ("mpy " if self.node == "*" else "add ") + "$" + str(self.tree_len()) + ";"
        else:
            code += self.node + ";"
        return code

    #Печать дерева
    @staticmethod
    def print_tree(t, l):
        if t is None:
            return ""
        return (Tree.print_tree(t.left, l + 1) +
                " " * l + t.node + "\n" +
                Tree.print_tree(t.right, l + 1))

#Смена слагаемых/множителей в коммутативных операциях
def opt12(code):
    pattern = r"load (\w+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|\$\d+);\n(add|mpy) (?!\1)(\w+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|\$\d+);\n"
    code = re.sub(pattern, r'load \3;\n\2 \1;\n', code)
    print(code)
    return code

#Удаление STORE a LOAD a
def opt3(code):
    pattern = r"store (\w+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|\$\d+);\nload (\1);\n"
    code = re.sub(pattern, "", code)
    print(code)
    return code

#Удаление STORE a LOAD b STORE + замена b на a
def opt4(code):
    pattern = r"load (\w+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|\$\d+);\nstore (?!\1)(\w+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|\$\d+);\n(load(.*\n)*)(add|mpy) (\2)"
    code = re.sub(pattern, r'\3\5 \1', code)
    print(code)
    return code

#Оптимизация кода
def optimize(code):
    while True:
        print(code)
        l = len(code)
        code = opt12(code)
        code = opt3(code)
        code = opt4(code)
        if l == len(code):
            return code

#Проверка на одинаковое количество открывающихся и закрывающихся скобок
def bracket_balance(tokens):
    stack = []
    for token in tokens:
        if token == '(':
            stack.append(token)
        elif token == ')':
            if not stack:
                return False
            top_char = stack.pop()
            if (top_char == "(" and token != ")"):
                return False
    return not stack

#Создание списка со всеми операторами, переменными и константами
def token_list(expr):
    pattern = r"[a-zA-Z]\w*|[+*=]|[()]|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"
    return re.findall(pattern, expr)

#Составление таблицы имён
def names_find(expr, file):
    tablenames = {}
    pattern = r"[a-zA-Z]\w*|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"
    matches = re.finditer(pattern, expr)
    for match in matches:
        if match[0] not in tablenames:
            tablenames[match[0]] = []
    for k, v in tablenames.items():
        if k[0] >= '0' and k[0] <= '9':
            file.write(f"{k} constant\n")
        else:
            s = k
            for j in v:
                s += f"[{j}]"
            file.write(f"{s} variable\n")

#Составление обратной польской записи
def opz_gen(expr):
    precedence = {'+': 1, '*': 2}
    opz = []
    stack = []
    for token in expr:
        if token[0].isdigit() or token[0].isalpha():
            opz.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                opz.append(stack.pop())
            stack.pop()
        else:
            while stack and precedence.get(token, 0) <= precedence.get(stack[-1], 0):
                opz.append(stack.pop())
            stack.append(token)
    while stack:
        opz.append(stack.pop())
    return opz


if __name__ == "__main__":
    with open("output.txt", "w") as fout:
        fin = open("input.txt", "r")
        expression = fin.readline()
        pattern = (r'('
                   r'^([a-zA-Z_]\w*)\s*\=\s*'
                   r'\(*'
                   r'(([a-zA-Z_]\w*)|(\d+(?:\.\d+)?(?:[eE][+-]?\d+)?))'
                   r'('
                   r'\s*[*+]\s*\(*(([a-zA-Z_]\w*)|(\d+(?:\.\d+)?(?:[eE][+-]?\d+)?))\s*\)*'
                   r')*'
                   r')$')
        match = re.match(pattern, expression)
        if match:
            tokens = token_list(expression)
            if bracket_balance(tokens):
                fout.write("Name table:\n")
                names_find(expression, fout)
                opz = opz_gen(tokens[2:])
                opz.append(tokens[0])
                opz.append(tokens[1])
                T = Tree()
                for token in opz:
                    stack.append(token)
                T.build_tree()
                fout.write("\nTree:\n")
                fout.write(Tree.print_tree(T, 0))
                code = T.build_code()
                print(code)
                fout.write("\nPseudoprogram")
                fout.write(code)
                code = optimize(code)
                fout.write("\n\nPseudoprogram after optimization")
                fout.write(code)
            else:
                print("Brackets unbalanced")
        else:
            print("No matches")