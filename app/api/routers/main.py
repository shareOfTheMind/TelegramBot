import __init__ # all of the initialization that needs to be done, modification of sys path done there
from fastapi import FastAPI
import users, posts

app = FastAPI()

# Include routers for different endpoints
app.include_router(users.router)
app.include_router(posts.router)

# Example root route
@app.get("/")
async def root():
    return {"message": "Welcome to the API route for MindVirus"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)