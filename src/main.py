# src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import user_routes, role_routes,manifest_routes,baggage_case,auth,fligths_manifest
from .error_middleware import ErrorMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:3001", "https://platform-ground-ops.vercel.app", "https://arajet-app-odsgrounds-backend-dev-fudkd8eqephzdubq.eastus-01.azurewebsites.net"],
#    allow_origins=["http://localhost:3000", "https://platform-ground-ops.vercel.app", "https://your-production-url.com"],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
    
)

app.add_middleware(ErrorMiddleware)

app.include_router(user_routes.router, prefix="/api/users")
app.include_router(role_routes.router, prefix="/api/roles")
app.include_router(manifest_routes.router, prefix="/api/manifest")
app.include_router(baggage_case.router, prefix="/api/baggage-case")
app.include_router( auth.router, prefix="/api/login")
app.include_router( fligths_manifest.router, prefix="/api/fligths_manifest")
