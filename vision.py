from inference_sdk import InferenceHTTPClient

WORKSPACE = "vehicle-detection-bpir9"

client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",  # use local inference server
    api_key="6RHN1gwHSxMstwkPHPPO"
)


def detect_number_plate(image_path):
    result = client.run_workflow(
        workflow_id="license-plate-detection",
        workspace_name=WORKSPACE,
        images={
            "image": image_path
        }
    )
    predictions = result[0]['plate'][0]["predictions"][0]
    x = predictions["x"]
    y = predictions["y"]
    width = predictions["width"]
    height = predictions["height"]
    confidence = predictions["confidence"]

    return x, y, width, height, confidence
