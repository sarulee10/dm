from datetime import date


db.define_table(
    'role',
        Field('name', 'string', unique=True, requires=[IS_NOT_EMPTY()] ),
        Field('status', 'string', default='Actived', requires=IS_IN_SET(['Actived', 'Pending'])),
        Field('create_at', 'datetime', default=request.now, writable=False),
        Field('update_at', 'datetime', default=request.now, update=request.now, writable=False)
)

db.define_table(
    'user_account',
        Field('username', 'string', unique=True, requires=[IS_NOT_EMPTY()] ),
        Field('password', 'string'),
        Field('role_id', 'reference role', requires=IS_IN_DB(db, 'role.id', '%(name)s'), ondelete='CASCADE'),
        Field('fullname', 'string'),
        Field('tel', 'string'),
        Field('address', 'string'),
        Field('status', 'string', default='Actived', requires=IS_IN_SET(['Actived', 'Pending'])),
        Field('create_at', 'datetime', default=request.now, writable=False),
        Field('update_at', 'datetime', default=request.now, update=request.now, writable=False)
)

db.define_table(
    'room',
        Field('room_name', 'string', requires=[IS_NOT_EMPTY()] ),
        Field('room_owner_id', 'reference user_account', requires=IS_IN_DB(db, 'user_account.id', '%(id)s')),
        Field('room_price', 'double'),
        Field('create_at', 'datetime', default=request.now, writable=False),
        Field('update_at', 'datetime', default=request.now, update=request.now, writable=False)
)

db.define_table(
    'invoice',
        Field('invoice_date', 'date', requires=[IS_NOT_EMPTY()] ),
        Field('invoice_year', 'string', requires=[IS_NOT_EMPTY()] ),
        Field('invoice_month', 'string', requires=[IS_NOT_EMPTY()] ),
        Field('room_id','integer', requires=[IS_NOT_EMPTY()] ),
        Field('room_name','string'),
        Field('user_account_id', 'integer', requires=[IS_NOT_EMPTY()] ),
        Field('user_account_fullname', 'string'),
        Field('room_price', 'double'),
        Field('water_bill', 'double'),
        Field('power_bill', 'double'),
        Field('other_bill', 'double'),
        Field('payment_status', 'string', default='Unpaid', requires=IS_IN_SET(['Unpaid', 'Paid'])),
        Field('payment_name','string'),
        Field('payment_amount','double'),
        Field('create_at', 'datetime', default=request.now, writable=False),
        Field('update_at', 'datetime', default=request.now, update=request.now, writable=False)
)