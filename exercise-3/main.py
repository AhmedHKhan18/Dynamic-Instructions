from agents import Agent, Runner, trace, RunContextWrapper
from connection import config
import chainlit as cl
import asyncio
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class TravelPlanner(BaseModel):
    name: str
    age: int
    trip_type: str
    traveler_profile: str

personOne = TravelPlanner(name= "Ahmed", age= 17, trip_type= "Adventure", traveler_profile= "Solo")

def dynamic_instructions(ctx: RunContextWrapper[TravelPlanner], agent: Agent):
    if ctx.context.trip_type == "Adventure" and ctx.context.traveler_profile == "Solo":
        return "Suggest exciting activities, focus on safety tips, recommend social hostels and group tours for meeting people."
    elif ctx.context.trip_type == 'Cultural' and ctx.context.traveler_profile == "Family":
        return "Focus on educational attractions, kid-friendly museums, interactive experiences, family accommodations."
    elif ctx.context.trip_type == 'Business' and ctx.context.traveler_profile == "Executive":
        return "Emphasize efficiency, airport proximity, business centers, reliable wifi, premium lounges."

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