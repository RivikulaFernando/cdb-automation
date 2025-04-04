from inference_sdk import InferenceHTTPClient

WORKSPACE = "vehicle-detection-bpir9"

client = InferenceHTTPClient(
    api_url="http://localhost:9001",  # use local inference server
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
    predictions = result[0]['plate']['predictions'][0]
    x = predictions["x"]
    y = predictions["y"]
    width = predictions["width"]
    height = predictions["height"]
    confidence = predictions["confidence"]

    return x, y, width, height, confidence

def detect_number_plate_vlm(image_path):
    result = client.run_workflow(
        workflow_id="license-plate-detection-gemini",
        workspace_name=WORKSPACE,
        images={
            "image": image_path
        }
    )
    plate = result[0]['results'][0]['license_plate']

    return plate

def identify_vehicle_details(image_path):
    result = client.run_workflow(
        workflow_id="vehicle-details-identification",
        workspace_name=WORKSPACE,
        images={
            "image": image_path
        }
    )
    predictions = result[0]['vehicle_details']
    type = predictions["type"]
    brand = predictions["brand"]
    model = predictions["model"]
    color = predictions["color"]

    return type, brand, model, color


def vehicle_light_conditions(image_path):
    result = client.run_workflow(
        workflow_id="vehicle-parts-segmentation",
        workspace_name=WORKSPACE,
        images={
            "image": image_path
        }
    )

    return result[0]['light_conditions']

def get_verification_numbers(image_path):
    result = client.run_workflow(
        workflow_id="vehicle-identification-numbers",
        workspace_name=WORKSPACE,
        images={
            "image": image_path
        }
    )

    predictions = result[0]['identification_numbers']
    engine_number = predictions["engine_no"]
    chassis_number = predictions["chassis_no"]

    return engine_number, chassis_number
