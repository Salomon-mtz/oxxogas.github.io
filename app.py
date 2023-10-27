from flask import Flask, render_template
import oci

app = Flask(__name__)
app.static_folder = "static"
app.debug = True


@app.route("/oci")
def ociPlate():
    config = oci.config.from_file("/Users/salomon/Desktop/oxxoGas_app/oci/oci")
    ai_vision_client = oci.ai_vision.AIServiceVisionClient(config=config)
    # Envia la solicitud al servicio, algunos parámetros no son obligatorios, consulta la documentación de la API para obtener más información
    analyze_image_response = ai_vision_client.analyze_image(
        analyze_image_details=oci.ai_vision.models.AnalyzeImageDetails(
            features=[
                oci.ai_vision.models.ImageClassificationFeature(
                    feature_type="TEXT_DETECTION", max_results=130
                )
            ],
            image=oci.ai_vision.models.ObjectStorageImageDetails(
                source="OBJECT_STORAGE",
                namespace_name="axvnl9xrn6xz",
                bucket_name="oxxogas",
                object_name="car-pics/Cars432.png",
            ),
            compartment_id="ocid1.tenancy.oc1..aaaaaaaas244yut7vrorqgsz4jf3vs5dd7nl7tlcreo5bhuc52ddowy6q5mq",
        ),
        opc_request_id="XTOOOGSRULY7TEKOXIY1",
    )

    # Obtén los datos de la respuesta
    response_data = analyze_image_response.data
    return render_template("oci.html", response_data=response_data)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compra")
def compra():
    return render_template("compra.html")


@app.route("/datos")
def datos():
    return render_template("datos.html")


if __name__ == "__main__":
    app.run()
