from inference_sdk import InferenceHTTPClient

client = InferenceHTTPClient(
    api_url="http://localhost:9001", # use local inference server
    api_key="6RHN1gwHSxMstwkPHPPO"
)

def detect_car_details(image_path):
    result = client.run_workflow(
        workspace_name="vehicle-detection-bpir9",
        workflow_id="vehicle-details-identification",
        images={
            "image": image_path
        }
    )
    license_plate = ""

    try:
        license_plate = result[0]["google_gemini"][0]["output"]
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError("Failed to extract license plate information") from e
    finally:
        return license_plate