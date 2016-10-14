from flask import Flask, render_template, request, redirect, Markup
from wiki_linkify import wiki_linkify
import pg, datetime, markdown
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
        page_content = query[0].page_content
        wiki_linkified_content = wiki_linkify(page_content)
        print page_content
        return render_template(
            "placeholderpage.html",
            page_name = page_name,
            query=query[0],
            page_content = Markup(markdown.markdown(wiki_linkified_content))
        )

@app.route("/<page_name>/edit")
def edit_page(page_name):
    query = db.query("select * from page where title = '%s'" % page_name).namedresult()
    if len(query) == 0:
        return render_template(
            "edit.html",
            page_name=page_name,
            query=query
        )
    else:
        return render_template(
            "edit.html",
            page_name=page_name,
            query=query[0]
        )

@app.route("/<page_name>/save", methods=["POST"])
def save_content(page_name):
    id = request.form.get("id")
    page_content = request.form.get("page_content")
    author_name = request.form.get("author_name")
    last_mod_date = request.form.get("last_mod_date")
    action = request.form.get("submit_button")
    if action == "update":
        db.update(
            "page", {
                "id": id,
                "page_content": page_content,
                "author_name": author_name,
                "last_mod_date": last_mod_date,
            }
        )
    elif action == "create":
        db.insert (
            "page",
            title=page_name,
            page_content=page_content,
            author_name=author_name
        )
    else:
        pass
    return redirect("/%s" % page_name)

@app.route("/AllPages")
def all_pages():
    query = db.query("select title from page order by title;").namedresult()
    return render_template(
        "allpages.html",
        query=query
    )

@app.route("/search")
def search_pages():
    search = request.args.get("search")
    page = db.query("select title from page where title = '%s'" % search).namedresult()
    print search
    print page
    if len(page) == 0:
        return redirect("/%s" % search)
    else:
        return render_template(
            "search.html",
            search=search,
            page=page
        )

if __name__ == "__main__":
    app.run(debug=True)
