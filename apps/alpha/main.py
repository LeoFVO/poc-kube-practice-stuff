import os
from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

beta_url = os.getenv("BETA_URL", "http://beta:8000")
charlie_url = os.getenv("CHARLIE_URL", "http://charlie:8000")

@app.get("/sentences")
async def get_sentence():
    try:
        async with httpx.AsyncClient() as client:
            adjective = await client.get(f"{beta_url}/adjectives")
            noun = await client.get(f"{charlie_url}/nouns")

            adjective.raise_for_status()
            noun.raise_for_status()

            sentence = f"The {noun.json()['noun']} is {adjective.json()['adjective']}"
            return {"sentence": sentence}

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with services: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
