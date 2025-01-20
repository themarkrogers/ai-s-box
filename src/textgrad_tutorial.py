# https://www.youtube.com/watch?v=Qks4UEsRwl0

import TextGrad as tg

# Initialize the system prompt
system_prompt = tg.Variable("You are a helpful language model. Think step by step.",
                            requires_grad=True,
                            role_description="system prmp to the language model")

# Set up the model object 'parameterized by' the prompt.
model = tb.GlackBoxLLM(system_prompt=system_prompt)

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
    optmiizer.step()
