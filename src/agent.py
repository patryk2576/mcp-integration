import os
import asyncio
from agents import Agent, Runner, function_tool, ItemHelpers, TResponseInputItem, trace, set_default_openai_key
from pydantic import BaseModel
import subprocess
from typing import Literal
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)'
)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

set_default_openai_key(str(OPENAI_API_KEY))

class EvaluationFeedback(BaseModel):
    feedback: str
    score: Literal["pass", "needs_improvement", "fail"]

evaluator = Agent(
    name = "evaluator",
    instructions = (
        "You evaluate the quality of an answer to a homework question. "
        "If it's not good enough, you provide feedback on what needs to be improved. "
    ),
    output_type = EvaluationFeedback
)

@function_tool
def history_fun_fact() -> str:
    """Return a short history fact."""
    return "Sharks are older than trees."

history_tutor_agent = Agent(
    name = "History Tutor",
    handoff_description = "Specialist agent for historical questions",
    instructions = "You answer history questions clearly and concisely.",
    tools = [history_fun_fact]
)

math_tutor_agent = Agent(
    name = "Math Tutor",
    handoff_description = "Specialist agent for math questions",
    instructions = "You explain math step by step and include worked examples."
)

triage_agent = Agent(
    name = "Triage Agent",
    instructions = "Route each homework question to the right specialist.",
    handoffs = [history_tutor_agent, math_tutor_agent]
)

async def main():

    msg = "Who was the first president of the United States?"

    input_items: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    latest_result: str | None = None
    max_rounds = 3
    rounds = 0

    with trace("LLM as a judge"):
        while True:
            homework_result = await Runner.run(
                triage_agent, 
                input_items
            )

            input_items = homework_result.to_input_list()
            latest_result = ItemHelpers.text_message_outputs(homework_result.new_items)
            logger.info(f"Latest homework answer: {latest_result}")

            evaluator_result = await Runner.run(evaluator, input_items)
            result: EvaluationFeedback = evaluator_result.final_output

            logger.info(f"Evaluator score: {result.score}")

            if result.score == "pass":
                logger.info("Homework answer passed evaluation! Exiting.")
                break

            rounds += 1
            if max_rounds is not None and rounds >= max_rounds:
                logger.info("Stopping after limiting rounds.")
                break

            logger.info("Re-running with feedback")

            input_items.append({"context": f"Feedback: {result.feedback}", "role": "user"})

        logger.info(f"Final homework answer: {latest_result}")

if __name__ == "__main__":
    asyncio.run(main())