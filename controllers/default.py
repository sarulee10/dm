# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------
from datetime import datetime, timedelta
#from gluon.tools import Auth
#import calendar
import json
import hashlib
import os

from pprint import pprint



# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin group
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki()

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)




def index():
    redirect(URL('invoice_user' ) )
    return locals()

def check_login():
    if session.user_id is None:
        session.flash = 'ใส่ข้อมูลเพื่อเข้าสู่ระบบ...'
        redirect(URL('login' ) )
    return locals()

def login():

    return locals()

def logout_process():
    session.clear()
    session.renew()
    redirect(URL('login' ) )
    return locals()

def login_process():
    username = request.vars.username
    password = request.vars.password

    if username :
        selected_user_account = db(
            db.user_account.username == username
        ).select().first()

        if selected_user_account is None :
            session.flash = 'ไม่เจอชื่อผู้ใช้งานนี้...'
            redirect(URL('login' ) )

        checkpassword = selected_user_account.password
        if checkpassword == password :
            session.user_id = selected_user_account.id
            session.role_id = selected_user_account.role_id
            session.username = selected_user_account.username

            selected_user_account_role_name = db(
                db.role.id == selected_user_account.role_id
            ).select().first()

            if selected_user_account_role_name:
                session.role_name = selected_user_account_role_name.name


            session.flash = 'เข้าสู่ระบบสำเร็จ...'
            redirect(URL('invoice_user'))

    session.flash = 'เข้าสู่ระบบไม่สำเร็จ...'
    redirect(URL('login') )

    return locals()




def user_account():

    # inner join
    result = db(
        (db.user_account.role_id == db.role.id)
        ).select(orderby  = [db.user_account.role_id,db.user_account.username])

    result_role = db(
        (db.role)
        ).select()

    return locals()

def user_account_delete_process():
    user_account_id=request.vars.user_account_id
    if user_account_id:
        result = db(
            (db.user_account.id==user_account_id)
            ).delete()
        if result:
            session.flash='ข้อมูลถูกลบแล้ว...'
            redirect(URL('user_account'))
        session.flash='ข้อมูลไม่สามารถลบได้เนื่องจากไม่เจอรหัสผู้ใช้...'
        redirect(URL('user_account'))
    session.flash='ข้อมูลไม่สามารถลบได้เนื่องจากไม่มีรหัสผู้ใช้...'
    redirect(URL('user_account'))
    return locals()







def user_account_edit_process():
    user_account_id=request.vars.user_account_id
    user_account_username=request.vars.user_account_username
    user_account_password=request.vars.user_account_password
    user_account_role_id=request.vars.user_account_role_id
    user_account_fullname=request.vars.user_account_fullname
    user_account_tel=request.vars.user_account_tel
    user_account_address=request.vars.user_account_address

    if user_account_id and user_account_fullname:
        result = db(
            (db.user_account.id==user_account_id)
        ).select().first()
        if result is not None:
            result.update_record (
                username = user_account_username,
                password = user_account_password if user_account_password else result.password,
                role_id = user_account_role_id,
                fullname = user_account_fullname,
                tel = user_account_tel,
                address = user_account_address,

            )
            session.flash='ข้อมูลถูกปรับปรุงแล้ว...'
            redirect(URL('user_account'))
        session.flash='ข้อมูลไม่สามารถปรับปรุงได้เนื่องจากไม่เจอชื่อผู้ใช้งานนี้...'
        redirect(URL('user_account'))
    session.flash='ข้อมูลไม่สามารถปรับปรุงได้เนื่องจากไม่มีชื่อผู้ใช้งานและชื่อผู้เช่าให้ครบถ้วน...'
    redirect(URL('user_account'))
    return locals()


def user_account_new_process():
    user_account_username=request.vars.user_account_username
    user_account_password=request.vars.user_account_password
    user_account_role_id=request.vars.user_account_role_id
    user_account_fullname=request.vars.user_account_fullname
    user_account_tel=request.vars.user_account_tel
    user_account_address=request.vars.user_account_address



    if user_account_username and user_account_password and user_account_fullname:
        found_username = db(
            db.user_account.username == user_account_username
        ).count()
        if found_username == 0:
            new_user_account = db.user_account.insert(
                username = user_account_username,
                password = user_account_password,
                role_id = user_account_role_id,
                fullname = user_account_fullname,
                tel = user_account_tel,
                address = user_account_address,
                
            )
            if new_user_account:
                session.flash='ข้อมูลถูกเพิ่มแล้ว...'
                redirect(URL('user_account'))
        session.flash='ข้อมูลไม่สามารถเพิ่มได้เนื่องจากมีชื่อผู้งานนี้แล้ว...'
        redirect(URL('user_account'))
    session.flash='ข้อมูลไม่สามารถเพิ่มได้เนื่องจากไม่มีชื่อผู้งาน,รหัสผ่านและชื่อผู้เช่าให้ครบถ้วน...'
    redirect(URL('user_account'))

    return locals()



def room():

    #left join
    result = db().select(
            db.room.ALL,
            db.user_account.ALL,
            left=[
                db.user_account.on(
                    db.room.room_owner_id == db.user_account.id
                )    
            ]
        ,orderby = db.room.room_name)
    
    result_user_account = db(
        (db.user_account)
    ).select()


    return locals()

def room_delete_process():
    room_id=request.vars.room_id
    if room_id:
        result = db(
            (db.room.id==room_id)
            ).delete()
        if result:
            session.flash='ข้อมูลถูกลบแล้ว...'
            redirect(URL('room'))
        session.flash='ข้อมูลไม่สามารถลบได้...'
        redirect(URL('room'))
    session.flash='ข้อมูลไม่สามารถลบได้เนื่องจากไม่มีรหัสห้องพัก...'
    redirect(URL('room'))
    return locals()




def room_new_process():
    room_name=request.vars.room_name
    room_owner_id=request.vars.room_owner_id
    room_price=request.vars.room_price
    




    if room_name:
        found_room_name = db(
            db.room.room_name == room_name
        ).count()
        if found_room_name == 0:
            new_room = db.room.insert(
                room_name = room_name,
                room_owner_id = room_owner_id,
                room_price = room_price,
            )
            if new_room:
                session.flash='ข้อมูลถูกเพิ่มแล้ว...'
                redirect(URL('room'))
        session.flash='ข้อมูลไม่สามารถเพิ่มได้เนื่องจากมีชื่อห้องพักนี้แล้ว...'
        redirect(URL('room'))
    session.flash='ข้อมูลไม่สามารถเพิ่มได้เนื่องจากไม่มีชื่อห้องพัก...'
    redirect(URL('room'))

    return locals()




def room_edit_process():
    room_id=request.vars.room_id
    room_name=request.vars.room_name
    room_owner_id=request.vars.room_owner_id
    # room_owner_split=request.vars.room_owner.split(":")
    room_price=request.vars.room_price

    # if room_owner is '':
    #     room_owner_id=''
    #     room_owner_fullname=''
    # else:
    #     room_owner_id=room_owner_split[0]
    #     room_owner_fullname=room_owner_split[1]

    # date_today = datetime.now()
    # month_today = date_today.month
    # year_today = date_today.year

    if room_id:
        result = db(
            (db.room.id==room_id)
        ).select().first()
        if result is not None:
            result.update_record (
                room_name = room_name,
                room_owner_id = room_owner_id,
                room_price = room_price,
            )
            session.flash='ข้อมูลถูกปรับปรุงแล้ว...'
            redirect(URL('room'))
        session.flash='ข้อมูลไม่สามารถปรับปรุงได้เนื่องจากไม่เจอรหัสห้องพักนี้...'
        redirect(URL('room'))
    session.flash='ข้อมูลไม่สามารถปรับปรุงได้เนื่องจากไม่มีรหัสห้องพัก...'
    redirect(URL('room'))
    return locals()


def search_room_name(room_owner_id):
    room_owner_id=request.vars.room_owner_id

    result_user_account = db(
        (db.user_account.id==room_owner_id)
    ).select().first()
    return result_user_account.fullname

def invoice():

    date_today = datetime.now().date()
    month_today = date_today.month
    year_today = date_today.year

    invoice_month=request.vars.invoice_month
    invoice_year=request.vars.invoice_year
    
    
    result_user_account = db(
        (db.user_account)
    ).select()
    
    result1=''
    result2=''
    result3=''


    month_list = ["","มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]





    if invoice_month and invoice_year:


        result1 = db(db.room.room_owner_id != db.invoice.user_account_id).select(
            db.room.ALL,
            db.invoice.ALL,
            left=[
                db.invoice.on(
                    (db.invoice.invoice_year == invoice_year)
                    &(db.invoice.invoice_month == invoice_month)
                    &(db.room.id ==  db.invoice.room_id)
                    # &(db.room.room_owner_id == db.invoice.user_account_id)

                    )

            ],orderby  = [db.invoice.id ,db.invoice.invoice_year ,db.invoice.invoice_month ,db.invoice.room_id]
        )

        result2 = db(db.room.room_owner_id == db.invoice.user_account_id).select(
            db.room.ALL,
            db.invoice.ALL,
            left=[
                db.invoice.on(
                    (db.invoice.invoice_year == invoice_year)
                    &(db.invoice.invoice_month == invoice_month)
                    &(db.room.id ==  db.invoice.room_id)
                    &(db.room.room_owner_id == db.invoice.user_account_id)
                    
                    )

            ],orderby  = [db.invoice.id ,db.invoice.invoice_year ,db.invoice.invoice_month ,db.invoice.room_id]
        )

        result3 = db((db.room.room_owner_id != None)&(db.invoice.id == None)).select(
            db.room.ALL,
            db.invoice.ALL,
            left=[
                db.invoice.on(
                    (db.invoice.invoice_year == invoice_year)
                    &(db.invoice.invoice_month == invoice_month)
                    &(db.room.id ==  db.invoice.room_id)
                    &(db.room.room_owner_id == db.invoice.user_account_id)

                    )

            ],orderby  = [db.invoice.invoice_year ,db.invoice.invoice_month ,db.invoice.room_id]
        )
 

    return locals()





def invoice_new_process():
    invoice_date=request.vars.invoice_date
    invoice_month=request.vars.invoice_month
    invoice_year=request.vars.invoice_year
    room_id=request.vars.room_id
    room_name=request.vars.room_name
    user_account_id=request.vars.user_account_id
    user_account_fullname=request.vars.user_account_fullname
    room_price=request.vars.room_price
    water_bill=request.vars.water_bill
    power_bill=request.vars.power_bill
    other_bill=request.vars.other_bill

    if invoice_month and invoice_year and room_id and user_account_id:
        print(invoice_month+"-------"+invoice_year)
        found_invoice = db(
            (db.invoice.invoice_month == invoice_month)
            &(db.invoice.invoice_year == invoice_year)
            &(db.invoice.room_id == room_id)
            &(db.invoice.user_account_id == user_account_id)
        ).count()
        if found_invoice == 0:
            room_invoice_new = db.invoice.insert(
                invoice_date = invoice_date,
                invoice_month = invoice_month,
                invoice_year = invoice_year,
                room_id = room_id,
                room_name = room_name,
                user_account_id = user_account_id,
                user_account_fullname = user_account_fullname,
                room_price = room_price,
                water_bill = water_bill,
                power_bill = power_bill,
                other_bill = other_bill,

                
            )
            session.flash='ข้อมูลถูกเพิ่มแล้ว...'
            redirect(URL('invoice',vars=dict(invoice_month=invoice_month,invoice_year=invoice_year)))
        session.flash='ข้อมูลไม่สามารถเพิ่มได้เนื่องจากมีใบแจ้งค่าเช่านี้แล้ว...'
        redirect(URL('invoice',vars=dict(invoice_month=invoice_month,invoice_year=invoice_year)))
    session.flash='ข้อมูลไม่สามารถเพิ่มได้เนื่องจากมีข้อมูลไม่ครบถ้วน...'
    redirect(URL('invoice',vars=dict(invoice_month=invoice_month,invoice_year=invoice_year)))




    return locals()



def invoice_delete_process():
    invoice_id=request.vars.invoice_id
    invoice_month=request.vars.invoice_month
    invoice_year=request.vars.invoice_year
    
    if invoice_id:
        result = db(
            (db.invoice.id==invoice_id)
            ).delete()
        if result:
            session.flash='ข้อมูลถูกลบแล้ว...'
            redirect(URL('invoice',vars=dict(invoice_month=invoice_month,invoice_year=invoice_year)))
        session.flash='ข้อมูลไม่สามารถลบได้เนื่องจากไม่เจอรหัสใบแจ้งค่าเช่านี้...'
        redirect(URL('invoice',vars=dict(invoice_month=invoice_month,invoice_year=invoice_year)))
    session.flash='ข้อมูลไม่สามารถลบได้เนื่องจากไม่มีรหัสใบแจ้งค่าเช่า...'
    redirect(URL('invoice',vars=dict(invoice_month=invoice_month,invoice_year=invoice_year)))
    return locals()



def invoice_edit_process():
    invoice_id=request.vars.invoice_id
    
    invoice_year=request.vars.invoice_year
    invoice_month=request.vars.invoice_month
    room_id=request.vars.room_id
    room_name=request.vars.room_name
    user_account_id=request.vars.user_account_id
    user_account_fullname=request.vars.user_account_fullname
    room_price=request.vars.room_price
    water_bill=request.vars.water_bill
    power_bill=request.vars.power_bill
    other_bill=request.vars.other_bill

    if invoice_id:
        result = db(
            (db.invoice.id==invoice_id)
        ).select().first()
        if result is not None:
            result.update_record (
                room_price = room_price,
                water_bill = water_bill,
                power_bill = power_bill,
                other_bill = other_bill,
            )
            session.flash='ข้อมูลถูกปรับปรุงแล้ว...'
            redirect(URL('invoice',vars=dict(invoice_month=invoice_month,invoice_year=invoice_year)))
        session.flash='ข้อมูลไม่สามารถปรับปรุงได้เนื่องจากไม่เจอรหัสใบแจ้งค่าเช่านี้...'
        redirect(URL('invoice',vars=dict(invoice_month=invoice_month,invoice_year=invoice_year)))
    session.flash='ข้อมูลไม่สามารถปรับปรุงได้เนื่องจากไม่มีรหัสใบแจ้งค่าเช่า...'
    redirect(URL('invoice',vars=dict(invoice_month=invoice_month,invoice_year=invoice_year)))
    return locals()

def invoice_receipt():
    invoice_id=request.vars.invoice_id
    if invoice_id:
        result = db(
            (db.invoice.id==invoice_id)
        ).select().first()
    return locals()



def payment():
    invoice_month=request.vars.invoice_month
    invoice_year=request.vars.invoice_year

    date_today = datetime.now()
    month_today = date_today.month
    year_today = date_today.year

    result=''

    month_list = ["","มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]

    if invoice_month and invoice_year:
        result = db(
            (db.invoice.invoice_month==invoice_month)
            &(db.invoice.invoice_year==invoice_year)
        ).select(orderby  = [db.invoice.id ,db.invoice.invoice_year ,db.invoice.invoice_month ,db.invoice.room_id])


    return locals()


def payment_edit_process():
    invoice_id=request.vars.invoice_id
    invoice_year=request.vars.invoice_year
    invoice_month=request.vars.invoice_month
    room_id=request.vars.room_id
    room_name=request.vars.room_name
    user_account_id=request.vars.user_account_id
    user_account_fullname=request.vars.user_account_fullname
    payment_amount=request.vars.payment_amount
    payment_name=request.vars.payment_name
    # payment_status=request.vars.payment_status
    # other_bill=request.vars.other_bill

    if payment_amount:
        payment_status = "Paid"
    else:
        payment_status = "Unpaid"


    if invoice_id:
        result = db(
            (db.invoice.id==invoice_id)
        ).select().first()
        if result is not None:
            result.update_record (
                payment_amount = payment_amount,
                payment_name = payment_name,
                payment_status = payment_status,
            )
            session.flash='ข้อมูลถูกปรับปรุงแล้ว...'
            redirect(URL('payment',vars=dict(invoice_month=invoice_month,invoice_year=invoice_year)))
        session.flash='ข้อมูลไม่สามารถปรับปรุงได้เนื่องจากไม่เจอรหัสใบแจ้งค่าเช่านี้...'
        redirect(URL('payment',vars=dict(invoice_month=invoice_month,invoice_year=invoice_year)))
    session.flash='ข้อมูลไม่สามารถปรับปรุงได้เนื่องจากไม่มีรหัสใบแจ้งค่าเช่า...'
    redirect(URL('payment',vars=dict(invoice_month=invoice_month,invoice_year=invoice_year)))
    return locals()

def invoice_user():
    check_login()
    user_id=session.user_id

    month_list = ["","มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]


    if user_id:
        result = db(
            (db.invoice.user_account_id==user_id)
        ).select(orderby  = [db.invoice.invoice_year ,db.invoice.invoice_month ,db.invoice.room_id])
    return locals()




def invoice_list():

    records_json = json.dumps(
        [dict(
            id = idx +1,
            ห้อง = "101",
            ผู่เช่า = "AA",
            ค่าน้ำ = 20,
            ค่าไฟ = 60,
            ค่าห้อง = 4500,
            อื่นๆ = 0,
            บันทึก = '',
        ) for idx, item in enumerate([1]) ],
        default=str,
    )


    companies = []
    company_id = '0'


    return locals()

def payment_list():

    records_json = json.dumps(
        [dict(
            id = idx +1,
            ห้อง = "101",
            ผู่เช่า = "AA",
            ใบแจ้งหนี้ = "100123",
            วันที่ = "2024-03-05",
            ค่าเข่า = 4500,
            ชำระ = 0,
            บันทึก = '',
        ) for idx, item in enumerate([1]) ],
        default=str,
    )




    companies = []
    company_id = '0'
    return locals()

def dashboard():

    return locals()
