class Wireer(object):
    def __init__(self):
        self.calls = []

    def route(self, *args, **kwargs):
        def decorator(view_func):
            self.calls.append((view_func, args, kwargs,))

            return view_func

        return decorator

    def wire_up(self, app):
        for view_func, args, kwargs in self.calls:
            app.route(*args, **kwargs)(view_func)
