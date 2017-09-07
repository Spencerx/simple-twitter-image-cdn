import json
import base64
import hashlib
import os.path

from flask import Flask
from flask import request
from flask import render_template
from urllib.parse import urlparse

from database import DB

MEDIA = "./media"
MARK = "data:image/png;base64"

app = Flask(__name__, static_folder="media")
db = DB()


def encod(text):
	h = hashlib.new("md5", text.encode("utf8"))
	return h.hexdigest()


@app.route("/upload", methods=["POST"])
def upload():
	title = request.form.get("title")
	link = request.form.get("link")
	data = request.form.get("data")

	if data and title:
		if data.startswith(MARK):
			image = data.replace(MARK, "")
			try:
				filename = encod(title)
				path = "{media}/{filename}.png".format(media=MEDIA, filename=filename)
				with open(path, "wb+") as fd:
					fd.write(base64.b64decode(image))

				db.add("imagedata", {
					"id": filename,
					"title": title,
					"link": link
				})

				url = urlparse(request.url)
				link = "{s}://{h}/image/{i}".format(s=url.scheme, h=url.netloc, i=filename)
				return json.dumps({
					"success": True,
					"data": {
						"title": title,
						"url": link
					}
				}), 200
			except Exception as err:
				print(err)
				return "Internal server error", 500
		else:
			return "Bad request", 400
	else:
		return "Bad request", 400


@app.route("/image/<string:filename>", methods=["GET"])
def media(filename):
	if filename:
		try:
			data = db.get("imagedata", {"id": filename})
			if len({"title", "link"} & set(data.keys())) is not len({"title", "link"}):
				return "Not found", 404
		except Exception as e:
			print(e)
			return "Internal server error", 500

		url = urlparse(request.url)
		app = url.netloc.replace("img.", "")
		origin = "{s}://{h}".format(s=url.scheme, h=url.netloc)

		filename = "{filename}.png".format(filename=filename)
		path = "{media}/{filename}".format(media=MEDIA, filename=filename)
		if os.path.isfile(path):
			return render_template('image.html', title=data.get("title"), filename=filename, app=app, origin=origin, redirect=data.get("link"))
		else:
			return "Not found", 404
	else:
		return "Bad request", 400


if __name__ == "__main__":
	host = str(os.getenv('HOST', "0.0.0.0"))
	port = int(os.getenv('PORT', 80))

	app.run(host=host, port=port, debug=True)
