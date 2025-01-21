from dotenv import load_dotenv
from typing import Any
import os

import ollama


def create_system_prompt():
    with open("../data/rijndael-8-forward.tsv", "r") as known_s_box_1_file:
        known_s_box_1 = known_s_box_1_file.readlines()
    with open("../data/rijndael-8-reverse.tsv", "r") as known_s_box_2_file:
        known_s_box_2 = known_s_box_2_file.readlines()
    with open("../data/system_prompt.txt", "r") as system_prompt_file:
        raw_system_prompt = system_prompt_file.read()

    system_prompt = raw_system_prompt.format(example_sbox_1=known_s_box_1, example_sbox_2=known_s_box_2)

    return system_prompt


def create_user_prompt(input_length: int, output_length: int, num_unique_symbols: int) -> str:
    return f"""Can you create a cryptographic s-box that fit these parameters?
* number_of_characters_in_input: {input_length}
* number_of_characters_in_output: {output_length}
* number_of_possible_symbols: {num_unique_symbols}"""


def get_llm_response_for_prompt(system_prompt: str, user_prompt: str, model: Any = "mistral") -> Any:
    # response = ollama.chat(model=model, messages=[
    #     { "role": "user", "content": prompt }
    # ])
    # return response
    response = ollama.chat(
        # model="bge-base",
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": user_prompt},
        ],
    )
    response_text = response["message"]["content"]
    return response_text


def get_open_ai_api_key() -> str:
    load_dotenv()  # Load environment variables from the .env file
    api_key = os.getenv("OPEN_AI_API_KEY", None)
    if api_key is None:
        raise ValueError("Could not find OpenAI Api Key")
    return api_key


def get_s_box_for(input_length: int, output_length: int, num_unique_symbols: int, model_id: Any = "mistral") -> Any:
    system_prompt = create_system_prompt()
    user_query = create_user_prompt(input_length, output_length, num_unique_symbols)

    # output = run_text_bedrock_llm(prompt=query, system_prompt=system_prompt, model_id=model_id_sonnet)
    output = get_llm_response_for_prompt(system_prompt=system_prompt, user_prompt=user_query, model=model_id)
    return output
