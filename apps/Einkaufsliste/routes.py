from time import sleep
from datetime import datetime, timedelta
from icecream import ic
from sqlalchemy import or_
from sqlalchemy.orm import aliased
from sqlalchemy.sql import exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete


from flask import render_template, current_app as app, request, redirect, flash, url_for
from flask_login import current_user
from . import blueprint
from .models import import EinkaufslisteList, EinkaufslisteItem, EinkaufslisteOther, EinkaufslisteGroup, group_membership
from app.config import Config
from app.decorators import admin_required, enabled_required
from app.routes.admin.models import User
from app import db
from .forms import CreatNewList, CreatNewGroup, ModifyGroup
import json
import re

from math import ceil

config = Config()

print("Einkaufsliste Version 0.0.0")


@blueprint.route("/Einkaufsliste", methods=["GET"])
@admin_required
def Einkaufsliste():
    new_registration = User.query.filter(User.user_enable.is_(None)).count()
    page = request.args.get(
        "page", 1, type=int
    )  # Holt die aktuelle Seite aus der URL-Parameter

    # Abfrage mit Join und Filter
    # query = db.session.query(List, User).join(User)

    # query_test = db.session.query(Group,EinkaufslisteList).join(Group)
    # 1. Mache eine Abfrage der Tabelle List (die Einkaufslisten), in der gleichen Abfrage sollen noch die  Gruppen und die Benutzer gespeichert werden
    # 2. Führe ein join durch resp.
    # a) Die Tabelle Gruppe wird verknüfpt zwichen dem Eelement List.groip_id und der Tabelle Group.group_id
    # b) Die Tabelle User wird verknüfpt zwichen dem Eelement EinkaufslisteGroup.group_owner und der Tabelle User.id
    # Alias für User, weil wir sowohl den Besitzer als auch die Mitglieder betrachten
    Member = aliased(User)

    # Abfrage zur Ermittlung der Listen basierend auf Gruppenmitgliedschaft oder -besitz
    query = (
        db.session.query(EinkaufslisteList, EinkaufslisteGroup, User)
        .join(EinkaufslisteGroup, EinkaufslisteList.group_id == EinkaufslisteGroup.group_id)
        .join(User, EinkaufslisteGroup.group_owner == User.id)
        .outerjoin(group_membership, EinkaufslisteGroup.group_id == group_membership.c.group_id)
        .outerjoin(Member, group_membership.c.user_id == Member.id)
        .filter(
            or_(
                EinkaufslisteGroup.group_owner == current_user.id,
                Member.id == current_user.id,  # Prüft die Mitgliedschaft
            )
        )
        .distinct()
    )

    query = query.order_by(EinkaufslisteList.first_day.desc())

    # Paginieren der Ergebnisse mit korrekter Argumentübergabe
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    lists = pagination.items  # Die tatsächlichen Listen für die aktuelle Seite

    today = datetime.now().date()

    # Filtern und sortieren in Python (nicht ideal, aber notwendig, wenn spezielle Logik benötigt wird)
    # Hinweis: Dies ist ineffizient, wenn viele Daten vorhanden sind. Besser wäre es, wenn möglich, alles in der Datenbank zu machen.
    sorted_lists = sorted(
        lists,
        key=lambda x: (
            today >= x[0].first_day.date() and today <= x[0].last_day.date()
        ),
        reverse=True,
    )

    return render_template(
        "Einkaufsliste.html",
        user=current_user,
        new_registration=new_registration,
        lists=sorted_lists,
        pagination=pagination,
        today=today,
        datetime=datetime,
        config=Config,
    )


@blueprint.route("/newlist", methods=["GET", "POST"])
@enabled_required
def newlist():
    app.logger.debug("newlist wurde angesurft")
    # Anzeige für neue Account-Logins
    new_registration = User.query.filter(User.user_enable.is_(None)).count()
    form = CreatNewList()
    # Finde herraus in welcher Gruppe der Benutzer gehört, inkl. Gruppen in welche er Mitglied ist
    groups = EinkaufslisteGroup.query.filter(
        or_(
            EinkaufslisteGroup.group_owner == current_user.id,
            EinkaufslisteGroup.group_members.any(id=current_user.id),
        )
    ).all()

    if not groups:
        flash(
            "Keine Gruppenmitgliedschaft vorhanden. Bitte erstelle eine Gruppe oder tritt einer bei.",
            "warning",
        )

        return redirect(url_for("Einkaufsliste.home"))
    form.group_name.choices = [(group.group_id, group.group_name) for group in groups]

    if form.validate_on_submit():
        if form.submit.data:
            # Abfangen des Problem, dass Start und Enddatum nicht richtig sind
            if form.first_day.data > form.last_day.data:
                flash("Das Startdatum kann nicht nach dem Enddatum liegen.", "error")
                return redirect(url_for("Einkaufsliste.newlist"))

            # Abfangen des Problem, eine EinkaufsEinkaufslisteListe zu erstellen, welche bereits in
            # diesem datum Range erstellt wurde!
            # Nehmen Sie das Datum aus dem Formular und fügen Sie eine Zeitkomponente hinzu
            start_datetime = datetime.combine(form.first_day.data, datetime.min.time())
            end_datetime = datetime.combine(form.last_day.data, datetime.min.time())

            existing_list = EinkaufslisteList.query.filter(
                (EinkaufslisteList.first_day <= form.last_day.data)
                & (EinkaufslisteList.last_day >= form.first_day.data)
                & (EinkaufslisteList.group_id == form.group_name.data)
            ).first()

            today_existing_list = EinkaufslisteList.query.filter(
                (EinkaufslisteList.first_day <= end_datetime)
                & (EinkaufslisteList.last_day >= start_datetime)
                & (EinkaufslisteList.group_id == form.group_name.data)
            ).first()

            if (
                form.last_day.data == form.first_day.data
                and today_existing_list is not None
            ):
                existing_list = True

            if existing_list is not None:
                flash(
                    "Eine Einkaufsliste für diesen Zeitraum existiert bereits.",
                    "warning",
                )
                return redirect(url_for("Einkaufsliste.newlist"))

            # Datensatz kann erfasst werden
            new_list = EinkaufslisteList(
                user_id=current_user.id,
                first_day=form.first_day.data,
                last_day=form.last_day.data,
                group_id=form.group_name.data,
            )
            db.session.add(new_list)
            db.session.commit()
            list_id = new_list.list_id

            # Es gibt ein Other feld pro Einkaufs Range
            new_other = EinkaufslisteOther(user_id=current_user.id, list_id=list_id)
            db.session.add(new_other)
            db.session.commit()

            # Erstelle Einträge für jeden Tag zwischen Start- und Enddatum
            delta = form.last_day.data - form.first_day.data
            for i in range(delta.days + 1):
                date = form.first_day.data + timedelta(days=i)

                if (
                    form.no_lunch_on_weekday.data and date.weekday() < 5
                ):  # Überprüfung auf Wochentag (Montag bis Freitag)
                    pass  # Überspringe den Eintrag für new_lunch_item
                else:
                    new_lunch_item = EinkaufslisteItem(
                        user_id=current_user.id,
                        list_id=new_list.list_id,
                        item_name="",
                        to_eat_day=date,
                        meal="Mittag",
                        buy=False,
                    )
                    db.session.add(new_lunch_item)
                new_dinner_item = EinkaufslisteItem(
                    user_id=current_user.id,
                    list_id=new_list.list_id,
                    item_name="",
                    to_eat_day=date,
                    meal="Abend",
                    buy=False,
                )
                db.session.add(new_dinner_item)

            # Commite alle Tage
            db.session.commit()
            app.logger.info(
                f"Die Einkaufsliste {list_id} wurde durch {current_user.username} erstellt."
            )
            flash("Die Einkaufsliste wurde erfolgreich erstellt!", "success")

            return redirect(f"/einkauf/shiplist/{list_id}")
    return render_template(
        "newlist.html",
        user=current_user,
        form=form,
        new_registration=new_registration,
        config=Config,
    )


@blueprint.route("/newgroup", methods=["GET", "POST"])
@enabled_required
def newgroup():
    app.logger.debug("newgroup wurde angesurft")
    # Anzeige für neue Account-Logins
    new_registration = User.query.filter(User.user_enable.is_(None)).count()
    form = CreatNewGroup()
    form.group_members.choices = [
        (user.id, user.username)
        for user in User.query.filter(User.id != current_user.id).all()
    ]
    if form.validate_on_submit():
        app.logger.debug(
            "validate_on_submit der erstellung neuer Benutzer via Admin Settings"
        )
        # prüfe, ob der Gruppenname bereits existiert
        group = EinkaufslisteGroup.query.filter_by(group_name=form.group_name.data).first()
        if group is not None:
            flash("Dieser Gruppenname existiert bereits!", "warning")
            return redirect(url_for("Einkaufsliste.newgroup"))
        new_group = EinkaufslisteGroup(
            group_name=form.group_name.data,
            group_owner=current_user.id,
            group_public=form.group_public.data,
            group_visible=form.group_visible.data,
        )
        for user_id in form.group_members.data:
            user = User.query.get(user_id)
            new_group.group_members.append(user)
        db.session.add(new_group)
        db.session.commit()
        flash("Die neue Gruppe wurde erfolgreich erstellt!", "success")
        return redirect(url_for("Einkaufsliste.home"))

    return render_template(
        "newgroup.html",
        user=current_user,
        form=form,
        new_registration=new_registration,
        config=Config,
    )


@enabled_required
def ship_list(list_id):
    app.logger.debug(f"/access/shiplist/{list_id} wurde angesurft")
    # Anzeige für neue Account-Logins
    new_registration = User.query.filter(User.user_enable.is_(None)).count()


@blueprint.route("/shiplist/<list_id>", methods=["GET"])
@enabled_required
def ship_list(list_id):
    app.logger.debug(f"/access/shiplist/{list_id} wurde angesurft")
    # Anzeige für neue Account-Logins
    new_registration = User.query.filter(User.user_enable.is_(None)).count()

    # Alle Items mit list_id=list_id abrufen
    items = EinkaufslisteItem.query.filter_by(list_id=list_id).order_by(Item.to_eat_day)

    # einige Variabeln für die Seitenansicht
    list = List.query.filter_by(list_id=list_id).first()
    first_day = list.first_day.strftime("%d.%m.%Y")
    last_day = list.last_day.strftime("%d.%m.%Y")

    # Separate Listen für jede Mahlzeit erstellen
    mittagessen = []
    abendessen = []
    alle_items = []
    andere_items = []

    # Erstellung array für other
    other = EinkaufslisteOther.query.filter_by(list_id=list_id).first()
    other_user = User.query.filter_by(id=other.user_id).first()
    other_user_name = other_user.username if other_user else "Unbekannt"
    other_created_date = other.created_date.strftime("%d.%m.%Y")
    other_name = other.other_name
    if other.other_name is None:
        other_name = ""

    andere_items = [
        other.other_id,
        other_name,
        other_created_date,
        other_user_name,
        other.buy,
    ]

    # Items werden in die separate Gruppen hinzugefügt
    for item in items:
        created_date = item.created_date.strftime("%d.%m.%Y")
        to_eat_day_str = (
            item.to_eat_day.strftime("%d.%m.%Y")
            if item.to_eat_day
            else datetime.now().strftime("%d.%m.%Y")
        )
        to_eat_day_obj = datetime.strptime(to_eat_day_str, "%d.%m.%Y")
        week_day = to_eat_day_obj.strftime("%A")
        user = User.query.filter_by(id=item.user_id).first()
        name = user.username if user else "Unbekannt"

        # Hilfsvariable mit dem Datum erstellen
        item_date = (
            item.to_eat_day.strftime("%Y-%m-%d")
            if item.to_eat_day
            else datetime.now().strftime("%Y-%m-%d")
        )

        if item.meal == "Mittag":
            mittagessen.append(
                [
                    item.item_id,
                    week_day,
                    to_eat_day_str,
                    item.meal,
                    item.item_name,
                    [name, created_date],
                    item.buy,
                    item_date,
                ]
            )
        elif item.meal == "Abend":
            abendessen.append(
                [
                    item.item_id,
                    week_day,
                    to_eat_day_str,
                    item.meal,
                    item.item_name,
                    [name, created_date],
                    item.buy,
                    item_date,
                ]
            )

    # Sortieren der einzelnen Listen nach Datum und Mahlzeit
    mittagessen.sort(key=lambda x: (x[7]))
    abendessen.sort(key=lambda x: (x[7]))

    # Liste von Listen erstellen, in der jeder Eintrag ein Tag ist
    tage = []
    for entry in mittagessen + abendessen:
        if not tage or tage[-1][0][0] != entry[0]:
            tage.append([entry])
        else:
            tage[-1].append(entry)

    # Sortieren der Liste nach Datum
    tage.sort(key=lambda x: x[0][7])

    # Fügen Sie die Einträge in der gewünschten Reihenfolge in die alle_items Liste ein
    alle_items = []
    for tag in tage:
        for item in tag:
            alle_items.append(
                [item[0], item[1], item[2], item[3], item[4], item[5], item[6]]
            )

    return render_template(
        "shiplist.html",
        user=current_user,
        list_id=list_id,
        alle_items=alle_items,
        andere_items=andere_items,
        first_day=first_day,
        last_day=last_day,
        new_registration=new_registration,
        config=Config,
    )


@blueprint.route("/delete_group/<group_id>", methods=["GET", "POST"])
@enabled_required
def delete_group(group_id):
    app.logger.debug("/access/delete_group/<group_id> wurde angesurft")
    group = EinkaufslisteGroup.query.filter_by(group_id=group_id).first()

    if group is None:
        flash("Gruppe existiert nicht!", "warning")
        return redirect(url_for("Einkaufsliste.group"))

    if current_user.id != group.group_owner:
        flash("Du bist nicht der Gruppen-Besitzer!", "warning")
        return redirect(url_for("Einkaufsliste.group"))

    all_list_of_group = EinkaufslisteList.query.filter_by(group_id=group.group_id).all()
    for list in all_list_of_group:
        delete_list(list.list_id)

    db.session.delete(group)
    db.session.commit()
    flash("Die Gruppe wurde erfolgreich gelöscht!", "success")
    return redirect(url_for("Einkaufsliste.group"))


@blueprint.route("/delete_list/<list_id>", methods=["GET", "POST"])
@enabled_required
def delete_list(list_id):
    app.logger.debug("/access/delete_list/<list_id> wurde angesurft")
    other = EinkaufslisteOther.query.filter_by(list_id=list_id).all()
    items = EinkaufslisteItem.query.filter_by(list_id=list_id).all()
    list = EinkaufslisteList.query.filter_by(list_id=list_id).all()
    # Die Einkaufsliste so wie die einträge der items und oder müssen gelöscht werden
    # Fange von unten nach oben an
    # lösche other item
    for i in other:
        db.session.delete(i)
    # lösche items
    for i in items:
        db.session.delete(i)
    # lösche einkaufsliste
    for i in list:
        db.session.delete(i)
    # bestätige die löschsequenz
    db.session.commit()

    app.logger.info(
        f"Die Einkaufsliste {list_id} wurde durch {current_user.username} gelöscht"
    )
    flash(
        f"Die Einkaufsliste {list_id} wurde durch {current_user.username} gelöscht",
        "success",
    )

    return redirect(url_for("Einkaufsliste.home"))


@blueprint.route("/group", methods=["GET", "POST"])
@enabled_required
def group():
    app.logger.debug("group wurde angesurft")
    new_registration = User.query.filter(User.user_enable.is_(None)).count()

    # Erstelle eine Abfrage, die alle relevanten Gruppen basierend auf Sichtbarkeit und Mitgliedschaft zurückgibt
    if current_user.is_admin == True:
        all_groups = (
            db.session.query(EinkaufslisteGroup)
            .join(User, EinkaufslisteGroup.group_owner == User.id)
            .outerjoin(group_membership, EinkaufslisteGroup.group_id == group_membership.c.group_id)
            .distinct()
        )
    else:
        all_groups = (
            db.session.query(EinkaufslisteGroup)
            .join(User, EinkaufslisteGroup.group_owner == User.id)
            .outerjoin(group_membership, EinkaufslisteGroup.group_id == group_membership.c.group_id)
            .filter(
                or_(
                    EinkaufslisteGroup.group_visible == True,  # Gruppen, die sichtbar sind
                    EinkaufslisteGroup.group_owner
                    == current_user.id,  # Gruppen, deren Besitzer der aktuelle Benutzer ist
                    group_membership.c.user_id
                    == current_user.id,  # Gruppen, in denen der Benutzer Mitglied ist
                )
            )
            .distinct()
            .all()
        )

    return render_template(
        "group.html",
        user=current_user,
        new_registration=new_registration,
        config=Config,
        all_groups=all_groups,
    )


@blueprint.route("/request_join_group/<int:group_id>", methods=["GET", "POST"])
@enabled_required
def request_join_group(group_id):
    app.logger.debug("request_join_group wurde angesurft")
    new_registration = User.query.filter(User.user_enable.is_(None)).count()
    group = EinkaufslisteGroup.query.get(group_id)

    if group is None:
        flash("Diese Gruppe existiert nicht!", "warning")
        return redirect(url_for("einkauf.group"))

    # Prüfe ob der Benutzer Mitglied ist
    member_entry = (
        db.session.query(group_membership)
        .filter(
            group_membership.c.user_id == current_user.id,
            group_membership.c.group_id == group_id,
        )
        .first()
    )

    user_in_group = member_entry is not None

    if not group.group_visible and not user_in_group:
        flash("Diese Gruppe existiert nicht!", "warning")
        return redirect(url_for("einkauf.group"))

    if request.method == "POST":
        flash(
            "Deine Anfrage wurde erfolgreich an den Gruppen-Besitzer gesendet! Diese Funktion ist noch nicht implementiert!",
            "success",
        )
        return redirect(url_for("einkauf.group"))

    return render_template(
        "request_join_group.html",
        user=current_user,
        new_registration=new_registration,
        config=Config,
        group=group,
    )


@blueprint.route("/join_or_leave_group/<int:group_id>", methods=["GET", "POST"])
@enabled_required
def join_or_leave_group(group_id):
    app.logger.debug("join_group wurde angesurft")
    new_registration = User.query.filter(User.user_enable.is_(None)).count()
    group = EinkaufslisteGroup.query.get(group_id)

    if group is None:
        flash("Diese Gruppe existiert nicht!", "warning")
        return redirect(url_for("einkauf.group"))

    # Prüfe ob der Benutzer Mitglied ist
    member_entry = (
        db.session.query(group_membership)
        .filter(
            group_membership.c.user_id == current_user.id,
            group_membership.c.group_id == group_id,
        )
        .first()
    )

    user_in_group = member_entry is not None

    if not group.group_public and not user_in_group:
        flash("Es muss eine Anfrage an den Gruppen-Owner gesendet werden!", "warning")
        return redirect(url_for("einkauf.request_join_group", group_id=group_id))

    if not group.group_visible and not user_in_group:
        flash("Diese Gruppe existiert nicht!", "warning")
        return redirect(url_for("einkauf.group"))

    if request.method == "POST":
        if not user_in_group:
            # Füge benutzer in die Gruppe hinzu
            new_member = group_membership.insert().values(
                user_id=current_user.id, group_id=group_id
            )
            db.session.execute(new_member)
            db.session.commit()
            flash(
                f"Du bist erfolgreich in die Gruppe {group.group_name} beigetreten!",
                "success",
            )
        else:
            # Entferne Benutzer
            db.session.execute(
                delete(group_membership).where(
                    group_membership.c.user_id == current_user.id,
                    group_membership.c.group_id == group_id,
                )
            )
            db.session.commit()
            flash(
                f"Du hast erfolgreich die Gruppe {group.group_name} verlassen!",
                "success",
            )

        return redirect(url_for("einkauf.group"))

    return render_template(
        "join_or_leave_group.html",
        user=current_user,
        new_registration=new_registration,
        config=Config,
        group=group,
        user_in_group=user_in_group,
    )


@blueprint.route("/edit_group/<group_id>", methods=["GET", "POST"])
@enabled_required
def edit_group(group_id):
    app.logger.debug("edit_group wurde angesurft")
    new_registration = User.query.filter(User.user_enable.is_(None)).count()
    # Hier fehlt noch die Filterung nach Gruppen, bei welchen visibal = true ist, allerdings sollen die Eigene Gruppen angezeigt werden
    group = EinkaufslisteGroup.query.get(group_id)
    form = ModifyGroup(obj=group)
    form.group_members.choices = [
        (user.id, user.username)
        for user in User.query.filter(User.id != current_user.id).all()
    ]

    # 7. Gruppe existiert nicht
    # --> Gruppe nicht gefunden
    if group is None:
        flash("Diese Gruppe existiert nicht!", "warning")
        return redirect(url_for("einkauf.group"))

    # Setzen der Auswahlmöglichkeiten und der Standardwerte für die Gruppenmitglieder
    form.group_members.data = [user.id for user in group.group_members]

    if current_user.id != group.group_owner and not current_user.is_admin:
        # Erstellen Sie eine Subquery, die prüft, ob eine Mitgliedschaft existiert
        # Prüfe ob der Benutzer Mitglied ist
        member_entry = (
            db.session.query(group_membership)
            .filter(
                group_membership.c.user_id == current_user.id,
                group_membership.c.group_id == group_id,
            )
            .first()
        )

        user_in_group = member_entry is not None

        # Szenarion um abzudeken
        # 1. User ist Mitglied der Gruppe, die Gruppe ist öffentlich
        # Benutzer kann die Gruppe verlassen
        # 2. User ist nicht Mitglied der Gruppe, aber die Gruppe ist öffentlich
        # Benutzer kann die Gruppe beitreten (ohne Admin zu fragen)
        if group.group_public:
            return redirect(url_for("einkauf.join_or_leave_group", group_id=group_id))

        # 3. User ist Mitglied der Gruppe, aber die Gruppe ist nicht öffentlich
        # Benutzer kann die Gruppe verlassen
        if not group.group_public and user_in_group:
            return redirect(url_for("einkauf.join_or_leave_group", group_id=group_id))

        # 4. User ist nicht Mitglied der Gruppe, aber die Gruppe ist nicht öffentlich
        # Benutzer kann Anfrage an Admin stellen, der er in die Gruppe beitreten kann
        if not group.group_public and not user_in_group:
            flash(
                "Es muss eine Anfrage an den Gruppen-Owner gesendet werden!", "warning"
            )
            return redirect(url_for("einkauf.request_join_group", group_id=group_id))
        # 5. User ist Mitglied der Gruppe, aber die Gruppe ist nicht sichtbar
        # Benutzer kann die Gruppe verlassen
        if not group.group_visible and user_in_group:
            return redirect(url_for("einkauf.join_or_leave_group", group_id=group_id))

        # 6. User ist nicht Mitglied der Gruppe, aber die Gruppe ist nicht sichtbar
        # Bei Anfrage an die Seite, kommt die Meldung --> Gruppe nicht gefunden
        if not group.group_visible and not user_in_group:
            flash("Diese Gruppe existiert nicht!", "warning")
            return redirect(url_for("einkauf.group"))

    if form.validate_on_submit():
        if EinkaufslisteGroup.query.filter(
            EinkaufslisteGroup.group_name == form.group_name.data, EinkaufslisteGroup.group_id != group_id
        ).first():
            flash("Dieser Gruppenname existiert bereits!", "warning")
            return redirect(url_for("edit_group", group_id=group_id))

        group.group_name = form.group_name.data
        group.group_public = form.group_public.data
        group.group_visible = form.group_visible.data

        # Update der Mitglieder
        current_member_ids = {member.id for member in group.group_members}
        new_member_ids = set(form.group_members.data)

        # Mitglieder entfernen, die nicht mehr in der neuen Liste sind
        for member in group.group_members[:]:
            if member.id not in new_member_ids:
                group.group_members.remove(member)

        # Neue Mitglieder hinzufügen
        for user_id in new_member_ids:
            if user_id not in current_member_ids:
                user = User.query.get(user_id)
                if user:
                    group.group_members.append(user)

        try:
            db.session.commit()
            flash(
                "Die Gruppeneinstellungen wurden erfolgreich aktualisiert.", "success"
            )
        except IntegrityError:
            db.session.rollback()
            flash(
                "Ein Fehler ist aufgetreten. Einige Benutzer sind möglicherweise schon Mitglieder.",
                "error",
            )

        return redirect(url_for("Einkaufsliste.group"))
    return render_template(
        "modify_group.html",
        user=current_user,
        new_registration=new_registration,
        config=Config,
        form=form,
        group=group,
    )
