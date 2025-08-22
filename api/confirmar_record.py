# api/confirmar_record.py

from flask import Flask, request, jsonify, render_template
import requests, os

app = Flask(__name__, template_folder="../templates")
api = app  # Vercel necesita esta variable

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = "Confirmaciones_de_Entrega"


@app.route("/test", methods=["GET"])
def test():
    return "¡Funciona!", 200

@app.route("/", methods=["GET"])
def confirmar_record():
    record_id = request.args.get("record_id")
    unique_number = request.args.get("unique_number")

    if not record_id or not unique_number:
        return jsonify({"error": "Faltan parámetros record_id o unique_number."}), 400

    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    read_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}/{record_id}"

    try:
        read_response = requests.get(read_url, headers=headers)
        read_response.raise_for_status()
        record_data = read_response.json()

        airtable_token = record_data['fields'].get('Codigo_unico')

        if unique_number != airtable_token:
            return jsonify({"error": "Número único incorrecto. Verificación fallida."}), 403

        update_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

        data = {
            "records": [
                {"id": record_id, "fields": {"Verificado": "Verificado"}}
            ]
        }

        update_response = requests.patch(update_url, headers=headers, json=data)
        update_response.raise_for_status()

        return render_template("confirmation.html"), 200

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return jsonify({"error": "Registro no encontrado. Verificación fallida."}), 404
        else:
            return jsonify({"error": f"Error de API: {e}"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error de conexión: {e}"}), 500

