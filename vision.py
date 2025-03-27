from inference_sdk import InferenceHTTPClient

client = InferenceHTTPClient(
    api_url="http://localhost:9001", # use local inference server
    api_key="6RHN1gwHSxMstwkPHPPO"
)

def detect_car_details(image_path):
    result = client.run_workflow(
        workspace_name="vehicle-detection-bpir9",
        workflow_id="identification",
        images={
            "image": image_path
        }
    )
    return result