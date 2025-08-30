from agents import Agent, Runner, trace, RunContextWrapper
from connection import config
import chainlit as cl
import asyncio
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class MedicalExplaination(BaseModel):
    name: str
    age: int
    person_type: str

personOne = MedicalExplaination(name= "Ahmed", age= 17, person_type= "Doctor")

def dynamic_instructions(ctx: RunContextWrapper[MedicalExplaination], agent: Agent):
    if ctx.context.person_type == "Patient":
        return "Use simple, non-technical language. Explain medical terms in everyday words. Be empathetic and reassuring."
    elif ctx.context.person_type == 'Medical Student':
        return "Use moderate medical terminology with explanations. Include learning opportunities."
    elif ctx.context.person_type == 'Doctor':
        return "Use full medical terminology, abbreviations, and clinical language. Be concise and professional."

personal_agent = Agent(
    name = "Personal Agent",
    instructions = dynamic_instructions
)


@cl.on_message
async def main(input: cl.Message):
    with trace("Exercise 1"):
        user_input = input.content

        result = Runner.run_streamed(
            personal_agent, 
            input = user_input,
            run_config=config,
            context = personOne
        )

    msg = cl.Message(content="")
    await msg.send() 

    async for event in result.stream_events():
        if event.type == 'raw_response_event' and isinstance(event.data, ResponseTextDeltaEvent):
            msg.content += event.data.delta
            await msg.update() 

    #  msg.content = result.final_output.response
    # await msg.update()


                

if __name__ == "__main__":
    asyncio.run(main())