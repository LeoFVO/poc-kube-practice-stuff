from fastapi import FastAPI
import random

app = FastAPI()

nouns = ["cat", "dog", "tree", "mountain", "ocean"]

@app.get("/nouns")
def get_noun():
    random_noun = random.choice(nouns)
    return {"noun": random_noun}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
