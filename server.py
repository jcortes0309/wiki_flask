from flask import Flask, render_template, request, redirect
import pg, datetime
app = Flask("wiki")

db = pg.DB(dbname="wiki")
db.debug = True

@app.route("/")
def home_page():
    return redirect("/homepage")

@app.route("/<page_name>")
def place_holder(page_name):
    query = db.query("select * from page where title = '%s'" % page_name).namedresult()
    if len(query) == 0:
        return render_template(
            "placeholderpage.html",
            page_name = page_name,
            query=query
        )
    else:
        return render_template(
            "placeholderpage.html",
            page_name = page_name,
            query=query[0]
        )

@app.route("/<page_name>/edit")
def edit_page(page_name):
    query = db.query("select * from page where title = '%s'" % page_name).namedresult()
    print query
    return render_template(
        "edit.html",
        page_name=page_name
    )

@app.route("/<page_name>/save", methods=["POST"])
def save_content(page_name):
    print page_name
    page_content = request.form.get("page_content")
    author_name = request.form.get("author_name")
    db.insert (
        "page",
        title=page_name,
        page_content=page_content,
        author_name=author_name
    )
    return redirect("/%s" % page_name)

if __name__ == "__main__":
    app.run(debug=True)
