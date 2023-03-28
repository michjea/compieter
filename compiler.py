# coding=utf-8
import AST
from AST import addToClass

operations = {
    '+': 'ADD',
    '-': 'SUB',
    '*': 'MUL',
    '/': 'DIV',
    '%': 'MOD'
}

variables = {}  # variable : indice pile
stack = []


@addToClass(AST.ProgramNode)
def compile(self):
    """Noeud de programme. Retourne la suite d'opcodes de tous les enfants."""
    bytecode = ""
    for c in self.children:
        bytecode += c.compile()
    return bytecode


@addToClass(AST.TokenNode)
def compile(self):
    '''
    Noeud terminal.
    Si c'est une variable : empile la valeur de la variable.
    Si c'est une constante : empile la constante.
    '''
    bytecode = ""
    val = self.tok
    print(stack)

    if isinstance(self.tok, str):
        print(val)
        if not val.startswith("'"):
            val = stack[variables[self.tok]]

            stack.append(val)

            if isinstance(val, str):
                val = ord(val)
        else:
            val = val.replace("'", "")
            stack.append(val)
            val = ord(val)
    else:
        stack.append(val)

    bytecode += "PUSH %s\n" % val
    print("bytecode tokennode ", bytecode)
    return bytecode


@addToClass(AST.AssignNode)
def compile(self):
    '''
    Noeud d'assignation de variable.
    Exécute le noeud à droite du signe =.
    Dépile un élément et le met dans ID.
    '''
    bytecode = ""
    bytecode += self.children[1].compile()

    variables[self.children[0].tok] = len(stack) - 1

    return bytecode


@addToClass(AST.PrintCNode)
def compile(self):
    '''
    Noeud d'affichage.
    Exécute le noeud à droite du PRINT.
    Dépile un élément et l'affiche.
    '''
    bytecode = ""
    bytecode += self.children[0].compile()

    val = stack.pop()

    if isinstance(val, str):
        bytecode += "PRINTC %s\n" % ord(val)
    else:
        bytecode += "PRINTC %s\n" % val

    return bytecode


@addToClass(AST.PrintNode)
def compile(self):
    '''
    Noeud d'affichage.
    Exécute le noeud à droite du PRINT.
    Dépile un élément et l'affiche.
    '''
    bytecode = ""
    bytecode += self.children[0].compile()

    val = stack.pop()

    if isinstance(val, str):
        bytecode += "PRINTC %s\n" % ord(val)
    else:
        bytecode += "PRINT %s\n" % val

    return bytecode


@addToClass(AST.OpNode)
def compile(self):
    '''
    Noeud d'opération arithmétique.
    Si c'est une opération unaire (nombre négatif), empile le nombre et l'inverse.
    Si c'est une opération binaire, empile les enfants puis l'opération.
    '''
    bytecode = ""

    if len(self.children) == 1:
        bytecode += "USUB\n"
        bytecode += self.children[0].compile()
    elif self.op in ["<", ">", "<=", ">=", "==", "!="]:
        pass
    else:
        for c in self.children:
            val = c.tok

            # if val is a variable, get its value
            if isinstance(val, str):
                if val.isalpha():
                    indice = variables[val]
                    val = stack[indice]
                    if isinstance(val, str):
                        val = ord(val)
                else:
                    val = val.replace("'", "")
                    val = ord(val)

            bytecode += "PUSH %s\n" % val
            stack.append(val)
        op2 = stack.pop()
        op1 = stack.pop()
        if operations[self.op] == "ADD":
            res = op1 + op2
        elif operations[self.op] == "SUB":
            res = op1 - op2
        elif operations[self.op] == "MUL":
            res = op1 * op2
        elif operations[self.op] == "MOD":
            res = op1 % op2
        elif operations[self.op] == "DIV":
            if op2 != 0:
                res = op1 // op2
            else:
                print(f"Warning: Division by zero")
                return bytecode
        else:
            res = op1
        bytecode += operations[self.op] + "\n"
        stack.append(res)
    return bytecode


@addToClass(AST.IfNode)
def compile(self):
    condition = eval_condition(self.children[0])

    bytecode = ""
    if condition:
        bytecode += self.children[1].compile()
    else:
        if len(self.children) > 2:
            bytecode += self.children[2].compile()

    return bytecode


def eval_condition(condition):
    if condition.op in ['==', '!=', '<', '>', '<=', '>=']:
        left = int(stack[variables[condition.children[0].tok]]) if condition.children[0].tok in variables else int(
            condition.children[0].tok)
        right = int(stack[variables[condition.children[1].tok]]) if condition.children[1].tok in variables else int(
            condition.children[1].tok)
        if condition.op == '==':
            return left == right
        elif condition.op == '!=':
            return left != right
        elif condition.op == '<':
            return left < right
        elif condition.op == '>':
            return left > right
        elif condition.op == '<=':
            return left <= right
        elif condition.op == '>=':
            return left >= right
    elif condition.op in ['and', 'or']:
        left = eval_condition(condition.children[0])
        right = eval_condition(condition.children[1])
        if condition.op == 'and':
            return left and right
        elif condition.op == 'or':
            return left or right


@addToClass(AST.WhileNode)
def compile(self):
    '''
    Noeud de boucle while.
    Saute au label de la condition défini plus bas.
    Insère le label puis le corps du body.
    Insère le label puis le corps de la condition.
    Réalise un saut conditionnel sur le résultat de la condition (empilé).
    '''

    bytecode = ""

    condition = eval_condition(self.children[0])

    while (condition):
        bytecode += self.children[1].compile() + "\n"
        condition = eval_condition(self.children[0])

    return bytecode


if __name__ == "__main__":
    from parser_1 import parse
    import sys
    import os
    prog = open(sys.argv[1]).read()
    ast = parse(prog)
    print(ast)
    compiled = ast.compile()
    name = os.path.splitext(sys.argv[1])[0]+'.vm'
    outfile = open(name, 'w')
    outfile.write(compiled)
    outfile.close()
    print("Wrote output to", name)
