from fastapi import FastAPI
import random

app = FastAPI()

adjectives = ["beautiful", "colorful", "vibrant", "joyful", "mysterious"]

@app.get("/adjectives")
def get_adjective():
    random_adjective = random.choice(adjectives)
    return {"adjective": random_adjective}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
