import __init__ # all of the initialization that needs to be done, modification of sys path done there
import users, posts
from fastapi import FastAPI
from __init__ import LOGGING_CONFIG

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
    try:
        uvicorn.run(app, host="0.0.0.0", port=5952, log_config=LOGGING_CONFIG)
    except ValueError as ex:
        if "configure handler 'file'" in str(ex):
            print("Starting HTTP server without logging...")
            uvicorn.run(app, host="0.0.0.0", port=5952)
        else:
            print(f"AN ERROR OCCURRED WHILE STARTING THE API\n{str(ex)}")
    # uvicorn.run(app, host="0.0.0.0", port=5952) 