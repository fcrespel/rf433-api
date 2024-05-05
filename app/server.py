#!/usr/bin/python3

import argparse
import logging
from contextlib import asynccontextmanager

import odroid_wiringpi as wiringpi
import uvicorn
from chacondio10.routes import router as chacondio10_router
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
  logger.info(f"Setting up WiringPi for GPIO {app.state.gpio}")
  if wiringpi.wiringPiSetup() == -1:
    raise Exception("Failed to initialize WiringPi")
  wiringpi.pinMode(app.state.gpio, wiringpi.OUTPUT)
  yield

app = FastAPI(title="Remote Control REST API", description="REST API to use an RF 433 MHz transmitter as a remote control", version="1.0", lifespan=lifespan)
app.include_router(chacondio10_router)
app.state.gpio = 0
app.state.chacondio10 = {}

@app.get("/", include_in_schema=False)
async def home_page():
  return RedirectResponse("/docs")

@app.get("/health", tags=["health"])
async def health():
  return {"status": "UP"}

def parse_args():
  parser = argparse.ArgumentParser(description=app.title)
  parser.add_argument("-a", "--address", help="Address to bind to (default: 127.0.0.1)", type=str, default="127.0.0.1")
  parser.add_argument("-p", "--port", help="Port to listen on (default: 8001)", type=int, default=8001)
  parser.add_argument("-g", "--gpio", help="GPIO WiringPi pin number (default: 0)", type=int, choices=range(0, 30), metavar="GPIO", default=0)
  parser.add_argument("-l", "--log-level", help="Log level (default: INFO)", type=str, default="INFO", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"])
  return parser.parse_args()

def main():
  args = parse_args()
  app.state.gpio = args.gpio
  uvicorn.run(app, host=args.address, port=args.port, log_level=logging.getLevelName(args.log_level))

if __name__ == "__main__":
  main()
