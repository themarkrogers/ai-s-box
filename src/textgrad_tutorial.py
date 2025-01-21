# https://www.youtube.com/watch?v=Qks4UEsRwl0

import textgrad as tg

# Initialize the system prompt
system_prompt = tg.Variable(
    "You are a helpful language model. Think step by step.",
    requires_grad=True,
    role_description="system prompt to the language model",
)

# Set up the model object 'parameterized by' the prompt.
llm_engine = tg.get_engine("gpt-3.5-turbo")
model = tg.BlackBoxLLM(llm_engine, system_prompt=system_prompt)

# Optimize the system prompt
optimizer = tg.TextualGradientDescent(parameters=[system_prompt])

for iteration in range(max_iterations):
    batch_x, batch_y = next(train_loader)
    optimizer.zero_grad()
    # Do the forward pass
    responses = model(batch_x)
    losses = [loss_fn(response, y) for (response, y) in zip(responses, batch_y)]
    total_loss = tg.sum(losses)
    # Do the backward pass and compute gradients
    total_loss.backward()
    # Update the system prompt
    optimizer.step()
