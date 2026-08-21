"""Reflex configuration for Takdora."""

import os

import reflex as rx


config = rx.Config(
    app_name="takdora",
    api_url=os.getenv("API_URL", "http://localhost:8000"),
    backend_path=os.getenv("BACKEND_PATH", ""),
    db_url=os.getenv("DATABASE_URL", "postgresql+psycopg://takdora:takdora@db:5432/takdora"),
    telemetry_enabled=False,
)
