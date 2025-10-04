from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import blueprint, app_logger
from app.config import Config
from app.decorators import admin_required, enabled_required
from app import db

# for Debuging
from icecream import ic

# from .models import xx
# from app.admin.models import User@
# from app.helper_functions.helper_db_file import check_if_user_has_admin_rights
# from . import socketio_events

FOODS = [
    # Italienisch
    {"name": "Pizza Margherita", "emoji": "🍕", "kategorie": "italienisch"},
    {"name": "Spaghetti Carbonara", "emoji": "🍝", "kategorie": "italienisch"},
    {"name": "Lasagne", "emoji": "🍝", "kategorie": "italienisch"},
    {"name": "Risotto", "emoji": "🍚", "kategorie": "italienisch"},
    {"name": "Ravioli", "emoji": "🥟", "kategorie": "italienisch"},
    # Asiatisch
    {"name": "Sushi", "emoji": "🍣", "kategorie": "asiatisch"},
    {"name": "Ramen", "emoji": "🍜", "kategorie": "asiatisch"},
    {"name": "Pad Thai", "emoji": "🍜", "kategorie": "asiatisch"},
    {"name": "Curry", "emoji": "🍛", "kategorie": "asiatisch"},
    {"name": "Pho Suppe", "emoji": "🍲", "kategorie": "asiatisch"},
    {"name": "Gebratener Reis", "emoji": "🍚", "kategorie": "asiatisch"},
    {"name": "Dim Sum", "emoji": "🥟", "kategorie": "asiatisch"},
    {"name": "Miso Suppe", "emoji": "🍵", "kategorie": "asiatisch"},
    {"name": "Chow Mein", "emoji": "🍜", "kategorie": "asiatisch"},
    # Deutsch / Europäisch
    {"name": "Schnitzel mit Pommes", "emoji": "🍖", "kategorie": "deutsch"},
    {"name": "Currywurst", "emoji": "🌭", "kategorie": "deutsch"},
    {"name": "Spätzle", "emoji": "🍝", "kategorie": "deutsch"},
    {"name": "Sauerbraten", "emoji": "🥩", "kategorie": "deutsch"},
    {"name": "Käsespätzle", "emoji": "🧀", "kategorie": "deutsch"},
    {"name": "Bratwurst", "emoji": "🌭", "kategorie": "deutsch"},
    # Amerikanisch / Fast Food
    {"name": "Burger", "emoji": "🍔", "kategorie": "amerikanisch"},
    {"name": "Hot Dog", "emoji": "🌭", "kategorie": "amerikanisch"},
    {"name": "BBQ Ribs", "emoji": "🍖", "kategorie": "amerikanisch"},
    {"name": "Mac and Cheese", "emoji": "🧀", "kategorie": "amerikanisch"},
    {"name": "Chicken Wings", "emoji": "🍗", "kategorie": "amerikanisch"},
    # Mexikanisch
    {"name": "Tacos", "emoji": "🌮", "kategorie": "mexikanisch"},
    {"name": "Burrito", "emoji": "🌯", "kategorie": "mexikanisch"},
    {"name": "Quesadilla", "emoji": "🌮", "kategorie": "mexikanisch"},
    {"name": "Nachos", "emoji": "🧀", "kategorie": "mexikanisch"},
    {"name": "Enchiladas", "emoji": "🌯", "kategorie": "mexikanisch"},
    # Indisch / Orientalisch
    {"name": "Chicken Tikka Masala", "emoji": "🍛", "kategorie": "indisch"},
    {"name": "Butter Chicken", "emoji": "🍗", "kategorie": "indisch"},
    {"name": "Biryani", "emoji": "🍚", "kategorie": "indisch"},
    {"name": "Falafel", "emoji": "🧆", "kategorie": "orientalisch"},
    {"name": "Kebab", "emoji": "🥙", "kategorie": "orientalisch"},
    {"name": "Hummus mit Pita", "emoji": "🫓", "kategorie": "orientalisch"},
    # Verschiedenes / Leicht
    {"name": "Caesar Salad", "emoji": "🥗", "kategorie": "salat"},
    {"name": "Griechischer Salat", "emoji": "🥗", "kategorie": "salat"},
    {"name": "Tomatensuppe", "emoji": "🍲", "kategorie": "suppe"},
    {"name": "Kürbissuppe", "emoji": "🍲", "kategorie": "suppe"},
    {"name": "Sandwich", "emoji": "🥪", "kategorie": "leicht"},
    {"name": "Wrap", "emoji": "🌯", "kategorie": "leicht"},
    # Fisch / Meeresfrüchte
    {"name": "Fish and Chips", "emoji": "🐟", "kategorie": "fisch"},
    {"name": "Paella", "emoji": "🥘", "kategorie": "fisch"},
    {"name": "Garnelen", "emoji": "🦐", "kategorie": "fisch"},
    # Vegetarisch / Vegan
    {"name": "Veggie Burger", "emoji": "🍔", "kategorie": "vegetarisch"},
    {"name": "Gemüsepfanne", "emoji": "🥘", "kategorie": "vegetarisch"},
    {"name": "Tofu Stir-Fry", "emoji": "🥘", "kategorie": "vegetarisch"},
    {"name": "Quinoa Bowl", "emoji": "🥗", "kategorie": "vegetarisch"},
    {"name": "Gemüsesuppe", "emoji": "🍲", "kategorie": "vegetarisch"},
]

config = Config()
app_logger.info("Starte App-WasEssen Route Initialization")
print("WasEssen Version 0.0.0")


@blueprint.route("/WasEssen_index", methods=["GET"])
@enabled_required
def WasEssen_index():
    return render_template(
        "WasEssen.html", user=current_user, config=config, FOODS=FOODS
    )


app_logger.info("Starte Ende Route Initialization")
