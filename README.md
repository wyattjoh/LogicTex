# LogicTex

## Usage
***python3 shell***

	>>> from logic_tex import LogicTable
	>>> expression = [['A', '&', 'B'], '=', ['~', 'B']]
	>>> lt = LogicTable(expression)
	>>> lt.generate_question('3.1Eb')
	\input{3.1Eb.tex}

***assignment.tex***

	\documentclass[11pt, oneside]{article}
	\usepackage{geometry}
	\geometry{letterpaper}
	\usepackage{graphicx}
	\usepackage{amssymb}

	\begin{document}
	\input{3.1Eb.tex}
	\end{document}  

***3.1Eb.tex***

	\begin{tabular}{ c c | c c c c c c }
		A & B & (A & $\&$ & B) & $\equiv$ & $\lnot$ & B \\
		\hline
		T & T & T & T & T & F & F & T \\
		T & F & T & F & F & F & T & F \\
		F & T & F & F & T & T & F & T \\
		F & F & F & F & F & F & T & F \\
	\end{tabular}

## Testing

Testing is done via doctest.

	python3 logic_table.py
