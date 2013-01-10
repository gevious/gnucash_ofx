#!/usr/bin/env python

import sys
import os
import errno
import gnucashxml.gnucashxml as gcx
from datetime import datetime
from decimal import Decimal

GEN_DATE = datetime.now().strftime("%Y%m%d%H%M%s")
OFX_HEADER = """<?xmlversion="1.0" encoding="UTF-8" standalone="no"?>
<?OFX OFXHEADER="200" VERSION="200" SECURITY="NONE" OLDFILEUID="NONE" \
NEWFILEUID="NONE"?>
<OFX>
    <SIGNONMSGSRSV1>
        <SONRS>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            <DTSERVER>%s</DTSERVER>
            <LANGUAGE>ENG</LANGUAGE>
        </SONRS>
    </SIGNONMSGSRSV1>
    <BANKMSGSRSRSV1>
        <STMTTRNRS>
            <TRNUID>1</TRNUID>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            <STMTRS>
                <CURDEF>USD</CURDEF>""" % GEN_DATE

if len(sys.argv) < 2:
    print "Usage: ./convert.py <gnucashFile.xml> [ofxOutputDir]"
    exit(1)

# creating output dir if it doesn't exist
output_dir = './output' if len(sys.argv) < 3 else sys.argv[2]
try:
    os.makedirs(output_dir)
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(output_dir):
        pass
    else:
        print "Error creating OFX output dir: {0}".format(e.strerror)
        raise

# Checking for the existance of the gnucash file
try:
    f = open(sys.argv[1], 'r')
    f.close()
except IOError as e:
    print "Error opening gnucash file: {0}".format(e.strerror)
    raise


def valid_type(actype):
    if actype in ("CREDIT", "RECEIVABLE"):
        return "LIABILITY"
    if actype == "BANK":
        return "ASSET"
    return actype

book = gcx.from_filename(sys.argv[1])

for account, subaccounts, splits in book.walk():
    if len(splits) == 0:
        continue
    txt = OFX_HEADER
    account.actype = valid_type(account.actype)
    txt += """
                <BANKACCTFROM>
                    <BANKID>%s</BANKID>
                    <ACCTID></ACCTID>
                    <ACCTTYPE>%s</ACCTTYPE>
                </BANKACCTFROM>
                <BANKTRANLIST>
                    <DTSTART></DTSTART>
                    <DTEND></DTEND>""" % (account.name, account.actype)
    total = Decimal(0)
    for s in splits:
        trn_type = "DEBIT"
        if account.actype in ("ASSET", "EXPENSE"):
            if Decimal(s.value) < 0:
                trn_type = "CREDIT"
        elif Decimal(s.value) >= 0:
            trn_type = "CREDIT"
        total += Decimal(s.value)
        amt = str(abs(Decimal(s.value)))
        fitid = "" if s.memo is None else s.memo
        date = datetime.strftime(s.transaction.date, "%Y%m%d%H%M%S")

        txt += """
                    <STMTTRN>
                        <TRNTYPE>%s</TRNTYPE>
                        <DTPOSTED>%s</DTPOSTED>
                        <TRNAMT>%s</TRNAMT>
                        <FITID>%s</FITID>
                        <MEMO>%s</MEMO>
                    </STMTTRN>""" % \
               (trn_type, date, amt, fitid, s.transaction.description)
    txt += """
                </BANKTRANLIST>
                <LEDGERBAL>
                    <BALAMT>%s</BALAMT>
                    <DTASOF></DTASOF>
                </LEDGERBAL>
            </STMTRS>
        </STMTTRNRS>
    </BANKMSGSRSV1>
</OFX>""" % str(total)
    f = open("%s/%s.ofx" % (output_dir, account.name), "w")
    f.write(txt)
    f.close()
