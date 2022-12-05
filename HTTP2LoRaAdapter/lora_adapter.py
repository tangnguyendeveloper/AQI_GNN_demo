from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json
import serial

class LoRa:
    def __init__(self, uart_port: str, baudrate: int = 115200):
        self.__serial = serial.Serial(
            port=uart_port,
            baudrate=baudrate, timeout=1
        )


    def __del__(self):
        self.__serial.close()


    async def send_message(self, msg: str) -> int:
        return self.__serial.write(msg.encode("unicode_escape"))


    async def receive_message(self) -> str:
        return self.__serial.readline().decode("unicode_escape")




class TimeStamp(BaseModel):
    co: float
    no2: float
    o3: float
    pm25: float
    
    def PreProcessing(self):
        
        if self.co < 30:
            self.co = (self.co / 30) * 0.16
        elif self.co < 100:
            self.co = (((self.co - 30) / 70) * 0.16) + 0.16
        elif self.co < 800:
            self.co = (((self.co - 100) / 700) * 0.16) + 0.32
        elif self.co < 1500:
            self.co = (((self.co - 800) / 700) * 0.16) + 0.64
        else:
            self.co = min((((self.co - 1500) / 100) * 0.2) + 0.8, 1.0)
            
        if self.no2 < 0.2:
            self.no2 = (self.no2 / 0.2) * 0.16
        elif self.no2 < 50:
            self.no2 = (((self.no2 - 0.2) / 49.8) * 0.16) + 0.16
        elif self.no2 < 140:
            self.no2 = (((self.no2 - 50) / 90) * 0.16) + 0.48
        else:
            self.no2 = min((((self.no2 - 140) / 10) * 0.2) + 0.8, 1.0)
            
        if self.o3 < 0.2:
            self.o3 = (self.o3 / 0.2) * 0.16
        elif self.o3 < 0.9:
            self.o3 = (((self.o3 - 0.2) / 0.7) * 0.16) + 0.16
        else:
            self.o3 = min((((self.o3 - 0.9) / 0.1) * 0.2) + 0.8, 1.0)
        
        if self.pm25 < 5e-5:
            self.pm25 = round(self.pm25 / 5e-5, 8) * 0.16
        else:
            self.pm25 = 1.0


origins = [
    "http://localhost",
    "http://localhost:8000",
]
    
app = FastAPI(title="LoRa Adapter")
lora = LoRa("COM4", 9600)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/lora_api/")
async def LoRaAPI(timestap: TimeStamp):
    
    raw = timestap.dict()
    raw["tag"] = 0
    raw = json.dumps(raw)
    
    timestap.PreProcessing()
    processed = timestap.dict()
    processed["tag"] = 1
    processed = json.dumps(processed)
    
    await lora.send_message(raw + "\n")
    await lora.send_message(processed + "\n")
    
    print(raw)
    print(processed)
    
    return timestap

    
    
