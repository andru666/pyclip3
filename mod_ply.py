#Embedded file name: /build/PyCLIP/android/app/mod_ply.py
import sys
sys.path.insert(0, '../..')
sys.path.insert(0, './ply')
import ply.lex as lex
import ply.yacc as yacc
import time, re

class Parser():
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.names = {}
        lex.lex(module=self)
        yacc.yacc(module=self)

    def calculate(self, value):
        return yacc.parse(value, debug=0)


class Calc(Parser):
    result = ''
    tokens = ('NAME', 'HEXSTR', 'NUMBER', 'HEX', 'FLOAT', 'PLUS', 'MINUS', 'BAND', 'EXP', 'TIMES', 'DIVIDE', 'EQUALS', 'NEQ', 'LPAREN', 'RPAREN', 'LT', 'GT', 'GE', 'LE', 'AND', 'OR', 'SHIFT', 'QUEST', 'DOTS', 'STRCONST', 'HEXTOASCII', 'HEXTOSTR', 'HEXTODEC', 'LADAHEXTODEC')
    t_OR = '\\|\\|'
    t_AND = '\\&\\&'
    t_BAND = '\\&'
    t_EQUALS = '=='
    t_NEQ = '\\!='
    t_PLUS = '\\+'
    t_MINUS = '-'
    t_EXP = '\\*\\*'
    t_TIMES = '\\*'
    t_DIVIDE = '/'
    t_LPAREN = '\\('
    t_RPAREN = '\\)'
    t_SHIFT = '\\#'
    t_QUEST = '\\?'
    t_DOTS = '\\:'
    t_LT = '<'
    t_GT = '>'
    t_LE = '<='
    t_GE = '>='
    t_STRCONST = '\\"([^\\\\\\n]|(\\\\.))*?\\"'
    t_ignore = ' \t'

    def t_LADAHEXTODEC(self,t):
        return t
    t_LADAHEXTODEC.__doc__ = '\\$LadaToDec\\$\\([a-fA-F0-9][a-fA-F0-9]*\\)'

    def t_HEXTOASCII(self, t):
        return t

    t_HEXTOASCII.__doc__ = '\\$HexaToAscii\\$\\([a-fA-F0-9][a-fA-F0-9]*\\)'

    def t_HEXTOSTR(self, t):
        return t

    t_HEXTOSTR.__doc__ = '\\$HexaToString\\$\\([a-fA-F0-9][a-fA-F0-9]*\\)'

    def t_HEXTODEC(self, t):
        return t

    t_HEXTODEC.__doc__ = '\\$HexaToDec\\$\\([a-fA-F0-9][a-fA-F0-9]*\\)'

    def t_HEX(self, t):
        t.value = int(t.value, 0)
        return t

    t_HEX.__doc__ = '0x[a-fA-F0-9][a-fA-F0-9]*'

    def t_NAME(self, t):
        return t

    t_NAME.__doc__ = '[a-zA-Z_][a-zA-Z0-9_]*'

    def t_FLOAT(self, t):
        t.value = float(t.value)
        return t

    t_FLOAT.__doc__ = '((\\d*\\.\\d+)(E[\\+-]?\\d+)?|([1-9]\\d*E[\\+-]?\\d+))'

    def t_HEXSTR(self, t):
        t.value = t.value
        return t

    t_HEXSTR.__doc__ = '[a-fA-F0-9]*[a-fA-F][a-fA-F0-9]*'

    def t_NUMBER(self, t):
        t.value = int(t.value)
        return t

    t_NUMBER.__doc__ = '\\d+'

    def t_newline(self, t):
        t.lexer.lineno += t.value.count('\n')

    t_newline.__doc__ = '\\n+'

    def t_error(self, t):
        t.lexer.skip(1)

    precedence = (('left', 'PLUS', 'MINUS'),
     ('left', 'TIMES', 'DIVIDE'),
     ('left', 'EXP'),
     ('left', 'SHIFT'),
     ('left', 'LE'),
     ('left', 'GE'),
     ('left', 'LT'),
     ('left', 'GT'),
     ('left', 'OR'),
     ('left', 'AND'),
     ('right', 'UMINUS'))

    def p_statement_expr(self, p):
        p[0] = p[1]

    p_statement_expr.__doc__ = 'statement : expression'

    def p_expression_binop(self, p):
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '*':
            p[0] = p[1] * p[3]
        elif p[2] == '/':
            p[0] = p[1] / p[3]
        elif p[2] == '**':
            p[0] = p[1] ** p[3]
        elif p[2] == '&':
            p[0] = p[1] & p[3]

    p_expression_binop.__doc__ = '\n        expression : expression MINUS expression\n                   | expression TIMES expression\n                   | expression DIVIDE expression\n                   | expression EXP expression\n                   | expression BAND expression\n        '

    def p_expression_plus(self, p):
        if type(p[1]) is str or type(p[3]) is str:
            p[0] = str(p[1]).replace('"', '') + str(p[3])
        else:
            p[0] = p[1] + p[3]

    p_expression_plus.__doc__ = 'expression : expression PLUS expression'

    def p_expression_uminus(self, p):
        p[0] = -p[2]

    p_expression_uminus.__doc__ = 'expression : MINUS expression %prec UMINUS'

    def p_expression_equals(self, p):
        if p[1] == p[3]:
            p[0] = 1
        else:
            p[0] = 0

    p_expression_equals.__doc__ = 'expression : expression EQUALS expression'

    def p_expression_notequals(self, p):
        if p[1] != p[3]:
            p[0] = 1
        else:
            p[0] = 0

    p_expression_notequals.__doc__ = 'expression : expression NEQ expression'

    def p_expression_le(self, p):
        if p[1] <= p[3]:
            p[0] = 1
        else:
            p[0] = 0

    p_expression_le.__doc__ = 'expression : expression LE expression'

    def p_expression_lt(self, p):
        if p[1] < p[3]:
            p[0] = 1
        else:
            p[0] = 0

    p_expression_lt.__doc__ = 'expression : expression LT expression'

    def p_expression_ge(self, p):
        if p[1] >= p[3]:
            p[0] = 1
        else:
            p[0] = 0

    p_expression_ge.__doc__ = 'expression : expression GE expression'

    def p_expression_gt(self, p):
        if p[1] > p[3]:
            p[0] = 1
        else:
            p[0] = 0

    p_expression_gt.__doc__ = 'expression : expression GT expression'

    def p_expression_or(self, p):
        if p[1] or p[3]:
            p[0] = 1
        else:
            p[0] = 0

    p_expression_or.__doc__ = 'expression : expression OR expression'

    def p_expression_and(self, p):
        if p[1] and p[3]:
            p[0] = 1
        else:
            p[0] = 0

    p_expression_and.__doc__ = 'expression : expression AND expression'

    def p_expression_shift(self, p):
        p[0] = p[1] >> p[3] & 1

    p_expression_shift.__doc__ = 'expression : expression SHIFT expression'

    def p_expression_condition(self, p):
        if p[1]:
            p[0] = p[3]
        else:
            p[0] = p[5]

    p_expression_condition.__doc__ = 'expression : expression QUEST expression DOTS expression'

    def p_expression_strconst(self, p):
        p[0] = p[1]

    p_expression_strconst.__doc__ = 'expression : STRCONST'

    def p_expression_HexaToDec(self, p):
        tmp = p[1]
        tmp = tmp.replace('$HexaToDec$(', '')
        tmp = tmp.replace(')', '')
        p[0] = tmp

    p_expression_HexaToDec.__doc__ = 'expression : HEXTODEC'

    def p_expression_LADA(self, p):
        tmp = p[1]
        tmp = tmp.replace("$LadaToDec$(","")
        tmp = tmp.replace(")","")
        tmp = tmp.replace(' ', '')
        if len(tmp) == 4:
            tmp = tmp[2:]+tmp[:2]
        elif len(tmp) == 8:
            tmp = tmp[6:]+tmp[4:6]+tmp[2:4]+tmp[:2]
        p[0] = int(tmp, 16)
    p_expression_LADA.__doc__='expression : LADAHEXTODEC'

    def p_expression_HexaToString(self, p):
        tmp = p[1]
        tmp = tmp.replace('$HexaToString$(', '')
        tmp = tmp.replace(')', '')
        p[0] = tmp

    p_expression_HexaToString.__doc__ = 'expression : HEXTOSTR'

    def p_expression_HexaToAscii(self, p):
        tmp = p[1]
        tmp = tmp.replace('$HexaToAscii$(', '')
        tmp = tmp.replace(')', '')
        tmp = tmp.replace(' ', '')
        if len(tmp) % 2:
            tmp = '0' + tmp
        p[0] = bytes.fromhex(tmp).decode('utf-8')

    p_expression_HexaToAscii.__doc__ = 'expression : HEXTOASCII'

    def p_expression_group(self, p):
        p[0] = p[2]

    p_expression_group.__doc__ = 'expression : LPAREN expression RPAREN'

    def p_expression_number(self, p):
        p[0] = p[1]

    p_expression_number.__doc__ = 'expression : NUMBER'

    def p_expression_hex(self, p):
        p[0] = p[1]

    p_expression_hex.__doc__ = 'expression : HEX'

    def p_expression_hexstr(self, p):
        p[0] = p[1]

    p_expression_hexstr.__doc__ = 'expression : HEXSTR'

    def p_expression_float(self, p):
        p[0] = p[1]

    p_expression_float.__doc__ = 'expression : FLOAT'

    def p_expression_name(self, p):
        try:
            p[0] = self.names[p[1]]
        except LookupError:
            if re.match('^[a-fA-F0-9]*$',p[1]) != None:
                p[0] = p[1]
            else:
                p[0] = 0

    p_expression_name.__doc__ = 'expression : NAME'


if __name__ == '__main__':
    tb = time.time()
    calc = Calc()
    te = time.time()
    value = '(((_STATUSDTC&amp;0x1F)== 0x01)&amp;&amp; ((_STATUSDTC#5== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?2:((((_STATUSDTC&amp;0x1F)== 0x02)&amp;&amp; ((_STATUSDTC#5== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?4:((((_STATUSDTC&amp;0x1F)== 0x03)&amp;&amp; ((_STATUSDTC#5== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?6:((((_STATUSDTC&amp;0x9F)== 0x9F)&amp;&amp; ((_STATUSDTC#5== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?8:((((_STATUSDTC&amp;0x9F)== 0x8E)&amp;&amp; ((_STATUSDTC#5== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?10:((((_STATUSDTC&amp;0x9F)== 0x89)&amp;&amp; ((_STATUSDTC#5== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?14:((((_STATUSDTC&amp;0x9F)== 0x93)&amp;&amp; ((_STATUSDTC#5== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?16:((((_STATUSDTC&amp;0x9F)== 0x88)&amp;&amp; ((_STATUSDTC#5== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?12:((((_STATUSDTC&amp;0x1F)== 0x01)&amp;&amp; ((_STATUSDTC#6== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?1:((((_STATUSDTC&amp;0x1F)== 0x02)&amp;&amp; ((_STATUSDTC#6== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?3:((((_STATUSDTC&amp;0x1F)== 0x03)&amp;&amp; ((_STATUSDTC#6== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?5:((((_STATUSDTC&amp;0x9F)== 0x9F)&amp;&amp; ((_STATUSDTC#6== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?7:((((_STATUSDTC&amp;0x9F)== 0x8E)&amp;&amp; ((_STATUSDTC#6== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?9:((((_STATUSDTC&amp;0x9F)== 0x89)&amp;&amp; ((_STATUSDTC#6== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?13:((((_STATUSDTC&amp;0x9F)== 0x93)&amp;&amp; ((_STATUSDTC#6== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?15:((((_STATUSDTC&amp;0x9F)== 0x88)&amp;&amp; ((_STATUSDTC#6== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93))))?11:0)))))))))))))))'
    value = value.replace('&amp;', '&')
    value = value.replace('_STATUSDTC', '0x' + 'C9')
    tb = time.time()
    te = time.time()
    value = '((_STATUSDTC#5== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93)))?1:(((_STATUSDTC#6== 0x01)&amp;&amp;(((_STATUSDTC&amp;0x1F)== 0x01)||((_STATUSDTC&amp;0x1F)== 0x02)||((_STATUSDTC&amp;0x1F)== 0x03)||((_STATUSDTC&amp;0x9F)== 0x9F)||((_STATUSDTC&amp;0x9F)== 0x8E)||((_STATUSDTC&amp;0x9F)== 0x88)||((_STATUSDTC&amp;0x9F)== 0x89)||((_STATUSDTC&amp;0x9F)== 0x93)))?2:0)'
    value = value.replace('&amp;', '&')
    value = value.replace('_STATUSDTC', '0x' + 'D3')
    tb = time.time()
    te = time.time()
    value = '(1.0 * (100*_VXX_SPG_PWM_SP)) /256'
    value = value.replace('&amp;', '&')
    value = value.replace('_VXX_SPG_PWM_SP', '0x' + 'D3')
    tb = time.time()
    te = time.time()
    value = '(_MODULE_ABSENT_9!= 0x00)?(((_BOOLEEN_CONTACT_EMBRAYAGE== 0x00)||(_BOOLEEN_CONTACT_EMBRAYAGE== 0x01))?((_BOOLEEN_CONTACT_EMBRAYAGE== 0x01)?1:((_BOOLEEN_CONTACT_EMBRAYAGE== 0x00)?0:1)):0):0'
    value = value.replace('&amp;', '&')
    value = value.replace('_MODULE_ABSENT_9', '0x' + '01')
    value = value.replace('_BOOLEEN_CONTACT_EMBRAYAGE', '0x' + '00')
    tb = time.time()
    te = time.time()
    value = '_VIN'
    value = value.replace('_VIN', '11223344556677889900AABBCCDDEEFF1122')
    tb = time.time()
    te = time.time()
