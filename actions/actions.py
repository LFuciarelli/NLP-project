from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import sympy as sp
import re
from sympy.printing.str import StrPrinter

# Removes non-mathematical terms
def clean_equation(equation_str):
    # Matches only allowed characters
    cleaned_equation = re.sub(r"[^+\-*/=x\d.\s/]", "", equation_str)

    # Removes extra whitespace
    cleaned_equation = re.sub(r"\s+", " ", cleaned_equation).strip()

    return cleaned_equation

def multby_helper(s):
    if s == "half":
        return f"1/2 *"
    elif s == "a quarter":
        return f"1/4 *"
    elif s == "a third":
        return f"1/3 *"
    elif s == "double":
        return "2 *"
    elif s == "triple":
        return "3 *"
    elif str(s).find(".") >= 0:
        return f"{s} *"
    else:
        return s

class SolveEquationAction(Action):
    def name(self):
        return "action_solve_equation"

    def run(self, dispatcher, tracker, domain):
        entities = tracker.latest_message.get("entities", []) or [] #tracker.latest_message.get("number") or [] 
        extracted_positions = {}

        for entity in entities:
            extracted_positions[entity["start"]] = multby_helper(entity["value"])

        sort_dict = dict(sorted(extracted_positions.items(), key=lambda item: item[0]))
        equation = " ".join(f"{v}".strip().lower() for v in sort_dict.values())
        try:
            x = sp.Symbol("x")
            if equation.count("=") > 1:
                last_equals_index = equation.rfind("=")
                equation = equation[:last_equals_index].replace("= ", "") + equation[last_equals_index:]
            if equation.count("=") == 0:
                equation += " ="
            if equation.count("x") == 0 and equation[-1] == "=":
                equation += " x"
            equation = clean_equation(equation)
            dispatcher.utter_message(f"Equivalent equation: {equation}")
            lhs, rhs = equation.split("=")
            solution = sp.solve(sp.sympify(lhs) - sp.sympify(rhs), x)
            #solution = sp.solve(sp.sympify(equation))

            # Case in which it is not an equation to solve but an equation to check the validity
            if len(solution) == 0:
                solution = eval(equation.replace("=", "=="))
                dispatcher.utter_message(f"The solution is: {solution}")
            else:
                dispatcher.utter_message(f"The solution is: { StrPrinter({'full_prec': False}).doprint(sp.Float(solution[0], 5))}")
        except Exception as e:
            dispatcher.utter_message(f"Could not parse the equation. \nPlease, try rephrasing your math problem.")

        return []