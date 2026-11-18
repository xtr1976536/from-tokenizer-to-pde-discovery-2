"""Strict Cartesian source parser; symbols have declared roles before renaming.

Unlike the historical parser, z and r are not silently reserved coordinates.
This permits the source's graffiti field z in a genuinely 2D model and rejects
unmapped radial/third-axis derivatives. It does not rewrite legacy code.
"""
import re
from coefficient_free import Parser as HistoricalParser, OPERATORS, GREEK
from ast_runtime import Unsupported

# TeX unbraced subscripts consume ONE token. In mu_1u the field u is not
# part of the coefficient's name; mu_{1u} would be a different, braced name.
PARAM = re.compile(r'(?:\\[A-Za-z]+|[A-Za-z])(?:_\{[^{}]*\}|_[A-Za-z0-9])?')


class Parser(HistoricalParser):
    def derivative_variables(self):
        grouped = self.peek() == '{'
        if grouped:
            self.take('{')
        axes = ''
        while self.peek() in self.coordinates:
            axis = self.take()
            repeat = 1
            # In u_x^2 the superscript is OUTSIDE the unbraced subscript:
            # it squares u_x. Only x^2 INSIDE a subscript group repeats x.
            if grouped and self.peek() == '^':
                self.take('^')
                repeat = self.integer_exponent()
            axes += axis * repeat
            if not grouped:
                break
        if grouped:
            self.take('}')
        if not axes or len(axes) > 8:
            raise Unsupported('Derivative coordinates required (max order 8)')
        return axes


def parse(text, fields, scalar_parameters=(), coordinates=('x', 'y', 't')):
    text = re.sub(r'\\(?:biggl|biggr|bigl|bigr|Big|big)\b', '', text)
    text = re.sub(r'\\partial_\{([xyt]{2,8})\}\^\{?([2-8])\}?',
                  lambda m: r'\partial_{' + m[1] + '}' if len(m[1]) == int(m[2]) else m[0], text)
    text = re.sub(r'\\partial\^\{?([2-8])\}?_\{([xyt]{2,8})\}',
                  lambda m: r'\partial_{' + m[2] + '}' if len(m[2]) == int(m[1]) else m[0], text)
    text = text.replace(r'\nabla^2', r'\Delta').replace(r'\triangle', r'\Delta')
    names = []
    for match in PARAM.finditer(text):
        name = match.group()
        if name in OPERATORS or name in fields or name in coordinates:
            continue
        base = name.split('_')[0]
        if base in OPERATORS or base in fields:
            continue
        if name.startswith('\\') and base not in GREEK and name not in scalar_parameters:
            raise Unsupported('Unknown macro: ' + name)
        tail = text[match.end():]
        if re.match(r'\s*\(', tail) and name not in ('e',) and name not in scalar_parameters:
            group = re.match(r'\s*\(([^()]*)\)', tail)
            if group and name in GREEK and all(c in ''.join(coordinates) + ', ' for c in group[1]):
                raise Unsupported('Variable coefficient function requires structural treatment: ' + name)
            if base not in GREEK or group and group[1].strip() in fields:
                raise Unsupported('Unspecified function: ' + name)
        if name == 'i':
            raise Unsupported('Complex field system requires explicit real/imaginary decomposition')
        names.append(name)
    parameters = tuple(sorted(set(names), key=len, reverse=True))
    ast = Parser(text, fields=fields, coordinates=coordinates, parameters=parameters).parse()
    return ast, parameters
