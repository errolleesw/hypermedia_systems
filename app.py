# ./app.py

from flask import Flask, flash, redirect, render_template, request
from contacts_model import Contact


app = Flask(__name__)

app.secret_key = b'hypermedia rocks' # this is needed for flash to work.


# Load contacts from JSON into the mock database
Contact.load_db()

@app.route("/")
def index():
    return redirect("/contacts")


@app.route("/contacts")
def contacts():
    search = request.args.get("q")
    page = int(request.args.get("page", 1))
    if search is not None:
        contacts_set = Contact.search(search)
        print(contacts_set)
    else:
        contacts_set = Contact.all(page)
        print(contacts_set)
    return render_template("index.html",
      contacts=contacts_set, page=page)

@app.route("/contacts/new", methods=['GET'])
def contacts_new_get():
    return render_template("new.html", contact=Contact())

@app.route("/contacts/new", methods=['POST'])
def contacts_new():
    c = Contact(
      None, # no need to populate id.
      request.form['first_name'],
      request.form['last_name'],
      request.form['phone'],
      request.form['email'])
    if c.save(): 
        flash("Created New Contact!")
        return redirect("/contacts") 
    else:
        return render_template("new.html", contact=c)
    
@app.route("/contacts/<contact_id>")
def contacts_view(contact_id=0):
    contact = Contact.find(contact_id)
    return render_template("show.html", contact=contact)

@app.route("/contacts/<contact_id>/edit", methods=["GET"])
def contacts_edit_get(contact_id=0):
    contact = Contact.find(contact_id)
    return render_template("edit.html", contact=contact)

@app.route("/contacts/<contact_id>/edit", methods=["POST"])
def contacts_edit_post(contact_id=0):
    c = Contact.find(contact_id)
    c.update(
      request.form['first_name'],
      request.form['last_name'],
      request.form['phone'],
      request.form['email'])
    if c.save(): 
        flash("Updated Contact!")
        return redirect("/contacts/" + str(contact_id)) 
    else:
        return render_template("edit.html", contact=c) 
    
@app.route("/contacts/<contact_id>", methods=["DELETE"])
def contacts_delete(contact_id=0):
    contact = Contact.find(contact_id)
    contact.delete()
    flash("Deleted Contact!")
    return redirect("/contacts", 303) # update to use the 303 response code to issue a GET to the new location instead of a DELETE.

# validating emails on the serverside.
@app.route("/contacts/<contact_id>/email", methods=["GET"])
def contacts_email_get(contact_id=0):
    c = Contact.find(contact_id) 
    c.email = request.args.get('email') 
    c.validate() 
    return c.errors.get('email') or "" 