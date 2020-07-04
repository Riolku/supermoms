from supermoms import db

# Helper mixin for database classes

class Helper:
  
  @classmethod
  def add(cls, _flush = True, **kwargs):
    
    obj = cls(**kwargs)
    db.session.add(obj)
    
    if _flush: db.session.commit()
    
    return obj
  
  @classmethod
  def remove(cls, obj, _flush = True):
    db.session.delete(obj)
    
    if _flush: db.session.commit()