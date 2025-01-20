""" From: https://www.youtube.com/watch?v=41EfOY0Ldkc """

import dspy
import torch
import torch.nn as nn
import torch.nn.functional as F


class MultiHopQA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=3)
        self.gen_query = dspy.ChainOfThought("context, question -> query")
        self.gen_answer = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = []
        for hop in range(2):
            query = self.gen_query(context=context, question=question).query
            context += self.retrieve(query).passages
        return self.gen_answer(context=context, question=question)


class MultiHopQAWithAssertions(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=3)
        self.generate_query = dspy.ChainOfThought("context, question -> query")
        self.generate_answer = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context, queries = [], [question]

        for hop in range(2):
            query = self.generate_query(context=context, question=question).query

            dspy.Suggest(len(query) < 100,
                         "Query should be less than 100 characters")

            dspy.Suggest(is_distinct_query(query, queries),
                         f"Query should be distinct from {queries}")

            context += self.retrieve(query).passages
            queries += query
        return self.generate_answer(context=context, question=question)


class LongFormQAWithAssertions(dspy.Module):
    def __init__(self, passages_per_hop=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.generate_query = dspy.ChainOfThought("context, question -> query")
        self.generate_cited_paragraph = dspy.ChainOfThought("context, question -> paragraph")  # better with field description

    def forward(self, question):
        context = []

        for hop in range(2):
            query = self.generate_query(context=context, question=question).query
            context += self.retrieve(query).passages

        pred = self.generate_cited_paragraph(context=context, question=question)
        dspy.Suggest(citations_check(pred.paragraph),
                     "Every 1-2 sentences should have citations: 'text... [x].'")

        for line, citation in get_lines_and_citations(pred, context):
            dspy.Suggest(is_faithful(line, citation), f"Your output should be based on the context: '{citations}'")

        return pred


class GenerateAnswers(dspy.Signature):
    """Answers questions with short factoid answers."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")


class ProcessEmails(dspy.Module):
    def __init__(self, num_messages=3):
        super().__init__()

        self.weaviate_retriever = dspy.Retrieve(k=3, retriever=weaviate_rm)
        self.podcast_email = dspy.Predict("email -> podcast_yes_or_no")
        self.generate_query = dspy.Predict("email -> podcast_research_query")
        self.you_retriever = dspy.Retrieve(k=3, retriever=you_rm)
        self.podcast_outline = dspy.ChainOfThought("email, research -> podcast_discussion_topics")

    def forward(self, emails, date):
        podcast_outlines = []
        for email in emails:
            emails = self.weaviate_retriever(metadata=date)
            if self.podcast_email(emails):
                research_query = self.generate_query(email)
                research_contexts = self.you_retriever(research_query)
                podcast_outlines.append({
                    "email": email,
                    "outline_proposal": self.podcast_outline(email, research_contexts)
                })
        return podcast_outlines


class Net(nn.Module):

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Convd2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswers)

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate_answer(context=context, question=question)


class SimplifiedBootstrapFewShot(Teleprompter):
    def __init__(self, metric=None):
        self.metric = metric

    def compile(self, student, trainset, teacher=None):
        teacher = teacher if teacher is not None else student
        compiled_program = student.deepcopy()

        # Step 1: Prepare mappings between student and teacher Predict modules.
        # Note: other modules will rely on Predict internally.
        assert student_and_teacher_have_compatible_predict_modules(student, teacher)
        name2predictor, predictor2name = map_predictors_recursively(student, teacher)

        # Step 2: Bootstrap traces for each Predict module.
        # We'll loop over the training set. We'll try each example once for simplicity.
        for example in trainset:
            if we_found_enough_bootstrapped_demos(): break

            # turn on compiling mode which will allow us to keep track of the traces
            with dspy.settings.context(compiling=True):
                # run the teacher program on the example, and get its final prediction
                # note that compiling=True may affect  the internal behavior here
                prediction = teacher(**example.inputs())

                # get the trace of all the internal Predict calls from the teacher program
                predicted_traces = dspy.settings.trace

            # if the prediction is valid, add the example to the traces
            if self.metric(example, prediction, predicted_traces):
                for predictor, inputs, outputs in predicted_traces:
                    d = dspy.Example(automated=True, **inputs, **outputs)
                    predictor_name = self.predictor2name[id(predictor)]
                    compiled_program[predictor_name].demonstrations.append(d)

        return compiled_program
