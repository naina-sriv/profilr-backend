from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    """Enable CORS for frontend communication."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # replace '*' with frontend URL in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
