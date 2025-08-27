from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import blueprint
from app.config import Config
from app.decorators import admin_required, enabled_required
from app import db

# for Debuging
from icecream import ic

# from .models import xx
# from app.admin.models import User@
# from app.helper_functions.helper_db_file import check_if_user_has_admin_rights

from .models import CalculatorCalcWay


config = Config()

print("Calculator Version 0.0.0")


@blueprint.route("/Calculator_index", methods=["GET"])
@enabled_required
def Calculator_index():
    return render_template("Calculator.html", user=current_user, config=config)


@blueprint.route("/safe_calc_way", methods=["Post"])
@enabled_required
def safe_calc_way():
    calc_way = request.json.get("calc_way")
    result = request.json.get("result")
    print(f"Der Rechenweg lautet {calc_way} und das Egebnis {result}")
    if calc_way is None or calc_way == "" or calc_way == "-?-":
        print("Kein gültiger Rechenweg! ")
        return jsonify({"error": "Kein gültiger Rechenweg!", "calc_way": calc_way})
    else:
        new_calc_way = CalculatorCalcWay(
            user_id=current_user.id, calc_way=calc_way, result=result
        )
        db.session.add(new_calc_way)
        db.session.commit()
        return jsonify(
            {
                "success": f"Rechenweg {calc_way} gespeichert  mit dem Ergebnis {result}",
                "calc_way": calc_way,
            }
        )


@blueprint.route("/show_saved_calc", methods=["GET"])
@enabled_required
def show_saved_calc():
    # Alle gespeicherten Rechnungen des aktuellen Users holen
    saved_calcs = (
        CalculatorCalcWay.query.filter_by(user_id=current_user.id)
        .order_by(CalculatorCalcWay.created_at.desc())
        .all()
    )

    # In Liste umwandeln für JSON
    calc_list = []
    for calc in saved_calcs:
        calc_list.append(
            {
                "id": calc.id,
                "calc_way": calc.calc_way,
                "result": calc.result,
                "created_at": calc.created_at.strftime(
                    "%d.%m.%Y %H:%M"
                ),  # Format: 27.08.2025 14:30
            }
        )

    # print(calc_list)

    return jsonify(
        {"success": True, "calculations": calc_list, "count": len(calc_list)}
    )
