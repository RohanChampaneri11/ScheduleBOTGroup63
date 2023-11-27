from .mood_events import MOOD_EVENT_MAP

import random

async def recommend_event(ctx, mood):
    mood = mood.lower()
    if mood in MOOD_EVENT_MAP:
        events = MOOD_EVENT_MAP[mood]
        recommended_event = random.choice(events)
        await ctx.send(f"How about attending a '{recommended_event}'?")
    else:
        await ctx.send("Sorry, I don't have recommendations for that mood yet.")
