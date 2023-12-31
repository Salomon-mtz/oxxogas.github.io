import json
import os
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_from_directory,
    redirect,
    session,
    url_for,
)
import oci
from oci.ai_anomaly_detection.models import DetectAnomaliesDetails
import postgrest
from supabase import create_client, Client

from io import BytesIO
import qrcode
from gotrue.types import User
import stripe

from twilio.rest import Client


app = Flask(__name__, template_folder="templates")
app.static_folder = "static"
app.debug = True
app.secret_key = os.urandom(24)


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
# return render_template("register.html", text_value=text_value)


# ADMIN OXXO GAS

config = oci.config.from_file(
    "/Users/salomon/Desktop/oxxogas.github.io/oci/oci"
)  # cambiar por tu path
ai_vision_client = oci.ai_vision.AIServiceVisionClient(config=config)

url: str = "https://rafdgizljnzrnmfguogm.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJhZmRnaXpsam56cm5tZmd1b2dtIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTgzNjU0OTAsImV4cCI6MjAxMzk0MTQ5MH0.7_0lzFml9UgLJ6m4nDCs3IhYam1ofa0FoCSYkpTm2VM"
supabase: Client = create_client(url, key)

stripe.api_key = "sk_test_51O9tjGJJgeLIT5WE5vjn0nzYZaCIqb7mYxjS7Mzu3yEpYcyWV47N5DrLDTLGjXi9OQwpEbK7UtIPo5npy0pXSLQj00xGEG2ZhI"


# Your Twilio Account SID and Auth Token
TWILIO_ACCOUNT_SID = "ACc2ef00cc9fd26b9c1ea712d8d490ab0c"
TWILIO_AUTH_TOKEN = "53b423ee8c6c75a344f78df2f9081fc8"

# Your Twilio phone number (this is the number provided by Twilio)
TWILIO_PHONE_NUMBER = "+13344014858"


@app.route("/oci", methods=["GET", "POST"])
def ociPlate():
    if "vendor_info" in session:
        if request.method == "POST":
            photo_data = request.form.get("photo")

            # Remove the base64 image prefix if present
            prefix = "data:image/jpeg;base64,"
            if photo_data.startswith(prefix):
                photo_data = photo_data[len(prefix) :]

            # Process the image using OCI AI Services
            plate_text = analyze_image(photo_data)

            # Redirect to the purchases route with plate_text as a parameter
            return redirect(url_for("purchases", plateid=plate_text))

        return render_template("oci.html")
    else:
        return redirect(url_for("login"))


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
    print(lines)

    text_value = "No se detectó texto en la imagen"

    if lines:
        for line in lines:
            if "-" in line.text:
                text_value = line.text.replace("-", "")
                break

    return text_value



@app.route("/register")
def register():
    if "vendor_info" in session:
        return render_template("register.html")
    else:
        return redirect(url_for("login"))


@app.route("/submit", methods=["POST"])
def submit_form():
    message = None
    if request.method == "POST":
        # Get form data
        plateid = request.form.get("plateid")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        sex = request.form.get("sex")
        age = request.form.get("age")
        raw_phone = request.form.get("phone")
        email = request.form.get("email")
        phone = "+52" + raw_phone
        # Create a dictionary with the data
        customer_data = {
            "plateid": plateid,
            "first_name": first_name,
            "last_name": last_name,
            "sex": sex,
            "age": age,
            "phone": phone,
            "email": email,
        }

        try:
            # Insert the data into the Supabase table
            data, count = supabase.table("CLIENTS").insert([customer_data]).execute()

            # Data insertion successful
            message = "Registro exitoso!"
        except postgrest.exceptions.APIError as e:
            if "duplicate key value violates unique constraint" in e.message:
                # Duplicate key violation error
                message = "Este número de placa ya está registrado."
            else:
                # Other API error
                message = f"Error al insertar datos: {e.message}"

        return render_template("register.html", message=message)

    return render_template("register.html")


@app.route("/compra", methods=["GET", "POST"])
def compra():
    if "vendor_info" in session:
        if request.method == "POST":
            # Get form data from the request
            plateid = request.form["plateid"]
            amount = float(request.form.get("amount"))
            liters = float(request.form.get("liters"))
            branch = int(request.form.get("branch"))
            payment_method = request.form["payment_method"]
            gas_type = request.form["gas_type"]

            # Prepare data to be inserted into the PURCHASE_HISTORY table
            new_purchase_data = {
                "plateid": plateid,
                "amount": amount,
                "liters": liters,
                "branch": branch,
                "payment_method": payment_method,
                "gas_type": gas_type,
                "status": True,  # Set status to True
            }

            # Send a POST request to the PURCHASE_HISTORY table
            response = (
                supabase.table("PURCHASE_HISTORY").insert([new_purchase_data]).execute()
            )
            print(response)

            return redirect(
                url_for("compra")
            )  # Redirect to the compra route after submission

        return render_template("compra.html")
    else:
        return redirect(url_for("login"))


@app.route("/branch")
def branches():
    if "vendor_info" in session:
        url: str = "https://rafdgizljnzrnmfguogm.supabase.co"
        key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJhZmRnaXpsam56cm5tZmd1b2dtIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTgzNjU0OTAsImV4cCI6MjAxMzk0MTQ5MH0.7_0lzFml9UgLJ6m4nDCs3IhYam1ofa0FoCSYkpTm2VM"
        supabase: Client = create_client(url, key)
        response = supabase.table("BRANCH").select("*").execute()
        print(response)
        data = response.data
        return render_template("branch.html", data=data)
    else:
        return redirect(url_for("login"))


ITEMS_PER_PAGE = 20  # or any other number you'd like


@app.route("/datos")
@app.route("/datos/page/<int:page>")
def datos(page=1):
    if "vendor_info" in session:
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
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    message = None
    if request.method == "POST":
        # Get the username and password from the form
        id = int(request.form.get("id"))
        password = request.form.get("password")

        try:
            # Query the "vendors" table in Supabase
            vendors = (
                supabase.from_("VENDORS")
                .select("*")
                .eq("id", id)
                .eq("password", password)
                .execute()
            )

            vendors_data = vendors.data

            # Check if a matching vendor was found
            if vendors.data and len(vendors.data) == 1:
                # Successful login, store vendor information in the session
                vendor_info = {
                    "username": vendors_data[0]["username"],
                    "id": vendors_data[0]["id"],
                    "branch_id": vendors_data[0]["branch_id"],
                }
                session["vendor_info"] = vendor_info

                print("Login successful!", "success")
                message = "Inicio exitoso!"

                # Redirect to the purchases page or another appropriate route
                return redirect(url_for("purchases"))
            else:
                # Invalid credentials, show an error alert
                print("Invalid username or password", "danger")
                message = "Usuario o contraseña incorrectos"
        except Exception as e:
            # Handle the query error, show an error alert
            print(f"Error querying the database: {str(e)}")
            message = "Error al consultar la base de datos"

    return render_template("login.html", message=message)


@app.route("/purchases")
def purchases():
    if "vendor_info" in session:
        # Obtener el plateid del parámetro de consulta
        plateid = request.args.get("plateid", "DEFAULT_PLATE_ID")
        branch_id = session['vendor_info']['branch_id']

        # Obtener datos de compra
        response = (
            supabase.table("PURCHASE_HISTORY")
            .select("*")
            .eq("plateid", plateid)
            .eq("status", True)
            .eq("branch", branch_id)
            .execute()
        )

        if len(response.data) > 0:
            purchase = response.data[0]

            # Obtener el teléfono del cliente de la tabla CLIENTS
            client_response = (
                supabase.table("CLIENTS").select("phone").eq("plateid", plateid).execute()
            )

            if len(client_response.data) > 0:
                phone_number = client_response.data[0]["phone"]

                # Aquí deberías enviar un mensaje de texto al número de teléfono
                send_text_message(phone_number, "Revisa tus promociones en: http://127.0.0.1/main en la pestana de promociones OXXO GAS")

                # Continuar con el resto del código

                # Obtener el título de la sucursal de la tabla BRANCH
                branch_response = (
                    supabase.table("BRANCH")
                    .select("branch_title")
                    .eq("id", purchase["branch"])
                    .execute()
                )

                if len(branch_response.data) > 0:
                    branch_title = branch_response.data[0]["branch_title"]
                else:
                    branch_title = "Sucursal Desconocida"

                return render_template(
                    "purchase.html", purchase=purchase, branch_title=branch_title
                )
            else:
                return render_template("purchase.html", error="Cliente no encontrado")
        else:
            return render_template("purchase.html", error="Compra no encontrada")
    else: 
        return redirect(url_for("login"))

def send_text_message(phone_number, message):
    # Initialize Twilio client
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    try:
        # Send SMS using Twilio
        twilio_client.messages.create(
            body=message, from_=TWILIO_PHONE_NUMBER, to=phone_number
        )
        print(f"Message sent successfully to {phone_number}")
    except Exception as e:
        print(f"Error sending message to {phone_number}: {str(e)}")


@app.route("/dispatch", methods=["POST"])
def dispatch_purchase():
    purchase_id = request.form.get("purchase_id", type=int)
    new_status = False
    print(type(new_status))
    print(purchase_id)

    # Asegúrate de que la respuesta de Supabase se maneje correctamente aquí.
    response = (
        supabase.table("PURCHASE_HISTORY")
        .update({"status": new_status})
        .eq("id", purchase_id)
        .execute()
    )

    print(response)

    # Redirige al usuario de vuelta a la página de compras
    return render_template("success_update.html")


# CUSTOMER OXXO GAS


@app.route("/", methods=["GET", "POST"])
def index():
    message = None

    if request.method == "POST":
        # Get form data
        plateid = request.form.get("plateid")
        password = request.form.get("password")

        print(plateid)
        print(password)

        # Query the Supabase client table for user credentials
        response = (
            supabase.table("CLIENTS")
            .select("*")
            .eq("plateid", plateid)
            .eq("password", password)
            .execute()
        )
        print("respuesta", response)
        user_data = response.data

        # Check if user exists and password matches
        if user_data and len(user_data) > 0 and user_data[0]["password"] == password:
            # Successful login
            message = "Inicio exitoso!"
            session["user_info"] = {
                "plateid": plateid,
                "first_name": user_data[0]["first_name"],
                "last_name": user_data[0]["last_name"],
                "phone": user_data[0]["phone"],
                "email": user_data[0]["email"],
                "client_type": user_data[0]["client_type"],
            }
            print(session["user_info"])
            return redirect(url_for("master"))
        else:
            # Invalid login
            message = "Usuario o contraseña incorrectos"

    return render_template("index.html", message=message)


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/signup-post", methods=["POST"])
def signup_form():
    message = None
    if request.method == "POST":
        # Get form data
        plateid = request.form.get("plateid")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        sex = request.form.get("sex")
        age = request.form.get("age")
        raw_phone = request.form.get("phone")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = "+52" + raw_phone

        # Create a dictionary with the data
        client_data = {
            "plateid": plateid,
            "first_name": first_name,
            "last_name": last_name,
            "sex": sex,
            "age": age,
            "phone": phone,
            "email": email,
            "password": password,
        }

        print(client_data)

        try:
            # Insert the data into the Supabase table
            data, count = supabase.table("CLIENTS").insert([client_data]).execute()

            # Data insertion successful
            message = "Registro exitoso!"
            return render_template("index.html", message=message)
        except postgrest.exceptions.APIError as e:
            if "duplicate key value violates unique constraint" in e.message:
                # Duplicate key violation error
                message = "Este número de placa ya está registrado."
            else:
                # Other API error
                message = f"Error al insertar datos: {e.message}"

        return render_template("signup.html", message=message)

    return render_template("signup.html")


@app.route("/main")
def master():
    if "user_info" in session:
        url: str = "https://rafdgizljnzrnmfguogm.supabase.co"
        key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJhZmRnaXpsam56cm5tZmd1b2dtIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTgzNjU0OTAsImV4cCI6MjAxMzk0MTQ5MH0.7_0lzFml9UgLJ6m4nDCs3IhYam1ofa0FoCSYkpTm2VM"
        supabase: Client = create_client(url, key)
        user_info = session["user_info"]
        client_type = user_info["client_type"]
        plate_number = user_info["plateid"]
        response = supabase.table("BRANCH").select("*").execute()
        fuel = supabase.table("FUEL").select("*").execute()
        promotions = supabase.table("PROMOTIONS").select("*").eq("client_type",client_type).execute()
        reciepts = (
            supabase.table("PURCHASE_HISTORY")
            .select("*")
            .eq("plateid", session["user_info"]["plateid"])
            .order("created_at.desc")
            .execute()
        )

        data = response.data
        fuel_data = fuel.data
        reciepts_data = reciepts.data
        promotions_data = promotions.data
        print(fuel_data)
        return render_template(
            "master.html", data=data, fuel_data=fuel_data, reciepts_data=reciepts_data, promotions_data=promotions_data
        )
    else:
        return redirect(url_for("index"))


def generate_qr_code(plate_number):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(plate_number)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("static/plate_qr.png")


@app.route("/profile")
def profile():
    if "user_info" in session:
        # Access user information from the session
        user_info = session["user_info"]
        plate_number = user_info["plateid"]
        # Generate the QR code with the plate number
        generate_qr_code(plate_number)
        return render_template("profile.html", plate_number=plate_number)
    else:
        # Handle the case when user_info is not in the session (not logged in)
        return redirect(url_for("index"))


@app.route("/qr_code/<filename>")
def send_qr_code(filename):
    return send_from_directory("static", filename)


@app.route("/buy", methods=["GET", "POST"])
def buy():
    if "user_info" in session:
        url: str = "https://rafdgizljnzrnmfguogm.supabase.co"
        key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJhZmRnaXpsam56cm5tZmd1b2dtIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTgzNjU0OTAsImV4cCI6MjAxMzk0MTQ5MH0.7_0lzFml9UgLJ6m4nDCs3IhYam1ofa0FoCSYkpTm2VM"
        supabase: Client = create_client(url, key)
        response = supabase.table("BRANCH").select("*").execute()
        data = response.data

        fuel_type = request.args.get("fuel_type")
        fuel_price = request.args.get("fuel_price")
        return render_template(
            "fuel-checkout.html", data=data, fuel_type=fuel_type, fuel_price=fuel_price
        )
    else:
        return redirect(url_for("index"))


@app.route("/process_purchase", methods=["POST"])
def process_purchase():
    if "user_info" in session:
        message = None
        user_info = session["user_info"]
        customer_email = user_info.get("email")
        if request.method == "POST":
            # Get form data
            amount = float(request.form.get("amount"))
            liters = float(request.form.get("liters"))
            plateid = user_info["plateid"]
            branch = int(request.form.get("branch"))
            payment_method = request.form.get("payment_method")
            gas_type = request.form.get("fuel_type")
            status = True

            # Create a dictionary with the data
            purchase_data = {
                "amount": amount,
                "liters": liters,
                "plateid": plateid,
                "branch": branch,
                "payment_method": payment_method,
                "gas_type": gas_type,
                "status": status,
            }

            try:
                # Insert the data into the Supabase table

                data, count = (
                    supabase.table("PURCHASE_HISTORY").insert([purchase_data]).execute()
                )

                # Data insertion successful
                message = "Registro exitoso!"
                print(message)
                if payment_method == "tarjeta":
                    # Convertir el precio a un entero seguro para Stripe
                    product_price = int(amount * 100)
                    try:
                        # Crear la sesión de pago con Stripe
                        checkout_session = stripe.checkout.Session.create(
                            payment_method_types=["card", "oxxo"],
                            line_items=[
                                {
                                    "price_data": {
                                        "currency": "mxn",
                                        "unit_amount": product_price,
                                        "product_data": {
                                            "name": "Gasolina " + gas_type,
                                            "description": "Cobro de gasolina solicitada",
                                            "images": ["static/gas.jpg"],
                                        },
                                    },
                                    "quantity": 1,
                                },
                            ],
                            mode="payment",
                            success_url=url_for("success_stripe", _external=True)
                            + "?session_id={CHECKOUT_SESSION_ID}",
                            # cancel_url=url_for('buy', _external=True),
                            customer_email=customer_email,
                        )
                        return redirect(checkout_session.url, code=303)
                    except Exception as e:
                        return str(e)
                elif payment_method == "efectivo":
                    # Aquí tu lógica para el pago en efectivo...
                    return redirect(url_for("success"))
            except postgrest.exceptions.APIError as e:
                if "duplicate key value violates unique constraint" in e.message:
                    # Duplicate key violation error
                    message = "Este número de placa ya está registrado."
                    print(message)
                else:
                    # Other API error
                    message = f"Error al insertar datos: {e.message}"
                    print(message)

            return render_template("fuel-checkout.html", message=message)

        return redirect(url_for("process_purchase"))
    else:
        return redirect(url_for("index"))


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/success_stripe", methods=["GET"])
def success_stripe():
    # Retrieve the Stripe session ID from the URL query parameters
    session_id = request.args.get("session_id")

    if session_id:
        try:
            payment = stripe.checkout.Session.retrieve(session_id)
            purchase_id = payment.payment_intent
        except stripe.error.StripeError as e:
            purchase_id = "Error retrieving payment"
    else:
        purchase_id = "Session ID not found"

    return render_template("success_stripe.html", purchase_id=purchase_id)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
