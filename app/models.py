from . import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(40), primary_key=True)
    uuid = db.Column(db.String(36), unique=True)
    display_name = db.Column(db.String(60), default=None)
    tenant_id = db.Column(db.String(16), default=None)
    tenant_uuid = db.Column(db.String(36), default=None)
    cookie = db.Column(db.String(), default=None)
    mail = db.Column(db.String(60), default=None)
    company = db.Column(db.String(60), default=None)
    mobile = db.Column(db.String(60), default=None)

    def __repr__(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'display_name': self.display_name,
            'tenant_id': self.tenant_id,
            'tenant_uuid': self.tenant_uuid,
            # 'cookie': self.cookie,
            'mail': self.mail,
            'company': self.company,
            'mobile': self.mobile
        }

    def dict(self):
        return self.__repr__()

    @staticmethod
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def identify(payload):
        return User.query.filter(id=payload['identity']).first()


