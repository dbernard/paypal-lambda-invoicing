import csv
import json
import logging
import paypalrestsdk
from paypalrestsdk import Invoice
from datetime import datetime
from dateutil.relativedelta import relativedelta
from boto.s3.connection import S3Connection


log = logging.getLogger()
log.setLevel(logging.INFO)

auth = {}
with open('auth.json', 'rb') as f:
    auth = json.load(f)

paypalrestsdk.configure({
    'client_id': str(auth['paypal']['client_id']),
    'client_secret': str(auth['paypal']['client_secret'])
})

log.info('Connected to PayPal SDK')

CONN = S3Connection()
# Your bucket name
BUCKET = CONN.get_bucket('my-bucket')
# Your customer file name
KEY = BUCKET.get_key('test.csv')

log.info('Connected to S3')


def get_customer_config():
    customers = []

    KEY.get_contents_to_filename('/tmp/tmp.csv')

    with open('/tmp/tmp.csv', 'rb') as f:
        rows = csv.DictReader(f)
        for row in rows:
            customers.append(row)

    return customers

def is_payment_due(today, next_due):
    if today >= next_due:
        return True
    else:
        return False

def set_next_payment_date(date, months):
    interval = relativedelta(months=int(months))
    next_payment = date + interval

    return next_payment

def write_new_file(customers):
    with open('/tmp/test_write.csv', 'wb') as file:
        writer = csv.DictWriter(file, customers[0].keys())
        writer.writeheader()
        writer.writerows(customers)

    KEY.set_contents_from_filename('/tmp/test_write.csv')

def build_invoice(event, context):
    log.info('Getting customer config')
    customers = get_customer_config()

    for customer in customers:
        next_due = datetime.strptime(customer['next_payment_date'], '%m/%d/%Y')
        if not is_payment_due(datetime.now().date(), next_due.date()):
            log.info('No payment due for {} until {}'.format(
                customer['customer_email'], next_due.strftime('%m/%d/%Y')))
            continue

        invoice = Invoice({
            'merchant_info': {
                'email': 'EMAIL@email.com',
                'first_name': 'FIRSTNAME',
                'last_name': 'LASTNAME'
            },
            'billing_info': [
                {
                    'email': customer['customer_email']
                }
            ],
            'items': [
                {
                    'name': 'Hosting Plan',
                    'quantity': 1,
                    'unit_price': {
                        'currency': 'USD',
                        'value': float(customer['plan_rate'])
                    }
                }
            ]
        })

        if invoice.create():
            log.info("Invoice[%s] created successfully" % (invoice.id))
        else:
            log.info(invoice.error)

        if invoice.send():
            log.info("Invoice[%s] sent successfully" % (invoice.id))
        else:
            log.info(invoice.error)

        next_payment = set_next_payment_date(next_due, customer['bill_freq'])
        customer['next_payment_date'] = next_payment.strftime('%m/%d/%Y')

    log.info('Writing new customers file to S3')
    write_new_file(customers)

if __name__ == '__main__':
    build_invoice()


