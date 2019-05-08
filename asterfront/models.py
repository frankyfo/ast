# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from ami import AsteriskAmi


class BlackListed(models.Model):
    number = models.CharField(verbose_name='Номер Абонента', max_length=11)
    add_date = models.DateTimeField(auto_now_add=True)
    cause = models.CharField(verbose_name='Причина', max_length=512)
    creator = models.ForeignKey(User)

    def save(self, *args, **kwargs):
        if AsteriskAmi().put_db('blacklist', self.number, self.cause):
            super(BlackListed, self).save(*args, **kwargs) # Call the "real" save() method.
        else:
            raise ValueError

    def delete(self, *args, **kwargs):
        if AsteriskAmi().del_db('blacklist', self.number):
            super(BlackListed, self).delete(*args, **kwargs) # Call the "real" save() method.
        else:
            raise ValueError


class Abonent(models.Model):
    oper_id = models.IntegerField()
    abonent = models.CharField(primary_key=True, max_length=15)

    class Meta:
        managed = False
        db_table = 'abonent'


class Agents(models.Model):
    oper_id = models.IntegerField()
    phone = models.IntegerField()
    queue = models.IntegerField()
    penalty = models.IntegerField()
    status = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'agents'


class CallList(models.Model):
    date = models.DateTimeField()
    from_number = models.BigIntegerField()
    to_number = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'call_list'


class CallsHistory(models.Model):
    calldate = models.DateTimeField()
    task_id = models.IntegerField()
    client_id = models.CharField(max_length=30)
    op_id = models.IntegerField()
    phone = models.CharField(max_length=15)
    call_status = models.CharField(max_length=100)
    duration = models.IntegerField()
    success = models.IntegerField()
    uniqueid = models.CharField(max_length=100)
    event_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'calls_history'


class Cdr(models.Model):
    calldate = models.DateTimeField()
    clid = models.CharField(max_length=80)
    src = models.CharField(max_length=80)
    dst = models.CharField(max_length=80)
    dcontext = models.CharField(max_length=80)
    channel = models.CharField(max_length=80)
    dstchannel = models.CharField(max_length=80)
    lastapp = models.CharField(max_length=80)
    lastdata = models.CharField(max_length=80)
    duration = models.IntegerField()
    billsec = models.IntegerField()
    disposition = models.CharField(max_length=45)
    amaflags = models.IntegerField()
    accountcode = models.CharField(max_length=20)
    uniqueid = models.CharField(max_length=32)
    userfield = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'cdr'


class Lead(models.Model):
    date = models.DateTimeField()
    tel = models.CharField(max_length=13)
    lead = models.TextField()

    class Meta:
        managed = False
        db_table = 'lead'


class Operators(models.Model):
    pincode = models.IntegerField()
    oper_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'operators'


class QueueLog(models.Model):
    time = models.CharField(max_length=26)
    callid = models.CharField(max_length=32)
    queuename = models.CharField(max_length=32)
    agent = models.CharField(max_length=32)
    event = models.CharField(max_length=32)
    data1 = models.CharField(max_length=100)
    data2 = models.CharField(max_length=100)
    data3 = models.CharField(max_length=100)
    data4 = models.CharField(max_length=100)
    data5 = models.CharField(max_length=100)
    queue_mark = models.IntegerField(blank=True, null=True)
    mark_context = models.IntegerField()

    def get_caller(self):
        call_cdr = Cdr.objects.using('asterisk').filter(uniqueid=self.callid).last()
        return call_cdr.src if call_cdr else None

    def __str__(self):
        return self.time

    def __unicode__(self):
        return self.time

    class Meta:
        managed = False
        db_table = 'queue_log'


class Regions(models.Model):
    region = models.IntegerField()
    callcenter = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'regions'
