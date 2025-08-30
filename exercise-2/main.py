from agents import Agent, Runner, trace, RunContextWrapper
from connection import config
import chainlit as cl
import asyncio
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class AirlineSeatBooking(BaseModel):
    name: str
    age: int
    seat_preference: str
    travel_experience: str

personOne = AirlineSeatBooking(name= "Ahmed", age= 17, seat_preference= "window", travel_experience= "First-time")

def dynamic_instructions(ctx: RunContextWrapper[AirlineSeatBooking], agent: Agent):
    if ctx.context.seat_preference == "window" and ctx.context.travel_experience == "First-time":
        return "Explain window benefits, mention scenic views, reassure about flight experience."
    elif ctx.context.seat_preference == 'aisle' and ctx.context.travel_experience == "occasional":
        return "Explain aisle seat benefits and mention its views and flight experince."
    elif ctx.context.seat_preference == 'middle' and ctx.context.travel_experience == "frequent":
        return "Acknowledge the compromise, suggest strategies, offer alternatives."
    elif ctx.context.seat_preference == 'any' and ctx.context.travel_experience == "premium":
        return "Highlight luxury options, upgrades, priority boarding."

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