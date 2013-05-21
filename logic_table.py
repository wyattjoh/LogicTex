"""
LogicTex generates LaTeX files for given logical expressions and outputs the
nessesary input statements for use in your main latex program.

Copyright (C) 2013 Wyatt Johnson <wyatt@wyattjohnson.ca>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


class LatexTable:
    """
    Generates tables for LaTeX given head of table and data for table. Non-portable ATM.
    """
    def __init__(self, head, data):
        self._head = head
        self._data = data

    def _pt(self, val):
        if val:
            return 'T'
        else:
            return 'F'

    def _get_head(self):
        """
        >>> lt = LatexTable('lala', [[['T', 'F'], ['T', 'F', 'T', 'F']], [['lala'], ['lala']]])
        >>> lt._get_head()
        '\\\\begin{tabular}{ c c | c c c c }\\n'
        """
        head_data = "\\begin{tabular}{"

        num_vars = len(self._data[0][0])
        num_resu = len(self._data[0][1])

        for i in range(num_vars):
            head_data = head_data + " c"

        head_data = head_data + " |"

        for i in range(num_resu):
            head_data = head_data + " c"

        head_data = head_data + " }\n"

        return head_data

    def _get_foot(self):
        return '\\end{tabular}\n'

    def _get_latex_line(self, data):
        lcd = data[0]
        rcd = data[1]

        string = ""

        string = string + "\t"

        for element in lcd + rcd[:-1]:
            string = string + "%1s & " % self._pt(element)

        string = string + "%1s \\\\\n" % self._pt(rcd[-1])

        return string

    def _get_latex_lines(self):
        data_lines = ""

        for data_entry in self._data:
            data_lines = data_lines + self._get_latex_line(data_entry)

        return data_lines

    def __str__(self):
        string_data = ""

        string_data = string_data + self._get_head()
        string_data = string_data + self._head
        string_data = string_data + '\t\\hline\n'
        string_data = string_data + self._get_latex_lines()
        string_data = string_data + self._get_foot()

        return string_data


class Operators:
    ops = ['&', '=', '|', '~', 'i']

    def parse(self, op, lhs, rhs=None):
        args = {
            '&': self.land,
            '=': self.leq,
            '|': self.lor,
            '~': self.lnot,
            'i': self.lif
        }

        try:
            fct = args[op]

            return fct(lhs, rhs)
        except KeyError:
            raise Exception("Operator: %s is undefined." % op)

    def land(self, lhs, rhs):
        """
        >>> op = Operators()
        >>> op.land(True, True)
        True
        >>> op.land(True, False)
        False
        >>> op.land(False, True)
        False
        >>> op.land(False, False)
        False
        """
        if lhs and rhs:
            return True
        else:
            return False

    def leq(self, lhs, rhs):
        """
        >>> op = Operators()
        >>> op.leq(True, True)
        True
        >>> op.leq(True, False)
        False
        >>> op.leq(False, True)
        False
        >>> op.leq(False, False)
        True
        """
        if lhs is rhs:
            return True
        else:
            return False

    def lor(self, lhs, rhs):
        """
        >>> op = Operators()
        >>> op.lor(True, True)
        True
        >>> op.lor(True, False)
        True
        >>> op.lor(False, True)
        True
        >>> op.lor(False, False)
        False
        """
        if lhs or rhs:
            return True
        else:
            return False

    def lnot(self, lhs, rhs):
        """
        >>> op = Operators()
        >>> op.lnot(True, True)
        False
        >>> op.lnot(True, False)
        False
        >>> op.lnot(False, True)
        True
        >>> op.lnot(False, False)
        True
        """
        if not lhs:
            return True
        else:
            return False

    def lif(self, lhs, rhs):
        """
        >>> op = Operators()
        >>> op.lif(True, True)
        True
        >>> op.lif(True, False)
        False
        >>> op.lif(False, True)
        True
        >>> op.lif(False, False)
        True
        """
        if lhs:
            if rhs:
                return True
            else:
                return False
        else:
            return True


OP = Operators()


class LogicTable:
    atomic_operators = {
        '~': "$\lnot$"
    }
    other_operators = {
        '&': "$\&$",
        '|': "$\lor$",
        '=': "$\equiv$",
        'i': "$\supset$"
    }
    operators = atomic_operators
    operators.update(other_operators)

    def __init__(self, expression):
        """
        >>> expression = [['A', '&', 'B'], '=', ['~', 'B']]
        >>> lt = LogicTable(expression)
        """

        self._expression = expression
        self._parse_chars()  # Generates the self._chars
        self._perms = self._gen_perm()  # Generates all permutations of logical groups
        self._parse_groups()

        self.comp_perm()

    def comp_perm(self, expression=None, permutations=None, **kwargs):
        """
        >>> expression = ['~', 'B']
        >>> lt = LogicTable(expression)
        >>> lt.comp_perm()
        [([True], [False, True]), ([False], [True, False])]
        >>> expression = ['A', '&', 'A']
        >>> lt = LogicTable(expression)
        >>> lt._chars
        ['A']
        >>> lt.comp_perm()
        [([True], [True, True, True]), ([False], [False, False, False])]
        >>> expression = ['~', ['A', '&', 'A']]
        >>> lt = LogicTable(expression)
        >>> lt._chars
        ['A']
        >>> lt.comp_perm()
        [([True], [False, True, True, True]), ([False], [True, False, False, False])]
        >>> expression = ['~', 'B']
        >>> lt = LogicTable(expression)
        >>> lt.comp_perm(simple=True)
        [([True], [False]), ([False], [True])]
        >>> expression = ['A', '&', 'A']
        >>> lt = LogicTable(expression)
        >>> lt._chars
        ['A']
        >>> lt.comp_perm(simple=True)
        [([True], [True]), ([False], [False])]
        >>> expression = ['~', ['A', '&', 'A']]
        >>> lt = LogicTable(expression)
        >>> lt._chars
        ['A']
        >>> lt.comp_perm(simple=True)
        [([True], [False]), ([False], [True])]
        """
        if expression is None:
            expression = self._expression.copy()

        if permutations is None:
            permutations = self._perms

        result = []

        for permutation in permutations:
            final_connective, solved_expression = self._ed(expression, permutation)
            # print("Solved Expression: %s" % str(solved_expression))

            if kwargs.get('simple', False):
                final_connective, solved_expression = self._ed(expression, permutation)
                result.append((permutation, [final_connective]))
            else:
                collapsed_expression = self._collapse_list(solved_expression)

                result.append((permutation, collapsed_expression))

        self._result = result.copy()

        return result.copy()

    def _ed(self, element, permutation):
        ret = []

        op = None

        if type(element) is list:
            element_length = len(element)

            if element_length > 3:
                raise Exception('Invalid element length: %s' % element)

            if element_length is 3:
                # Decompile into three sections and parse
                lhs, lhs_r = self._ed(element[0], permutation)
                rhs, rhs_r = self._ed(element[2], permutation)

                op = op_r = OP.parse(element[1], lhs, rhs)

                ret.append(lhs_r)
                ret.append(op_r)
                ret.append(rhs_r)

            if element_length is 2:
                # Decompile into two sections and parse
                rhs, rhs_r = self._ed(element[1], permutation)

                op = op_r = OP.parse(element[0], rhs)

                ret.append(op_r)
                ret.append(rhs_r)

        elif type(element) is str:
            op = ret = permutation[self._chars.index(element)]

        return op, ret

    def _parse_chars(self, expression=None):
        """
        >>> expression = [['B', '&', 'A'], '=', ['~', 'B']]
        >>> lt = LogicTable(expression)
        >>> lt._chars
        ['A', 'B']
        """
        if expression is None:
            expression = self._expression
            self._chars = []

        if len(expression) <= 1 and type(expression) is str:
            if expression not in self.operators and expression not in self._chars:
                self._chars.append(expression)
        else:
            for element in expression:
                self._parse_chars(element)

        self._chars = sorted(self._chars)

    def _parse_groups(self, expression=None):
        """
        >>> expression = [['A', '&', 'B'], '=', ['~', 'B']]
        >>> lt = LogicTable(expression)
        >>> lt._group
        ['A', '&', 'B', '=', '~', 'B']
        """
        if expression is None:
            expression = self._expression
            self._group = []

        if len(expression) <= 1:
            self._group.append(expression)
        else:
            for element in expression:
                self._parse_groups(element)

    def _collapse_list(self, expanded_list):
        """
        >>> expression = [['A', '&', 'B'], '=', ['~', 'B']]
        >>> lt = LogicTable(expression)
        >>> expanded_list = [['1', '2', '3'], '4', ['5', '6']]
        >>> lt._collapse_list(expanded_list)
        ['1', '2', '3', '4', '5', '6']
        >>> expanded_list = [[False, False, False], False, [False, True]]
        >>> lt._collapse_list(expanded_list)
        [False, False, False, False, False, True]
        >>> expanded_list = [[0, 0, 0], 0, [0, 1]]
        >>> lt._collapse_list(expanded_list)
        [0, 0, 0, 0, 0, 1]
        """
        # from itertools import chain

        ret = []

        for item in expanded_list:
            if type(item) is list:
                coll = list(self._collapse_list(item))
                ret = ret + coll
            else:
                ret.append(item)

        return ret

    def _gen_perm(self):
        """
        >>> expression = ['A']
        >>> lt = LogicTable(expression)
        >>> lt._gen_perm()
        [[True], [False]]
        >>> expression = [['B', '&', 'A'], '=', ['~', 'B']]
        >>> lt = LogicTable(expression)
        >>> lt._chars
        ['A', 'B']
        >>> lt._gen_perm()
        [[True, True], [True, False], [False, True], [False, False]]
        """
        import itertools

        char_count = len(self._chars)
        perms = []

        for perm in itertools.product([True, False], repeat=char_count):
            perms.append(list(perm))

        return perms

    def exp_to_str(self, expression=None):
        """
        >>> expression = [[['A', '&', 'B'], '=', ['~', 'B']], '&', 'C']
        >>> lt = LogicTable(expression)
        >>> lt.exp_to_str()
        '((A & B) = ~ B) & C'
        """
        if expression is None:
            expression = self._expression

        string = ""

        if len(expression) <= 1:
            return str(expression)

        for element in expression:
            if type(element) is list:
                if len(element) > 2:
                    string = string + '('
                    string = string + self.exp_to_str(element)
                    string = string + ')'
                else:
                    string = string + self.exp_to_str(element)
            elif type(element) is str:
                if element in self.operators:
                    string = string + " " + element + " "
                else:
                    string = string + element

        string = string.replace("  ", " ")

        return string

    def _tex_head(self, **kwargs):
        """
        >>> expression = [['A', '&', 'B'], '=', ['~', 'B']]
        >>> lt = LogicTable(expression)
        >>> lt._tex_head()
        '\\tA & B & (A & $\\\\&$ & B) & $\\\\equiv$ & $\\\\lnot$ & B \\\\\\\\\\n'
        >>> lt._tex_head(simple=True)
        '\\tA & B & (A $\\\\&$ B) $\\\\equiv$ $\\\\lnot$ B \\\\\\\\\\n'
        """
        array = self.exp_to_str().strip().split(' ')
        tex = "\t"

        for element in self._chars:
            tex = tex + element + ' & '

        if kwargs.get('simple', False):
            for element in array[:-1]:
                if element in self.operators:
                    element = self.operators[element]

                tex = tex + element + ' '

            tex = tex + array[-1] + ' \\\\\n'

        else:
            for element in array[:-1]:
                if element in self.operators:
                    element = self.operators[element]

                tex = tex + element + ' & '

            tex = tex + array[-1] + ' \\\\\n'

            tex = tex.replace('& ( & $\lnot$ &', '& ( $\lnot$ &')

        return tex

    def _generate_tex(self, **kwargs):
        tex_head = self._tex_head(**kwargs)
        tex_data = self.comp_perm(**kwargs)

        self._tt = LatexTable(tex_head, tex_data)

        return str(self._tt)

    def generate_question(self, qid, **kwargs):
        """
        Generates the LaTeX source in a file designated by qid.

        >>> expression = [['A', '&', 'B'], '=', ['~', 'B']]
        >>> lt = LogicTable(expression)
        >>> lt.generate_question('tester')
        \input{tester.tex}
        """

        if kwargs.get('perm_ovr', None) is not None:
            self._perms = [kwargs.get('perm_ovr', None)]

        tex = self._generate_tex(**kwargs)
        with open("%s.tex" % qid, "w") as tex_file:
            tex_file.write(str(tex))

        print("\\input{%s.tex}" % qid)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
