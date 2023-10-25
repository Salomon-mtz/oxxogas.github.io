import cx_Oracle as oracledb
from flask import Flask, render_template

app = Flask(__name__)
app.static_folder = "static"
app.debug = True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compra")
def compra():
    return render_template("compra.html")


@app.route("/datos")
def datos():
    data = oxxoGas()
    return render_template("datos.html", data=data)


def oxxoGas():
    connection = oracledb.connect(
        user="admin",
        password="Tyctoj-7sypca-coxnuh",
        dsn="oxxogas_low",
        config_dir="OracleCloud/MYDB/tnsnames.ora",
        wallet_location="OracleCloud/MYDB/wallet",
        wallet_password="Tyctoj-7sypca-coxnuh",
    )
    # Replace this query with your specific SQL query
    sql_query = "SELECT * FROM OXXOGASDB_CLIENTS"
    cursor = connection.cursor()
    cursor.execute(sql_query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    return data


if __name__ == "__main__":
    app.run()
