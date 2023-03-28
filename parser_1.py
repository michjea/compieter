import ply.yacc as yacc

from lex import tokens
import AST

vars = {}


def p_programme_statement(p):
    ''' programme : statement '''
    p[0] = AST.ProgramNode(p[1])


def p_programme_recursive(p):
    ''' programme : statement ';' programme '''
    p[0] = AST.ProgramNode([p[1]]+p[3].children)


def p_statement(p):
    ''' statement : assignation
        | structure '''
    if hasattr(p[1], 'children') and hasattr(p[1].children[1], 'tok'):
        if p[1].children[1].tok in vars:
            vars[p[1].children[0].tok] = p[1].children[1].tok
        else:
            if isinstance(p[1].children[1].tok, str):
                vars[p[1].children[0].tok] = p[1].children[1].tok
            else:
                vars[p[1].children[0].tok] = int(p[1].children[1].tok)
    p[0] = p[1]


def p_statement_print(p):
    ''' statement : PRINT expression '''
    p[0] = AST.PrintNode(p[2])


def p_statement_printc(p):
    ''' statement : PRINTC expression '''
    p[0] = AST.PrintCNode(p[2])


def p_structure(p):
    ''' structure : WHILE '(' condition ')' '{' programme '}' 
        | IF '(' condition ')' '{' programme '}' 
        | IF '(' condition ')' '{' programme '}' ELSE '{' programme '}' '''
    if p[1].upper() == 'WHILE':
        p[0] = AST.WhileNode([p[3], p[6]])
    elif p[1].upper() == 'IF':
        print(len(p))
        if len(p) == 12:
            p[0] = AST.IfNode([p[3], p[6], p[10]])
        else:
            p[0] = AST.IfNode([p[3], p[6]])


def p_condition(p):
    ''' condition : condition AND condition 
        | condition OR condition 
        | expression COMP_OP expression
        | '(' condition ')' '''

    if len(p) == 4:
        if p[2] in ['==', '!=', '<', '>', '<=', '>=']:
            p[0] = AST.OpNode(p[2], [p[1], p[3]])
            p[0].op = p[2]
        elif p[2] in ['and', 'or']:
            p[0] = AST.OpNode(p[2], [p[1], p[3]])
            p[0].op = p[2]
    elif len(p) == 3:
        p[0] = p[2]


def p_expression_op(p):
    '''expression : expression ADD_OP expression
        | expression MUL_OP expression'''
    p[0] = AST.OpNode(p[2], [p[1], p[3]])


def p_expression_num_or_var(p):
    '''expression : NUMBER
        | IDENTIFIER
        | CHAR '''
    p[0] = AST.TokenNode(p[1])


def p_expression_paren(p):
    '''expression : '(' expression ')' '''
    p[0] = p[2]


def p_minus(p):
    ''' expression : ADD_OP expression %prec UMINUS'''
    p[0] = AST.OpNode(p[1], [p[2]])


def p_assign(p):
    ''' assignation : IDENTIFIER '=' expression '''
    p[0] = AST.AssignNode([AST.TokenNode(p[1]), p[3]])


def p_error(p):
    if p:
        print("Syntax error in line %d" % p.lineno)
        parser.errok()
    else:
        print("Sytax error: unexpected end of file!")


precedence = (
    ('left', 'ADD_OP'),
    ('left', 'MUL_OP'),
    ('right', 'UMINUS'),
    ('left', 'AND'),
    ('left', 'OR'),
)


def parse(program):
    return yacc.parse(program)


parser = yacc.yacc(outputdir='generated')

if __name__ == "__main__":
    import sys

    prog = open(sys.argv[1]).read()
    #prog = open('fibonacci.txt').read()
    result = yacc.parse(prog)
    if result:
        print(result)

        import os
        os.environ["PATH"] += os.pathsep + \
            'C:/Program Files (x86)/Graphviz2.38/bin/'
        graph = result.makegraphicaltree()
        name = os.path.splitext(sys.argv[1])[0]+'-ast.pdf'
        #name = os.path.splitext("fibonacci.txt")[0]+'-ast.pdf'
        graph.write_pdf(name)
        print("wrote ast to", name)
    else:
        print("Parsing returned no result!")
