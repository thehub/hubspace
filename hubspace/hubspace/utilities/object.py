from hubspace import model

def get_attribute_names(obj):
  '''returns a list of guessed attribute names (columns) from an SQLObject'''
  return [c.name.replace('ID','') for c in obj.sqlmeta.columnList]

def create_object(objecttype, **kwargs):
    '''Helper function to create an object'''
  
    theclass = getattr(model, objecttype)
    attrs = get_attribute_names(theclass)
    remove = [kwarg for kwarg in kwargs if kwarg not in attrs]
    for kwarg in remove:
        del kwargs[kwarg]
    obj = theclass(**kwargs)
    return obj


def obj_of_type(type, id):
    theclass = getattr(model, type)
    return theclass.get(id)


def modify_attributes(obj, attributes_dict):
    for name, value in attributes_dict.iteritems():
        modify_attribute(obj, name, value)
        
    
def modify_attribute(obj, name, value):
    '''Modifies an SQLObject - deprecated we should use the MetaWrapper object to access attributes safely''' 
    attrs = get_attribute_names(obj)
    if name in attrs:
        current_val = getattr(obj, name)
        try:
            current_val = current_val.id
        except:
            pass
        if value != current_val:
            setattr(obj, name, value)
            return value
        return None #what better constant can we use here?
    else:
        return False


def get_attribute(location, type, id, name):
  '''gets an attribute from an SQLObject'''
  theclass = getattr(hubspace.model,type)
  obj = theclass.get(id)
  return getattr(obj,name)
