import dark_pattern_controller


def register_routes(app):
    app.register_blueprint(dark_pattern_controller.dark_pattern)
    return app
