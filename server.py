from flask import Flask, render_template, request, redirect, Markup
from wiki_linkify import wiki_linkify
import pg, markdown
from datetime import datetime
app = Flask("wiki")

db = pg.DB(dbname="wiki")
db.debug = True

@app.route("/")
def home_page():
    return redirect("/homepage")

@app.route("/<page_name>")
def place_holder(page_name):
    # Query database looking for existing information for the page called by the user
    query = db.query("select * from page where title = '%s'" % page_name).namedresult()
    # No information was found in the database for the page
    if len(query) == 0:
        return render_template(
            "placeholderpage.html",
            page_name = page_name,
            query=query
        )
    # Information was found in the database for the page
    else:
        query = query[0]
        print query
        # Query database looking for historical information for the page called by the user
        query_history = db.query("select * from page_history where page_id = '%s' order by version_number DESC;" % query.id).namedresult()
        print query_history
        page_content = query.page_content
        wiki_linkified_content = wiki_linkify(page_content)

        if len(query_history) > 0:
            return render_template(
                "placeholderpage.html",
                page_name = page_name,
                query = query,
                page_content = Markup(markdown.markdown(wiki_linkified_content)),
                query_history = query_history
            )
        else:
            return render_template(
                "placeholderpage.html",
                page_name = page_name,
                query = query,
                page_content = Markup(markdown.markdown(wiki_linkified_content)),
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
    action = request.form.get("submit_button")

    if action == "update":
        query = db.query("select * from page where title = '%s'" % page_name)
        result_list = query.namedresult()
        print result_list
        result_list = result_list[0]
        print result_list
        db.insert(
            "page_history",
            title = page_name,
            page_content = result_list.page_content,
            author_name = result_list.author_name,
            last_mod_date = result_list.last_mod_date,
            page_id = result_list.id,
            version_number = result_list.version_number
        )

    current_time = datetime.now()
    last_mod_time = current_time.strftime('%Y/%m/%d %H:%M:%S')
    id = request.form.get("id")
    page_content = request.form.get("page_content")
    author_name = request.form.get("author_name")
    last_mod_date = request.form.get("last_mod_date")
    version_number = request.form.get("version_number")
    if action == "update":
        db.update(
            "page", {
                "id": id,
                "page_content": page_content,
                "author_name": author_name,
                "last_mod_date": last_mod_time,
                "version_number": int(version_number) + 1
            }
        )
    elif action == "create":
        db.insert (
            "page",
            title = page_name,
            page_content = page_content,
            author_name = author_name,
            last_mod_date = last_mod_time,
            version_number = 1
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
