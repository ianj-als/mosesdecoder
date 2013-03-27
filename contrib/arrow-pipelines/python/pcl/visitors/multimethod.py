#
# Multi-method decorator
#
registry = {}
class_registry = {}

def __make_key(klass, types):
    keys = [klass]
    keys.extend(types)
    return tuple(keys)

#
# Decorate methods with this, whose arguments are the types
#
def multimethod(*types):
    def decorator(method):
        global class_registry
        class_registry[types] = method
        def wrapper(target_obj, *args, **kwargs):
            global registry
            keys = __make_key(target_obj.__class__, [arg.__class__ for arg in args])
            target_method = registry[keys]
            if target_method:
                return target_method(target_obj, *args, **kwargs)
            else:
                raise LookupError("Method not registered for type %s" % arg_types)
        return wrapper
    return decorator

#
# Decorate the class whose methods a decorated with the multi-method decorator
#
def multimethodclass(klass):
    global class_registry
    registrations = {__make_key(klass, types) : class_registry[types] for types in class_registry}
    registry.update(registrations)
    class_registry = {}
    return klass
