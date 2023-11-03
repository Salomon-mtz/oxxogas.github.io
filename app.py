import json
from flask import Flask, render_template, request
import oci
from oci.ai_anomaly_detection.models import DetectAnomaliesDetails
from supabase import create_client, Client
import base64
import os
import tempfile
from io import BytesIO


app = Flask(__name__)
app.static_folder = "static"
app.debug = True


# @app.route("/oci")
# def ociPlate():
#     config = oci.config.from_file("/Users/salomon/Desktop/oxxoGas_app/oci/oci")
#     ai_vision_client = oci.ai_vision.AIServiceVisionClient(config=config)

# Send the request to the service
# analyze_image_response = ai_vision_client.analyze_image(
#     analyze_image_details=oci.ai_vision.models.AnalyzeImageDetails(
#         features=[
#             oci.ai_vision.models.ImageClassificationFeature(
#                 feature_type="TEXT_DETECTION", max_results=130
#             )
#         ],
#         image=oci.ai_vision.models.ObjectStorageImageDetails(
#             source="OBJECT_STORAGE",
#             namespace_name="axvnl9xrn6xz",
#             bucket_name="oxxogas",
#             object_name="car-pics/Cars432.png",
#         ),
#         compartment_id="ocid1.tenancy.oc1..aaaaaaaas244yut7vrorqgsz4jf3vs5dd7nl7tlcreo5bhuc52ddowy6q5mq",
#     ),
#     opc_request_id="XTOOOGSRULY7TEKOXIY1",
# )

# # Get the "text" value using the provided methods
# text_value = analyze_image_response.data.image_text.lines[0].text
# print(type(text_value))
# return render_template("index.html", text_value=text_value)

config = oci.config.from_file("/Users/salomon/Desktop/oxxoGas_app/oci/oci")
ai_vision_client = oci.ai_vision.AIServiceVisionClient(config=config)


@app.route("/oci", methods=["GET", "POST"])
def ociPlate():
    if request.method == "POST":
        # Handle the photo input if the request is POST
        photo_data = request.form.get("photo")

        # Remove the base64 image prefix if present
        prefix = "data:image/jpeg;base64,"
        if photo_data.startswith(prefix):
            photo_data = photo_data[len(prefix) :]

        # Process the image using OCI AI Services and search for license plates
        text_value = analyze_image(photo_data)
        print(text_value)

        # Return the results to the user
        return text_value  # Replace with your actual results

    # If the request is not POST, render the form template
    return render_template("oci.html")


def analyze_image(image_data_base64_str):
    analyze_image_response = ai_vision_client.analyze_image(
        analyze_image_details=oci.ai_vision.models.AnalyzeImageDetails(
            features=[
                oci.ai_vision.models.ImageClassificationFeature(
                    feature_type="TEXT_DETECTION", max_results=130
                )
            ],
            image=oci.ai_vision.models.InlineImageDetails(
                data=image_data_base64_str,  # Pass the base64 string directly
            ),
            compartment_id="ocid1.tenancy.oc1..aaaaaaaas244yut7vrorqgsz4jf3vs5dd7nl7tlcreo5bhuc52ddowy6q5mq",
        ),
        opc_request_id="XTOOOGSRULY7TEKOXIY1",
    )

    # Assuming the API response can be accessed like this; may require adjustment based on actual response format
    lines = analyze_image_response.data.image_text.lines
    if lines:
        text_value = lines[0].text
    else:
        text_value = "No se detectó texto en la imagen"
    return text_value


@app.route("/")
def index():
    import sys

    print(sys.path)

    return render_template("index.html")


@app.route("/compra")
def compra():
    return render_template("compra.html")


@app.route("/branch")
def branches():
    url: str = "https://rafdgizljnzrnmfguogm.supabase.co"
    key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJhZmRnaXpsam56cm5tZmd1b2dtIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTgzNjU0OTAsImV4cCI6MjAxMzk0MTQ5MH0.7_0lzFml9UgLJ6m4nDCs3IhYam1ofa0FoCSYkpTm2VM"
    supabase: Client = create_client(url, key)
    response = supabase.table("BRANCH").select("*").execute()
    print(response)
    data = response.data
    return render_template("branch.html", data=data)


ITEMS_PER_PAGE = 20  # or any other number you'd like


@app.route("/datos")
@app.route("/datos/page/<int:page>")
def datos(page=1):
    url: str = "https://rafdgizljnzrnmfguogm.supabase.co"
    key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJhZmRnaXpsam56cm5tZmd1b2dtIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTgzNjU0OTAsImV4cCI6MjAxMzk0MTQ5MH0.7_0lzFml9UgLJ6m4nDCs3IhYam1ofa0FoCSYkpTm2VM"
    supabase: Client = create_client(url, key)
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE - 1
    response = supabase.table("CLIENTS").select("*").range(start, end).execute()
    total_items = (
        supabase.table("CLIENTS").select("plateid", count="exact").execute().count
    )  # Assuming 'id' is a column in your table
    total_pages = (
        total_items + ITEMS_PER_PAGE - 1
    ) // ITEMS_PER_PAGE  # Ceiling division

    data = response.data
    return render_template(
        "datos.html", data=data, current_page=page, total_pages=total_pages
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
