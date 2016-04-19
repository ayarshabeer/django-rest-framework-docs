import json
import inspect
from django.contrib.admindocs.views import simplify_regex
from django.utils.encoding import force_str


class ApiEndpoint(object):

    def __init__(self, pattern, regex_pattern=None,is_root=True):
        self.pattern = pattern
        self.callback = pattern.callback
        # self.name = pattern.name
        self.docstring = self.__get_docstring__()
        self.name_parent = simplify_regex(regex_pattern).strip('/').split("/")[0].strip() if  not is_root else "root"
        self.path = simplify_regex(regex_pattern)
        self.allowed_methods = self.__get_allowed_methods__()
        # self.view_name = pattern.callback.__name__
        self.errors = None
        self.fields = self.__get_serializer_fields__()
        self.fields_json = self.__get_serializer_fields_json__()
        self.permissions = self.__get_permissions_class__()
    def __get_allowed_methods__(self):
        return [force_str(m).upper() for m in self.callback.cls.http_method_names if hasattr(self.callback.cls, m)]

    def __get_docstring__(self):
        return inspect.getdoc(self.callback)

    def __get_permissions_class__(self):
        for perm_class in self.pattern.callback.cls.permission_classes:
            return perm_class.__name__

    def __get_serializer_fields__(self):
        fields = []

        if hasattr(self.callback.cls, 'serializer_class') and hasattr(self.callback.cls.serializer_class, 'get_fields'):
            serializer = self.callback.cls.serializer_class
            if hasattr(serializer, 'get_fields'):
                try:
                    fields = [{
                        "name": key,
                        "type": str(field.__class__.__name__),
                        "required": field.required
                    } for key, field in serializer().get_fields().items()]
                except KeyError as e:
                    self.errors = e
                    fields = []

                # FIXME:
                # Show more attibutes of `field`?

        return fields

    def __get_serializer_fields_json__(self):
        # FIXME:
        # Return JSON or not?
        return json.dumps(self.fields)
