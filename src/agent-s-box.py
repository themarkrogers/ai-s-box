from src.utils import get_s_box_for


def main() -> None:
    input_length = 3
    output_length = 3
    num_unique_symbols = 5 * 5 * 5

    model_id = "mistral"

    output = get_s_box_for(input_length, output_length, num_unique_symbols, model_id=model_id)
    print(f"{output=}")
