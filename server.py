import flask
import pydantic
from flask import jsonify, request
from flask.views import MethodView

from models import Advertisement, Session
from schema import CreateAds, UpdateAds

app = flask.Flask("app")


class HttpError(Exception):
    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


def validate(validation_schema, validation_data):
    try:
        model = validation_schema(**validation_data)
        return model.dict(exclude_none=True)
    except pydantic.ValidationError as err:
        raise HttpError(400, err.errors())


@app.errorhandler(HttpError)
def error_handler(er: HttpError):
    response = jsonify({"status": "error", "description": er.message})
    response.status_code = er.status_code
    return response


def get_ad(session, ad_id):
    ad = session.get(Advertisement, ad_id)
    if ad is None:
        raise HttpError(404, "ad not found")
    return ad


class AdView(MethodView):
    def get(self, ad_id: int):
        with Session() as session:
            ad = get_ad(session, ad_id)
            return jsonify(
                {
                    "id": ad.id,
                    "title": ad.title,
                    "creation_time": ad.creation_time,
                    "description": ad.description,
                    "owner": ad.owner,
                }
            )

    def patch(self, ad_id: int):
        validated_json = validate(UpdateAds, request.json)
        with Session() as session:
            ad = get_ad(session, ad_id)
            for field, value in validated_json.items():
                setattr(ad, field, value)
            session.add(ad)
            session.commit()
            return jsonify({"status": "success"})

    def post(self):
        validated_json = validate(CreateAds, request.json)
        with Session() as session:
            ad = Advertisement(**validated_json)
            session.add(ad)
            session.commit()
            return jsonify(
                {
                    "id": ad.id,
                    "title": ad.title,
                    "owner": ad.owner,
                    "description": ad.description,
                }
            )

    def delete(self, ad_id: int):
        with Session() as session:
            ad = get_ad(session, ad_id)
            session.delete(ad)
            session.commit()
            return jsonify({"status": "success"})


ad_view = AdView.as_view("ads")

app.add_url_rule(
    "/advertisement/<int:ad_id>", view_func=ad_view, methods=["GET", "DELETE", "PATCH"]
)
app.add_url_rule("/advertisement/", view_func=ad_view, methods=["POST"])

if __name__ == "__main__":
    app.run()
