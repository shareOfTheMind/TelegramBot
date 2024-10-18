import sys
import os

# Append the base directory of your project to sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.append(base_dir)

from fastapi import FastAPI
import users, posts

app = FastAPI()

# Include routers for different endpoints
app.include_router(users.router)
app.include_router(posts.router)

# Example root route
@app.get("/")
async def root():
    return {"message": "Welcome to the API"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)