"""
Make a dspy.Signature that takes in English and outputs python3 code
* Ensure that the output of the generated python3 code is always a list[list[str]]

Make a dspy.Module that leverages that Signature
* Use the validate_s_box function to assign a score
* Use the known-good s-boxes as Few Shot examples to seed the AI Program
* Iterate until a few candidate s-boxes are generated
* Write those to disk (as we validate each one)
"""

from typing import Any

from dspy.teleprompt import BootstrapFewShot
import dspy

from src.evaluate_s_box import evaluate_s_box


class CryptographicSBoxQA(dspy.Signature):
    """
    Generate python3 function that creates a 2-dimensional array of strings representing a cryptographic S-box.
    """

    question = dspy.InputField(desc="input_length: int, output_length: int, num_unique_symbols: int")
    # answer = dspy.OutputField(desc="a python3 function that returns a list[list[str]]")
    answer = dspy.OutputField(desc="a list[list[str]]")


# def evaluate_s_box_code(s_box_function: func) -> float:
#     ...


class CryptographicSBoxModule(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        tuple_str = "(input_length, output_length, num_unique_symbols)"
        self.generate_answer = dspy.ChainOfThought(f"{tuple_str} -> python3 function")

    def forward(self, question):
        context = self.retrieve(question).passages
        prediction = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=prediction.answer)


def build_s_box_teleprompter(train_set: Any) -> Any:  # ToDo: Determine actual types & tighten signature
    # Set up a basic teleprompter, which will compile our AI program.
    teleprompter = BootstrapFewShot(metric=evaluate_s_box)

    compiled_s_box_program = teleprompter.compile(CryptographicSBoxModule(), trainset=train_set)  # Compile!
    return compiled_s_box_program
