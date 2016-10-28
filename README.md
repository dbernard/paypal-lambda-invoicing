# AWS Lambda Invoicing

Simple Lambda code to create PayPal invoices from a CSV containing customer
info.


## Lambda build

To build a package zip to deploy to lambda, make sure all placeholder values and
auth configurations are set, then run the provided script:

```
./lambdabuild.sh
```

This should create a ZIP file in the top level directory to deploy to Lambda.

