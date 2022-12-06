import numpy as np
import tensorflow.lite as tflite
import json
import paho.mqtt.publish as publish
import serial
import asyncio


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



TF_MODEL_PATH = "AQI_GNN_final/AQI_model_GNN_final.tflite"
model = None
input_tensor_index = None
output_tensor_index = None



input_queue = np.zeros(32, dtype=np.float32)

async def LoadModel():
    global model, input_tensor_index, output_tensor_index
    
    model = tflite.Interpreter(model_path=TF_MODEL_PATH)
    model.allocate_tensors()
    input_tensor_index = model.get_input_details()[0]["index"]
    output_tensor_index = model.get_output_details()[0]["index"]


async def Predict(input_tensor):
    model.set_tensor(input_tensor_index, input_tensor)
    model.invoke()
    return model.get_tensor(output_tensor_index)


def load_configure() -> dict:
    js_conf = None
    with open("gateway_config.json") as f_js:
        js_conf = json.load(f_js)
    return js_conf


async def Publish_Predict(js_conf, msg):
    global input_queue
    
    input_queue[4:] = input_queue[:-4]
    input_queue[0] = msg["co"]
    input_queue[1] = msg["no2"]
    input_queue[2] = msg["o3"]
    input_queue[3] = msg["pm25"]
    
    if model is None:
        await LoadModel()
        
    result = (await Predict(input_queue.reshape(1, 32))).reshape(6)
    json_data = json.dumps({
        "Fresh": round(float(result[0]*100), 2),
        "Polluted":  round(float(result[1]*100), 2),
        "Headaches":  round(float(result[2]*100), 2),
        "Pneumonia":  round(float(result[3]*100), 2),
        "Convulsions_or_Nausea": round(float(result[4]*100), 2),
        "Death":  round(float(result[5]*100), 2)
    })
    publish.single(
        topic=js_conf["publish_topic"]["aqi"],
        payload=json_data,
        hostname=js_conf["mqtt_server"],
        port=js_conf["mqtt_port"]
    )
    print("Publish", json_data, "to", js_conf["mqtt_server"], "done.")


async def main():
    js_conf = load_configure()
    
    lora = LoRa(js_conf["lora_port"], js_conf["lora_baudrate"])
    print("LoRa receiving ... ", js_conf["lora_port"])
    
    loop = asyncio.get_event_loop()
    
    while True:
        try:
            msg = await lora.receive_message()
            if msg != "":
                msgs = msg.splitlines()
                #print(msgs)
                
                for i in range(len(msgs)):
                    msgs[i] = json.loads(msgs[i])
                    tag = msgs[i].pop("tag", None)
                    
                    if tag == 0:
                        msgs[i] = json.dumps(msgs[i])
                        publish.single(
                            topic=js_conf["publish_topic"]["sensors"],
                            payload=msgs[i],
                            hostname=js_conf["mqtt_server"],
                            port=js_conf["mqtt_port"]
                        )
                        print("Publish", msgs[i], "to", js_conf["mqtt_server"], "done.")
                    elif tag == 1:
                        await loop.create_task(Publish_Predict(js_conf, msgs[i]))   
                
            await asyncio.sleep(0.01)
        except Exception as e:
            print(e)
    


if __name__ == "__main__":
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

'''
@app.post("/aqi_status/")
async def aqi_status(timestap: TimeStamp):
    global input_queue
    
    input_queue[4:] = input_queue[:-4]
    input_queue[0] = timestap.co
    input_queue[1] = timestap.no2
    input_queue[2] = timestap.o3
    input_queue[3] = timestap.pm25
    
    if model is None:
        await LoadModel()
    
    result = (await Predict(input_queue.reshape(1, 32))).reshape(6)
    response = PredictResult(
        Fresh = result[0],
        Polluted = result[1],
        Headaches = result[2],
        Pneumonia = result[3],
        Convulsions_or_Nausea = result[4],
        Death = result[5]
    )
    return response
'''